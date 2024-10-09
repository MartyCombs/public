#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#


import os
import hashlib
import random
import struct
from Crypto.Cipher import AES
from .mylog import MyLog



class Crypt(object):
    '''Encrypt and decrypt backups using AES-256.

    ATTRIBUTES
        debug          : Enable debug mode.
        log_level      : Log level.

    METHODS
        encrypt_file   : Encrypt a file. Extension '.enc' is appended.
        decrypt_file   : Decrypt a file. Extension '.enc' is assumed.
    '''


    def __init__(self, debug=False, loglevel='WARNING'):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log

        self.key_file = self._get_keyfile()
        self.key_identifier = None
        return



    def _get_keyfile(self):
        cfg = conf.Conf(debug=self.debug, loglevel=self.loglevel)
        cfg.read()
        return cfg.encryption_key_filename



    def _read_key(self):
        '''As a security by obscurity measure, the key in the file is longer
        than 32 characters however:

            The first 32 characters are used for the encryption.

            The last 4 characters are displayed when requested.

        This ensures that at no time are characters used to encrypt present
        in any communications associated with a key yet permits someone
        determine the key used for encryptions in event it is rotated out.
        '''
        with open(self.key_file, 'r') as f:
            key = f.readline().rstrip()
        f.close()
        self.key_identifier = key[-4:]
        self.log.debug('Loaded encryption key "...{}" from "{}"'.format(
            self.key_identifier, self.key_file))
        return key[:32].encode('utf8')



    def _check_key(self, identifier=None):
        if not self.key_identifier:    self._read_key()
        if identifier == self.key_identifier: return True
        return False



    def encrypt_file(self, in_filename=None,
                           out_filename=None,
                           chunksize=64*1024):
        ''' Encrypts a file using AES (CBC mode) with the given key.

            in_filename:
                Name of the input file

            out_filename:
                If None, '<in_filename>.enc' will be used.

            chunksize:
                Sets the size of the chunk which the function
                uses to read and encrypt the file. Larger chunk
                sizes can be faster for some files and machines.
                chunksize must be divisible by 16.
        '''
        if not out_filename:
            out_filename = in_filename + '.enc'
        self.log.info('Encrypting {} --> {}'.format(in_filename, out_filename))
        encryptor                          = AES.new(self._read_key(), AES.MODE_CBC)
        filesize                           = os.path.getsize(in_filename)
        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(struct.pack('<4s', self.key_identifier.encode('utf-8')))
                outfile.write(encryptor.iv)
                while True:
                    chunk                  = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk              += b' ' * (16 - len(chunk) % 16)
                    outfile.write(encryptor.encrypt(chunk))
        self.log.info('Encryption complete : {}'.format(out_filename))
        return



    def decrypt_file(self, in_filename, out_filename=None, chunksize=24*1024):
        ''' Decrypts a file using AES (CBC mode) with the given key.
        Parameters are similar to encrypt_file, with one difference:
        out_filename, if not supplied will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then out_filename will be 'aaa.zip')
        '''
        if not out_filename:
            out_filename                   = os.path.splitext(in_filename)[0]
        self.log.info('Decrypting {} --> {}'.format(in_filename, out_filename))
        with open(in_filename, 'rb') as infile:
            origsize                       = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            key_identifier                 = struct.unpack('<4s', infile.read(4))[0].decode('utf-8')
            iv                             = infile.read(16)
            decryptor                      = AES.new(self._read_key(), AES.MODE_CBC, iv)
            if self._check_key(key_identifier) == False: raise Exception('Key identifier used to encrypt "{}" does not match current key "{}".'.format(key_identifier, self.key_identifier))
            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk                  = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))
                outfile.truncate(origsize)
        self.log.info('Decryption complete : {}'.format(out_filename))
        return



#=============================================================================#
# END
#=============================================================================#
