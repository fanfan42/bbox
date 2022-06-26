from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import logging

class Logger:
    '''
    This class creates a logger object to print some information/warning/error messages
    '''
    __slots__ = ['logger']

    def __init__(self):
        # Setup logging facility
        formatter = logging.Formatter ('%(levelname)s: %(message)s')

        console = logging.StreamHandler ()
        console.setFormatter (formatter)

        self.logger = logging.getLogger ()
        self.logger.addHandler (console)
        self.logger.setLevel (logging.INFO)

    def get_logger(self):
        '''
        Returns the logger previously created
        '''
        return self.logger
