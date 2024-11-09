#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import re
import configparser
from mylog import MyLog


class S3BackupConf(object):
    '''Manage S3 backup configuration file.

    ATTRIBUTES
        encryption_key_filename : S3 URL for the metadata file.

        metadata_destination    : Local destination for the metadata files.

        manifest_destination    : Local destination for the manifest files
                                  which list the contents of tar archives.
                                  Archives are assumed to be compressed with
                                  .tar.gz extension.

    '''

    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    DEF_CONFIG_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 's3backup.cfg'
    DEF_CONFIG = {
        'encryption_key_filename'  : 'etc/encryption_key',
        'metadata_destination'     : 'meta/BUCKET_NAME/PATH',
        'manifest_destination'     : 'manifest/BUCKET_NAME/PATH',
        'drop_dir'                 : 'work/10-drop',
        'manifest_dir'             : 'work/20-tar_manifest',
        'encrypt_dir'              : 'work/30-encrypt',
        'metadata_dir'             : 'work/40-create_metadata',
        's3upload_dir'             : 'work/50-s3_upload'
    }



    def __init__(self, debug=False, loglevel='WARNING'):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.top_dir = self.TOP_DIR
        self.filename = self.DEF_CONFIG_FILE

        # Config parameters
        self.encryption_key_filename = self.DEF_CONFIG['encryption_key_filename']
        self.metadata_destination = self.DEF_CONFIG['metadata_destination']
        self.manifest_destination = self.DEF_CONFIG['manifest_destination']
        self.drop_dir = self.DEF_CONFIG['drop_dir']
        self.manifest_dir = self.DEF_CONFIG['manifest_dir']
        self.encrypt_dir = self.DEF_CONFIG['encrypt_dir']
        self.metadata_dir = self.DEF_CONFIG['metadata_dir']
        self.s3upload_dir = self.DEF_CONFIG['s3upload_dir']
        return



    def read(self):
        '''Read the configuration file.
        '''
        self.log.debug('Reading {}'.format(self.DEF_CONFIG_FILE))
        cfg = configparser.RawConfigParser()
        cfg.read(self.DEF_CONFIG_FILE)
        self.encryption_key_filename = cfg.get(
            'DEFAULT', 'encryption_key_filename')
        self.metadata_destination = cfg.get(
            'DEFAULT', 'metadata_destination')
        self.manifest_destination = cfg.get(
            'DEFAULT', 'manifest_destination')
        self.manifest_destination = cfg.get(
            'DEFAULT', 'drop_dir')
        self.manifest_destination = cfg.get(
            'DEFAULT', 'manifest_dir')
        self.manifest_destination = cfg.get(
            'DEFAULT', 'encrypt_dir')
        self.manifest_destination = cfg.get(
            'DEFAULT', 'metadata_dir')
        self.manifest_destination = cfg.get(
            'DEFAULT', 's3upload_dir')
        return



    def print(self):
        report = '{}\n'.format('='*76)
        report += '{:<25} {}\n'.format('encryption_key_filename',
                                       self.encryption_key_filename)
        report += '{:<25} {}\n'.format('metadata_destination',
                                       self.metadata_destination)
        report += '{:<25} {}\n'.format('manifest_destination',
                                       self.manifest_destination)
        report += '{:<25} {}\n'.format('drop_dir',
                                       self.drop_dir)
        report += '{:<25} {}\n'.format('manifest_dir',
                                       self.manifest_dir)
        report += '{:<25} {}\n'.format('encrypt_dir',
                                       self.encrypt_dir)
        report += '{:<25} {}\n'.format('metadata_dir',
                                       self.metadata_dir)
        report += '{:<25} {}\n'.format('s3upload_dir',
                                       self.s3upload_dir)
        report += '{}\n'.format('='*76)
        return report



    def create(self):
        '''Create the config file with all default values.
        '''
        div = '#{}#'.format('='*76)
        cfg = ''
        cfg += '{}\n'.format(div)
        cfg += '# Read by python ConfigParser\n'
        cfg += '{}'.format(self._conf_header())
        cfg += '\n'
        cfg += '[DEFAULT]\n'
        for key in self.DEF_CONFIG.keys():
            cfg += '{} = {}\n'.format(key, self.DEF_CONFIG[key])
        cfg += '\n\n\n'
        cfg += '{}\n# END\n{}\n'.format(div, div)
        return cfg
        with open(self.filename, 'w') as c:
            c.write(cfg)
        self.log.info('Created config "{}"'.format(self.DEF_CONFIG_FILE))
        return



    def _conf_header(self):
        header = ''
        header += '''#
# Configuration file for backups to S3.  Please read the documentation
# regarding the standard process for backing up files in the README.
#
# All directory paths which do not start with '/' are relative to the
# top level working directory:
#
#     {}
#       '''.format(self.TOP_DIR)
        header += '''
# encryption_key_filename      File name containing the AES-256 encryption
#                              key for encrypting backups.
#                              PROTECT this file with minimal read permissions
#                              (chmod 400 FILENAME).
#
#                              READ CAREFULLY regarding management of this file
#                              in the README.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['encryption_key_filename'])
        header += '''
# metadata_destination         Local destination where metadata files are stored
#                              after the entire process is finished.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['metadata_destination'])
        header += '''
# manifest_destination         Local destination for the manifest files
#                              which list the contents of tar archives.
#
#                              See NOTES section about archives in the README.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['manifest_destination'])
        header += '''
# drop_dir                     Drop directory for files which need to be
#                              processed by the wrapper script.  This is the
#                              initial directory for the start of the backup
#                              process.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['drop_dir'])
        header += '''
# manifest_dir                 Manifests are created for archives located here.
#                              Once a manifest is successfully created, they
#                              are moved to the next directory.  Files are simply
#                              moved to the next directory in the process.
#
#                              See NOTES section about archives in the README.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['manifest_dir'])
        header += '''
# encrypt_dir                  Files, archives, and manifest files - if present
#                              in this directory are encrypted.
#
#                              After successful encryption:
#
#                              * The original, unencrypted file is delete.
#
#                              * Any manifest files are moved to the next
#                                directory in the process.
#
#                              * Encrypted files are moved to the next
#                                directory in the process.
#
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['encrypt_dir'])
        header += '''
# metadata_dir                 Files and archives located here will have metadata
#                              files created in JSON format for later locating
#                              the files in S3, determining their size, checksum,
#                              encryption key used, etc. on the file.
#
#                              Only encrypted manifest files will have metadata
#                              files created.  The unencrypted manifest files are
#                              assumed to be stored locally in a secure location.
#
#                              After successful creation of metadata files, all
#                              files are moved to the next directory in the process.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['metadata_dir'])
        header += '''
# s3upload_dir                 Files and archives located here will be uploaded
#                              to the S3 bucket listed in the metadata file for
#                              that file or archive.
#
#                              After successful upload to S3:
#
#                              * The original file or archive will be deleted.
#
#                              * Any pretaining unencrypted manifest - if one
#                                exists - will be moved to the directory defined
#                                in the 'manifest_destination' config variable.
#
#                              * All metadata files are moved to the directory
#                                defined in the 'metadata_destination' config
#                                variable.
#                              [DEFAULT: {}]
        '''.format(self.DEF_CONFIG['s3upload_dir'])
        return header



#=============================================================================#
# END
#=============================================================================#
