#!/usr/bin/env python3
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create_metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create_metadata/bin/create_metadata.py
#=============================================================================#

import sys
import os
import argparse
import time
from metadata import MetaData
from metadata_conf import MetadataConf
from mylog import MyLog



def parse_arguments():
    c = MetadataConf()
    parser = argparse.ArgumentParser(
        description='''Create metadata files for the files listed for
            later uploading to S3.  Parameters are configured based
            on data in a config file {}.  Parameters included as
            an option overrides configuration file settings.
            '''.format(c.filename),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Script function arguments.
    parser.add_argument('--debug', action='store_true', default=False,
        help='Enable debug mode.')
    parser.add_argument('--loglevel', action='store', default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--force', action='store_true', default=False,
        help='Overwrite any existing metadata file.')
    parser.add_argument('--showprogress', action='store_true',
        default=False,
        help='Enable progress bar for large files.')

    # Metadata file settings
    parser.add_argument('--backup_source', action='store',
        type=str, default=None,
        help='Set backup source.')
    parser.add_argument('--encryption_key', action='store',
        type=str, default=None,
        help='Set the encryption key and method used.')
    parser.add_argument('--s3_url', action='store',
        type=str, default=None,
        help='Set S3 URL where the backup is stored.')
    parser.add_argument('--s3_url_metadata', action='store',
        type=str, default=None,
        help='Set S3 URL where the metadata file is stored.')
    parser.add_argument('files', action='store', nargs='+',
        type=str, default=None,
        help='Files to process.')
    return parser.parse_args()


def main():
    args = parse_arguments()
    l = MyLog(program=__name__, debug=args.debug, loglevel=args.loglevel)
    log = l.log

    # Sort through the list of files passed.  We have some restrictions
    # regarding what we will or will not do.
    clean_list = []
    for file in args.files:
        fullpath = os.path.realpath(file)
        (base, ext) = os.path.splitext(fullpath)
        if ext == '.meta':
            raise Exception('''
                Will not create a metadata file from another metadata file.
                That is too meta for me.
            ''')
        if os.path.exists(fullpath + '.meta') and not args.force:
            raise Exception('''
            Metadata file already exists.
            {}
            Use --force to overwrite
            '''.format((fullpath + '.meta')))
        clean_list.append(fullpath)


    # Read settings from the configuration file and override any passed as
    # arguments.
    cfg = MetadataConf(debug=args.debug, loglevel=args.loglevel)
    cfg.read()

    # Pass arguments through the config file to perform any necessary checks.
    if args.backup_source:   cfg.set_backup_source(args.backup_source)
    if args.encryption_key:  cfg.set_encryption_key(args.encryption_key)
    if args.s3_url:          cfg.set_s3_url(args.s3_url)
    if args.s3_url_metadata: cfg.set_s3_url_metadata(args.s3_url_metadata)

    # Build a dictionary of MetaData() class instances for each file.
    md_files = {}
    for file in clean_list:
        md = MetaData(debug=args.debug,
                      loglevel=args.loglevel,
                      showprogress=args.showprogress,
                      filename=file)
        md.set_backup_source(cfg.backup_source)
        backup_time = time.strftime('%Y-%m-%d %H:%M:%S %z', time.gmtime())
        md.set_backup_date(backup_time)
        md.set_encryption_key(cfg.encryption_key)
        full_s3_url = cfg.s3_url + '/' + os.path.basename(md.filename)
        md.set_s3_url(full_s3_url)
        full_md_s3_url = cfg.s3_url_metadata + (
            '/' + os.path.basename(md.metadata_filename))
        md.set_s3_url_metadata(full_md_s3_url)
        md.add_file_stats()
        md_files[file] = md

    # Write each of the metadta files.
    for file in md_files.keys():
        log.info('Writing metadata file for "{}"'.format(os.path.basename(file)))
        md_files[file].write()
        log.debug('Contents\n{}\n{}\n{}'.format('='*76,
                                                md_files[file].format(),
                                                '='*76))
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#
