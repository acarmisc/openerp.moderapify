import unittest
from confiky import Confiky
from erp_xmlrpc import OpenErp
from helpers import LocalDatabase
import requests


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.config = Confiky(files='settings.ini', required_sections=['webservice', 'server', 'test'])
        self.erp = OpenErp(config_object=self.config.server, user=self.config.test.username, password=self.config.test.password)
        self.db = LocalDatabase(self.config.test.localdb)
        self.db.init_db()
        self.token = '1234'

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

    def test_get_all_credentials(self):
        res = self.db.get_all_credentials()
        self.assertEqual(len(res), 0)

    def test_create_credentials(self):
        id = self.db.save_credentials(self.token, self.config.test.username, self.config.test.password)
        res = self.db.get_all_credentials()

        self.db.clear_session(username=self.config.test.username)

        self.assertEqual(len(res), 1)

    def test_get_credential_by_token(self):
        id = self.db.save_credentials(self.token, self.config.test.username, self.config.test.password)
        credential = self.db.get_credentials_by_token(self.token)

        self.assertIsNotNone(credential)


if __name__ == '__main__':
    unittest.main()
