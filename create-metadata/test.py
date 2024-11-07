#!/usr/bin/env python3

from metadata import MetaData
from mylog import MyLog

l = MyLog(debug=True)
log = l.log
log.debug('Loading MetaData class')
m = MetaData(debug=True)
m.set_filename('create_metadata.sh')
m.set_backup_date('2024-09-30 17:11:29 -0600')
m.set_source('work')
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

log.debug('Reading "create_metadata.sh.meta"')
m2 = MetaData(debug=True)
m2.load('create_metadata.sh.meta')
print(m2.format())
