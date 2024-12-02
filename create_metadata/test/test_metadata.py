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

filename = os.path.realpath(sys.argv[1])
l = MyLog(debug=True)
log = l.log
log.debug('Testing MetaData class')
m = MetaData(debug=True)
m.set_filename(filename)
m.set_backup_date('2024-09-30 17:11:29 -0600')
m.set_backup_source('work')
m.add_file_stats()
m.set_s3_url('s3://some-bucket/some/path')
m.set_s3_url_metadata('s3://some-bucket/some/other/path')
filecontents = m.format()
div = '='*76
log.debug('File contents will be:\n{}\n{}\n{}'.format(div, filecontents, div))
log.debug('Metadata file name should be {}'.format(filename))
log.debug('Writing "{}"'.format(m.md_filename))
with open(m.md_filename, 'w') as f:
    f.write(filecontents)
f.close()

log.debug('Reading "{}.meta"'.format(filename))
m2 = MetaData(debug=True)
metafile = filename + '.meta'
m2.load(metafile)
filecontents2 = m2.format()

if filecontents != filecontents2:
    log.error('MetaData class FAILED!')
    log.error('Original file contents:\n{}\n{}\n{}\n'.format('='*76, filecontents, '='*76))
    log.error('Loaded file contents:\n{}\n{}\n{}\n'.format('='*76, filecontents2, '='*76))
    raise Exception('Test failed!')

log.info('MetaData class PASSED')
sys.exit()



#=============================================================================#
# END
#=============================================================================#
