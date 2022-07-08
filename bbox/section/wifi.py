from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from dataclasses import dataclass, asdict
from getpass import getpass

cache_wifi = None

@dataclass(slots = True)
class WiFi:
    '''
    This class creates a WiFi object
    PARAMS:
        all params in https://api.bbox.fr/doc/apirouter/#api-Wi_Fi-put_v1_wireless_id
    '''
    id: int
    ssid: str
    passphrase: str
    radio: str
    unified: int
    security: str='WPA+WPA2'
    enable: int=1
    channel: int=0
    encryption: str='AES'
    dfs: int=1
    greenap: int=0
    hidden: int=0

    def _format(self, raw_data):
        '''
        Internal method to get the equivalent information in a raw GET call for getting actual Wifi configured than the current wifi 
        '''
        data = dict()
        for i in (24,5):
            str_i = str(i)
            data[i] = dict()
            data[i]['id'] = i
            data[i]['ssid'] = raw_data['ssid'][str_i]['id']
            data[i]['passphrase'] = raw_data['ssid'][str_i]['security']['passphrase']
            data[i]['security'] = raw_data['ssid'][str_i]['security']['protocol']
            data[i]['enable'] = raw_data['radio'][str_i]['state']
            data[i]['radio'] = raw_data['radio'][str_i]['standard']
            data[i]['channel'] = raw_data['radio'][str_i]['channel']
            data[i]['encryption'] = raw_data['ssid'][str_i]['security']['encryption']
            if 'dfs' in raw_data['radio'][str_i]:
                data[i]['dfs'] = raw_data['radio'][str_i]['dfs']
            if 'greenap' in raw_data['radio'][str_i]:
                data[i]['greenap'] = raw_data['radio'][str_i]['greenap']
            data[i]['hidden'] = raw_data['ssid'][str_i]['hidden']
            data[i]['unified'] = raw_data['unified']
        return data

    def _get_if_empty_pass(self):
        '''
        Internal method which gets the passphrase for a Wifi if let empty in the inventory file
        '''
        try1 = 'a'
        try2 = 'b'
        while try1 != try2:
            try1 = getpass('Enter passphrase for SSID %s : ' % self.ssid)
            try2 = getpass('Re-enter passphrase for SSID %s : ' % self.ssid)
        return try1

    def update(self, logger, api):
        '''
        Method which updates a Wifi configuration
        '''
        global cache_wifi

        if self.passphrase == None or self.passphrase == '':
            self.passphrase = self._get_if_empty_pass()
        if not cache_wifi:
            cache_wifi = api.get_str('GET', '/wireless').decode('utf-8').strip('[]')
        ssids = self._format(json.loads(cache_wifi)['wireless']) 
        for id in ssids:
            temp_wifi = WiFi(**ssids[id])
            if self == temp_wifi:
                logger.info('WiFi %s has no need to be updated' % self.ssid)
                return
        else:
            logger.info('Updating WiFi %s' % self.ssid)
            api.get_str('PUT', '/wireless/%i' % self.id, asdict(self))
            return

class WifiManager:
    '''
    This class manages WiFi objects
    Also, sets the Wifi state and WPS state
    PARAMS:
        logger, (MANDATORY), a logger object to print informational object
        api, (MANDATORY), an API object to control the bbox
        wifis, a dict containing wifi configuration to apply
    '''
    __slots__ = ['logger', 'api', 'conf', 'wifis']

    def __init__(self, logger, api, wifis):
        self.logger = logger
        self.api = api
        self.conf = wifis.pop('conf')
        self.wifis = wifis

    def conf_section(self):
        convert = ('disabled','enabled')
        self.logger.info('Update WiFi and WPS states: WiFi : %s | WPS : %s' % (convert[self.conf['enable']], convert[self.conf['wps']]))
        self.api.get_str('PUT', '/wireless', {'enable':self.conf['enable'],'enable':self.conf['wps']})

    def deploy(self):
        '''
        Method which deploys wifis in inventory file
        '''
        self.logger.info('---------- SECTION WiFi, WPS ----------')
        for wifi in self.wifis:
            oWiFi = WiFi(ssid = wifi, **self.wifis[wifi])
            oWiFi.update(self.logger, self.api)
        self.logger.info('---------- END SECTION WiFi, WPS ----------')
