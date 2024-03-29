#!/usr/bin/env python3
from __future__ import (absolute_import, division, print_function)

import argparse
import os
import sys
import json

from pprint import pprint
from datetime import datetime
from bbox.logger import Logger
from bbox.api import BBoxAPI
from bbox.dataloader import DataLoader, Config
from bbox.section.hosts import HostManager
from bbox.section.fwv4 import Fwv4Manager
from bbox.section.fwv6 import Fwv6Manager
from bbox.section.nat import NatManager
from bbox.section.wifi import WifiManager
from bbox.section.wifischeduler import WifischedulerManager
from bbox.section.accesscontrol import AccesscontrolManager
from bbox.section.dyndns import DyndnsManager
from bbox.section.device import DeviceManager

def get_api_and_logger(config_file):
    '''
    Get API and logger objects
    '''
    config = Config(os.path.expanduser(config_file))
    logger = Logger()
    api = BBoxAPI(logger.get_logger(), config.url, config.password)

    return (logger.get_logger(), api)

def raw_api_call(args):
    '''
    Raw API call
    ex: bbox_cli.py raw GET '/firewall/rules'
    '''
    logger, api = get_api_and_logger('~/.bbox.config')
    logger.info('RAW API call: Method=%s | Path=%s | Params=%s' % (args.method, args.path, args.params))
    pprint(api.get_str(args.method, args.path, args.params), sort_dicts = False, indent=2)
    
def deploy_inventory(args):
    '''
    Configure the BBox with Inventory file
    ex: bbox_cli.py apply /root/inventory [-l host]
    '''
    logger, api = get_api_and_logger('~/.bbox.config')
    dl = DataLoader(logger, args.file)
    data = dl.get_data()
    bkp_name = None

    if len(data) > 0:
        choices = ('y', 'Y')
        backup = input("Do you want to make a backup before apply (Default: no) ? (y|N) : ")
        if backup in choices:
            bkp_name = 'Backup_' + datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
            logger.warning('You can only store 2 backups, at the third, the second backup id is deleted')
            logger.info('Create backup %s' % bkp_name)
            api.get_str('POST', '/configs?btoken=', {'name':bkp_name})
        for section in data:
            if args.limit is None or section == args.limit:
                manager = getattr(sys.modules[__name__], section.capitalize() + 'Manager')(logger, api, data[section])
                manager.conf_section()
                manager.deploy()
        logger.info('Apply succesfully completed on %s inventory' % args.file)
        if bkp_name:
            restore = input('Do you want to restore the previous backup (Default: no)? (y|N) : ')
            if restore in choices:
                backups = json.loads(api.get_str('GET', '/configs'))['configs']
                for bkp in backups:
                    if bkp['name'] == bkp_name:
                        logger.info('Restore backup %s' % bkp_name)
                        api.get_str('POST', '/configs/%i?btoken=' % bkp['id'], {'restore': 1})
                        break
                
def main():
    parser = argparse.ArgumentParser(description='Python3 CLI utility for Bouygues Telecom\'s BBox Miami Router API.')
    parsers = parser.add_subparsers(help='CLI to control BBOx\'s Router')

    parser_raw = parsers.add_parser('raw', help='Execute raw command')
    parser_raw.add_argument('method', action='store', help='HTTP method', metavar='VERB')
    parser_raw.add_argument('path', action='store', help='API command', metavar='PATH')
    parser_raw.add_argument('params', action='store', nargs='?', help='API command arguments', metavar='ARGS')
    parser_raw.set_defaults(func=raw_api_call)

    limits = ('wifi','host','fwv4','fwv6','nat','wifischeduler','accesscontrol','dyndns','device')
    parser_apply = parsers.add_parser('apply', help='deploy from inventory file')
    parser_apply.add_argument('file', action='store', help='Inventory file path', metavar='FILE')
    parser_apply.add_argument('-l', '--limit', required=False, action='store', choices=limits, help='limit apply to a section of the inventory', metavar='SECTION')
    parser_apply.set_defaults(func=deploy_inventory)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
