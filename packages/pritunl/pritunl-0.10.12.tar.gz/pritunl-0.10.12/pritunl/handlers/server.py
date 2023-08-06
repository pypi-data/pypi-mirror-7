from pritunl.constants import *
from pritunl.exceptions import *
from pritunl.server import Server
from pritunl.node_server import NodeServer
from pritunl.organization import Organization
from pritunl.log_entry import LogEntry
from event import Event
import pritunl.utils as utils
from pritunl import app_server
import flask
import re
import random

def _network_invalid():
    return utils.jsonify({
        'error': NETWORK_INVALID,
        'error_msg': NETWORK_INVALID_MSG,
    }, 400)

def _interface_invalid():
        return utils.jsonify({
            'error': INTERFACE_INVALID,
            'error_msg': INTERFACE_INVALID_MSG,
        }, 400)

def _port_invalid():
        return utils.jsonify({
            'error': PORT_INVALID,
            'error_msg': PORT_INVALID_MSG,
        }, 400)

def _dh_param_bits_invalid():
        return utils.jsonify({
            'error': DH_PARAM_BITS_INVALID,
            'error_msg': DH_PARAM_BITS_INVALID_MSG,
        }, 400)

def _local_network_invalid():
    return utils.jsonify({
        'error': LOCAL_NETWORK_INVALID,
        'error_msg': LOCAL_NETWORK_INVALID_MSG,
    }, 400)

def _dns_server_invalid():
    return utils.jsonify({
        'error': DNS_SERVER_INVALID,
        'error_msg': DNS_SERVER_INVALID_MSG,
    }, 400)

@app_server.app.route('/server', methods=['GET'])
@app_server.app.route('/server/<server_id>', methods=['GET'])
@app_server.auth
def server_get(server_id=None):
    if server_id:
        return utils.jsonify(Server.get_server(server_id).dict())
    else:
        servers = []
        servers_dict = {}
        servers_sort = []

        for server in Server.iter_servers():
            servers.append(server.dict())

        return utils.jsonify(servers)

@app_server.app.route('/server', methods=['POST'])
@app_server.app.route('/server/<server_id>', methods=['PUT'])
@app_server.auth
def server_put_post(server_id=None):
    network_used = set()
    interface_used = set()
    port_used = set()
    for server in Server.iter_servers():
        if server.id == server_id:
            continue
        network_used.add(server.network)
        interface_used.add(server.interface)
        port_used.add('%s%s' % (server.port, server.protocol))

    name = None
    name_def = False
    if 'name' in flask.request.json:
        name_def = True
        name = utils.filter_str(flask.request.json['name'])

    type = SERVER
    type_def = False
    if 'type' in flask.request.json:
        type_def = True
        if flask.request.json['type'] == NODE_SERVER:
            type = NODE_SERVER

    network = None
    network_def = False
    if 'network' in flask.request.json:
        network_def = True
        network = flask.request.json['network']

        if network not in SAFE_PUB_SUBNETS:
            network_split = network.split('/')
            if len(network_split) != 2:
                return _network_invalid()

            address = network_split[0].split('.')
            if len(address) != 4:
                return _network_invalid()
            for i, value in enumerate(address):
                try:
                    address[i] = int(value)
                except ValueError:
                    return _network_invalid()
            if address[0] != 10:
                return _network_invalid()

            if address[1] > 255 or address[1] < 0 or \
                    address[2] > 255 or address[2] < 0:
                return _network_invalid()

            if address[3] != 0:
                return _network_invalid()

            try:
                subnet = int(network_split[1])
            except ValueError:
                return _network_invalid()

            if subnet < 8 or subnet > 24:
                return _network_invalid()

    interface = None
    interface_def = False
    if 'interface' in flask.request.json:
        interface_def = True
        interface = flask.request.json['interface']

        if not re.match('^[a-z0-9]+$', interface):
            return _interface_invalid()

        if interface[:3] != 'tun':
            return _interface_invalid()

        try:
            interface_num = int(interface[3:])
        except ValueError:
            return _interface_invalid()

        if interface_num > 64:
            return _interface_invalid()

        interface = interface[:3] + str(interface_num)

    protocol = 'udp'
    protocol_def = False
    if 'protocol' in flask.request.json:
        protocol_def = True
        protocol = flask.request.json['protocol'].lower()

        if protocol not in ('udp', 'tcp'):
            return utils.jsonify({
                'error': PROTOCOL_INVALID,
                'error_msg': PROTOCOL_INVALID_MSG,
            }, 400)

    port = None
    port_def = False
    if 'port' in flask.request.json:
        port_def = True
        port = flask.request.json['port']

        try:
            port = int(port)
        except ValueError:
            return _port_invalid()

        if port < 1 or port > 65535:
            return _port_invalid()

    dh_param_bits = None
    dh_param_bits_def = False
    if 'dh_param_bits' in flask.request.json:
        dh_param_bits_def = True
        dh_param_bits = flask.request.json['dh_param_bits']

        try:
            dh_param_bits = int(dh_param_bits)
        except ValueError:
            return _dh_param_bits_invalid()

        if dh_param_bits not in VALID_DH_PARAM_BITS:
            return _dh_param_bits_invalid()

    mode = None
    mode_def = False
    if 'mode' in flask.request.json:
        mode_def = True
        mode = flask.request.json['mode']

        if mode not in (ALL_TRAFFIC, LOCAL_TRAFFIC, VPN_TRAFFIC):
            return utils.jsonify({
                'error': MODE_INVALID,
                'error_msg': MODE_INVALID_MSG,
            }, 400)

    local_networks = None
    local_networks_def = False
    if 'local_networks' in flask.request.json:
        local_networks_def = True
        local_networks = flask.request.json['local_networks'] or []

        for local_network in local_networks:
            local_network_split = local_network.split('/')
            if len(local_network_split) != 2:
                return _local_network_invalid()

            address = local_network_split[0].split('.')
            if len(address) != 4:
                return _local_network_invalid()
            for i, value in enumerate(address):
                try:
                    address[i] = int(value)
                except ValueError:
                    return _local_network_invalid()
            if address[0] > 255 or address[0] < 0 or \
                    address[1] > 255 or address[1] < 0 or \
                    address[2] > 255 or address[2] < 0 or \
                    address[3] > 254 or address[3] < 0:
                return _local_network_invalid()

            try:
                subnet = int(local_network_split[1])
            except ValueError:
                return _local_network_invalid()

            if subnet < 8 or subnet > 30:
                return _local_network_invalid()

    dns_servers = None
    dns_servers_def = False
    if 'dns_servers' in flask.request.json:
        dns_servers_def = True
        dns_servers = flask.request.json['dns_servers'] or []

        for dns_server in dns_servers:
            if not re.match(IP_REGEX, dns_server):
                return _dns_server_invalid()

    search_domain = None
    search_domain_def = False
    if 'search_domain' in flask.request.json:
        search_domain_def = True
        search_domain = utils.filter_str(flask.request.json['search_domain'])

    public_address = None
    public_address_def = False
    if 'public_address' in flask.request.json:
        public_address_def = True
        public_address = utils.filter_str(flask.request.json['public_address'])

    debug = False
    debug_def = False
    if 'debug' in flask.request.json:
        debug_def = True
        debug = True if flask.request.json['debug'] else False

    otp_auth = False
    otp_auth_def = False
    if 'otp_auth' in flask.request.json:
        otp_auth_def = True
        otp_auth = True if flask.request.json['otp_auth'] else False

    lzo_compression = False
    lzo_compression_def = False
    if 'lzo_compression' in flask.request.json:
        lzo_compression_def = True
        lzo_compression = True if flask.request.json[
            'lzo_compression'] else False

    node_host = None
    node_host_def = False
    if 'node_host' in flask.request.json:
        node_host_def = True
        node_host = utils.filter_str(flask.request.json['node_host'])

    node_port = None
    node_port_def = False
    if 'node_port' in flask.request.json:
        node_port_def = True
        node_port = flask.request.json['node_port']

        if node_port is not None:
            try:
                node_port = int(node_port)
            except ValueError:
                return _port_invalid()

            if node_port < 1 or node_port > 65535:
                return _port_invalid()

    node_key = None
    node_key_def = False
    if 'node_key' in flask.request.json:
        node_key_def = True
        node_key = utils.filter_str(flask.request.json['node_key'])

    if not server_id:
        if not name_def:
            return utils.jsonify({
                'error': MISSING_PARAMS,
                'error_msg': MISSING_PARAMS_MSG,
            }, 400)

        if not network_def:
            network_def = True
            for i in xrange(5000):
                rand_network = '10.%s.%s.0/24' % (
                    random.randint(15,250), random.randint(15,250))
                if rand_network not in network_used:
                    network = rand_network
                    break
            if not network:
                return utils.jsonify({
                    'error': NETWORK_IN_USE,
                    'error_msg': NETWORK_IN_USE_MSG,
                }, 400)

        if not interface_def:
            interface_def = True
            for i in xrange(64):
                rand_interface = 'tun%s' % i
                if rand_interface not in interface_used:
                    interface = rand_interface
                    break
            if not interface:
                return utils.jsonify({
                    'error': INTERFACE_IN_USE,
                    'error_msg': INTERFACE_IN_USE_MSG,
                }, 400)

        if not port_def:
            port_def = True
            rand_ports = range(10000, 19999)
            random.shuffle(rand_ports)
            for rand_port in rand_ports:
                if '%s%s' % (rand_port, protocol) not in port_used:
                    port = rand_port
                    break
            if not port:
                return utils.jsonify({
                    'error': PORT_PROTOCOL_IN_USE,
                    'error_msg': PORT_PROTOCOL_IN_USE_MSG,
                }, 400)

        if not dh_param_bits_def:
            dh_param_bits_def = True
            dh_param_bits = DEFAULT_DH_PARAM_BITS

        if not mode_def:
            mode_def = True
            if local_networks_def and local_networks:
                mode = LOCAL_TRAFFIC
            else:
                mode = ALL_TRAFFIC

        if not public_address_def:
            public_address_def = True
            public_address = app_server.public_ip

    if network_def:
        if network in network_used:
            return utils.jsonify({
                'error': NETWORK_IN_USE,
                'error_msg': NETWORK_IN_USE_MSG,
            }, 400)
    if interface_def:
        if interface in interface_used:
            return utils.jsonify({
                'error': INTERFACE_IN_USE,
                'error_msg': INTERFACE_IN_USE_MSG,
            }, 400)
    if port_def:
        if '%s%s' % (port, protocol) in port_used:
            return utils.jsonify({
                'error': PORT_PROTOCOL_IN_USE,
                'error_msg': PORT_PROTOCOL_IN_USE_MSG,
            }, 400)

    if not server_id:
        if type == NODE_SERVER:
            server = NodeServer(
                name=name,
                network=network,
                interface=interface,
                port=port,
                protocol=protocol,
                dh_param_bits=dh_param_bits,
                mode=mode,
                local_networks=local_networks,
                dns_servers=dns_servers,
                search_domain=search_domain,
                public_address=public_address,
                otp_auth=otp_auth,
                lzo_compression=lzo_compression,
                debug=debug,
                node_host=node_host,
                node_port=node_port,
                node_key=node_key,
            )
        else:
            server = Server(
                name=name,
                network=network,
                interface=interface,
                port=port,
                protocol=protocol,
                dh_param_bits=dh_param_bits,
                mode=mode,
                local_networks=local_networks,
                dns_servers=dns_servers,
                search_domain=search_domain,
                public_address=public_address,
                otp_auth=otp_auth,
                lzo_compression=lzo_compression,
                debug=debug,
            )
    else:
        server = Server.get_server(id=server_id)
        if server.status:
            return utils.jsonify({
                'error': SERVER_NOT_OFFLINE,
                'error_msg': SERVER_NOT_OFFLINE_SETTINGS_MSG,
            }, 400)
        if name_def:
            server.name = name
        if network_def:
            server.network = network
        if interface_def:
            server.interface = interface
        if port_def:
            server.port = port
        if protocol_def:
            server.protocol = protocol
        if dh_param_bits_def:
            server.dh_param_bits = dh_param_bits
        if mode_def:
            server.mode = mode
        if local_networks_def:
            server.local_networks = local_networks
        if dns_servers_def:
            server.dns_servers = dns_servers
        if search_domain_def:
            server.search_domain = search_domain
        if public_address_def:
            server.public_address = public_address
        if otp_auth_def:
            server.otp_auth = otp_auth
        if lzo_compression_def:
            server.lzo_compression = lzo_compression
        if debug_def:
            server.debug = debug
        if server.type == NODE_SERVER:
            if node_host_def:
                server.node_host = node_host
            if node_port_def:
                server.node_port = node_port
            if node_key_def:
                server.node_key = node_key
        server.commit()

    for org in server.iter_orgs():
        Event(type=USERS_UPDATED, resource_id=org.id)
    return utils.jsonify(server.dict())

@app_server.app.route('/server/<server_id>', methods=['DELETE'])
@app_server.auth
def server_delete(server_id):
    server = Server.get_server(id=server_id)
    server.remove()
    return utils.jsonify({})

@app_server.app.route('/server/<server_id>/organization', methods=['GET'])
@app_server.auth
def server_org_get(server_id):
    orgs = []
    server = Server.get_server(id=server_id)
    for org in server.iter_orgs():
        orgs.append({
            'id': org.id,
            'server': server.id,
            'name': org.name,
        })
    return utils.jsonify(orgs)

@app_server.app.route('/server/<server_id>/organization/<org_id>',
    methods=['PUT'])
@app_server.auth
def server_org_put(server_id, org_id):
    server = Server.get_server(id=server_id)
    if server.status:
        return utils.jsonify({
            'error': SERVER_NOT_OFFLINE,
            'error_msg': SERVER_NOT_OFFLINE_ATTACH_ORG_MSG,
        }, 400)
    org = server.add_org(org_id)
    return utils.jsonify({
        'id': org.id,
        'server': server.id,
        'name': org.name,
    })

@app_server.app.route('/server/<server_id>/organization/<org_id>',
    methods=['DELETE'])
@app_server.auth
def server_org_delete(server_id, org_id):
    server = Server.get_server(id=server_id)
    if server.status:
        return utils.jsonify({
            'error': SERVER_NOT_OFFLINE,
            'error_msg': SERVER_NOT_OFFLINE_DETACH_ORG_MSG,
        }, 400)
    server.remove_org(org_id)
    return utils.jsonify({})

@app_server.app.route('/server/<server_id>/<operation>', methods=['PUT'])
@app_server.auth
def server_operation_put(server_id, operation):
    server = Server.get_server(id=server_id)

    try:
        if operation == START:
            server.start()
        if operation == STOP:
            server.stop()
        elif operation == RESTART:
            server.restart()
    except NodeConnectionError:
        return utils.jsonify({
            'error': NODE_CONNECTION_ERROR,
            'error_msg': NODE_CONNECTION_ERROR_MSG,
        }, 400)
    except InvalidNodeAPIKey:
        return utils.jsonify({
            'error': NODE_API_KEY_INVLID,
            'error_msg': NODE_API_KEY_INVLID_MSG,
        }, 400)

    return utils.jsonify(server.dict())

@app_server.app.route('/server/<server_id>/output', methods=['GET'])
@app_server.auth
def server_output_get(server_id):
    server = Server.get_server(id=server_id)
    return utils.jsonify({
        'id': server.id,
        'output': server.get_output(),
    })

@app_server.app.route('/server/<server_id>/output', methods=['DELETE'])
@app_server.auth
def server_output_delete(server_id):
    server = Server.get_server(id=server_id)
    server.clear_output()
    return utils.jsonify({})

@app_server.app.route('/server/<server_id>/bandwidth', methods=['GET'])
@app_server.app.route('/server/<server_id>/bandwidth/<period>',
    methods=['GET'])
@app_server.auth
def server_bandwidth_get(server_id, period=None):
    server = Server.get_server(id=server_id)
    return utils.jsonify(server.get_bandwidth(period=period))

@app_server.app.route('/server/<server_id>/tls_verify', methods=['POST'])
@app_server.local_auth
def server_tls_verify_post(server_id):
    org_id = flask.request.json['org_id']
    user_id = flask.request.json['user_id']

    server = Server(server_id)
    if not server:
        return utils.jsonify({
            'error': SERVER_INVALID,
            'error_msg': SERVER_INVALID_MSG,
        }, 401)
    org = server.get_org(org_id)
    if not org:
        LogEntry(message='User failed authentication, ' +
            'invalid organization "%s".' % server.name)
        return utils.jsonify({
            'error': ORG_INVALID,
            'error_msg': ORG_INVALID_MSG,
        }, 401)
    user = org.get_user(user_id)
    if not user:
        LogEntry(message='User failed authentication, ' +
            'invalid user "%s".' % server.name)
        return utils.jsonify({
            'error': USER_INVALID,
            'error_msg': USER_INVALID_MSG,
        }, 401)
    if user.disabled:
        LogEntry(message='User failed authentication, ' +
            'disabled user "%s".' % server.name)
        return utils.jsonify({
            'error': USER_INVALID,
            'error_msg': USER_INVALID_MSG,
        }, 401)

    return utils.jsonify({
        'authenticated': True,
    })

@app_server.app.route('/server/<server_id>/otp_verify', methods=['POST'])
@app_server.local_auth
def server_otp_verify_post(server_id):
    org_id = flask.request.json['org_id']
    user_id = flask.request.json['user_id']
    otp_code = flask.request.json['otp_code']
    remote_ip = flask.request.json.get('remote_ip')

    server = Server(server_id)
    if not server:
        return utils.jsonify({
            'error': SERVER_INVALID,
            'error_msg': SERVER_INVALID_MSG,
        }, 401)
    org = server.get_org(org_id)
    if not org:
        LogEntry(message='User failed authentication, ' +
            'invalid organization "%s".' % server.name)
        return utils.jsonify({
            'error': ORG_INVALID,
            'error_msg': ORG_INVALID_MSG,
        }, 401)
    user = org.get_user(user_id)
    if not user:
        LogEntry(message='User failed authentication, ' +
            'invalid user "%s".' % server.name)
        return utils.jsonify({
            'error': USER_INVALID,
            'error_msg': USER_INVALID_MSG,
        }, 401)
    if not user.verify_otp_code(otp_code, remote_ip):
        LogEntry(message='User failed two-step authentication "%s".' % (
            user.name))
        return utils.jsonify({
            'error': OTP_CODE_INVALID,
            'error_msg': OTP_CODE_INVALID_MSG,
        }, 401)

    return utils.jsonify({
        'authenticated': True,
    })

@app_server.app.route('/server/<server_id>/client_connect', methods=['POST'])
@app_server.local_auth
def server_client_connect_post(server_id):
    org_id = flask.request.json['org_id']
    user_id = flask.request.json['user_id']

    server = Server(server_id)
    if not server:
        return utils.jsonify({
            'error': SERVER_INVALID,
            'error_msg': SERVER_INVALID_MSG,
        }, 401)
    org = server.get_org(org_id)
    if not org:
        return utils.jsonify({
            'error': ORG_INVALID,
            'error_msg': ORG_INVALID_MSG,
        }, 401)
    user = org.get_user(user_id)
    if not user:
        return utils.jsonify({
            'error': USER_INVALID,
            'error_msg': USER_INVALID_MSG,
        }, 401)
    if user.type != CERT_CLIENT:
        return utils.jsonify({
            'error': USER_TYPE_INVALID,
            'error_msg': USER_TYPE_INVALID_MSG,
        }, 401)

    local_ip_addr, remote_ip_addr = server.get_ip_set(org.id, user_id)
    if local_ip_addr and remote_ip_addr:
        client_conf = 'ifconfig-push %s %s' % (local_ip_addr, remote_ip_addr)
    else:
        client_conf = ''

    return utils.jsonify({
        'client_conf': client_conf,
    })

@app_server.app.route('/server/<server_id>/client_disconnect',
    methods=['POST'])
@app_server.local_auth
def server_client_disconnect_post(server_id):
    org_id = flask.request.json['org_id']
    user_id = flask.request.json['user_id']

    server = Server(server_id)
    if not server:
        return utils.jsonify({
            'error': SERVER_INVALID,
            'error_msg': SERVER_INVALID_MSG,
        }, 401)
    org = server.get_org(org_id)
    if not org:
        return utils.jsonify({
            'error': ORG_INVALID,
            'error_msg': ORG_INVALID_MSG,
        }, 401)
    user = org.get_user(user_id)
    if not user:
        return utils.jsonify({
            'error': USER_INVALID,
            'error_msg': USER_INVALID_MSG,
        }, 401)

    return utils.jsonify({})
