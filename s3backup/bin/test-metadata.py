#!/usr/bin/env python3

import sys
import os
from metadata import MetaData
from mylog import MyLog

l = MyLog(debug=True)
log = l.log
log.debug('Testing MetaData class')
m = MetaData(debug=True)
m.set_filename('testfile')
m.set_backup_date('2024-09-30 17:11:29 -0600')
m.set_backup_source('work')
m.add_file_stats()
m.set_s3_url('s3://some-bucket/some/path')
m.set_s3_url_metadata('s3://some-bucket/some/other/path')
filecontents = m.format()
div = '='*76
log.debug('File contents will be:\n{}\n{}\n{}'.format(div, filecontents, div))
log.debug('Metadata file name should be create_metadata.sh.meta')
log.debug('Writing "{}"'.format(m.md_filename))
with open(m.md_filename, 'w') as f:
    f.write(filecontents)
f.close()

log.debug('Reading "testfile.meta"')
m2 = MetaData(debug=True)
m2.load('testfile.meta')
filecontents2 = m2.format()

os.remove('testfile.meta')
if filecontents == filecontents2:
    log.error('MetaData class FAILED!')
else:
    log.info('MetaData class PASSED')
sys.exit()
