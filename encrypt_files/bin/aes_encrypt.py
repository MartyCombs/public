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



def check_file(filename):
    encrypted_name = filename + '.enc'
    if os.path.exists(encrypted_name):
        raise Exception('Cannot encrypt!  Target file already exists "{}"'.format(
            encrypted_name))
    return



def main():
    args = parse_arguments()
    l = MyLog(debug=args.debug, loglevel=args.loglevel)
    log = l.log
    aesgcm = AESCrypt(debug=args.debug,
                      loglevel=args.loglevel,
                      showprogress=args.showprogress)

    # Confirm that a file of the same name as the encrypted one does not
    # already exist within the same directory.
    for file in args.files:
        check_file(os.path.realpath(file))

    for file in args.files:
        aesgcm.set_filename(file)
        aesgcm.encrypt()

    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#
