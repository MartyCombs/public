#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import os
import configparser
from mylog import MyLog


class EncConf(object):
    '''Manage encryption config.

    ATTRIBUTES
        debug                   Enable debug mode.

        loglevel                Set the python log level.

    METHODS
        read                    Read the configuration file.

        set_encryption_method   The encryption method for encrypting and
                                decrypting files.  It must be one of the
                                list of understood encryption methods.
                                {}

        set_gpg_key             If the encryption / decryption method is GPG,
                                use this key.

        set_keyfile             File containing the master key used to by
                                AES-GCM to encrypt/decrypt a file.

        set_chunk_size_kbytes   Chunk size for reading and writing while
                                encrypting or decrypting.

        set_key_size_bytes      Size of subsequent key generated from the
                                master key and a salt used to encrypt or
                                decrypt the file.

        set_nonce_size_bytes    Nonce size.

        print                   Print the configuration of parameters for
                                nice logging.

        build                   Build and return the configuration file for
                                writing.

    '''



    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    DEF_CONFIG_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 'encryption_config.cfg'
    DEF_CONFIG = {
        'encryption_method'        : 'AES-GCM',
        'gpg_key'                  : 'user@host',
        'keyfile'                  : 'etc/mykey',
        'chunk_size_kbytes'        : 64,
        'key_size_bytes'           : 32,
        'nonce_size_bytes'         : 12
    }
    ENCRYPTION_METHODS=['AES-GCM', 'GPG']



    def __init__(self, debug=False, loglevel='WARNING'):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.filename = self.DEF_CONFIG_FILE

        # Config parameters
        self.encryption_method = self.DEF_CONFIG['encryption_method']
        self.gpg_key = self.DEF_CONFIG['gpg_key']
        self.keyfile = self.DEF_CONFIG['keyfile']
        self.chunk_size_kbytes = self.DEF_CONFIG['chunk_size_kbytes']
        self.key_size_bytes = self.DEF_CONFIG['key_size_bytes']
        self.nonce_size_bytes = self.DEF_CONFIG['nonce_size_bytes']
        return



    def read(self):
        '''Read the configuration file.
        '''
        self.log.debug('Reading {}'.format(self.DEF_CONFIG_FILE))
        cfg = configparser.RawConfigParser()
        cfg.read(self.DEF_CONFIG_FILE)

        self.set_encryption_method(
            cfg.get('DEFAULT', 'encryption_method'))
        self.set_gpg_key(
            cfg.get('DEFAULT', 'gpg_key'))
        self.set_keyfile(self._add_path(
            cfg.get('DEFAULT', 'keyfile')))
        self.set_chunk_size_kbytes(
            cfg.get('DEFAULT', 'chunk_size_kbytes'))
        self.set_key_size_bytes(
            cfg.get('DEFAULT', 'key_size_bytes'))
        self.set_nonce_size_bytes(
            cfg.get('DEFAULT', 'nonce_size_bytes'))
        return



    def _add_path(self, path=None):
        '''If first character of a path is os.sep, assume the full path is
        specified.  Otherwise ASSUME that the path specified is relative
        to the top level directory.
        '''
        fullpath = None
        if path[0] == os.sep:
            fullpath = path
        else:
            fullpath = self.TOP_DIR + os.sep + path
        return fullpath




    def set_encryption_method(self, encryption_method=None):
        '''Set the encryption method to one of the accepted methods understood
        by this code.

        {}
        '''.format(self.ENCRYPTION_METHODS)
        if encryption_method == None: return
        if encryption_method not in self.ENCRYPTION_METHODS:
            raise Exception('Encryption method "{}" not understood'.format(
                encryption_method))
        self.encryption_method = encryption_method
        return



    def set_gpg_key(self, gpg_key=None):
        '''If encryption_method is "GPG", set the key which will be used to
        encrypt or decrypt the file.
        '''
        if gpg_key == None: return
        self.gpg_key = gpg_key
        return



    def set_keyfile(self, keyfile=None):
        '''If encryption_method is "AES-GCM" set the file containing the
        master key to encrypt or decrypt files.  The master key is used
        to derive another key which will be used to do the encryption.
        '''
        if keyfile == None: return
        self.keyfile = keyfile
        return



    def set_chunk_size_kbytes(self, chunk_size_kbytes=None):
        '''For large files, set the kilobytes for the chunks which will be
        encrypted.
        '''
        if chunk_size_kbytes == None: return
        self.chunk_size_kbytes = int(chunk_size_kbytes)
        return



    def set_key_size_bytes(self, key_size_bytes=None):
        '''Set the size of the key generated from the master key which
        will be used to encrypt or decrypt files.
        '''
        if key_size_bytes == None: return
        self.key_size_bytes = int(key_size_bytes)
        return



    def set_nonce_size_bytes(self, nonce_size_bytes=None):
        '''Set the size of the nonce used to encrypt or decrypt files.
        '''
        if nonce_size_bytes == None: return
        self.nonce_size_bytes = int(nonce_size_bytes)
        return



    def print(self):
        '''Report on the details read from the configuration file.
        '''
        report = '{}\n'.format('='*76)
        report += '{:<25} {}\n'.format('encryption_method', self.encryption_method)
        report += '{:<25} {}\n'.format('gpg_key', self.gpg_key)
        report += '{:<25} {}\n'.format('keyfile', self.keyfile)
        report += '{:<25} {}\n'.format('chunk_size_kbytes', self.chunk_size_kbytes)
        report += '{:<25} {}\n'.format('key_size_bytes', self.key_size_bytes)
        report += '{:<25} {}\n'.format('nonce_size_bytes', self.nonce_size_bytes)
        report += '{}\n'.format('='*76)
        return report




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
        cfg += 'encryption_method = {}\n'.format(self.encryption_method)
        cfg += 'gpg_key = {}\n'.format(self.gpg_key)
        cfg += 'keyfile = {}\n'.format(self.keyfile)
        cfg += 'chunk_size_kbytes = {}\n'.format(self.chunk_size_kbytes)
        cfg += 'key_size_bytes = {}\n'.format(self.key_size_bytes)
        cfg += 'nonce_size_bytes = {}\n'.format(self.nonce_size_bytes)
        cfg += '\n{}\n# END\n{}\n'.format(div, div)
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
# encryption_method            Method used to encrypt and decrypt files.
#                              ACCEPTED METHODS:
#                              [{}]
#                              [DEFAULT: {}]
#       '''.format(self.ENCRYPTION_METHODS,
                   self.DEF_CONFIG['encryption_method'])
        header += '''
# gpg_key                      If using GPG to encrypt or decrypt, use this key.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['gpg_key'])
        header += '''
# keyfile                      File containing key for encrypting files.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['keyfile'])
        header += '''
# chunk_size_kbytes            Chunk size for encrypting large files.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['chunk_size_kbytes'])
        header += '''
# key_size_bytes               Size of key used to encrypt.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['key_size_bytes'])
        header += '''
# nonce_size_bytes             Nonce size.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['nonce_size_bytes'])
        return header



#=============================================================================#
# END
#=============================================================================#
