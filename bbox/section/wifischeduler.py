from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from dataclasses import dataclass, asdict

@dataclass(slots = True)
class Scheduler:
    '''
    This class creates a Scheduler object
    PARAMS:
        all params in https://api.bbox.fr/doc/apirouter/index.html#api-Wi_Fi-post_v1_wireless_id
        or https://api.bbox.fr/doc/apirouter/index.html#api-ParentalControl-post_v1_parentalcontrol_scheduler
    '''
    start: str
    end: str
    enable: int=1

    def __post_init__(self):
        self.start = self.start.replace('_', ' ')
        self.end = self.end.replace('_', ' ')

    def create(self, logger, api, service, path):
        '''
        Method which create a Wifi Scheduler rule
        '''
        logger.info('%s Scheduler Rule will be created, start %s | stop %s' % (service, self.start, self.end))
        api.get_str('POST', '/%s/scheduler?btoken=' % path, asdict(self))

class WifischedulerManager:
    '''
    This class manages WiFi Scheduler rules
    Also, sets the Wifi Scheduler state
    PARAMS:
        logger, (MANDATORY), a logger object to print info message
        api, (MANDATORY), an API object to control the BBox
        rules, a dict containing rules to apply to the wifi scheduler
    '''
    __slots__ = ['logger', 'api', 'conf', 'rules']

    def __init__(self, logger, api, rules):
        convert = ('disabled', 'enabled')
        self.logger = logger
        self.api = api
        self.conf = rules.pop('conf')
        self.rules = rules
        self.logger.info('Update WiFi Scheduler state : %s' % convert[self.conf['enable']])
        self.api.get_str('PUT', '/wireless/scheduler', {'enable':self.conf['enable']})

    def deploy(self):
        '''
        Method which deploys WiFi Scheduler rule from inventory file
        '''
        self.logger.info('---------- SECTION WiFi Scheduler ----------')
        self.logger.info('Remove all previous rules in WiFi Scheduler')
        self.api.get_str('POST', '/wireless/scheduler?btoken=', {'enable':0,'start':'Sunday 0:00','end':'Saturday 23:59'})
        for rule in self.rules:
            oRule = Scheduler(**self.rules[rule])
            oRule.create(self.logger, self.api, 'Wifi', 'wireless')
        self.logger.info('---------- END SECTION WiFi Scheduler ----------')
