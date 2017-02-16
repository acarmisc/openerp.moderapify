from klein import run, route
from helpers import Responder, RequestParser, LocalDatabase, Security, config, credential_cached
import json
import uuid
from twisted.logger import Logger
from twisted.web.server import Session
from erp_xmlrpc import OpenErp


log = Logger()
db = LocalDatabase(config.server.localdb)
db.init_db()

@route('/')
def home(request):
    message = 'Welcome to Openerp ModernAPIfy!'
    session = request.getSession()
    request, response = Responder(request, message=message, payload=session.uid).build()
    return response

@route('/test_unauth')
def test_unauth(request):
    request, response = Responder(request).unauthorize()
    return response

@route('/api/logout/')
def logout(request):
    token = Security(request=request).token
    db.clear_session(token)

    request, response = Responder(request, message='Session closed.', payload=dict(token=token)).build()

@route('/api/login/', methods=['POST'])
def login(request):
    if ('username', 'password') not in request.args:
        Responder(request).error_data('Missing arguments')

    username = request.args.get('username')[0]
    password = request.args.get('password')[0]
    erp = OpenErp(config_object=config.server, user=username, password=password)
    if erp.uid:
        token = Security().token
        # User authorized
        db.save_credentials(token, username, password)
        request, response = Responder(request, message='Welcome!', payload=dict(token=token)).build()
    else:
        request, response = Responder(request).unauthorize()

    return response

@route('/api/models/<model>/<id>/', methods=['GET'])
@credential_cached
def find_by_id(request, model, id):
    erp = OpenErp(config_object=config.server, user=username, password=password)
    args = [('id', '=', id)]
    fields = request.args.get('fields')
    if fields:
        fields = fields[0].split(',')
    results = erp.find(model, args, fields=fields)
    log.debug('Received GET request for model %s with fields %s' % (model, fields))

    request, response = Responder(request, payload=results).build()

    return response

@route('/api/<model>/', methods=['GET'])
def find(request, model):
    erp = OpenErp(config.server)
    parser = RequestParser()
    query = parser.parse_query(request.args.get('query')[0])
    fields = parser.parse_fields(request.args.get('fields')[0])
    args = list()
    for el in query:
        args.append(tuple(el.split(',')))

    results = erp.find(model, args, fields=fields)

    request, response = Responder(request, payload=results).build()

    return response


run(config.webservice.host, config.webservice.port)
