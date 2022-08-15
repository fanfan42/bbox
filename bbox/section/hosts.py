from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from dataclasses import dataclass,asdict

cache_dhcp = None
cache_mac = None

@dataclass(slots = True)
class Host:
    '''
    This class creates/updates a dhcp reservation object like in https://api.bbox.fr/doc/apirouter/#api-DHCP-put_v1_dhcp_clients_id
    PARAMS:
        all params available in the URL above. Or see vars below this comment
        macfilter is an additional param which controls if the MAC address of the host is allowed in MAC filtering (WiFi only)
        access_control is an additional param which controls if the host is allowed to go to the Internet
    '''
    hostname: str
    macaddress: str
    ipaddress: str
    ip6address: str = ''
    enable: int = 1
    id: int = -1
    macfilter: int = 0
    access_control: int = 0

    def create_or_update(self, logger, api):
        '''
        Method which creates/updates an host in the DHCP/LAN BBox device
        '''
        global cache_dhcp

        if not cache_dhcp:
            cache_dhcp = api.get_str('GET', '/dhcp/clients')
        clients = json.loads(cache_dhcp)['dhcp']['clients']
        for host in clients:
            self.id = host['id']
            temp_host = Host(macfilter = self.macfilter, access_control = self.access_control, **host)
            if self.macaddress == temp_host.macaddress:
                if self == temp_host:
                    logger.info('Host %s has no need to be uptaded' % self.hostname)
                else:
                    logger.info('Host %s will be updated' % self.hostname)
                    api.get_str('PUT', '/dhcp/clients/%i' % self.id, self.get_query_host())
                break
        else:
            logger.info('Host %s will be created' % self.hostname)
            api.get_str('POST', '/dhcp/clients?btoken=', self.get_query_host(True))
        if self.macfilter == 1:
            self.toggle_macfilter(logger, api)
        if self.access_control == 1:
            logger.info('Add %s in parental access control, state : enabled' % self.hostname)
            api.get_str('PUT', '/parentalcontrol/hosts', {'enable':1,'macaddress':self.macaddress})

    def toggle_macfilter(self, logger, api):
        '''
        Method which allows/denies access to Wifi for an host
        '''
        global cache_mac
        convert = ('disabled', 'enabled')

        if not cache_mac:
            cache_mac = api.get_str('GET', '/wireless/acl')
        rules = json.loads(cache_mac)['acl']['rules']
        for rule in rules:
            if rule['macaddress'] == self.macaddress:
                if rule['enable'] != convert[self.macfilter]:
                    logger.info('Updating Wifi mac filtering on host %s - state: %s' % (self.hostname, convert[self.macfilter]))
                    api.get_str('PUT', '/wireless/acl/rules/%s' % rule['id'], {'enable':self.macfilter,'macaddress':self.macaddress})
                else:
                    logger.info('Host %s has no need to update its mac filter rule' % self.hostname)
                return
        else:
            logger.info('Activate Wifi mac filtering on host %s - state: %s' % (self.hostname, convert[self.macfilter]))
            api.get_str('POST', '/wireless/acl/rules?btoken=', {'enable':convert[self.macfilter],'macaddress':self.macaddress})

    def get_query_host(self, remove_id=False):
        '''
        Method which returns params needed for creating/updating an host in DHCP/LAN 
        '''
        params = asdict(self)
        del params['access_control']
        del params['macfilter']
        del params['ip6address']
        if remove_id:
            del params['id']
        return params

class HostManager:
    '''
    This class manages Host objects
    Also controls LED luminosity, DynDNS state, and WiFi MAC filtering state
    PARAMS:
        logger, (MANDATORY), a logger object for printing info message
        api, (MANDATORY), an API object used for updating the BBox
        hosts, list of hosts to create/update a DHCP reservation/ mac filtering rule/ parental access control rule
    '''
    __slots__ = ['logger', 'api', 'conf', 'hosts']

    def __init__(self, logger, api, hosts):
        self.logger = logger
        self.api = api
        self.conf = hosts.pop('conf')
        self.hosts = hosts

    def conf_section(self):
        convert = ('disabled','enabled')
        self.logger.info('Update WiFi MAC Filtering, state: %s' % convert[self.conf['macfilter']])
        self.api.get_str('PUT', '/wireless/acl', {'enable':self.conf['macfilter']})

    def deploy(self):
        '''
        Method which creates/updates DHCP reservation (and more)
        on each host in inventory file, host section 
        '''
        self.logger.info('---------- SECTION Host ----------')
        for host in self.hosts:
            oHost = Host(host, **self.hosts[host])
            oHost.create_or_update(self.logger, self.api)
        self.logger.info('---------- END SECTION Host ----------')
