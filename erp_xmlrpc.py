import xmlrpclib


class OpenErp:

    def __init__(self, config_object=None, host=None, dbname=None, user=None, password=None, token=None):
        if config_object:
            self.host = config_object.host
            self.dbname = config_object.dbname
        else:
            self.host = host
            self.dbname = dbname

        self.user = user
        self.password = password

        sock = xmlrpclib.ServerProxy('%s/xmlrpc/common' % self.host)

        self.uid = sock.login(self.dbname, self.user, self.password)
        self.sock = xmlrpclib.ServerProxy('%s/xmlrpc/object' % self.host, allow_none=True)

    def __repr__(self):
        return "<OpenERP at %s>" % self.host

    def create(self, model, data):
        res_id = self.sock.execute(self.dbname, self.uid, self.password, model, 'create', data)

    def update(self, model, ids, data):
        if not isinstance(args, dict):
            raise ValueError('Find args must be a dictionary.')

        results = self.sock.execute(self.dbname, self.uid, self.password, model, 'write', ids, data)

        return results

    def find(self, model, args, fields=None):
        if not fields:
            fields = ['id']

        if not isinstance(args, list):
            raise ValueError('Find args must be a list of tuple.')

        ids = self.sock.execute(self.dbname, self.uid, self.password, model, 'search', args)
        results = self.sock.execute(self.dbname, self.uid, self.password, model, 'read', ids, fields)
        return results

    def delete(self, model, ids):
        results = self.sock.execute(self.dbname, self.uid, self.password, model, 'unlink', ids)

        return results
