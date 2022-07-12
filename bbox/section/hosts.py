from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from dataclasses import dataclass,asdict

cache_dhcp = None
cache_nat = None

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
            cache_dhcp = api.get_str('GET', '/dhcp/clients').decode('utf-8').strip('[]')
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
        global cache_nat
        convert = ('disabled', 'enabled')

        if not cache_nat:
            cache_nat = api.get_str('GET', '/wireless/acl').decode('utf-8').strip('[]')
        rules = json.loads(cache_nat)['acl']['rules']
        for rule in rules:
            if rule['macaddress'] == self.macaddress:
                if rule['enable'] != convert[self.macfilter]:
                    logger.info('Updating Wifi mac filtering on host %s - state: %s' % (self.hostname, convert[self.macfilter]))
                    api.get_str('PUT', '/wireless/acl/rules/%s' % rule['id'], {'enable': self.macfilter, 'macaddress': self.macaddress})
                else:
                    logger.info('Host %s has no need to update its mac filter rule' % self.hostname)
                return
        else:
            logger.info('Activate Wifi mac filtering on host %s - state: %s' % (self.hostname, convert[self.macfilter]))
            api.get_str('POST', '/wireless/acl/rules?btoken=', {'enable': convert[self.macfilter],'macaddress': self.macaddress})

    def get_query_host(self, remove_id = False):
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
        self.apply_lan()
        self.apply_dhcp()
        self.logger.info('Update WiFi MAC Filtering, state: %s' % convert[self.conf['macfilter']])
        self.api.get_str('PUT', '/wireless/acl', {'enable':self.conf['macfilter']})
        self.logger.info('Update DynDNS, state: %s' % convert[self.conf['dyndns']])
        self.api.get_str('PUT', '/dyndns', {'enable':self.conf['dyndns']})
        self.logger.info('Change the LED luminosity, state: %s' % convert[self.conf['led']])
        self.api.get_str('PUT', '/device/display', {'luminosity': self.conf['led'] * 100})

    def apply_dhcp(self):
        '''
        Method which changes the DHCP subnet and lease per address
        '''
        state = json.loads(self.api.get_str('GET', '/dhcp').decode('utf-8').strip('[]'))
        to_comp = {
                'state':self.conf['enable'],
                'enable':self.conf['enable'],
                'minaddress':self.conf['dhcp_subnet'].split('-')[0],
                'maxaddress':self.conf['dhcp_subnet'].split('-')[1],
                'leasetime':self.conf['dhcp_lease']}
        if to_comp != state['dhcp']:
            self.logger.info('DHCP needs to be updated. range: %s | lease: %i sec' % (self.conf['dhcp_subnet'], to_comp['leasetime']))
            to_comp.pop('state')
            self.api.get_str('PUT', '/dhcp', to_comp)
        else:
            self.logger.info('DHCP server range %s has no need to be updated' % self.conf['dhcp_subnet'])

    def apply_lan(self):
        '''
        Method which changes the LAN information on the BBOX
        WARNING: if the Class C subnet is changed, the BBox reboots
        '''
        state = json.loads(self.api.get_str('GET', '/lan/ip').decode('utf-8').strip('[]'))['lan']['ip']
        if self.conf['lan_router_ip'] != state['ipaddress']:
            self.logger.info('LAN router IP %s needs to be updated' % self.conf['lan_router_ip'])
            self.api.get_str('PUT', '/lan', {'ipaddress':self.conf['lan_router_ip']})
            self.logger.warning('BBox needs to be rebooted, disconnect and reconnect your device from LAN/WiFi, re run the script after complete')
            self.api.get_str('POST', '/device/reboot?btoken=')
            exit (0)
        else:
            self.logger.info('LAN Router IP %s has no need to be updated' % self.conf['lan_router_ip'])

    def deploy(self):
        '''
        Method which creates/updates each host in inventory file, host section 
        '''
        self.logger.info('---------- SECTION Host, DHCP, LAN, ... ----------')
        for host in self.hosts:
            oHost = Host(host, **self.hosts[host])
            oHost.create_or_update(self.logger, self.api)
        self.logger.info('---------- END SECTION Host, DHCP, LAN, ... ----------')
