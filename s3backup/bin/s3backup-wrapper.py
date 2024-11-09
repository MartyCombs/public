#!/usr/bin/env python3
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create-metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/s3backup/bin/s3backup-wrapper.py
#=============================================================================#

import sys
import os
import argparse
import re
from mylog import MyLog



class S3BackupWrapper(object):
    '''Process files and archives for backup to S3.

    ATTRIBUTES
        debug      : Enable debug mode. Sets loglevel='DEBUG'.

        loglevel   : Set logging level [DEF: 'INFO']

    '''



    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    PROCESS_DIRS = (
        'drop'                 : '10-drop',
        'create_manifest'      : '20-tar_manifest',
        'encrypt'              : '30-encrypt',
        'create_metadata'      : '40-create_metadata',
    )



    def __init__(self, debug=None, loglevel='INFO',
                 force=False, showprogress=False):
        self.exit_status = 0
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.force = force
        self.showprogress = showprogress
        self.top_dir = self.TOP_DIR
        self.permitted_actions = [ 'create_manifest', 'encrypt',
                                   'create_metadata', 'upload' ]
        return



#----------------------------------------------------------------------------#
# BEGIN main program
def parse_arguments():
    '''Parse arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Create file meta-data.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', action='store_true', default=False,
        help='Enable debug mode.')
    parser.add_argument('--loglevel', action='store', default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--force', action='store_true', default=False,
        help='Overwrite existing metadata files.')
    parser.add_argument('--showprogress', action='store_true', default=False,
        help='Enable progress bar.')
    parser.add_argument('action', action='store', type=str,
        default=None,
        help='Action to take.')
    return parser.parse_args()



def main():
    args = parse_arguments()
    s = S3BackupWrapper(debug=args.debug,
                       loglevel=args.loglevel,
                       force=args.force,
                       showprogress=args.showprogress)
    print(s.top_dir)
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#
