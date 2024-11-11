#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import re
import tarfile
import argparse
from mylog import MyLog
from metadata_conf import MetadataConf
from s3backup_conf import S3BackupConf

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])

def parse_arguments():
    '''Parse arguments.
    '''
    parser = argparse.ArgumentParser(description='Create manifests for any archives.')
    parser.add_argument('--debug', action='store_true',
        default=False,
        help='Verbose output.')
    parser.add_argument('--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--noop', action='store_true',
        default=False,
        help='Take no action.')
    return parser.parse_args()



def main():
    args = parse_arguments()
    l = MyLog(debug=args.debug, loglevel=args.loglevel)
    log = l.log

    # Read the config.
    cfg = S3BackupConf(debug=args.debug, loglevel=args.loglevel)
    cfg.read()
    src_dir = cfg.drop_dir
    dest_dir = cfg.manifest_dir

    # Examine the source directory for archives and build manifests.
    re_targz = re.compile(r'^.*\.tar\.gz$')
    report = 'Source directory\n  {}\ncontains:\n{}\n'.format(src_dir,
                                                               '='*76)
    nodes = os.listdir(src_dir)
    manifests = {}
    for n in nodes:
        report += '    {}\n'.format(n)
        fullpath = src_dir + os.sep + n
        if re.match(re_targz, n):
            with tarfile.open(fullpath, 'r:gz') as tar:
                manifests[fullpath] = sorted(tar.getnames())
            tar.close()
    log.debug('{}\n'.format(report))

    # Move files to the destination directory.
    report = 'Moved the following files to\n  {}\n{}\n'.format(dest_dir,
                                                               '='*76)
    if args.noop == False:
        for node in nodes:
            report += '    {}\n'.format(node)
            src=src_dir + os.sep + node
            dst=dest_dir + os.sep + node
            os.rename(src, dst)
    log.debug('{}'.format(report))

    # Create manifest files in the destination directory.
    report = 'Created the following manifests in\n  {}\n{}\n'.format(dest_dir,
                                                                     '='*76)
    for m in manifests.keys():
        dst = dest_dir + os.sep + os.path.basename(m) + '.manifest'
        report += '    {}\n'.format(os.path.basename(dst))
        with open(dst, 'w') as f:
            for line in manifests[m]:
                f.write('{}\n'.format(line))
    log.debug('{}'.format(report))
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#

