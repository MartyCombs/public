#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import os
import configparser
from mylog import MyLog


class AWSConf(object):
    '''Manage the AWS S3 configuration file.

    ATTRIBUTES
        debug                   Enable debug mode.

        loglevel                Set the python log level.


    METHODS
        read                   Read the configuration file.

        set_mp_threshold       File size in bytes above which a file is uploaded
                               to S3 using multipart upload with BOTO3 S3 resource
                               with threading instead of the BOTO3 S3 client.

        set_max_concurrency    Maximum concurrent uploads to S3 for a multipart
                               upload.

        set_mp_chunksize       Chunk size for multipart upload.


        print                  Print the values of the configuration for
                               debug logging.

        build                  Return full contents of the configuration file
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
        '''Set the bytes at which an upload to S3 will use multipart upload.
        '''
        if mp_threshold == None: return
        self.mp_threshold = int(mp_threshold)
        self.log.debug('Set mp_threshold to {}'.format(mp_threshold))
        return



    def set_max_concurrency(self, max_concurrency=None):
        '''Set maximum concurrency of uploads for multipart upload.
        '''
        if max_concurrency == None: return
        self.max_concurrency = int(max_concurrency)
        self.log.debug('Set max_concurrency to {}'.format(max_concurrency))
        return



    def set_mp_chunksize(self, mp_chunksize=None):
        '''Set the chunk size for multipart upload.
        '''
        if mp_chunksize == None: return
        self.mp_chunksize = int(mp_chunksize)
        self.log.debug('Set mp_chunksize to {}'.format(mp_chunksize))
        return



    def print(self):
        '''Report on the details read from the configuration file.
        '''
        rpt = '{}\n'.format('='*76)
        rpt += '{:<25} {}\n'.format('mp_threshold', self.mp_threshold)
        rpt += '{:<25} {}\n'.format('max_concurrency', self.max_concurrency)
        rpt += '{:<25} {}\n'.format('mp_chunksize', self.mp_chunksize)
        rpt += '{}\n'.format('='*76)
        return rpt



    def build(self):
        '''Create the metadata configuration file for writing.
        '''
        div = '#{}#'.format('='*76)
        cfg = ''
        cfg += '{}\n'.format(div)
        cfg += '# Read by python ConfigParser\n'
        cfg += '{}'.format(self._conf_header())
        cfg += '\n'
        cfg += '[DEFAULT]\n'
        cfg += 'mp_threshold = {}\n'.format(self.mp_threshold)
        cfg += 'max_concurrency = {}\n'.format(self.max_concurrency)
        cfg += 'mp_chunksize = {}\n'.format(self.mp_chunksize)
        cfg += '\n\n{}\n# END\n{}\n'.format(div, div)
        return cfg



    def _conf_header(self):
        '''Header for the configuration file.
        '''
        header = ''
        header += '''#
# Created by
#    {}
# Configuration file for metadata file settings.
#       '''.format(__class__)
        header += '''
# mp_threshold                 Files above this threshold (in bytes) will
#                              use multipart upload with BOTO3 S3 resource
#                              and threads instead of the BOTO3 S3 client.
#                              [DEFAULT: {}] (32 MB)
#       '''.format(self.DEF_CONFIG['mp_threshold'])
        header += '''
# max_concurrency              Maximum concurrent uploads to run.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['max_concurrency'])
        header += '''
# mp_chunksize                 Size of chunks (in bytes) for a multipart
#                              upload.
#                              [DEFAULT: {}] (32 KB)
#       '''.format(self.DEF_CONFIG['mp_threshold'])
        return header



#=============================================================================#
# END
#=============================================================================#
