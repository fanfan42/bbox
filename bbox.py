#!/usr/bin/env python3

from __future__ import print_function

from http import cookies
import argparse
import json
import logging
import os
import urllib
from urllib.parse import urlparse
from urllib import parse
import sys
import requests

#BBox has a bad dhparam despite update in February 2022
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass
# End of bloc specific for bbox


class BBoxAPI:
    def __init__ (self, logger, url, password):
        components = urllib.parse.urlparse(url)

        if components[0] != 'https':
            logger.error ('URL scheme must be https://')
            sys.exit (1)

        self.cookie = None
        self.host = components[1]
        self.logger = logger
        self.path = components[2]

        (status, response) = self.query ('POST', 'api/v1/login', {'password': password, 'remember': '1'})
        cookie = status is not None and status['set-cookie'] or None

        if cookie is None:
            logger.error ('cannot authenticate to API (wrong password?)')
            sys.exit (1)

        self.cookie = cookies.BaseCookie ()
        self.cookie.load (cookie)

    def get_str (self, method, path, data = None):
        (status, response) = self.query (method, path, data)

        if status is not None:
            return response
        return ''

    def query (self, method, path, data = None):
        if path.endswith ('btoken='):
            (status, response) = self.query ('GET', 'api/v1/device/token')
            jtoken = json.loads (response)
            token = jtoken[0]['device']['token']
            if token is None:
                self.logger.warning ('cannot get device token')
                return {}
            path = path + token

        if data is not None:
            body = urllib.parse.urlencode (data)
        else:
            body = None
        if self.cookie is not None:
            headers = dict ((('Cookie', name + '=' + morsel.coded_value) for (name, morsel) in self.cookie.items ()))
        else:
            headers = {}

        if method == "GET":
            request = requests.get('https://' + self.host + '/' + path, data=body, headers=headers)
        elif method == "POST":
            request = requests.post('https://' + self.host + '/' + path, data=body, headers=headers)
        elif method == "PUT":
            request = requests.put('https://' + self.host + '/' + path, data=body, headers=headers)
        elif method == "DELETE":
            request = requests.delete('https://' + self.host + '/' + path, data=body, headers=headers)
        status = request.headers
        response = request.content

        if request.status_code != 200:
            self.logger.warning ('call {0} {1} returned {2} and {3} !!!'.format (method, path, status, response))
            return None, None
        return status, response

class Config:
    def __init__ (self, path):
        if os.path.isfile (path):
            with open (path, 'rb') as file:
                data = dict (json.load (file))
        else:
            data = {}
        self.password = data.get ('password', None)
        self.url = data.get ('url', 'https://192.168.1.254')

# Setup logging facility
formatter = logging.Formatter ('%(levelname)s: %(message)s')

console = logging.StreamHandler ()
console.setFormatter (formatter)

logger = logging.getLogger ()
logger.addHandler (console)
logger.setLevel (logging.INFO)

# Load configuration and setup API
config = Config (os.path.join (os.path.dirname (os.path.realpath (__file__)), '.bbox.config'))

if config.password is None:
    logger.error ('password is not defined')
    sys.exit (1)

# Parse command line arguments and execute command
parser = argparse.ArgumentParser (description = 'Python3 CLI utility for Bouygues Telecom\'s BBox Miami Router API.')
parsers = parser.add_subparsers (help = 'API command to execute')

parser_raw = parsers.add_parser ('raw', help = 'Execute raw command')
parser_raw.add_argument ('method', action = 'store', help = 'HTTP method', metavar = 'VERB')
parser_raw.add_argument ('path', action = 'store', help = 'API command', metavar = 'PATH')
parser_raw.add_argument ('params', action = 'store', nargs = '?', type = parse.parse_qsl, help = 'API command arguments', metavar = 'ARGS')
parser_raw.set_defaults (func = lambda logger, api, args: print (api.get_str (args.method, args.path, args.params)))

args = parser.parse_args ()
args.func (logger, BBoxAPI (logger, config.url, config.password), args)
