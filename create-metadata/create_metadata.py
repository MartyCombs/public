#!/usr/bin/env python3
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create-metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create-metadata/create_metadata.py
#=============================================================================#

import sys
import os
import argparse
import re
import time
from metadata import MetaData
from mylog import MyLog



class CreateMetadata(object):
    '''Create metadata files for backup to S3.

    ATTRIBUTES
        debug      : Enable debug mode. Sets loglevel='DEBUG'.

        loglevel   : Set logging level [DEF: 'INFO']

        source     : Source tag.

        bucket     : S3 bucket where file and metadata file are stored.

    '''


    DEFAULT_SOURCE = 'personal'
    DEFAULT_BUCKET = 'mcombs-backup'


    def __init__(self, debug=None, loglevel='INFO',
                 force=False, showprogress=False,
                 source=None, bucket=None):
        self.exit_status = 0
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.force = force
        self.showprogress = showprogress
        self.top_level = os.path.dirname(os.path.realpath(sys.argv[0]))

        self.md_filelist = {}
        self.source = self.set_source(source)
        self.bucket = self.set_bucket(bucket)
        return

    def set_source(self, source=None):
        '''Set source for metadate file
        '''
        if source:
            self.source = source
        else:
            self.source = CreateMetadata.DEFAULT_SOURCE
        return

    def set_bucket(self, bucket=None):
        '''Set bucket for metadate file
        '''
        if bucket:
            self.bucket = bucket
        else:
            self.bucket = CreateMetadata.DEFAULT_BUCKET
        return

    def get_files(self):
        '''Get the dictionary of metadata files and their contents.
        '''
        return self.md_filelist



    def precheck(self, filelist=None):
        '''Parse the list of files passed and returns a list of full paths to
        those files which pass the tests.
        '''
        clean_list = []
        for f in filelist:
            fullpath = os.path.realpath(f)
            (full_sans_ext, ext) = os.path.splitext(fullpath)
            basename = os.path.basename(fullpath)
            # Skip '.meta' files passed.
            if ext == '.meta':
                self.log.info('Skipping "{}"'.format(fullpath))
                continue

            # Unless we --force re-creation, skip any files which already
            # have a '.meta' file.
            metafile = fullpath + '.meta'
            if os.path.exists(metafile) and not self.force:
                self.log.warning('Metadata file already exists "{}"'.format(
                    metafile))
                continue
            clean_list.append(fullpath)
        return clean_list



    def build_files(self, filelist=None):
        '''Takes a list of full paths and builds a set of metadata files for
        each file passed.
        '''
        for f in filelist:
            self.log.info('Building metadata for "{}"'.format(os.path.basename(f)))
            md = MetaData(debug=self.debug, loglevel=self.loglevel,
                          showprogress=self.showprogress)
            md_fullpath = f + '.meta'
            f_basename = os.path.basename(f)
            md.set_filename(f)
            backup_time = time.strftime('%Y-%m-%d %H:%M:%S %z',
                                        time.gmtime())
            md.set_source(self.source)
            md.set_backup_date(backup_time)
            s3_url = 's3://{}/{}'.format(self.bucket, f_basename)
            md.set_s3_url(s3_url)
            s3_url_metadata = 's3://{}/{}'.format(self.bucket, md.md_filename)
            md.set_s3_url_metadata(s3_url_metadata)
            md.add_file_stats()
            self.md_filelist[md_fullpath] = md.format()
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
    parser.add_argument('--source', action='store', type=str,
        default=CreateMetadata.DEFAULT_SOURCE,
        help='Set source.')
    parser.add_argument('--bucket', action='store', type=str,
        default=CreateMetadata.DEFAULT_BUCKET,
        help='Set S3 bucket.')
    parser.add_argument('files', action='store', nargs='+', type=str,
        default=None,
        help='Files to process.')
    return parser.parse_args()



def main():
    args = parse_arguments()
    s = CreateMetadata(debug=args.debug,
                       loglevel=args.loglevel,
                       force=args.force,
                       showprogress=args.showprogress,
                       source=args.source,
                       bucket=args.bucket)
    metadata_candidates = s.precheck(args.files)
    s.build_files(metadata_candidates)
    metadata_files = s.get_files()
    for metafile in metadata_files.keys():
        s.log.info('Writing "{}"'.format(metafile))
        with open(metafile, 'w') as fw:
            fw.write(metadata_files[metafile])
        fw.close()
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#
