from klein import run, route
from helpers import Responder, Configuration
import json
from twisted.logger import Logger

from erp_xmlrpc import OpenErp

log = Logger()
config = Configuration()

@route('/')
def home(request):
    message = 'Welcome to Openerp ModernAPIfy!'
    request, response = Responder(request, message=message).build()
    return response

@route('/test_unauth')
def test_unauth(request):
    request, response = Responder(request).unauthorize()
    return response

@route('/api/<model>/<id>/', methods=['GET'])
def find_by_id(request, model, id):
    erp = OpenErp(config.server)
    args = [('id', '=', id)]
    fields = request.args.get('fields')[0].split(',')
    results = erp.find(model, args, fields=fields)
    log.debug('Received GET request for model %s with fields %s' % (model, fields))

    request, response = Responder(request, payload=results).build()

    return response

run("localhost", config.webservice.port)
