from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from dataclasses import dataclass, asdict
from getpass import getpass
from typing import Literal

cache_dyndns = None

@dataclass(slots = True)
class Dyndns:
    '''
    This class creates a Dyndns object
    PARAMS:
        all params in https://api.bbox.fr/doc/apirouter/#api-Dynamic_DNS-put_v1_dhcp_options
        Only the param device is not supported even if it's in the init vars
    '''
    host: str
    server: Literal['dyndns','no-ip','ovh','duiadns','changeip','duckdns']
    username: str
    password: str=''
    enable: int=1
    device: str=''
    record: str='A'
    id: int=-1

    def __post_init__(self):
        if self.password == '':
            try1 = 'a'
            try2 = 'b'
            while try1 != try2:
                try1 = getpass('Enter password for DynDNS entry %s, username %s : ' % (self.host, self.username))
                try2 = getpass('Re-enter password for DynDNS entry %s, username %s : ' % (self.host, self.username))
            self.password = try1

    def create_or_update(self, logger, api):
        '''
        Method which creates/updates a DynDNS service
        '''
        global cache_dyndns

        if not cache_dyndns:
            cache_dyndns = api.get_str('GET', '/dyndns').decode('utf-8').strip('[]')
        services = json.loads(cache_dyndns)['dyndns']['domain']
        for service in services:
            self.id = service['id']
            self.device = service['device']
            service.pop('status')
            service.pop('periodicupdate')
            temp_service = Dyndns(**service)
            if temp_service.host == self.host:
                if self == temp_service:
                    logger.info('DynDNS service %s on server %s has no need to be updated' % (self.host,self.server))
                else:
                    logger.info('Updating DynDNS service %s on server %s' % (self.host, self.server))
                    api.get_str('PUT', '/dyndns/%i' % self.id, self.get_query_host())
                return
        else:
            logger.info('DynDNS service %s will be created on server %s' % (self.host, self.server))
            api.get_str('POST', '/dyndns?btoken=', self.get_query_host(True))

    def get_query_host(self, remove_id = False):
        '''
        Method which gets correct params for API call
        '''
        params = asdict(self)
        del params['device']
        if remove_id:
            del params['id']
        return params

class DyndnsManager:
    '''
    This class manages DynDNS objects
    Also, sets the DynDNS state
    PARAMS:
        logger, (MANDATORY), a logger object to print informational object
        api, (MANDATORY), an API object to control the bbox
        services, a dict containing dynDNS services to apply
    '''
    __slots__ = ['logger', 'api', 'conf', 'services']

    def __init__(self, logger, api, services):
        self.logger = logger
        self.api = api
        self.conf = services.pop('conf')
        self.services = services

    def conf_section(self):
        convert = ('disabled','enabled')
        self.logger.info('Update DynDNS state: %s' % convert[self.conf['enable']])
        self.api.get_str('PUT', '/dyndns', {'enable':self.conf['enable']})

    def deploy(self):
        '''
        Method which deploys DynDNS services in inventory file
        '''
        self.logger.info('---------- SECTION DynDNS ----------')
        for dyndns in self.services:
            oDyndns = Dyndns(host = dyndns, **self.services[dyndns])
            oDyndns.create_or_update(self.logger, self.api)
        self.logger.info('---------- END SECTION DynDNS ----------')
