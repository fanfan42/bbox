from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from dataclasses import dataclass,asdict

@dataclass(slots = True)
class DHCPOption:
    '''
    This class creates/updates a dhcp option object like in https://api.bbox.fr/doc/apirouter/#api-DHCP-put_v1_dhcp_options
    PARAMS:
        all params available in the URL above.
    '''
    name: int
    value: str
    description: str = ''
    enable: int = 1

    def create(self, logger, api):
        '''
        Method which creates a DHCP option
        '''
        logger.info('DHCP option %s (description: %s) will be created' % (self.name, self.description))
        api.get_str('POST', '/dhcp/options?btoken=', asdict(self))

class DeviceManager:
    '''
    This class manages DHCPOption objects
    Also controls LED luminosity, LAN router IP and DHCP server state and range
    PARAMS:
        logger, (MANDATORY), a logger object for printing info message
        api, (MANDATORY), an API object used for updating the BBox
        options, list of DHCP options to create/update on DHCP server
    '''
    __slots__ = ['logger', 'api', 'conf', 'options']

    def __init__(self, logger, api, options):
        self.logger = logger
        self.api = api
        self.conf = options.pop('conf')
        self.options = options

    def conf_section(self):
        convert = ('disabled','enabled')
        iprange = self.conf['dhcp_subnet'].split('-')
        leasetime = self.conf['dhcp_lease'] if 'dhcp_lease' in self.conf else 86400
        state = json.loads(self.api.get_str('GET', '/lan/ip').decode('utf-8').strip('[]'))['lan']['ip']

        if self.conf['lan_router_ip'] != state['ipaddress']:
            self.logger.info('LAN router IP %s needs to be updated' % self.conf['lan_router_ip'])
            self.api.get_str('PUT', '/lan', {'ipaddress':self.conf['lan_router_ip']})
            self.logger.warning('BBox needs to be rebooted, disconnect and reconnect your device from LAN/WiFi, re run the script after complete')
            self.api.get_str('POST', '/device/reboot?btoken=')
            exit (0)

        self.logger.info('Update DHCP range, from %s to %s - state: %s' % (iprange[0], iprange[1], convert[self.conf['enable']]))
        self.api.get_str('PUT', '/dhcp', {'enable':self.conf['enable'],'minaddress':iprange[0],'maxaddress':iprange[1],'leasetime':leasetime})
        self.logger.info('Change the LED luminosity, state: %s' % convert[self.conf['led']])
        self.api.get_str('PUT', '/device/display', {'luminosity': self.conf['led'] * 100})

    def delete_all(self):
        '''
        Method which deletes all options in DHCP server
        '''
        raw = self.api.get_str('GET', '/dhcp/options').decode('utf-8').strip('[]')
        options = json.loads(raw)['dhcp']['options']
        for opt in options:
            self.logger.info('Deleting DHCP option %i, value: %s' % (opt['option'], opt['value']))
            self.api.get_str('DELETE', '/dhcp/options/%i' % opt['id'])

    def deploy(self):
        '''
        Method which creates/updates each DHCP option wanted in the DHCP server 
        '''
        self.logger.info('---------- SECTION Device ----------')
        self.delete_all()
        for opt in self.options:
            oOpt = DHCPOption(opt, **self.options[opt])
            oOpt.create(self.logger, self.api)
        self.logger.info('---------- END SECTION Device ----------')
