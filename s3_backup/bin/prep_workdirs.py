#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
from s3_backup_conf import S3BackupConf

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
def main():
    s3c = S3BackupConf()
    s3c.read()

    # If necessary, make directories for managing manifest and metadata files.
    if not os.path.isdir(s3c.metadata_destination):
        os.makedirs(s3c.metadata_destination)
    if not os.path.isdir(s3c.manifest_destination):
        os.makedirs(s3c.manifest_destination)

    # Make directories for the workflow.
    if not os.path.isdir(s3c.drop_dir):
        os.makedirs(s3c.drop_dir)
    if not os.path.isdir(s3c.manifest_dir):
        os.makedirs(s3c.manifest_dir)
    if not os.path.isdir(s3c.encrypt_dir):
        os.makedirs(s3c.encrypt_dir)
    if not os.path.isdir(s3c.metadata_dir):
        os.makedirs(s3c.metadata_dir)
    if not os.path.isdir(s3c.s3upload_dir):
        os.makedirs(s3c.s3upload_dir)

    return

if __name__ == "__main__":
    sys.exit(main())



#=============================================================================#
# END
#=============================================================================#

