#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
from mylog import MyLog
from s3_backup_conf import S3BackupConf
from s3_backup_common import S3BackupCommon

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])

# Read the config to create the custom description for the --help option.
cfg = S3BackupConf()
cfg.read()
src_dir = cfg.drop_dir
dst_dir = cfg.manifest_dir

# Pull in methods common to all actions.
common = S3BackupCommon(src_dir=src_dir, dst_dir=dst_dir)

# Custom help for argparse.
custom_help = '''Move files from drop directory "{}" to the manifest directory
    "{}".'''.format(str(os.sep).join(src_dir.split(os.sep)[-3:]),
                    str(os.sep).join(dst_dir.split(os.sep)[-3:]))
args = common.parse_arguments(description=custom_help)

# Adjust config attributes based on arguments passed.
cfg.debug = args.debug
cfg.loglevel = args.loglevel
l = MyLog(debug=args.debug, loglevel=args.loglevel)
log = l.log

# Get all files in the drop work directory.
filelist = common.get_clean_list(directory=src_dir,
                                 extensions=['all'])
if len(filelist) == 0:
    log.info('No files to process')
    sys.exit()

# Move all files from drop directory to manifest directory.
common.move_files(filelist=filelist)

# The drop directory is never purged because more files may be placed here.

#=============================================================================#
# END
#=============================================================================#

