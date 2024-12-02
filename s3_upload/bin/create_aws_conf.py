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
from aws_conf import AWSConf

def parse_arguments():
    '''Parse arguments.
    '''
    parser = argparse.ArgumentParser(description='''Create the configuration
        file for S3 AWS uploads.
        ''')
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
    myconf = AWSConf(debug=args.debug, loglevel=args.loglevel)
    conf_file = myconf.build()
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



#=============================================================================#
# END
#=============================================================================#
