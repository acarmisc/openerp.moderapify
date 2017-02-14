import unittest
from helpers import Configuration
from erp_xmlrpc import OpenErp
import requests


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.config = Configuration(sections=['webservice', 'server', 'test'])
        self.erp = OpenErp(config_object=self.config.server)

    def test_find(self):
        args = [('name', 'like', self.config.test.partner_name)]
        results = self.erp.find(model='res.partner', args=args)
        self.assertGreater(len(results), 0)

    def test_api_alive(self):
        response = requests.get('http://localhost:%s/' % self.config.webservice.port)
        response = response.json()

        self.assertEqual(response.get('message'), 'Welcome to Openerp ModernAPIfy!')

    def test_api_reserved(self):
        response = requests.get('http://localhost:%s/test_unauth' % self.config.webservice.port)
        status = response.status_code
        response = response.json()

        self.assertEqual(status, 401)

if __name__ == '__main__':
    unittest.main()
