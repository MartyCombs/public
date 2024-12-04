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
from aes_crypt import AESCrypt



def parse_arguments():
    '''Parse arguments.
    '''
    parser = argparse.ArgumentParser(description='''Encrypt multiple
    files using AES-GCM encryption.''')
    parser.add_argument('--debug', action='store_true',
        default=False,
        help='Verbose output.')
    parser.add_argument('--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--showprogress', action='store_true',
        default=False,
        help='Enable progress bar with large files.')
    parser.add_argument('files', action='store', nargs='+',
        type=str, default=None,
        help='Files to process.')
    return parser.parse_args()



def main():
    args = parse_arguments()
    l = MyLog(debug=args.debug, loglevel=args.loglevel)
    log = l.log
    aesgcm = AESCrypt(debug=args.debug,
                      loglevel=args.loglevel,
                      showprogress=args.showprogress)
    for file in args.files:
        aesgcm.set_filename(file)
        aesgcm.encrypt()
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#
