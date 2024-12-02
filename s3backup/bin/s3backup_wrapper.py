#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl
#=============================================================================#

import sys
import os
import argparse
import re
import subprocess
from mylog import MyLog
from s3backup_conf import S3BackupConf




def parse_arguments(actions=None):
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
    parser.add_argument('--noop', action='store_true',
        default=False,
        help='Take no action.')
    parser.add_argument('action', action='store', type=str,
        default=None,
        choices=actions,
        help='Action to take.')
    return parser.parse_args()



def get_interpretor(script=None):
    re_python = re.compile(r'^.*\.py$')
    re_bash = re.compile(r'^.*\.sh$')
    if re.match(re_python, script): return 'python3'
    if re.match(re_bash, script): return 'bash'
    return


def add_options(mylist=None):
    for o in sys.argv[1:-1]:
        mylist.append(o)
    return mylist



def main():
    top_dir = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    actions = [ 'ALL', 'drop', 'manifest', 'encrypt', 'metadata', 'upload' ]
    args = parse_arguments(actions=actions)
    l = MyLog(debug=args.debug, loglevel=args.loglevel)
    log = l.log
    cfg = S3BackupConf(debug=args.debug, loglevel=args.loglevel)
    cfg.read()
    scripts = {
        'drop'     : cfg.drop_script,
        'manifest' : cfg.manifest_script,
        'encrypt'  : cfg.encrypt_script,
        'metadata' : cfg.metadata_script,
        'upload'   : cfg.upload_script
    }
    if args.action == 'ALL' or args.action == 'drop':
        interpretor = get_interpretor(scripts['drop'])
        cmd=[interpretor, scripts['drop']]
        cmd = add_options(cmd)
        subprocess.run(cmd)
    if args.action == 'ALL' or args.action == 'manifest':
        interpretor = get_interpretor(scripts['manifest'])
        cmd=[interpretor, scripts['manifest']]
        cmd = add_options(cmd)
        subprocess.run(cmd)
    if args.action == 'ALL' or args.action == 'encrypt':
        interpretor = get_interpretor(scripts['encrypt'])
        cmd=[interpretor, scripts['encrypt']]
        cmd = add_options(cmd)
        subprocess.run(cmd)
    if args.action == 'ALL' or args.action == 'metadata':
        interpretor = get_interpretor(scripts['metadata'])
        cmd=[interpretor, scripts['metadata']]
        cmd = add_options(cmd)
        subprocess.run(cmd)
    if args.action == 'ALL' or args.action == 'upload':
        interpretor = get_interpretor(scripts['upload'])
        cmd=[interpretor, scripts['upload']]
        cmd = add_options(cmd)
        subprocess.run(cmd)
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#
