#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import datetime
import argparse
import json
from mylog import MyLog
from metadata import MetaData
from aws_s3 import AWSS3


def parse_arguments():
    '''Parse arguments.
    '''
    parser = argparse.ArgumentParser(
        description='''Given a list of metadata files ending in '.meta' upload
            them to S3.  The '.meta' files must be able to be parsed by the
            MetaData() class and sourcefiles must exist in the same directory
            as the '.meta' files.
            ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', action='store_true', default=False,
        help='Enable debug mode.')
    parser.add_argument('--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--showprogress', action='store_true',
        default=False,
        help='Enable progress bar for large files.')
    parser.add_argument('files', action='store', nargs='+',
        type=str, default=None,
        help='Files to process.')
    return parser.parse_args()



def build_list(args=None, filelist=None):
    '''Build a list of files to upload.
    '''
    upload_list = {}
    md = MetaData(debug=args.debug, loglevel=args.loglevel)
    for md_file in filelist:

        if not os.path.isfile(md_file):
            raise Exception('Not a file "{}'.format(md_file))

        # Check that the file passed is a '.meta' file.
        md_fullpath = os.path.realpath(md_file)
        md_dir = os.path.dirname(md_fullpath)
        ext = os.path.splitext(md_fullpath)[1]
        if ext != '.meta':
            raise Exception('Only pass files ending in .meta')

        # Parse the metadata file to find the S3 destination URLs.  Everything
        # else is derived from these URLs.
        md.load(md_fullpath)
        src_dst = md.get_s3_url()
        md_dst = md.get_s3_url_metadata()
        _check_metadata_file(mdref=md, file=md_file)

        # The source file should be in the same directory as the metadata file.
        src_fullpath = md_dir + os.sep + src_dst.split('/')[-1]
        if not os.path.isfile(src_fullpath):
            raise Exception('Could not find file {}'.format(src_fullpath))

        # Create the list.  Each file will have two entries as both the file
        # and its corresponding metadata file '.meta' are uploaded.
        (bucket,key) = _get_bucket_and_key(src_dst)
        upload_list[src_fullpath] = {
            'dst_url'          : src_dst,
            'bucket'           : bucket,
            'key'              : key,
        }
        (bucket,key) = _get_bucket_and_key(md_dst)
        upload_list[md_fullpath] = {
            'dst_url'          : md_dst,
            'bucket'           : bucket,
            'key'              : key,
        }
    return upload_list



def _check_metadata_file(mdref=None, file=None):
    if mdref.get_s3_url() == None or mdref.get_s3_url_metadata() == None:
        fileformat = json.dumps(mdref.MDINIT, indent=4)
        raise Exception('Metadata format for "{}" not understood.\n\n{}'.format(
            file, fileformat))
    return



def _get_bucket_and_key(url=None):
    '''Return S3 bucket and key from a URL.

        s3://BUCKET/KEY

    '''
    bucket = url.split('/')[2]
    key = '/'.join(url.split('/')[3:])
    return (bucket, key)



def get_report(upload_list=None):
    '''Return a nicely formatted report of files and their destination bucket
    and key for S3.
    '''
    rpt = '{}\n'.format('='*76)
    rpt += 'Files for upload to S3.\n\n'
    for src in upload_list.keys():
        rpt += '{}\n'.format(src)
        rpt += '    {:>10} : {}\n'.format('bucket',
                                          upload_list[src]['bucket'])
        rpt += '    {:>10} : {}\n'.format('key',
                                          upload_list[src]['key'])
        rpt += '\n'
    rpt += '{}\n'.format('='*76)
    return rpt



def main():
    args = parse_arguments()
    l = MyLog(program=__name__, debug=args.debug, loglevel=args.loglevel)
    log = l.log

    upload_list = build_list(args=args, filelist=args.files)
    log.debug('\n{}'.format(get_report(upload_list)))

    # Connect to S3 and confirm the bucket exists for each target URL in S3.
    # This custom code uses a custom set of access key and secret.
    s3 = AWSS3(debug=args.debug, loglevel=args.loglevel)
    s3.connect()
    for file in upload_list.keys():
        if not s3.bucket_exists(upload_list[file]['bucket']):
            raise Exception('Unable to locate bucket "{}"'.format(
                upload_list[file]['bucket']))

    for file in upload_list.keys():
        s3.upload(srcfile=file,
                  bucket=upload_list[file]['bucket'],
                  key=upload_list[file]['key'],
                  showprogress=args.showprogress)
    return



if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#
