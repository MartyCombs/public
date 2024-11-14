#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import argparse
from mylog import MyLog
from enc_conf import EncConf

def parse_arguments():
    '''Parse arguments.
    '''
    parser = argparse.ArgumentParser(description='Create encryption config file.')
    parser.add_argument('--debug', action='store_true',
        default=False,
        help='Verbose output.')
    parser.add_argument('--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--force', action='store_true',
        default=False,
        help='Force creation of configuration file even if it already exists.')
    parser.add_argument('--stdout', action='store_true',
        default=False,
        help='Echo contents of config to STDOUT.')
    return parser.parse_args()


def main():
    args = parse_arguments()
    l = MyLog(debug=args.debug, loglevel=args.loglevel)
    log = l.log
    myconf = EncConf(debug=args.debug, loglevel=args.loglevel)
    conf_file = myconf.create()
    if args.stdout == True:
        print(conf_file)
        return
    if os.path.isfile(myconf.filename) and not args.force:
        raise Exception('''
            Config exists.  "{}"
            Use --force to override.'''.format(myconf.filename))
    with open(myconf.filename, 'w') as c:
        c.write(conf_file)
    log.info('Created config "{}"'.format(myconf.filename))
    return



if __name__ == "__main__":
    sys.exit(main())

