from pritunl.constants import *
from pritunl.exceptions import *
from pritunl.organization import Organization
from pritunl.event import Event
from pritunl.log_entry import LogEntry
import pritunl.utils as utils
from pritunl import app_server
import flask
import math
import time

@app_server.app.route('/user/<org_id>', methods=['GET'])
@app_server.app.route('/user/<org_id>/<user_id>', methods=['GET'])
@app_server.app.route('/user/<org_id>/<int:page>', methods=['GET'])
@app_server.auth
def user_get(org_id, user_id=None, page=None):
    org = Organization.get_org(id=org_id)
    if user_id:
        return utils.jsonify(org.get_user(user_id).dict())
    else:
        page = flask.request.args.get('page', None)
        page = int(page) if page else page
        search = flask.request.args.get('search', None)
        limit = int(flask.request.args.get('limit', USER_PAGE_COUNT))
        otp_auth = False
        search_more = True
        server_count = 0
        clients = {}
        servers = []

        for server in org.iter_servers():
            servers.append(server)
            server_count += 1
            if server.otp_auth:
                otp_auth = True
            server_clients = server.clients
            for client_id in server_clients:
                client = server_clients[client_id]
                if client_id not in clients:
                    clients[client_id] = {}
                clients[client_id][server.id] = client

        users = []
        for user in org.iter_users(page=page, prefix=search,
                prefix_limit=limit):
            if user is None:
                search_more = False
                break
            is_client = user.id in clients
            user_dict = user.dict()
            user_dict['status'] = is_client
            user_dict['otp_auth'] = otp_auth
            server_data = []
            for server in servers:
                local_ip_addr, remote_ip_addr = server.get_ip_set(
                    org_id, user.id)
                data = {
                    'id': server.id,
                    'name': server.name,
                    'status': is_client and server.id in clients[user.id],
                    'local_address': local_ip_addr,
                    'remote_address': remote_ip_addr,
                    'real_address': None,
                    'virt_address': None,
                    'bytes_received': None,
                    'bytes_sent': None,
                    'connected_since': None,
                }
                if is_client:
                    client_data = clients[user.id].get(server.id)
                    if client_data:
                        data.update(client_data)
                server_data.append(data)
            user_dict['servers'] = server_data
            users.append(user_dict)

        if page is not None:
            return utils.jsonify({
                'page': page,
                'page_total': org.page_total,
                'server_count': server_count,
                'users': users,
            })
        elif search is not None:
            return utils.jsonify({
                'search': search,
                'search_more': search_more,
                'search_limit': limit,
                'search_count': org.get_last_prefix_count(),
                'search_time':  round((time.time() - flask.g.start), 4),
                'server_count': server_count,
                'users': users,
            })
        else:
            return utils.jsonify(users)

@app_server.app.route('/user/<org_id>', methods=['POST'])
@app_server.auth
def user_post(org_id):
    org = Organization.get_org(id=org_id)

    if isinstance(flask.request.json, list):
        users = []
        for user_data in flask.request.json:
            name = utils.filter_str(user_data['name'])
            email = utils.filter_str(user_data.get('email'))
            user = org.new_user(type=CERT_CLIENT, name=name, email=email)

            disabled = user_data.get('disabled')
            if disabled is not None:
                user.disabled = disabled
                user.commit()

            users.append(user.dict())
        return utils.jsonify(users)
    else:
        name = utils.filter_str(flask.request.json['name'])
        email = None
        if 'email' in flask.request.json:
            email = utils.filter_str(flask.request.json['email'])
        user = org.new_user(type=CERT_CLIENT, name=name, email=email)

        disabled = flask.request.json.get('disabled')
        if disabled is not None:
            user.disabled = disabled
            user.commit()

        return utils.jsonify(user.dict())

@app_server.app.route('/user/<org_id>/<user_id>', methods=['PUT'])
@app_server.auth
def user_put(org_id, user_id):
    org = Organization.get_org(id=org_id)
    user = org.get_user(user_id)

    name = flask.request.json.get('name')
    if name:
        name = utils.filter_str(name)

    if 'email' in flask.request.json:
        email = flask.request.json['email']
        if email:
            user.email = utils.filter_str(email)
        else:
            user.email = None

    disabled = flask.request.json.get('disabled')
    if disabled is not None:
        user.disabled = disabled

    if name:
        user.rename(name)
    else:
        user.commit()
        Event(type=USERS_UPDATED, resource_id=user.org.id)

    if disabled:
        if user.type == CERT_CLIENT:
            LogEntry(message='Disabled user "%s".' % user.name)

        for server in org.iter_servers():
            server_clients = server.clients
            if user_id in server_clients:
                server.restart()
    elif disabled == False and user.type == CERT_CLIENT:
        LogEntry(message='Enabled user "%s".' % user.name)

    send_key_email = flask.request.json.get('send_key_email')
    if send_key_email and user.email:
        try:
            user.send_key_email(send_key_email)
        except EmailNotConfiguredError:
            return utils.jsonify({
                'error': EMAIL_NOT_CONFIGURED,
                'error_msg': EMAIL_NOT_CONFIGURED_MSG,
            }, 400)
        except EmailFromInvalid:
            return utils.jsonify({
                'error': EMAIL_FROM_INVALID,
                'error_msg': EMAIL_FROM_INVALID_MSG,
            }, 400)
        except EmailApiKeyInvalid:
            return utils.jsonify({
                'error': EMAIL_API_KEY_INVALID,
                'error_msg': EMAIL_API_KEY_INVALID_MSG,
            }, 400)

    return utils.jsonify(user.dict())

@app_server.app.route('/user/<org_id>/<user_id>', methods=['DELETE'])
@app_server.auth
def user_delete(org_id, user_id):
    org = Organization.get_org(id=org_id)
    user = org.get_user(user_id)
    user_id = user.id
    user.remove()

    for server in org.iter_servers():
        server_clients = server.clients
        if user_id in server_clients:
            server.restart()

    return utils.jsonify({})

@app_server.app.route('/user/<org_id>/<user_id>/otp_secret', methods=['PUT'])
@app_server.auth
def user_otp_secret_put(org_id, user_id):
    org = Organization.get_org(id=org_id)
    user = org.get_user(user_id)
    user.generate_otp_secret()
    return utils.jsonify(user.dict())
