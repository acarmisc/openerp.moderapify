from klein import run, route, resource
from helpers import Responder, RequestParser, LocalDatabase, Security, credential_cached
import json
import uuid
from twisted.logger import Logger
from twisted.web.server import Session
from erp_xmlrpc import OpenErp
from confiky import Confiky

from optparse import OptionParser

parser = OptionParser()
parser.add_option("--settings")

(options, args) = parser.parse_args()

global config
config = Confiky(files=options.settings)

log = Logger()
db = LocalDatabase(config.server.localdb)
# NOTE: uncomment below line to recreate DB each time instant starts
# db.init_db()

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

@route('/logout/')
def logout(request):
    token = Security(config, request=request).token
    db.clear_session(token)

    request, response = Responder(request, message='Session closed.', payload=dict(token=token)).build()

@route('/login/', methods=['POST'])
def login(request):
    if ('username', 'password') not in request.args:
        Responder(request).error_data('Missing arguments')

    username = request.args.get('username')[0]
    password = request.args.get('password')[0]

    erp = OpenErp(config_object=config.server, user=username, password=password)
    if erp.uid:
        token = Security(config).token
        # User authorized
        db.save_credentials(token, username, password)

        log.info("Login success from %s" % username)
        request, response = Responder(request, message='Welcome!', payload=dict(token=token)).build()
    else:
        request, response = Responder(request).unauthorize()

    return response


@route('/models/<model>/', methods=['GET'])
@credential_cached
def model(request, model):
    parser = RequestParser()
    query = parser.parse_query(request.args.get('query'))
    fields = parser.parse_fields(request.args.get('fields'))
    erp = OpenErp(config_object=config.server, user=username, password=password)
    results = erp.find(model, query, fields=fields)

    log.info("Query on model %s from %s" % (model, request.getClientIP()))

    request, response = Responder(request, payload=results).build()

    return response


@route('/models/<model>/', methods=['POST'])
@credential_cached
def model_create(request, model):
    parser = RequestParser()
    payload = parser.parse_post(request.args)
    erp = OpenErp(config_object=config.server, user=username, password=password)
    results = erp.create(model, data=payload)

    request, response = Responder(request, payload=results).build()

    return response


@route('/models/<model>/<id>/', methods=['GET'])
@credential_cached
def model_get(request, model, id):
    args = [('id', '=', id)]
    fields = RequestParser().parse_fields(request.args.get('fields'))
    erp = OpenErp(config_object=config.server, user=username, password=password)
    results = erp.find(model, args, fields=fields)
    log.debug('Received GET request for model %s with fields %s' % (model, fields))

    request, response = Responder(request, payload=results).build()

    return response


run(config.webservice.host, config.webservice.port)
