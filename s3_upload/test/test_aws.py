#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
from aws_s3 import AWSS3
from aws_conf import AWSConf
from metadata import MetaData
from mylog import MyLog

def test_aws_conf(log):
    log.debug(
        '\n{}\nTesting aws_s3.AWSConf()\nNo files are written.\n\n'.format(
        '='*76))
    cfg = AWSConf(debug=True)
    contents = cfg.build()
    log.debug('Default config contents:\n{}'.format(contents))
    log.debug('Setting mp_threshold to 1 MB (1048576 B)')
    cfg.set_mp_threshold(1024*1024)

    log.debug('Setting max_concurrency to 4')
    cfg.set_max_concurrency(4)

    log.debug('Setting mp_chunksize to 1 KB (1024 B)')
    cfg.set_mp_chunksize(1024)

    log.debug('Printing new values\n{}'.format(cfg.print()))
    log.debug('PASSED')
    return



def test_metadata_file_parsing(log):
    testfile = 'testfile.txt.meta'
    log.debug('\n{}\nTesting parsing of metadata file.'.format('='*76))
    md = MetaData(debug=True)
    md.load(testfile)
    if (md.filename != 'testfile.txt') or (
        md.s3_url != 's3://BUCKET_NAME/PATH/testfile.txt'):
        raise Exception('Testing metadata class metadata.py FAIlED!')
    log.debug('PASSED')
    return



def test_aws_s3(log):
    log.debug('\n{}\nTesting aws_s3.AWSConf()'.format('='*76))
    log.debug('''
        You have to have both a config file
            {}
        and a credentials file with minimally read credentials to S3
            {}
    '''.format(AWSConf.DEF_CONFIG_FILE, AWSS3.DEF_CREDS_FILE))
    log.debug('Only connectivity is tested - not uploads.\n\n')
    s3 = AWSS3(debug=True)
    s3.connect()
    log.debug('PASSED')
    return



def main():
    l = MyLog(debug=True)
    log = l.log
    test_aws_conf(log)
    test_metadata_file_parsing(log)
    test_aws_s3(log)
    return


if __name__ == "__main__":
    sys.exit(main())




#=============================================================================#
# END
#=============================================================================#
