import json
from twisted.web import http
from twisted.enterprise import adbapi
import sqlite3
from confiky import Confiky
import uuid
from functools import wraps


config = Confiky(files='/etc/modernapify.ini')

class LocalDatabase:
    TABLE_NAME = "api_sessions"
    Q_INIT_DB = "CREATE TABLE api_sessions ( ID INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT, username VARCHAR(200), password VARCHAR(200) )"
    Q_GET_SESSION_ALL = "SELECT * FROM api_sessions" # wait for no parameters
    Q_GET_SESSION_BY_TOKEN = "SELECT username, password FROM api_sessions WHERE token = '%s'" # wait for token
    Q_GET_SESSION_BY_USERNAME_OR_TOKEN = Q_GET_SESSION_BY_TOKEN + " or username = '%s'" # wait for token, username
    Q_CLEAR_SESSION = "DELETE FROM api_sessions WHERE username = '%s' OR token = '%s'" # wait for username or token
    Q_INSERT_SESSION = "INSERT INTO api_sessions (token, username, password) VALUES ('%s', '%s', '%s')" # wait for token, username, password

    def __init__(self, localdb_name):
        filename = localdb_name
        self.conn = sqlite3.connect(localdb_name)
        self.c = self.conn.cursor()

    def init_db(self):
        self.c.execute("drop table if exists {};".format(self.TABLE_NAME))
        self.c.execute(self.Q_INIT_DB)
        return True

    def clear_session(self, username):
        self.c.execute(self.Q_CLEAR_SESSION % (username, username))
        self.conn.commit()
        return True

    def get_all_credentials(self):
        return self.c.execute(self.Q_GET_SESSION_ALL).fetchall()

    def save_credentials(self, token, username, password):
        self.clear_session(username)
        self.c.execute(self.Q_INSERT_SESSION % (token, username, password))
        self.conn.commit()

        return self.c.lastrowid

    def get_credentials_by_token(self, token):
        data = self.c.execute(self.Q_GET_SESSION_BY_TOKEN % token).fetchone()

        if data:
            return (data[0], data[1])

        return None

class Security:

    def __init__(self, token=None, request=None):
        self.token = token or uuid.uuid4().hex

        if request:
            self.request = request
            self.token = self._extract_token()

    def __repr__(self):
        return "<Security %s>" % self.token

    def _extract_token(self):
        
        headers = self.request.getAllHeaders()
        if 'authorization' in headers.keys():
            token = headers.get('authorization').split(' ')
            if token[0] != 'Token':
                raise ValueError('Wrong authentication header format.')

            token = token[1]
            return token

        else:
            request, response = Responder(self.request).error_data('Missing authentication header.')

        return None

    def is_authenticated(self):
        db = LocalDatabase(config.server.localdb)
        credentials = db.get_credentials_by_token(self.token)
        if credentials:
            return True

        return False

    def credentials(self):
        db = LocalDatabase(config.server.localdb)
        return db.get_credentials_by_token(self.token)

def credential_cached(original_function):
    @wraps(original_function)
    def validate_user(*args, **kwargs):
        request = args[0]
        security = Security(request=request)

        print security

        if security.is_authenticated():
            credentials = security.credentials()
            original_function.__globals__['username'] = credentials[0]
            original_function.__globals__['password'] = credentials[1]
            return original_function(*args, **kwargs)

        request, response = Responder(request).unauthorize()
        return response

    return validate_user


class RequestParser:

    @staticmethod
    def parse_query(query):
        criteria = list()
        if not query:
            return []

        query = query[0]
        print query
        if ':' in query:
            queries = query.split(':')
        else:
            queries = [query]
        print queries

        for q in queries:
            criteria.append(tuple(q.split(',')))

        print criteria
        return criteria

    @staticmethod
    def parse_fields(fields):
        if not fields:
            return []

        fields = fields[0]
        return fields.split(',')

class Responder:

    def __init__(self, request, message=None, payload=None, errors=list(), status=200, response_format='json'):
        self.request = request
        self.message = message
        self.payload = payload
        self.errors = errors
        self.status = status
        self.response_format = response_format

    def build(self):
        self.errors = list()

        if self.status == 401:
            self.errors.append('You are not authorized.')
            self.request.setResponseCode(http.UNAUTHORIZED)

        if self.response_format == 'json':
            return self.build_json()

        raise NotImplementedError("Only JSON format is supported at the moment!")

    def build_json(self):
        request = self.request.setHeader('Content-Type', 'application/json')

        response = dict(message=self.message, payload=self.payload, errors=self.errors)
        return request, json.dumps(response)

    def unauthorize(self, message=None):
        self.status = 401
        self.message = message
        return self.build()

    def error_data(self, message=None):
        self.status = 400
        self.message = message
        return self.build()

    def created(self, message=None):
        self.status = 201
        self.message = message
        return self.build()
