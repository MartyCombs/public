#!/usr/bin/env python3
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create_metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create_metadata/bin/metadata_conf.py
#=============================================================================#

import sys
import os
import re
import configparser
from mylog import MyLog


class MetadataConf(object):
    '''Manage metadata configuration file.

    ATTRIBUTES
        debug                   Enable debug mode.

        loglevel                Set the python log level.

    METHODS
        read                   Read the configuration file.

        set_backup_source      A text label for the backup such as
                               'personal', 'work', 'photos', etc.

        set_encryption_key     Key used to encrypt the backup.

        set_s3_url             S3 URL where to store the backup.

        set_s3_url_metadata    S3 URL for the metadata file.

        print                  Print the values of the configuration for
                               debug logging.

        build                  Return full contents of the configuration file
                               for writing.

    '''

    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    DEF_CONFIG_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 'metadata.cfg'
    DEF_CONFIG = {
        'backup_source'            : 'personal',
        'encryption_key'           : 'GPG',
        's3_url'                   : 's3://BUCKET_NAME/PATH',
        's3_url_metadata'          : 's3://BUCKET_NAME/PATH'
    }
    BACKUP_SOURCES = ['personal', 'work']
    S3_URL = re.compile(r's3://.*')


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
        self.encryption_key = self.DEF_CONFIG['encryption_key']
        self.s3_url = self.DEF_CONFIG['s3_url']
        self.s3_url_metadata = self.DEF_CONFIG['s3_url_metadata']
        return



    def read(self):
        '''Read the configuration file.
        '''
        self.log.debug('Reading {}'.format(self.DEF_CONFIG_FILE))
        cfg = configparser.RawConfigParser()
        cfg.read(self.DEF_CONFIG_FILE)
        self.set_backup_source(
            cfg.get('DEFAULT', 'backup_source'))
        self.set_encryption_key(
            cfg.get('DEFAULT', 'encryption_key'))
        self.set_s3_url(
            cfg.get('DEFAULT', 's3_url'))
        self.set_s3_url_metadata(
            cfg.get('DEFAULT', 's3_url_metadata'))
        return



    def set_backup_source(self, source=None):
        if source == None: return
        if source not in self.BACKUP_SOURCES:
            raise Exception('Backup source "{}" not in accepted list\n"{}"'.format(
                source, self.BACKUP_SOURCES))
        self.backup_source = source
        return


    def set_encryption_key(self, enckey=None):
        if enckey == None: return
        self.encryption_key = enckey
        return


    def set_s3_url(self, url=None):
        if url == None: return
        if not re.match(self.S3_URL, url):
            raise Exception('Unrecognized S3 url')
        self.s3_url = url
        return


    def set_s3_url_metadata(self, url=None):
        if url == None: return
        if not re.match(self.S3_URL, url):
            raise Exception('Unrecognized S3 url')
        self.s3_url_metadata = url
        return


    def print(self):
        report = '{}\n'.format('='*76)
        report += '{:<25} {}\n'.format('backup_source', self.backup_source)
        report += '{:<25} {}\n'.format('encryption_key', self.encryption_key)
        report += '{:<25} {}\n'.format('s3_url', self.s3_url)
        report += '{:<25} {}\n'.format('s3_url_metadata', self.s3_url_metadata)
        report += '{}\n'.format('='*76)
        return report



    def build(self):
        '''Create the metadata configuration file with all default values.
        '''
        div = '#{}#'.format('='*76)
        cfg = ''
        cfg += '{}\n'.format(div)
        cfg += '# Read by python ConfigParser\n'
        cfg += '{}'.format(self._conf_header())
        cfg += '\n'
        cfg += '[DEFAULT]\n'
        cfg += 'backup_source = {}\n'.format(self.backup_source)
        cfg += 'encryption_key = {}\n'.format(self.encryption_key)
        cfg += 's3_url = {}\n'.format(self.s3_url)
        cfg += 's3_url_metadata = {}\n'.format(self.s3_url_metadata)
        cfg += '\n{}\n# END\n{}\n'.format(div, div)
        return cfg



    def _conf_header(self):
        header = ''
        header += '''#
# Created by
#    {}
# Configuration file for metadata file settings.
#       '''.format(__class__)
        header += '''
# backup_source                Label for the backup source such as
#                              'personal', 'work', 'photos', etc.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['backup_source'])
        header += '''
# encryption_key               Key used to encrypt the backup.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['encryption_key'])
        header += '''
# s3_url                       S3 URL for the backup file.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['s3_url'])
        header += '''
# s3_url_metadata              S3 URL for the metadata file
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['s3_url_metadata'])
        return header



#=============================================================================#
# END
#=============================================================================#
