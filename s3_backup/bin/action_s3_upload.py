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
from post_process import PostProcess

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
SCRIPT = TOP_DIR + os.sep + 's3_upload' + os.sep + 'bin' + os.sep + 'upload.sh'

# Read the config to create the custom description for the --help option.
# This file has two destination directories.
cfg = S3BackupConf()
cfg.read()
src_dir = cfg.s3_upload_dir

# Pull in methods common to all actions.
common = S3BackupCommon(src_dir=src_dir)

# Custom help for argparse.
custom_help = '''Upload encrypted and metadata files in "{}" to S3.  Then move
unencrypted manifest files to "{}" and metadata files to "{}".'''.format(
    str(os.sep).join(src_dir.split(os.sep)[-3:]),
    str(os.sep).join(cfg.manifest_destination.split(os.sep)[-3:]),
    str(os.sep).join(cfg.metadata_destination.split(os.sep)[-3:]))
args = common.parse_arguments(description=custom_help)

# Adjust config attributes based on arguments passed.
cfg.debug = args.debug
cfg.loglevel = args.loglevel
l = MyLog(debug=args.debug, loglevel=args.loglevel)
log = l.log

# Process only metadata files from the source directory.  The URLs they
# contain refer to files which will be uploaded to S3.
filelist = common.get_clean_list(directory=src_dir,
                                 extensions=['.meta'])
if len(filelist) == 0:
    log.info('No files to process')
    sys.exit()

# Prep for running the subscript.
#     upload.sh does not take --noop option
cmd=['bash', SCRIPT]
subargs = sys.argv[1:]
if '--noop' in subargs: subargs.remove('--noop')
for a in subargs:
    cmd.append(a)
for f in filelist:
    cmd.append(f)
if args.noop:
    log.debug('NO-OP: Would run\n{}\n    {}\n{}'.format(
        '='*76, cmd, '='*76))
else:
    log.debug('Running\n{}\n    {}\n{}'.format('='*76, cmd, '='*76))
    results = subprocess.run(cmd)
    if results.returncode != 0:
        log.error('Failed to upload to S3!')
        sys.exit(results.returncode)

# After successful upload to S3, manifest files are moved to a subdirectory
# of manifest_destination and metadata files are moved to a subdirectory of
# metadata_destination based on the URLs within the metadata files.
manifests = common.get_clean_list(directory=src_dir,
                                  extensions=['.manifest'])
pp = PostProcess(debug=args.debug,
                 loglevel=args.loglevel,
                 manifest_src_files=manifests,
                 metadata_src_files=filelist,
                 manifest_destination=cfg.manifest_destination,
                 metadata_destination=cfg.metadata_destination)
pp.build()
pp.prep(noop=args.noop)
pp.process(noop=args.noop)

# Finally, clean any stragglers from the S3 upload work directory.
common.clean_src()



#=============================================================================#
# END
#=============================================================================#
