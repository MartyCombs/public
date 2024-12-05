#!/usr/bin/env python3
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create_metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create_metadata/test/test_metadata.py
#=============================================================================#

import sys
import os
from metadata import MetaData
from mylog import MyLog

l = MyLog(debug=True)
log = l.log
log.debug('\n\nTesting metadata.MetaData()\n')

testfile = 'testfile.txt'
testfile2 = 'testfile-2.txt.meta'

m = MetaData(debug=True)
m.set_filename(testfile)
m.set_backup_date('1999-12-31 23:59:59 -0000')
m.set_backup_source('work')
m.add_file_stats()
m.set_s3_url('s3://mybucket/key1')
m.set_s3_url_metadata('s3://my-other-bucket/key2')

# Print contents of the metadata file.
filecontents = m.format()
if m.metadata_filename != 'testfile.txt.meta':
    log.debug('''\nFAILED: Metadata file not what is expected.
        {} != {}\n'''.format( m.metadata_filename, 'testfile.txt.meta'))
else:
    log.debug('\nPASSED: Correct anticipated name for metatdata file\n')
m.write()

log.debug('Reading "{}"'.format(testfile2))
m2 = MetaData(debug=True)
m2.load(testfile2)
checksum = 'bf9bac8036ea00445c04e3630148fdec15aa91e20b753349d9771f4e25a4f68c82f9bd52f0a72ceaff5415a673dfebc91f365f8114009386c001f0d56c7015de'
if m2.file_checksum != checksum:
    log.debug('''\nFAILED: Checksum for {} does not match expected value
    {}
    '''.format(testfile2, checksum))
else:
    log.debug(
    '\nPASSED: Checksum for {} matches expected value.\n'.format(testfile2))

sys.exit()



#=============================================================================#
# END
#=============================================================================#
