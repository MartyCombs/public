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
from metadata import MetaData
from s3backup_conf import S3BackupConf

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
SCRIPT = TOP_DIR + os.sep + 's3_upload' + os.sep + 'bin' + os.sep + 'upload.sh'


def parse_arguments():
    '''Parse arguments.
    '''
    c = S3BackupConf()
    c.read()
    parser = argparse.ArgumentParser(description='''Upload encrypted and
        metadata files in {} to the S3 buckets referred to within the .meta
        files. Then move manifest files to {} and metadata files to
        {}.'''.format(
        str(os.sep).join(c.s3upload_dir.split(os.sep)[-3:]),
        c.manifest_destination,
        c.metadata_destination))
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
    src_dir = cfg.s3upload_dir
    dest_dir = cfg.metadata_dir

    # Process only metadata files from the source directory.  The URLs they
    # contain refer to files which will be uploaded to S3.
    filelist = get_clean_list(log=log, src_dir=src_dir,
        extensions=['.meta'])
    if len(filelist) == 0:
        log.info('No files to process')
        return

    # Prep for running the subscript.
    #     upload.sh does not take --noop option
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
            log.error('Failed to upload to S3!')
            sys.exit(results.returncode)


    '''
    After successful upload to S3, manifest files are moved to a subdirectory
    of manifest_destination and metadata files are moved to a subdirectory of
    metadata_destination based on the URLs within the metadata files.

    METADATA
        metadata_destination setting of /path/to/metadata

        s3_url_metadata setting of
            s3://mcombs-backup/test/test-archive.tar.gz.manifest.asc.meta

        /path/to/metadata/mcombs-backup/test/test-archive.tar.gz.manifest.asc.meta

    MANIFEST
        manifest_destination of /path/to/manifests

        s3_url setting of
            s3://mcombs-backup/test/test-archive.tar.gz.manifest.asc

        /path/to/manifests/mcombs-backup/test/test-archive.tar.gz.manifest.asc

    '''
    # Build two source --> destination lists.
    metadata_files = {}
    manifest_files = {}

    # Preliminarily create manifest source / destination list.
    man_src_files = get_clean_list(log=log,
                                   src_dir=src_dir,
                                   extensions=['.manifest'])
    for man in man_src_files:
        manifest_files[man] = None

    # Now sort through metadata files for 's3_url_metadata' and 's3_url'.
    md_src_files = get_clean_list(log=log, src_dir=src_dir, extensions=['.meta'])
    md = MetaData(debug=args.debug, loglevel=args.loglevel)
    for mdf in md_src_files:
        src_file = mdf
        md.load(mdf)
        sub_path = str(os.sep).join(md.get_s3_url_metadata().split('/')[2:])

        # Metadata file name will remain the same so sub_path includes
        # file name.
        dest_file = cfg.metadata_destination + os.sep + sub_path
        metadata_files[src_file] = dest_file

        # Any metadata files for manifests will have been encrypted and will
        # need the encryption extension stripped off.
        if 'manifest' in md.get_s3_url().split('.'):

            # Split along the '/' first.
            # Then split along the '.' to remove the encryption extension.
            sub_path = str(os.sep).join(md.get_s3_url().split('/')[2:])
            sub_path = '.'.join(sub_path.split('.')[:-1])

            # Look for the file within the manifest files to move and add
            # the destination.
            for man in manifest_files.keys():
                if os.path.basename(sub_path) == os.path.basename(man):
                    manifest_files[man] = cfg.manifest_destination + (
                                          os.sep + sub_path)

    # Create a list of directories and create them if they do not exist.
    dirs_to_check = {}
    for f in metadata_files.keys():
        dirs_to_check[os.path.dirname(metadata_files[f])] = None
    for f in manifest_files.keys():
        dirs_to_check[os.path.dirname(manifest_files[f])] = None


    # Create destination directories first.
    for d in dirs_to_check.keys():
        if not os.path.exists(d):
            if args.noop:
                log.debug('NO-OP: Would create directory\n\n    {}'.format(d))
            else:
                os.makedirs(d)


    # Move manifest files into place.
    log.info(
        'Moving manifest files from "{}" to "{}"'.format(
        src_dir,
        cfg.manifest_destination))
    report = 'Moved\n{}\nfrom {}\nto   {}\n'.format('='*76,
                                                  src_dir,
                                                  cfg.manifest_destination)
    for f in manifest_files.keys():
        report += '        {}\n'.format(os.path.basename(f))
        src=f
        dst=manifest_files[f]
        if args.noop == False: os.rename(src, dst)
    report += '{}\n'.format('='*76)
    if args.noop == True:
        log.debug('NO-OP: {}'.format(report))
    else:
        log.debug('{}'.format(report))

    # Move metadata files into place.
    log.info(
        'Moving metadata files from "{}" to "{}"'.format(
        src_dir,
        cfg.metadata_destination))
    report = 'Moved\n{}\nfrom {}\nto   {}\n'.format('='*76,
                                                  src_dir,
                                                  cfg.metadata_destination)
    for f in metadata_files.keys():
        report += '        {}\n'.format(os.path.basename(f))
        src=f
        dst=metadata_files[f]
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

