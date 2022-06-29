from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from bbox.section.wifischeduler import Scheduler

class AccesscontrolManager:
    '''
    This class manages Parental Access Control rules
    Also, sets the default Policy
    PARAMS:
        logger, (MANDATORY), a logger object to print info message
        api, (MANDATORY), an API object to control the BBox
        rules, a dict containing rules to apply to the Parental Access Control scheduler
    '''
    __slots__ = ['logger', 'api', 'conf', 'rules']

    def __init__(self, logger, api, rules):
        convert = ('disabled','enabled')
        self.logger = logger
        self.api = api
        self.conf = rules.pop('conf')
        self.rules = rules
        self.logger.info('Update Parental Access Control Scheduler, state : %s | policy: %s' % (convert[self.conf['enable']], self.conf['policy']))
        self.api.get_str('PUT', '/parentalcontrol', {'enable':self.conf['enable'],'defaultpolicy':self.conf['policy']})

    def deploy(self):
        '''
        Method which deploys Parental Access Control Scheduler rule from inventory file
        '''
        self.logger.info('---------- SECTION Parental Access Control ----------')
        self.logger.info('Remove all previous rules in Parental Access Control Scheduler')
        self.api.get_str('POST', '/parentalcontrol/scheduler?btoken=', {'enable':1,'start':'Sunday 0:00','end':'Saturday 23:59'})
        for rule in self.rules:
            oRule = Scheduler(**self.rules[rule])
            oRule.create(self.logger, self.api, 'Parental Access Control', 'parentalcontrol')
        self.logger.info('---------- END SECTION Parental Access Control ----------')
