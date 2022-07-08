from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from dataclasses import dataclass, asdict

@dataclass(slots = True)
class FWv6:
    '''
    This class creates an IPv6 firewall rule object like in https://api.bbox.fr/doc/apirouter/#api-Firewall-put_v1_firewall_create
    Also, enable/disable the IPv6 Firewall
    PARAMS:
        all the params described in the link above or params described under this comment
    '''
    description: str
    order: int
    protocols: str
    enable: int = 1
    action: str = 'Accept'
    srcip: str = ''
    srcipnot: int = 0
    srcmacnot: int = 0
    srcmacs: str = ''
    dstip: str = ''
    dstipnot: int = 0
    dstmacnot: int = 0
    dstmacs: str = ''
    srcports: str = ''
    srcportnot: int = 0
    dstports: str = ''
    dstportnot: int = 0
    ipprotocol: str = 'IPv6'

    def create(self, logger, api):
        '''
        Method which creates an IPv6 firewall rule
        '''
        logger.info('Rule FWv6 %s will be created' % self.description)
        api.get_str('POST', '/firewallv6/rules?btoken=', asdict(self))

class Fwv6Manager:
    '''
    This class manages FWv6 objects. When deployed, all previously rules are deleted, then re-created from inventory file
    PARAMS:
        logger, (MANDATORY), a logger object to print info message
        api, (MANDATORY), an API object to call BBox API
        rules, the rules wanted in IPv6 firewall. They are created in same order as described in inventory file
    '''
    __slots__ = ['logger', 'api', 'conf', 'rules']

    def __init__(self, logger, api, rules):
        self.logger = logger
        self.api = api
        self.conf = rules.pop('conf')
        self.rules = rules

    def conf_section(self):
        convert = ('disabled', 'enabled')
        self.logger.info('Update Firewallv6 state: %s' % convert[self.conf['enable']])
        self.api.get_str('PUT', '/firewall', {'enable':self.conf['enable']})

    def delete_all(self):
        '''
        Method which deletes all IPv6 firewall rules previously created
        '''
        raw = self.api.get_str('GET', '/firewallv6/rules').decode('utf-8').strip('[]')
        rules = json.loads(raw)['firewall']['rules']
        for rule in rules:
            self.logger.info('Deleting FWv6 rule %s' % rule['description'])
            self.api.get_str('DELETE', '/firewall/rules/%d' % rule['id'])

    def deploy(self):
        '''
        Method which creates IPv6 firewall rule
        '''
        i = 1
        self.logger.info('---------- SECTION Firewall IPv6 ----------')
        self.logger.info('Remove all previous rules in Firewall IPv6')
        self.delete_all()
        for rule in self.rules:
            oRule = FWv6(description = rule, order = i, **self.rules[rule])
            oRule.create(self.logger, self.api)
            i += 1
        self.logger.info('---------- END SECTION Firewall IPv6 ----------')
