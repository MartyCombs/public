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


class Conf(object):
    '''Manage configuration file

    ATTRIBUTES
        backup_source           : A text label for the backup such as
                                  'personal', 'work', 'photos', etc.

        file_checksum_method    : Checksum method for determining a file's
                                  authenticity.

        s3_url                  : S3 URL where to store the backup.

        s3_url_metadata         : S3 URL for the metadata file.

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
        'backup_source'            : 'personal',
        'file_checksum_method'     : 'sha512',
        's3_url'                   : 's3://BUCKET_NAME/PATH',
        's3_url_metadata'          : 's3://BUCKET_NAME/PATH',
        'encryption_key_filename'  : 'etc/encryption_key',
        'metadata_destination'     : 'meta/BUCKET_NAME/PATH',
        'manifest_destination'     : 'manifest/BUCKET_NAME/PATH'
    }
    CONFIG_HEADER = '''#
#
# backup_source                Label for the backup source such as
#                              'personal', 'work', 'photos', etc.
#
# file_checksum_method         Checksum method for confirming the authenticity.
#                              of the backup file.
#
# s3_url                       S3 URL for storing the backup file.
#                              [FORMAT: 's3://BUCKET_NAME/PATH'
#
# s3_url_metadata              S3 URL for storing the metadata file.  This
#                              could be in a separate location.
#                              [FORMAT: 's3://BUCKET_NAME/PATH'
#
# encryption_key_filename      File name containing the AES-256 encryption
#                              key for encrypting backups.
#                              PROTECT this file with minimal read permissions
#                              (chmod 400 FILENAME).
#                              [DEFAULT: etc/encryption_key
#
# metadata_destination         Local destination for the metadata files.
#                              [DEFAULT: meta/BUCKET_NAME/PATH]
#
# manifest_destination         Local destination for the manifest files
#                              which list the contents of tar archives.
#                              Archives are assumed to be compressed with
#                              .tar.gz extension.
#                              [DEFAULT: manifest/BUCKET_NAME/PATH]
#
    '''



    def __init__(self, debug=False, loglevel='WARNING'):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.top_dir = self.TOP_DIR
        self.filename = self.DEF_CONFIG_FILE

        # Config parameters
        self.backup_source = self.DEF_CONFIG['backup_source']
        self.file_checksum_method = self.DEF_CONFIG['file_checksum_method']
        self.s3_url = self.DEF_CONFIG['s3_url']
        self.s3_url_metadata = self.DEF_CONFIG['s3_url_metadata']
        self.encryption_key_filename = self.DEF_CONFIG['encryption_key_filename']
        self.metadata_destination = self.DEF_CONFIG['metadata_destination']
        self.manifest_destination = self.DEF_CONFIG['manifest_destination']
        return



    def read(self):
        '''Read the configuration file.
        '''
        self.log.debug('Reading {}'.format(self.DEF_CONFIG_FILE))
        cfg = configparser.RawConfigParser()
        cfg.read(self.DEF_CONFIG_FILE)
        self.backup_source = cfg.get(
            'DEFAULT', 'backup_source')
        self.file_checksum_method = cfg.get(
            'DEFAULT', 'file_checksum_method')
        self.s3_url = cfg.get(
            'DEFAULT', 's3_url')
        self.s3_url_metadata = cfg.get(
            'DEFAULT', 's3_url_metadata')
        self.encryption_key_filename = cfg.get(
            'DEFAULT', 'encryption_key_filename')
        self.metadata_destination = cfg.get(
            'DEFAULT', 'metadata_destination')
        self.manifest_destination = cfg.get(
            'DEFAULT', 'manifest_destination')
        return



    def print(self):
        report = '{}\n'.format('='*76)
        report += '{:<25} {}\n'.format('backup_source', self.backup_source)
        report += '{:<25} {}\n'.format('file_checksum_method',
                                       self.file_checksum_method)
        report += '{:<25} {}\n'.format('s3_url', self.s3_url)
        report += '{:<25} {}\n'.format('s3_url_metadata', self.s3_url_metadata)
        report += '{:<25} {}\n'.format('encryption_key_filename',
                                       self.encryption_key_filename)
        report += '{:<25} {}\n'.format('metadata_destination',
                                       self.metadata_destination)
        report += '{:<25} {}\n'.format('manifest_destination',
                                       self.manifest_destination)
        report += '{}\n'.format('='*76)
        return report



    def create(self):
        '''Create the config file with all default values.
        '''
        div = '#{}#'.format('='*76)
        cfg = ''
        cfg += '{}\n'.format(div)
        cfg += '# Read by python ConfigParser\n'
        cfg += '{}'.format(self.CONFIG_HEADER)
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



#=============================================================================#
# END
#=============================================================================#
