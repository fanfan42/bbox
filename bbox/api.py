from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import urllib
import requests

from http import cookies
from urllib.parse import urlparse
from urllib import parse

#BBox has a bad dhparam despite update in January 2023
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass
# End of bloc specific for bbox

class BBoxAPI:
    '''
    This class creates an object to access BBox API
    PARAMS:
        logger: (MANDATORY), the logger object
        url: (MANDATORY), the URL to call BBox API
        password: (MANDATORY), the password to access BBox API
    '''
    __slots__ = ['cookie', 'host', 'logger', 'path']

    def __init__(self, logger, url, password):
        components = urllib.parse.urlparse(url)

        if components[0] != 'https':
            logger.error ('API : URL scheme must be https://')
            raise

        self.cookie = None
        self.host = components[1]
        self.logger = logger
        self.path = components[2]

        (status, response) = self.query ('POST', '/login', {'password': password, 'remember': '1'})
        cookie = status is not None and status['set-cookie'] or None

        if cookie is None:
            self.logger.error ('API : cannot authenticate to API (wrong password?)')
            raise

        self.cookie = cookies.BaseCookie()
        self.cookie.load(cookie)

    def get_str (self, method, path, data = None):
        '''
        Get the string returned when calling the API
        PARAMS:
            method: (MANDATORY) GET, POST. PUT. DELETE
            path: (MANDATORY) the URI to call, ex: /wireless
            data: parameters id needed by the API
        '''
        (status, response) = self.query (method, path, data)

        if status is not None:
            return response.decode('utf-8').strip('[]')
        return ''

    def query (self, method, short_path, data = None):
        '''
        Get the status and string returned when calling the API
        PARAMS:
            method: (MANDATORY) GET, POST. PUT. DELETE
            path: (MANDATORY) the URI to call, ex: /wireless
            data: parameters id needed by the API
        '''
        path = 'api/v1' + short_path
        if path.endswith ('btoken='):
            (status, response) = self.query ('GET', '/device/token')
            jtoken = json.loads (response)
            token = jtoken[0]['device']['token']
            if token is None:
                self.logger.error ('API : cannot get device token')
                return {}
            path = path + token

        if data is not None:
            if isinstance(data, str):
                body = urllib.parse.urlencode(urllib.parse.parse_qsl(data))
            else:
                body = urllib.parse.urlencode(data)
        else:
            body = None
        if self.cookie is not None:
            headers = dict ((('Cookie', name + '=' + morsel.coded_value) for (name, morsel) in self.cookie.items ()))
        else:
            headers = {}

        request = getattr(requests, method.lower()) ('https://' + self.host + '/' + path, data=body, headers=headers)
        status = request.headers
        response = request.content

        if request.status_code != 200:
            self.logger.warning ('API : call {0} {1} returned {2} and {3} !!!'.format (method, path, status, response))
            return None, None
        return status, response
