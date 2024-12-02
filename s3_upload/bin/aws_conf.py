#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import os
import configparser
import boto3
from mylog import MyLog


class AWSConf(object):
    '''Manage the AWS S3 configuration file.

    ATTRIBUTES
        mp_threshold           File size in bytes above which a file is uploaded
                               to S3 using multipart upload.

        max_concurrency        Maximum concurrent uploads to S3 for a multipart
                               upload.

        mp_chunksize           Chunk size for multipart upload.


    METHODS
        read()                 Read the configuration file.

        set_backup_source()    Set the backup source.

        set_encryption_key()   Set the encryption key.

        set_s3_url()           Set the S3 URL for the file.

        set_s3_url_metadata()  Set the S3 URL for the metadata file.

        print()                Print the values of the configuration for
                               debug logging.

        build()                Return full contents of the configuration file
                               for writing.

    '''

    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    DEF_CONFIG_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 'aws_s3.cfg'
    DEF_CONFIG = {
        'mp_threshold'         : 32 * (1024 ** 2),
        'max_concurrency'      : 10,
        'mp_chunksize'         : 32 * 1024
    }

    def __init__(self, debug=None, loglevel='WARNING'):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=self.debug, loglevel=self.loglevel)
        self.log = l.log
        self.top_dir = self.TOP_DIR
        self.filename = self.DEF_CONFIG_FILE

        # Config settings.
        self.mp_threshold = self.DEF_CONFIG['mp_threshold']
        self.max_concurrency = self.DEF_CONFIG['max_concurrency']
        self.mp_chunksize = self.DEF_CONFIG['mp_chunksize']
        return



    def read(self):
        '''Read the configuration file.
        '''
        self.log.debug('Reading {}'.format(self.DEF_CONFIG_FILE))
        cfg = configparser.RawConfigParser()
        cfg.read(self.DEF_CONFIG_FILE)
        self.set_mp_threshold(
            cfg.get('DEFAULT', 'mp_threshold'))
        self.set_max_concurrency(
            cfg.get('DEFAULT', 'max_concurrency'))
        self.set_mp_chunksize(
            cfg.get('DEFAULT', 'mp_chunksize'))
        return



    def set_mp_threshold(self, mp_threshold=None):
        if mp_threshold == None: return
        self.mp_threshold = int(mp_threshold)
        return



    def set_max_concurrency(self, max_concurrency=None):
        if max_concurrency == None: return
        self.max_concurrency = int(max_concurrency)
        return



    def set_mp_chunksize(self, mp_chunksize=None):
        if mp_chunksize == None: return
        self.mp_chunksize = int(mp_chunksize)
        return



    def print(self):
        report = '{}\n'.format('='*76)
        report += '{:<25} {}\n'.format('mp_threshold', self.mp_threshold)
        report += '{:<25} {}\n'.format('max_concurrency', self.max_concurrency)
        report += '{:<25} {}\n'.format('mp_chunksize', self.mp_chunksize)
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
        for key in self.DEF_CONFIG.keys():
            cfg += '{} = {}\n'.format(key, self.DEF_CONFIG[key])
        cfg += '{}\n# END\n{}\n'.format(div, div)
        return cfg



    def _conf_header(self):
        header = ''
        header += '''#
# Created by
#    {}
# Configuration file for metadata file settings.
#       '''.format(__class__)
        header += '''
# mp_threshold                 Threshold in bytes where an upload to S3 is broken
#                              into a multipart upload.
#                              [DEFAULT: {}] (32 MB)
#       '''.format(self.DEF_CONFIG['mp_threshold'])
        header += '''
# max_concurrency              Maximum concurrent uploads running.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['max_concurrency'])
        header += '''
# mp_chunksize                 Threshold in bytes where an upload to S3 is broken
#                              into a multipart upload.
#                              [DEFAULT: {}] (32 KB)
#       '''.format(self.DEF_CONFIG['mp_threshold'])
        return header



#=============================================================================#
# END
#=============================================================================#
