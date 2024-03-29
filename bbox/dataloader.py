from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re

from configparser import RawConfigParser
from configparser import ParsingError
from getpass import getpass

class DataLoader:
    '''
    This class creates an object able to parse an INI like inventory file
    PARAMS:
        logger, (MANDATORY) a logger object to report messages during parsing
        inventory, (MANDATORY) a file with the state wanted for the BBox
    '''
    __slots__ = ['logger', 'data', 'inventory']

    def __init__ (self, logger, inventory):
        self.logger = logger
        self.data = dict()
        if not os.path.isfile(inventory):
            self.logger.error("DataLoader : invalid filename: '%s'" % inventory)
            raise
        self.inventory = inventory

    def _to_int(self, string):
        '''
        Internal method which returns an int if the string, "string", should be an int or the original "string"
        '''
        if not isinstance(string, int) and string.isdigit():
            return int(string)
        return string

    def _refine_data(self, unformatted_data):
        '''
        internal method which translates the pre parsed RawConfigParser object in an Ansible like Inventory file
        '''
        regex = re.compile(r'{{(?P<section>\w+(\-\w+)*)\.(?P<name>\w+(\-\w+)*)\.(?P<attrib>\w+(\-\w+)*)}}')
        for raw_section,entries in unformatted_data.items():
            section = raw_section.split(' ')[0]
            self.data[section] = dict()
            self.data[section]['conf'] = dict()
            for conf in raw_section.split(' ')[1:]:
                str_value = conf.split('=')[1]
                self.data[section]['conf'][conf.split('=')[0]] = self._to_int(str_value)
            for name,attribs in entries.items():
                self.data[section][name] = dict()
                for attrib in attribs.split(' '):
                    key = attrib.split('=')[0]
                    value = attrib.split('=')[1]
                    str_value = self._convert_templated_value(value, regex)
                    self.data[section][name][key] = self._to_int(str_value)

    def _convert_templated_value(self, value, regex):
        '''
        Internal method which gets the real value of a templated value
        '''
        if re.match(regex, value):
            new_value = value
            for imatch in re.finditer(regex, value):
                tmpl = imatch.groupdict()
                try:
                    is_value = self.data[tmpl.get('section')][tmpl.get('name')][tmpl.get('attrib')]
                    new_value = new_value.replace(imatch.group(), str(is_value))
                except KeyError:
                    self.logger.error('DataLoader : Templated value "%s" hasn\'t been declared before' % value)
                    raise
            return new_value
        return value

    def get_data(self):
        '''
        Method which returns the final data to be deployed
        '''
        if not len(self.data):
            parser = RawConfigParser(delimiters=(' '))
            parser.optionxform = str
            try:
                parser.read(self.inventory)
            except ParsingError:
                self.logger.error("DataLoader : INI Inventory cannot be parsed")
                raise
            self._refine_data(parser._sections)
        return self.data

class Config:
    '''
    This class creates a config object which contains the URL and password to call the BBox API
    PARAMS:
        path, (MANDATORY), the file with the URL and password (even empty) to call the BBox API
    '''
    __slots__ = ['url', 'password'] 

    def __init__ (self, path):
        if os.path.isfile(path):
            parser = RawConfigParser(delimiters=('='))
            parser.optionxform = str
            try:
                parser.read(path)
            except ParsingError:
                print("Config : INI config file in ~/.bbox.config  cannot be parsed")
                raise
            self.password = parser._sections['info']['password']
            if self.password == '':
                try1 = 'a'
                try2 = 'b'
                while try1 != try2:
                    try1 = getpass('Enter password for BBox API : ')
                    try2 = getpass('Re-enter password for BBox API : ')
                self.password = try1
            self.url = parser._sections['info']['url']
