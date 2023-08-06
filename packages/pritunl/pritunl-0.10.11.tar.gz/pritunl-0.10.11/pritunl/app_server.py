from constants import *
from cache import cache_db, persist_db
from event import Event
from config import Config
import utils
import flask
import cherrypy.wsgiserver
import cherrypy.wsgiserver.ssl_builtin
import os
import logging
import logging.handlers
import signal
import time
import json
import urllib2
import threading
import subprocess
import base64
import socket
import uuid

logger = None

class AppServer(Config):
    # deprecated = password, dh_param_bits
    bool_options = {'debug', 'log_debug', 'auto_start_servers',
        'get_public_ip', 'get_notifications', 'inline_certs', 'ssl',
        'static_cache', 'pooler'}
    int_options = {'port', 'session_timeout', 'key_bits', 'dh_param_bits',
        'org_pool_size', 'user_pool_size', 'server_user_pool_size',
        'server_pool_size', 'server_log_lines'}
    path_options = {'log_path', 'db_path', 'www_path', 'data_path',
        'server_cert_path', 'server_key_path'}
    str_options = {'bind_addr', 'password', 'public_ip_server',
        'notification_server', 'dh_param_bits_pool'}
    list_options = {'dh_param_bits_pool'}
    default_options = {
        'auto_start_servers': True,
        'get_public_ip': True,
        'inline_certs': True,
        'get_notifications': True,
        'ssl': True,
        'static_cache': True,
        'bind_addr': DEFAULT_BIND_ADDR,
        'port': DEFAULT_PORT,
        'session_timeout': DEFAULT_SESSION_TIMEOUT,
        'key_bits': DEFAULT_KEY_BITS,
        'dh_param_bits': DEFAULT_DH_PARAM_BITS,
        'pooler': True,
        'org_pool_size': DEFAULT_ORG_POOL_SIZE,
        'user_pool_size': DEFAULT_USER_POOL_SIZE,
        'server_user_pool_size': DEFAULT_SERVER_USER_POOL_SIZE,
        'server_pool_size': DEFAULT_SERVER_POOL_SIZE,
        'dh_param_bits_pool': DEFAULT_DH_PARAM_BITS_POOL,
        'server_log_lines': DEFAULT_SERVER_LOG_LINES,
        'db_path': DEFAULT_DB_PATH,
        'www_path': DEFAULT_WWW_PATH,
        'data_path': DEFAULT_DATA_PATH,
        'public_ip_server': DEFAULT_PUBLIC_IP_SERVER,
        'notification_server': DEFAULT_NOTIFICATION_SERVER,
    }
    read_env = True

    def __init__(self):
        Config.__init__(self)
        self.app = None
        self.interrupt = False
        self.public_ip = None
        self.conf_path = DEFAULT_CONF_PATH
        self.notification = ''
        self.www_state = OK
        self.vpn_state = OK
        self.sub_active = False
        self.sub_status = None
        self.sub_amount = None
        self.sub_period_end = None
        self.sub_cancel_at_period_end = None
        self.openssl_heartbleed = not utils.check_openssl()
        self.local_api_key = uuid.uuid4().hex

    def __getattr__(self, name):
        if name == 'web_protocol':
            if not self.ssl:
                return 'http'
            return 'https'
        elif name == 'password_data':
            if self.password[:2] == '1$':
                pass_split = self.password.split('$')
                return (1, pass_split[1], pass_split[2])
            else:
                return (0, PASSWORD_SALT_V0, self.password)
        elif name == 'ssl':
            if self.debug:
                return False
        return Config.__getattr__(self, name)

    def load_public_ip(self, attempts=1, timeout=5):
        for i in xrange(attempts):
            if not self.get_public_ip or self.public_ip:
                return
            if i:
                time.sleep(3)
                logger.debug('Retrying get public ip address...')
            logger.debug('Getting public ip address...')
            try:
                request = urllib2.Request(self.public_ip_server)
                response = urllib2.urlopen(request, timeout=timeout)
                self.public_ip = json.load(response)['ip']
                break
            except:
                pass
        if not self.public_ip:
            logger.exception('Failed to get public ip address...')

    def subscription_update(self):
        if SUB_OFF:
            return
        cur_sub_active = self.sub_active
        license = persist_db.get('license')
        if not license:
            self.sub_active = False
            self.sub_status = None
            self.sub_amount = None
            self.sub_period_end = None
            self.sub_cancel_at_period_end = None
        else:
            try:
                response = utils.request.get(SUBSCRIPTION_SERVER,
                    json_data={'license': license},
                    timeout=HTTP_REQUEST_TIMEOUT)
                # License key invalid
                if response.status_code == 470:
                    persist_db.remove('license')
                    self.subscription_update()
                    return
                data = response.json()
            except:
                logger.exception('Failed to check subscription status...')
                data = {}
            self.sub_active = data.get('active', True)
            self.sub_status = data.get('status', 'unknown')
            self.sub_amount = data.get('amount')
            self.sub_period_end = data.get('period_end')
            self.sub_cancel_at_period_end = data.get('cancel_at_period_end')
        if cur_sub_active is not None and cur_sub_active != self.sub_active:
            if self.sub_active:
                Event(type=SUBSCRIPTION_ACTIVE)
            else:
                Event(type=SUBSCRIPTION_INACTIVE)

    def subscription_dict(self):
        return {
            'license': bool(persist_db.get('license')),
            'active': self.sub_active,
            'status': self.sub_status,
            'amount': self.sub_amount,
            'period_end': self.sub_period_end,
            'cancel_at_period_end': self.sub_cancel_at_period_end,
        }

    def _check_updates(self):
        while True:
            if self.get_notifications:
                logger.debug('Checking notifications...')
                try:
                    request = urllib2.Request(self.notification_server + \
                        '/%s' % self._get_version())
                    response = urllib2.urlopen(request, timeout=60)
                    data = json.load(response)

                    self.notification = data.get('message', '')
                    self.www_state = data.get('www', OK)
                    self.vpn_state = data.get('vpn', OK)
                except:
                    logger.exception('Failed to check notifications.')
            logger.debug('Checking subscription status...')
            try:
                self.subscription_update()
            except:
                logger.exception('Failed to check subscription status.')
            time.sleep(UPDATE_CHECK_RATE)

    def _setup_public_ip(self):
        thread = threading.Thread(target=self.load_public_ip,
            kwargs={'attempts': 5})
        thread.daemon = True
        thread.start()

    def _setup_updates(self):
        thread = threading.Thread(target=self._check_updates)
        thread.daemon = True
        thread.start()

    def _setup_app(self):
        self.app = flask.Flask(APP_NAME)
        self.app.secret_key = os.urandom(32)

        @self.app.before_request
        def before_request():
            flask.g.start = time.time()

        @self.app.after_request
        def after_request(response):
            response.headers.add('Execution-Time',
                int((time.time() - flask.g.start) * 1000))
            return response

        global logger
        logger = self.app.logger

    def auth(self, call):
        def _wrapped(*args, **kwargs):
            if not utils.check_session():
                raise flask.abort(401)
            return call(*args, **kwargs)
        _wrapped.__name__ = '%s_auth' % call.__name__
        return _wrapped

    def local_auth(self, call):
        def _wrapped(*args, **kwargs):
            api_key = flask.request.headers.get('API-Key', None)
            if api_key != self.local_api_key:
                logger.error('Local auth error, invalid api key.')
                raise flask.abort(401)
            return call(*args, **kwargs)
        _wrapped.__name__ = '%s_local_auth' % call.__name__
        return _wrapped

    def _setup_conf(self):
        self.set_path(self.conf_path)
        if not os.path.isdir(self.data_path):
            os.makedirs(self.data_path)

    def _setup_log(self):
        if self.log_debug:
            self.log_level = logging.DEBUG
        else:
            self.log_level = logging.INFO

        if self.log_path:
            self.log_handler = logging.handlers.RotatingFileHandler(
                self.log_path, maxBytes=1000000, backupCount=1)
        else:
            self.log_handler = logging.StreamHandler()

        global logger
        if not logger:
            logger = logging.getLogger(APP_NAME)

        logger.setLevel(self.log_level)
        self.log_handler.setLevel(self.log_level)

        self.log_handler.setFormatter(logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(module)s][%(lineno)d] ' +
            '%(message)s'))

        logger.addHandler(self.log_handler)

    def _setup_db(self):
        persist_db.persist(self.db_path)

    def _setup_handlers(self):
        import handlers

    def _get_version_int(self, version):
        return int(''.join([x.zfill(2) for x in version.split('.')]))

    def _get_version(self):
        from pritunl import __version__
        return self._get_version_int(__version__)

    def _get_data_version(self):
        version_path = os.path.join(self.data_path, VERSION_NAME)
        if os.path.isfile(version_path):
            with open(version_path, 'r') as version_file:
                return self._get_version_int(
                    version_file.readlines()[0].strip())

    def _upgrade_db(self):
        version = self._get_version()
        cur_version = self._get_data_version()

        if cur_version and cur_version < self._get_version_int('0.10.5'):
            logger.info('Upgrading database to v0.10.5...')
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def _upgrade_data(self):
        version = self._get_version()
        cur_version = self._get_data_version()

        if cur_version and cur_version < self._get_version_int('0.10.5'):
            logger.info('Upgrading data to v0.10.5...')
            from server import Server
            for server in Server.iter_servers():
                server._upgrade_0_10_5()

            from organization import Organization
            for org in Organization.iter_orgs():
                org._upgrade_0_10_5()

        if cur_version and cur_version < self._get_version_int('0.10.6'):
            logger.info('Upgrading data to v0.10.6...')
            if self.password:
                from cache import persist_db
                logger.info('Upgrading config to v0.10.6...')
                salt = base64.b64encode(
                    '2511cebca93d028393735637bbc8029207731fcf')
                password = base64.b64encode(self.password.decode('hex'))
                persist_db.dict_set('auth', 'password',
                    '0$%s$%s' % (salt, password))
                self.password = None
                self.commit()

            from server import Server
            for server in Server.iter_servers():
                server._upgrade_0_10_6()

        if cur_version and cur_version < self._get_version_int('0.10.9'):
            logger.info('Upgrading data to v0.10.9...')
            from server import Server
            for server in Server.iter_servers():
                server._upgrade_0_10_9()

            from organization import Organization
            for org in Organization.iter_orgs():
                for user in org.iter_users():
                    user._upgrade_0_10_9()
                org.sort_users_cache()

        if cur_version != version:
            from pritunl import __version__
            version_path = os.path.join(self.data_path, VERSION_NAME)
            with open(version_path, 'w') as version_file:
                version_file.write('%s\n' % __version__)

    def _fill_cache(self):
        logger.info('Preloading cache...')
        from organization import Organization
        for org in Organization.iter_orgs():
            org._cache_users()

        from server import Server
        for server in Server.iter_servers():
            server.load()

    def _setup_pooler(self):
        if self.pooler:
            from pooler import Pooler
            Pooler().start()

    def _setup_queues(self):
        from server import Server
        Server.setup_ip_pool_queue()

        from organization import Organization
        Organization.setup_sort_users_queue()

    def _setup_all(self):
        self._setup_app()
        self._setup_conf()
        self._setup_log()
        self._setup_public_ip()
        self._setup_updates()
        self._upgrade_db()
        self._setup_db()
        self._setup_handlers()
        self._upgrade_data()
        self._fill_cache()
        self._setup_pooler()
        self._setup_queues()

    def _setup_server_cert(self):
        if self.server_cert_path and self.server_key_path:
            self._server_cert_path = self.server_cert_path
            self._server_key_path = self.server_key_path
        else:
            self._server_cert_path = os.path.join(self.data_path,
                SERVER_CERT_NAME)
            self._server_key_path = os.path.join(self.data_path,
                SERVER_KEY_NAME)

            if not os.path.isfile(self._server_cert_path) or \
                    not os.path.isfile(self._server_key_path):
                logger.info('Generating server ssl cert...')
                try:
                    subprocess.check_call([
                        'openssl', 'req', '-batch', '-x509', '-nodes',
                        '-newkey', 'rsa:4096',
                        '-days', '3652',
                        '-keyout', self._server_key_path,
                        '-out', self._server_cert_path,
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError:
                    logger.exception('Failed to generate server ssl cert.')
                    raise
                os.chmod(self._server_key_path, 0600)

    def _run_wsgi(self):
        if self.ssl:
            self._setup_server_cert()
        from log_entry import LogEntry
        logger.info('Starting server...')

        if self.auto_start_servers:
            from pritunl.server import Server
            for server in Server.iter_servers():
                if server.org_count:
                    try:
                        server.start()
                    except:
                        logger.exception('Failed to auto start server. %r' % {
                            'server_id': server.id,
                        })

        server = cherrypy.wsgiserver.CherryPyWSGIServer(
            (self.bind_addr, self.port), self.app,
            request_queue_size=SERVER_REQUEST_QUEUE_SIZE,
            server_name=cherrypy.wsgiserver.CherryPyWSGIServer.version)
        if self.ssl:
            server.ssl_adapter = \
                cherrypy.wsgiserver.ssl_builtin.BuiltinSSLAdapter(
                    self._server_cert_path, self._server_key_path)
        try:
            server.start()
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logger.exception('Server error occurred')
            raise
        finally:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            logger.info('Stopping server...')
            LogEntry(message='Web server stopped.')
            self.interrupt = True
            server.stop()

    def _run_wsgi_debug(self):
        from log_entry import LogEntry
        logger.info('Starting debug server...')

        # App.run server uses werkzeug logger
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(self.log_level)
        werkzeug_logger.addHandler(self.log_handler)

        try:
            self.app.run(host=self.bind_addr, port=self.port, threaded=True)
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logger.exception('Server error occurred')
            raise
        finally:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            logger.info('Stopping debug server...')
            LogEntry(message='Web server stopped.')
            self.interrupt = True

    def _run_server(self):
        from log_entry import LogEntry
        LogEntry(message='Web server started.')
        if self.debug:
            self._run_wsgi_debug()
        else:
            self._run_wsgi()

    def run_server(self):
        self._setup_all()
        self._run_server()
