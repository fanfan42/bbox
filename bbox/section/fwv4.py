from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from dataclasses import dataclass, asdict

@dataclass(slots = True)
class FWv4:
    '''
    This class creates an object like the one described in https://api.bbox.fr/doc/apirouter/#api-Firewall-put_v1_firewall_create
    All previously rules created are deleted
    PARAMS:
        All params available the URL given before, or see below this comment if URL not up to date
    '''
    description: str
    order: int
    protocols: str
    enable: int = 1
    action: str = 'Accept'
    srcip: str = ''
    srcipnot: int = 0
    dstip: str = ''
    dstipnot: int = 0
    srcports: str = ''
    srcportnot: int = 0
    dstports: str = ''
    dstportnot: int = 0

    def create(self, logger, api):
        '''
        Method which creates an IPv4 firewall rule
        '''
        logger.info('Rule %s will be created' % self.description)
        api.get_str('POST', '/firewall/rules?btoken=', asdict(self))

class Fwv4Manager:
    '''
    This class manages FWv4 objects to be created
    it also deletes all previously created rules
    Finally, enable or not the IPv4 firewall, disable/enable the ping responder, disable/enable the Gamer mode
    PARAMS:
        logger, (MANDATORY), a logger informational object
        api, (MANDATORY), an API object to call the BBox API
        rules, rules to be deployed in Firewall IPv4
    '''
    __slots__ = ['logger', 'api', 'conf', 'rules']

    def __init__(self, logger, api, rules):
        self.logger = logger
        self.api = api
        self.conf = rules.pop('conf')
        self.rules = rules
        self.logger.info('Update Firewallv4 state: %i' % self.conf['enable'])
        self.api.get_str('PUT', '/firewall', {'enable':self.conf['enable']})
        self.logger.info('Update Ping responder state: %i' % self.conf['ping_responder'])
        self.api.get_str('PUT', '/firewall/pingresponder', {'enable': self.conf['ping_responder']})
        self.logger.info('Update Gamer Mode state: %d' % self.conf['gamer_mode'])
        self.api.get_str('PUT', '/firewall/gamermode', {'enable':self.conf['gamer_mode']})

    def delete_all(self):
        '''
        Method which deletes all rules in IPv4 Firewall
        '''
        raw = self.api.get_str('GET', '/firewall/rules').decode('utf-8').strip('[]')
        rules = json.loads(raw)['firewall']['rules']
        for rule in rules:
            self.logger.info('Deleting FWv4 rule %s' % rule['description'])
            self.api.get_str('DELETE', '/firewall/rules/%d' % rule['id'])

    def deploy(self):
        '''
        Method which creates an IPv4 firewall rule. Each rule is ordered like in the inventory file
        '''
        i = 1
        self.delete_all()
        for rule in self.rules:
            oRule = FWv4(description = rule, order = i, **self.rules[rule])
            oRule.create(self.logger, self.api)
            i += 1
