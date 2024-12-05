#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import argparse
import subprocess
from mylog import MyLog
from s3backup_conf import S3BackupConf

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
SCRIPT = TOP_DIR + os.sep + 'create_metadata' + os.sep + 'bin' + os.sep + 'create_metadata.sh'


def parse_arguments():
    '''Parse arguments.
    '''
    c = S3BackupConf()
    c.read()
    parser = argparse.ArgumentParser(description='''Create metadata files for
        any encrypted files in {} and move all files over to {}.'''.format(
        str(os.sep).join(c.metadata_dir.split(os.sep)[-3:]),
        str(os.sep).join(c.s3upload_dir.split(os.sep)[-3:])))
    parser.add_argument('--debug', action='store_true',
        default=False,
        help='Verbose output.')
    parser.add_argument('--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--noop', action='store_true',
        default=False,
        help='Take no action.')
    parser.add_argument('--showprogress', action='store_true',
        default=False,
        help='Enable progress bar when summing large files.')
    args = parser.parse_args()
    if args.noop == True: args.debug = True
    return args



def get_clean_list(log=None, src_dir=None, extensions=['all']):
    '''Examine source directory for files to process.  Exclude directories and
    special files.

    RETURN
            List of full paths to files.
    '''
    log.info('Examining "{}"'.format(src_dir))
    filelist = os.listdir(src_dir)
    cleaned_list = []
    report = 'Processing from\n{}\n  "{}"\n'.format('='*76, src_dir)
    for f in filelist:
        ext = os.path.splitext(f)[1]
        fullpath = src_dir + os.sep + f
        # Exclude special files.
        if f == '.DS_Store':
            log.warning('Excluding special file {}'.format(fullpath))
        elif os.path.isfile(fullpath) and ('all' in extensions or ext in extensions):
            cleaned_list.append(fullpath)
            report += '        {}\n'.format(f)
        else:
            log.warning('Excluding {}'.format(f))
    report += '{}\n'.format('='*76)
    log.debug('{}'.format(report))
    return cleaned_list



def main():
    args = parse_arguments()
    l = MyLog(debug=args.debug, loglevel=args.loglevel)
    log = l.log

    # Read the config.
    cfg = S3BackupConf(debug=args.debug, loglevel=args.loglevel)
    cfg.read()
    src_dir = cfg.metadata_dir
    dest_dir = cfg.s3upload_dir

    # Process only encrypted files from the source directory.
    filelist = get_clean_list(log=log, src_dir=src_dir, extensions=['.enc', '.asc'])
    if len(filelist) == 0:
        log.info('No files to process')
        return

    # Prep for running the subscript.
    #     create_metadata.sh does not take --noop option
    cmd=['bash', SCRIPT]
    subargs = sys.argv[1:]
    if '--noop' in subargs: subargs.remove('--noop')
    for a in subargs:
        cmd.append(a)
    for f in filelist:
        cmd.append(f)
    if args.noop:
        log.debug('NO-OP: Would run\n{}\n    {}\n{}'.format(
            '='*76, cmd, '='*76))
    else:
        log.debug('Running\n{}\n    {}\n{}'.format('='*76, cmd, '='*76))
        results = subprocess.run(cmd)
        if results.returncode != 0:
            log.error('Failed to create metadata files!')
            sys.exit(results.returncode)

    # After successful creation of metadata files, the following
    # files are moved to the next directory in the workflow:
    #    - encrypted files (.asc, .enc)
    #    - manifest files  (.manifest)
    #    - metadata files (.meta)
    move_filelist = get_clean_list(log=log, src_dir=src_dir,
        extensions=['.enc', '.asc', '.manifest', '.meta'])

    # Move files to the destination directory.
    log.info('Moving files from "{}" to "{}"'.format(src_dir, dest_dir))
    report = 'Moved\n{}\nfrom {}\nto   {}\n'.format('='*76, src_dir, dest_dir)
    for f in move_filelist:
        report += '        {}\n'.format(os.path.basename(f))
        src=f
        dst=dest_dir + os.sep + os.path.basename(f)
        if args.noop == False: os.rename(src, dst)
    report += '{}\n'.format('='*76)
    if args.noop == True:
        log.debug('NO-OP: {}'.format(report))
    else:
        log.debug('{}'.format(report))

    # Clean the source directory of all remaining files.
    log.debug('Cleaning "{}"'.format(src_dir))
    for f in os.listdir(src_dir):
        filename = src_dir + os.sep + f
        if args.noop == False:  os.remove(filename)
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#

