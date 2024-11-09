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


class MetadataConf(object):
    '''Manage metadata configuration file.

    ATTRIBUTES
        backup_source           : A text label for the backup such as
                                  'personal', 'work', 'photos', etc.

        encryption_key          : Key used to encrypt the backup.

        s3_url                  : S3 URL where to store the backup.

        s3_url_metadata         : S3 URL for the metadata file.

    '''

    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    DEF_CONFIG_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 'metadata.cfg'
    DEF_CONFIG = {
        'backup_source'            : 'personal',
        'encryption_key'           : 'GPG key',
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
        backup_source = cfg.get('DEFAULT', 'backup_source')
        self.backup_source = self.set_backup_source(backup_source)
        encryption_key = cfg.get('DEFAULT', 'encryption_key')
        self.encryption_key = self.set_encryption_key(encryption_key)
        s3_url = cfg.get('DEFAULT', 's3_url')
        self.s3_url = self.set_s3_url(s3_url)
        s3_url_metadata = cfg.get('DEFAULT', 's3_url_metadata')
        self.set_s3_url_metadata(s3_url_metadata)
        return



    def set_backup_source(self, source=None):
        '''
        '''
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



    def create(self):
        '''Create the metadata configuration file with all default values.
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
# Configuration file for metadata file settings.
#       '''
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
