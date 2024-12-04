#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from tqdm import tqdm
from base64 import b64encode
from enc_conf import EncConf
from mylog import MyLog

class AESCrypt(object):
    '''Methods for encrypting and decrypting files using AES-GCM encryption.
    The encrypted file will have within it at the beginning, tag, salt, and
    nonce.

    WARNING
    The decrypt() method expects the file to be in this format with the
    same number of bytes allocated for each.

    ATTRIBUTES
        debug              Enable debug mode.

        loglevel           Set the python log level.

        showprogress       Show progress via tqdm.

    METHODS
        set_filename       Set the filename before performing the encrypt()
                           or decrypt() methods.

        encrypt            Encrypt the file.

        decrypt            Decrypt the file.

    '''
    def __init__(self, debug=False, loglevel='WARNING', showprogress=False):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.showprogress = showprogress

        self._filename = None
        self._salt_size = 16
        self._stats = { 'salt' : None, 'nonce' : None, 'key' : None, 'tag' : None,
                        'infile_size' : 0, 'outfile_size' : 0 }
        cfg = EncConf(debug=self.debug, loglevel=self.loglevel)
        cfg.read()
        self._keyfile = cfg.keyfile
        self._chunk_size = int(cfg.chunk_size_kbytes * 1024)
        self._key_size = int(cfg.key_size_bytes)
        self._nonce_size = int(cfg.nonce_size_bytes)
        return



    def set_filename(self, path=None):
        '''Set the real path to the file (follow symlinks).  The resulting
        encrypted or decrypted file will end up the same directory as this
        starting file.
        '''
        if path == None: return
        self._filename = os.path.realpath(path)
        self.log.debug('Set filename to "{}"'.format(self._filename))
        return



    def _generate_key(self, master_key: bytes, salt: bytes) -> bytes:
        '''Take a master key and salt and return a key for encryption or
        decryption.
        '''
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self._key_size,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(master_key)



    def _read_master_key(self):
        '''Read the master key and convert it to bytes.
        '''
        if os.path.getsize(self._keyfile) == 0:
            raise Exception(
                'Master key file is empty "{}"'.format(self._keyfile))
        with open(self._keyfile, 'r') as f:
            key = f.read().strip()
        f.close()
        master_key_bytes = key.encode("utf-8")
        return master_key_bytes



    def _setup_progressbar(self):
        '''Enable the progress bar based on filesize.
        '''
        bar = tqdm(total=self._stats['infile_size'],
                   ascii=" >>>>>>>>>=",
                   unit='B',
                   unit_scale=True,
                   desc=os.path.basename(self._filename))
        return bar



    def _print_stats(self):
        '''Print the internal statistics of the file from __init__().  This
        includes salt, nonce, key, etc.
        '''
        rpt = '\n'
        rpt += '{}\n'.format('='*76)
        for k in self._stats.keys():
            rpt += '{:<15} {}\n'.format(k, self._stats[k])
        rpt += '{}\n'.format('='*76)
        return rpt



    def encrypt(self):
        '''Encrypt the file set by set_filename() method.  The encrypted file
        will have '.enc' appended to the name and will end up in the same
        directory.
        '''
        if self._filename == None:
            raise Exception('Set filename with set_filename() method first')
        input_file = self._filename
        output_file = self._filename + '.enc'
        self.log.debug('Encrypting "{}"'.format(os.path.basename(input_file)))

        # Generate a random salt and nonce
        salt = os.urandom(self._salt_size)
        nonce = os.urandom(self._nonce_size)
        self._stats['salt'] = b64encode(salt).decode('utf-8')
        self._stats['nonce'] = b64encode(nonce).decode('utf-8')

        # Derive a key from the master key and salt
        master_key = self._read_master_key()
        key = self._generate_key(master_key, salt)
        self._stats['key'] = b64encode(key).decode('utf-8')

        # Initialize cipher with AES alrorithm and GCM mode (with the nonce)
        # backend=default_backend() normally implies use of the normal
        # cryptographic backend - i.e. openssl
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        ).encryptor()

        # Set up the progress bar.
        self._stats['infile_size'] = os.path.getsize(input_file)
        if self.showprogress == True: bar = self._setup_progressbar()

        # Set aside the first 16 bytes for the encryption tag and then
        # write salt and nonce to the beginning of the output file
        with open(output_file, 'wb') as out_file:
            out_file.write(b'\x00' * 16)  # Reserved for encyryptor tag.
            out_file.write(salt)
            out_file.write(nonce)

            # Encrypt the file in chunks
            with open(input_file, 'rb') as in_file:
                while chunk := in_file.read(self._chunk_size):
                    encrypted_chunk = encryptor.update(chunk)
                    out_file.write(encrypted_chunk)
                    if self.showprogress == True: bar.update(len(chunk))


            # Finalize encryption and write the authentication tag to the
            # beginning of the file.
            out_file.write(encryptor.finalize())
            self._stats['tag'] = b64encode(encryptor.tag).decode('utf-8')
            out_file.seek(0)
            out_file.write(encryptor.tag)
            in_file.close()
        if self.showprogress == True: bar.close()
        out_file.close()
        self._stats['outfile_size'] = os.path.getsize(output_file)
        if self.debug: self.log.debug('{}'.format(self._print_stats()))
        return



    def decrypt(self):
        '''Decrypt the file set by set_filename() method.  The file must end
        in '.enc'.  The end result will end up in the same directory.
        '''
        if self._filename == None:
            raise Exception('Set filename with set_filename() method first')
        input_file = self._filename
        (basename, ext) = os.path.splitext(input_file)
        if ext != '.enc':
            raise Exception('Unrecognized extension "{}"'.format(ext))
        output_file = basename
        self.log.debug('Decrypting "{}"'.format(os.path.basename(input_file)))

        self._stats['infile_size'] = os.path.getsize(input_file)
        if self.showprogress == True: bar = self._setup_progressbar()

        with open(input_file, 'rb') as in_file:
            # Read salt, nonce, and tag from the input file
            tag = in_file.read(16)
            salt = in_file.read(self._salt_size)
            nonce = in_file.read(self._nonce_size)
            self._stats['tag'] = b64encode(tag).decode('utf-8')
            self._stats['salt'] = b64encode(salt).decode('utf-8')
            self._stats['nonce'] = b64encode(nonce).decode('utf-8')

            # Derive the same key using the master key and salt
            master_key = self._read_master_key()
            key = self._generate_key(master_key, salt)
            self._stats['key'] = b64encode(key).decode('utf-8')

            # Initialize decipher with AES alrorithm and GCM mode (with the nonce)
            # backend=default_backend() normally implies use of the normal
            # cryptographic backend - i.e. openssl
            decryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            ).decryptor()

            # Decrypt the file in chunks
            with open(output_file, 'wb') as out_file:
                while chunk := in_file.read(self._chunk_size):
                    decrypted_chunk = decryptor.update(chunk)
                    out_file.write(decrypted_chunk)
                    if self.showprogress == True: bar.update(len(chunk))

                # Finalize decryption (verifies integrity)
                decryptor.finalize()
            out_file.close()
        self._stats['outfile_size'] = os.path.getsize(output_file)
        if self.showprogress == True: bar.close()
        in_file.close()
        if self.debug: self.log.debug('{}'.format(self._print_stats()))
        return



#=============================================================================#
# END
#=============================================================================#
