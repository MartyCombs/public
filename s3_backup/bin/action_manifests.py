#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import re
import tarfile
from mylog import MyLog
from s3_backup_conf import S3BackupConf
from s3_backup_common import S3BackupCommon

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])

# Read the config to create the custom description for the --help option.
cfg = S3BackupConf()
cfg.read()
src_dir = cfg.manifest_dir
dst_dir = cfg.encrypt_dir

# Pull in methods common to all actions.
common = S3BackupCommon(src_dir=src_dir, dst_dir=dst_dir)

# Custom help for argparse.
custom_help = '''Create manifests for any archives in "{}" and move all files
over to "{}".'''.format(str(os.sep).join(src_dir.split(os.sep)[-3:]),
                        str(os.sep).join(dst_dir.split(os.sep)[-3:]))
args = common.parse_arguments(description=custom_help)

# Adjust config attributes based on arguments passed.
cfg.debug = args.debug
cfg.loglevel = args.loglevel
l = MyLog(debug=args.debug, loglevel=args.loglevel)
log = l.log

re_targz = re.compile(r'^.*\.tar\.gz$')
# Examine all files in the manifest work directory.
filelist = common.get_clean_list(directory=src_dir,
                                 extensions=['all'])
if len(filelist) == 0:
    log.info('No files to process')
    sys.exit()

# Build manifests
manifests = {}
for f in filelist:
    if not re.match(re_targz, f): continue
    if args.noop == False:
        with tarfile.open(f, 'r:gz') as tar:
            manifests[f] = sorted(tar.getnames())
        tar.close()
    else:
        manifests[f] = None


# Manifests are created in the same directory as archives.
log.info('Creating manifests for archives')

# Build the report...
report = 'Manifests created\n\nin {}\n'.format(src_dir)
for m in manifests.keys():
    filename = m + '.manifest'
    report += '        {}\n'.format(os.path.basename(filename))

# ...then do the work.
if args.noop == True:
    log.debug('NO-OP: {}'.format(report))
else:
    for m in manifests.keys():
        filename = m + '.manifest'
        with open(filename, 'w') as f:
            for line in manifests[m]:
                f.write('{}\n'.format(line))
        f.close()
    log.debug('{}'.format(report))

# Now that we have added manifests to the manifest work directory, move all
# move all to the encryption work directory.
filelist = common.get_clean_list(directory=src_dir,
                                 extensions=['all'])
common.move_files(filelist=filelist)

# Clean the manifest work directory of any stragglers.
common.clean_src()



#=============================================================================#
# END
#=============================================================================#

