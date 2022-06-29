from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from dataclasses import dataclass, asdict

cache_nat = None

@dataclass(slots = True)
class NATRule:
    '''
    This class creates/updates a NAT Rule in the BBox
    PARAMS:
        logger, (MANDATORY), a logger object to print info message
        api, (MANDATORY), an API object to control the BBox
    PARAMS:
        all params described in https://api.bbox.fr/doc/apirouter/#api-NAT_PMP-GetNatRulesID
    '''
    description: str
    protocol: str
    internalip: str
    internalport: int
    enable: int = 1
    externalip: str = ''
    externalport: int = ''
    id: int = -1

    def create_or_update(self, logger, api):
        '''
        Method which creates/updates a NAT rule
        '''
        global cache_nat

        if not cache_nat:
            cache_nat = api.get_str('GET', '/nat/rules').decode('utf-8').strip('[]')
        rules = json.loads(cache_nat)['nat']['rules']
        for rule in rules:
            self.id = rule['id']
            temp_rule = NATRule(**rule)
            if temp_rule.description == self.description:
                if self == temp_rule:
                    logger.info('NAT rule %s has no need to be updated' % self.description)
                else:
                    logger.info('Updating NAT rule %s' % self.description)
                    api.get_str('PUT', '/nat/rules/%i' % self.id, self.get_query_host())
                return
        else:
            logger.info('NAT rule %s will be created' % self.description)
            api.get_str('POST', '/nat/rules?btoken=', self.get_query_host(True))

    def get_query_host(self, remove_id = False):
        '''
        Method which gets correct params for API call
        '''
        params = asdict(self)
        # Bouygues, WTF ?
        params['ipaddress'] = params.pop('internalip')
        params['internal_port'] = params.pop('internalport')
        params['ipremote'] = params.pop('externalip')
        params['external_port'] = params.pop('externalport')
        if remove_id:
            del params['id']
        return params

class NatManager:
    '''
    This class manages NATRule object to create/update
    Also controls UPnP and DMZ states
    PARAMS:
        logger, (MANDATORY), a logger object to print info message
        api, (MANDATORY), an API object to control the BBox
        rules, NAT rules to be deployed
    '''
    __slots__ = ['logger', 'api', 'conf', 'rules']

    def __init__(self, logger, api, rules):
        convert = ('disabled', 'enabled')
        self.logger = logger
        self.api = api
        self.conf = rules.pop('conf')
        self.rules = rules
        self.logger.info('Update NAT state: %s' % convert[self.conf['enable']])
        self.api.get_str('PUT', '/nat/rules', {'enable':self.conf['enable']})
        self.logger.info('Update UPnP state: %s' % convert[self.conf['upnp']])
        self.api.get_str('PUT', '/upnp/igd', {'enable': self.conf['upnp']})
        self.logger.info('Update DMZ state: %s' % convert[self.conf['dmz']])
        self.api.get_str('PUT', '/nat/dmz', {'enable':self.conf['dmz']})

    def deploy(self):
        '''
        Method which creates/updates NAT rules
        '''
        self.logger.info('---------- SECTION NAT ----------')
        for rule in self.rules:
            oRule = NATRule(description = rule, **self.rules[rule])
            oRule.create_or_update(self.logger, self.api)
        self.logger.info('---------- END SECTION NAT ----------')
