#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import argparse
from backup import mylog
from backup import conf

def parse_arguments():
    '''Parse arguments.
    '''
    parser = argparse.ArgumentParser(description='Create a configuration file for S3 backups.')
    parser.add_argument('--debug', action='store_true',
        default=False,
        help='Verbose output.')
    parser.add_argument('--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--force', action='store_true',
        default=False,
        help='Force creation of confiuration file even if it already exists.')
    return parser.parse_args()



def main():
    args = parse_arguments()
    l = mylog.MyLog(debug=args.debug, loglevel=args.loglevel)
    log = l.log
    myconf = conf.Conf(debug=args.debug, loglevel=args.loglevel)
    conf_file = myconf.create_config()
    if os.path.isfile(myconf.filename) and not args.force:
        raise Exception('''
            Config already exists!
            "{}"
            Use --force to override.
        '''.format(myconf.filename))
    with open(myconf.filename, 'w') as c:
        c.write(conf_file)
    log.info('Created config "{}"'.format(myconf.filename))
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#


