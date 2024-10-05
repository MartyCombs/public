#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import argparse
import re
import time
from metadata import metadata
from metadata import mylog

DEFAULT_SOURCE = 'personal'
DEFAULT_BUCKET = 'mcombs-backup'


class CreateMetadata(object):
    '''Create backup file metadata

        Parameters:
            debug      : Enable debug mode. Sets log level to 'debug'.
            loglevel   : Set logging level [DEF: 'info']
    '''
    def __init__(self, debug=None, loglevel='info',
                 source=DEFAULT_SOURCE, bucket=DEFAULT_BUCKET):
        self.exit_status = 0
        self.debug = debug
        self.loglevel = loglevel.upper()
        self.top_level = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.source = source
        self.bucket = bucket
        l = mylog.MyLog(program=__name__, debug=debug)
        self.log = l.log
        return


def main():
    parser = argparse.ArgumentParser(
        description='Create file meta-data.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', action='store_true', default=False,
        help='Enable debug mode.')
    parser.add_argument('--loglevel', action='store', default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--force', action='store_true', default=False,
        help='Overwrite existing stats files.')
    parser.add_argument('--progress', action='store_true', default=False,
        help='Enable progress bar.')
    parser.add_argument('--source', action='store', type=str,
        default=DEFAULT_SOURCE,
        help='Set source.')
    parser.add_argument('--bucket', action='store', type=str,
        default=DEFAULT_BUCKET,
        help='Set S3 bucket.')
    parser.add_argument('files', action='store', nargs='+', type=str,
        default=None,
        help='Files to process.')
    args = parser.parse_args()
    s = CreateMetadata(debug=args.debug,
                       loglevel=args.loglevel,
                       bucket=args.bucket)

    # Start
    files_to_stat = []
    meta = metadata.MetaData(debug=args.debug,
                             loglevel=args.loglevel,
                             progress=args.progress)
    for f in args.files:
        fullpath = os.path.abspath(f)
        (base, ext) = os.path.splitext(fullpath)
        basename = os.path.basename(fullpath)
        # If file passed is a meta-data file, skip it.
        if ext == '.meta':
            s.log.warning('Skipping meta-data file "{}"'.format(fullpath))
            continue
        metafile = base + '.meta'
        if os.path.exists(metafile) and not args.force:
            s.log.warning('Meta-data file already exists "{}" and --force not specified.  Skipping.'.format(metafile))
            continue
        meta.init_file_stats(filename=fullpath)
        files_to_stat.append(fullpath)
    for f in files_to_stat:
        (base, ext) = os.path.splitext(f)
        metafile = base + '.meta'
        basename = os.path.basename(f)
        f_mtime = time.strftime('%Y-%m-%d %H:%M:%S %z',
                                time.gmtime(os.path.getmtime(f)))
        #
        # Check for a date in the name of the file.  If not found,
        # use the mtime for the archive.
        datefound = re.match(r'.*-(\d\d\d\d)-(\d\d)-(\d\d)\.*', basename)
        if datefound:
            (yr,mth,dy) = datefound.group(1,2,3)
        else:
            (yr,mth,dy) = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d) .*',
                                   f_mtime).group(1,2,3)
        metabasename = os.path.basename(metafile)
        meta.set_source(filename=basename, backup_source=s.source)
        meta.set_date(filename=basename, backup_date=f_mtime)
        meta.set_s3_url(filename=basename,
                        s3_url=('s3://' + s.bucket + '/' + basename))
        meta.set_s3_url_metadata(filename=f,
                                 s3_url_metadata=('s3://' + s.bucket
                                                  + '/' + metabasename))
        meta.add_file_stats(filename=f)
        s.log.info('Writing meta-data file "{}"'.format(metafile))
        fw = open(metafile, 'w')
        fw.write(meta.format(f))
        fw.close()



if __name__ == "__main__":
    main()



#=============================================================================#
# END
#=============================================================================#
