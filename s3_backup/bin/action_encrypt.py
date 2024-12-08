#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import subprocess
from mylog import MyLog
from s3_backup_conf import S3BackupConf
from s3_backup_common import S3BackupCommon

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
SCRIPT = TOP_DIR + os.sep + 'encrypt_files' + os.sep + 'bin' + os.sep + 'encrypt_files.sh'

# Read the config to create the custom description for the --help option.
cfg = S3BackupConf()
cfg.read()
src_dir = cfg.encrypt_dir
dst_dir = cfg.metadata_dir

# Pull in methods common to all actions.
common = S3BackupCommon(src_dir=src_dir, dst_dir=dst_dir)

# Custom help for argparse.
custom_help = '''Encrypt files in "{}" and move encrypted files and manifests
on to "{}".'''.format(str(os.sep).join(src_dir.split(os.sep)[-3:]),
                      str(os.sep).join(dst_dir.split(os.sep)[-3:]))
args = common.parse_arguments(description=custom_help)

# Adjust config attributes based on arguments passed.
cfg.debug = args.debug
cfg.loglevel = args.loglevel
l = MyLog(debug=args.debug, loglevel=args.loglevel)
log = l.log

# Get all files in the encryption work directory.
filelist = common.get_clean_list(directory=src_dir,
                                 extensions=['all'])
if len(filelist) == 0:
    log.info('No files to process')
    sys.exit()

# Prep for running the subscript.
#     encrypt_files.sh does not take --noop option
cmd=['bash', SCRIPT]
subargs = sys.argv[1:]
if '--noop' in subargs: subargs.remove('--noop')
for a in subargs:
    cmd.append(a)
for f in filelist:
    cmd.append(f)
report = 'Running\n\n{}\n\n'.format(cmd)
if args.noop:
    log.debug('NO-OP: {}'.format(report))
else:
    log.debug('{}'.format(report))
    results = subprocess.run(cmd)
    if results.returncode != 0:
        log.error('Failed to encrypt files!')
        sys.exit(results.returncode)

# After successful encryption, the following files are moved from the
# encryption work directory to the metadata work directory:
#    - encrypted files (.asc, .enc)
#    - manifest files  (.manifest)
filelist = common.get_clean_list(directory=src_dir,
                                 extensions=['.enc', '.asc', '.manifest'])
common.move_files(filelist=filelist)

# The encryption work directory is then purged.  This should be
# unencrypted files.
common.clean_src()



#=============================================================================#
# END
#=============================================================================#

