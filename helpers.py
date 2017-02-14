import os
import ConfigParser

import json
from twisted.web import http

class ConfigurationSection:
    pass

class Configuration:

    def __init__(self, custom_file=None, sections=['webservice', 'server']):
        cfile = custom_file or './settings.ini'
        config = ConfigParser.SafeConfigParser()
        config.optionxform = str

        try:
            config.read(cfile)
        except Exception, e:
            raise ValueError('Unable to find settings.ini file in the root folder')

        self.config = config
        for section in sections:
            setattr(self, section, ConfigurationSection)
            el = getattr(self, section)
            el.__dict__.update(config.items(section))

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
