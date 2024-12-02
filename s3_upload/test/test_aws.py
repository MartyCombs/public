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

def test_aws_conf():
    sys.stderr.write('\nTesting aws_s3.AWSConf()\n\n')
    sys.stderr.write('No files are written.\n')
    cfg = AWSConf(debug=True)
    contents = cfg.build()
    sys.stderr.write('Default config contents:\n{}\n'.format(contents))
    sys.stderr.write('Setting mp_threshold to 1 MB (1048576 B)\n')
    cfg.set_mp_threshold(1024*1024)

    sys.stderr.write('Setting max_concurrency to 4\n')
    cfg.set_max_concurrency(4)

    sys.stderr.write('Setting mp_chunksize to 1 KB (1024 B)\n')
    cfg.set_mp_chunksize(1024)

    sys.stderr.write('Printing new values\n{}\n'.format(cfg.print()))
    return

def test_aws_s3():
    sys.stderr.write('\nTesting aws_s3.AWSConf()\n\n')
    sys.stderr.write('''You have to have both a config file
        {}
    and a credentials file with minimally read credentials to S3
        {}
    \n'''.format(AWSConf.DEF_CONFIG_FILE, AWSS3.DEF_CREDS_FILE))
    sys.stderr.write('Only connectivity is tested - not uploads.\n\n')
    s3 = AWSS3(debug=True)
    s3.connect()
    return


def main():
    test_aws_conf()
    test_aws_s3()
    return


if __name__ == "__main__":
    sys.exit(main())




#=============================================================================#
# END
#=============================================================================#
