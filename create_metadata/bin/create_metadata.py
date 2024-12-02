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



def precheck(files=None, log=None, args=None):
    '''Examine the list of files passed and returns a list of full paths to
    those files which pass the tests.
    '''
    clean_list = []
    for f in files:
        fullpath = os.path.realpath(f)
        (full_sans_ext, ext) = os.path.splitext(fullpath)
        basename = os.path.basename(fullpath)
        # Skip '.meta' files passed.
        if ext == '.meta':
            log.debug('Skipping "{}"'.format(fullpath))
            continue

        # Unless we --force re-creation, skip any files which already
        # have a '.meta' file.
        metafile = fullpath + '.meta'
        if os.path.exists(metafile) and not args.force:
            log.warning('Metadata file already exists "{}"'.format(
                metafile))
            continue
        clean_list.append(fullpath)
    return clean_list



def build_files(files=None, log=None, args=None, cfg=None):
    '''Take a list of full paths and builds a set of metadata files for
    each file passed.
    '''
    md_files = {}
    for f in files:
        log.debug('Building metadata for "{}"'.format(os.path.basename(f)))
        md = MetaData(debug=args.debug, loglevel=args.loglevel,
                      showprogress=args.showprogress)
        md_fullpath = f + '.meta'
        f_basename = os.path.basename(f)
        md.set_filename(f)
        md.set_backup_source(cfg.backup_source)
        backup_time = time.strftime('%Y-%m-%d %H:%M:%S %z',
                                    time.gmtime())
        md.set_backup_date(backup_time)
        md.set_encryption_key(cfg.encryption_key)
        # Filenames are added to the beginning of the S3 URLs.
        s3_url = '{}/{}'.format(cfg.s3_url, f_basename)
        md.set_s3_url(s3_url)
        s3_url_metadata = '{}/{}'.format(cfg.s3_url_metadata, md.md_filename)
        md.set_s3_url_metadata(s3_url_metadata)
        md.add_file_stats()
        md_files[md_fullpath] = md.format()
    return md_files



def main():
    '''Create metatdata files for files listed.  Some values within the metadata
    files can be set with either a configuration file or by passing arguments
    to this script.

    Arguments passed take precedence over values in an optional configuration file.
    '''

    # Start with some default settings which can be pulled from a configuration
    # file or overriddden with command options.
    settings = {
        'backup_source'        : 'personal',
        'encryption_key'       : 'GPG',
        's3_url'               : 's3://backup',
        's3_url_metadata'      : 's3://backup'
    }

    args = parse_arguments()
    l = MyLog(program=__name__, debug=args.debug, loglevel=args.loglevel)
    log = l.log
    metadata_candidates = precheck(files=args.files, log=log, args=args)

    # Read settings from the configuration file and override any passed as
    # arguments.
    cfg = MetadataConf(debug=args.debug, loglevel=args.loglevel)
    cfg.read()
    if args.backup_source:  cfg.set_backup_source(args.backup_source)
    if args.encryption_key: cfg.set_encryption_key(args.encryption_key)
    if args.s3_url: cfg.set_s3_url(args.s3_url)
    if args.s3_url_metadata: cfg.set_s3_url_metadata(args.s3_url_metadata)
    metadata_files = build_files(files=metadata_candidates, log=log, args=args,
                                 cfg=cfg)
    for metafile in metadata_files.keys():
        log.info('Writing "{}"'.format(metafile))
        with open(metafile, 'w') as fw:
            fw.write(metadata_files[metafile])
            log.debug('Contents\n{}\n{}\n{}'.format(
                '='*76,
                metadata_files[metafile],
                '='*76))
        fw.close()
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#
