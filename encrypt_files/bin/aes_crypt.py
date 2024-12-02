#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import re
import progressbar
from base64 import b64encode
from enc_conf import EncConf
from mylog import MyLog



class AESCrypt(object):
    '''Methods for encrypting and decrypting files.
    '''
    def __init__(self, debug=False, loglevel='WARNING', showprogress=False):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.showprogress = showprogress

        self.filename = None
        self.re_encrypted = re.compile(r'^(.*)\.enc$')
        self.encrypted = None
        self.salt_size = 16
        self.stats = { 'salt' : None, 'nonce' : None, 'key' : None, 'tag' : None,
                       'infile_size' : 0, 'outfile_size' : 0 }
        cfg = EncConf(debug=self.debug, loglevel=self.loglevel)
        cfg.read()
        self.keyfile = cfg.keyfile
        self.chunk_size = int(cfg.chunk_size_kbytes * 1024)
        self.key_size = int(cfg.key_size_bytes)
        self.nonce_size = int(cfg.nonce_size_bytes)
        return



    def set_filename(self, path=None):
        if path == None: return
        self.filename = os.path.realpath(path)
        self.log.debug('Set filename to "{}"'.format(self.filename))
        return



    def _generate_key(self, password: bytes, salt: bytes) -> bytes:
        '''Take a master key with salt and return a key for encryption or
        decryption.
        '''
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_size,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password)



    def _read_password(self):
        '''Read the master password and convert it to bytes.
        '''
        with open(self.keyfile, 'r') as f:
            key = f.read().strip()
        f.close()
        password_bytes = key.encode("utf-8")
        return password_bytes



    def _setup_progressbar(self):
        progressmax = self.stats['infile_size'] / self.chunk_size
        if self.stats['infile_size'] % self.chunk_size > 0:
            progressmax += 1
        if self.showprogress == True:
            widgets = [progressbar.ETA(), ' ',
                       progressbar.Bar('=', '[', ']', ' '), ' ',
                       progressbar.Percentage()]
            bar = progressbar.ProgressBar(widgets=widgets,
                                          maxval=progressmax,
                                          term_width=80).start()
        return bar



    def _print_stats(self):
        rpt = '\n'
        rpt += '{}\n'.format('='*76)
        for k in self.stats.keys():
            rpt += '{:<15} {}\n'.format(k, self.stats[k])
        rpt += '{}\n'.format('='*76)
        return rpt



    def encrypt(self):
        '''Encrypt the file set by set_filename() method.  The encrypted file
        will have '.enc' appended to the name.
        '''
        if self.filename == None:
            raise Exception('Set filename with set_filename() method first')
        input_file = self.filename
        output_file = self.filename + '.enc'
        self.log.debug('Encrypting "{}"'.format(os.path.basename(input_file)))

        # Generate a random salt and nonce
        salt = os.urandom(self.salt_size)
        nonce = os.urandom(self.nonce_size)
        self.stats['salt'] = b64encode(salt).decode('utf-8')
        self.stats['nonce'] = b64encode(nonce).decode('utf-8')

        # Derive a key from the password and salt
        password = self._read_password()
        key = self._generate_key(password, salt)
        self.stats['key'] = b64encode(key).decode('utf-8')

        # Initialize cipher with AES alrorithm and GCM mode (with the nonce)
        # backend=default_backend() normally implies use of the normal
        # cryptographic backend - i.e. openssl
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        ).encryptor()

        # Set up the progress bar.
        self.stats['infile_size'] = os.path.getsize(input_file)
        if self.showprogress == True: bar = self._setup_progressbar()

        # Set aside the first 16 bytes for the encryption tag and then
        # write salt and nonce to the beginning of the output file
        with open(output_file, 'wb') as out_file:
            out_file.write(b'\x00' * 16)  # Reserved for encyryptor tag.
            out_file.write(salt)
            out_file.write(nonce)

            # Encrypt the file in chunks
            with open(input_file, 'rb') as in_file:
                i = 0
                while chunk := in_file.read(self.chunk_size):
                    encrypted_chunk = encryptor.update(chunk)
                    out_file.write(encrypted_chunk)
                    i = i + 1
                    if self.showprogress == True: bar.update(i)


            # Finalize encryption and write the authentication tag to the
            # beginning of the file.
            out_file.write(encryptor.finalize())
            self.stats['tag'] = b64encode(encryptor.tag).decode('utf-8')
            out_file.seek(0)
            out_file.write(encryptor.tag)
            in_file.close()
        if self.showprogress == True: bar.finish()
        out_file.close()
        self.stats['outfile_size'] = os.path.getsize(output_file)
        if self.debug: self.log.debug('{}'.format(self._print_stats()))
        return



    def decrypt(self):
        '''Decrypt the file set by set_filename() method.  The file must end
        in '.enc'
        '''
        if self.filename == None:
            raise Exception('Set filename with set_filename() method first')
        input_file = self.filename
        is_encrypted = re.match(self.re_encrypted, input_file)
        if not is_encrypted:
            raise Exception('Unrecognized extension.')
        output_file = is_encrypted.group(1)
        self.log.debug('Decrypting "{}"'.format(os.path.basename(input_file)))

        self.stats['infile_size'] = os.path.getsize(input_file)
        if self.showprogress == True: bar = self._setup_progressbar()
        i = 0

        with open(input_file, 'rb') as in_file:
            # Read salt, nonce, and tag from the input file
            tag = in_file.read(16)
            salt = in_file.read(self.salt_size)
            nonce = in_file.read(self.nonce_size)
            self.stats['tag'] = b64encode(tag).decode('utf-8')
            self.stats['salt'] = b64encode(salt).decode('utf-8')
            self.stats['nonce'] = b64encode(nonce).decode('utf-8')

            # Derive the same key using the password and salt
            password = self._read_password()
            key = self._generate_key(password, salt)
            self.stats['key'] = b64encode(key).decode('utf-8')

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
                while chunk := in_file.read(self.chunk_size):
                    decrypted_chunk = decryptor.update(chunk)
                    out_file.write(decrypted_chunk)
                    i = i + 1
                    if self.showprogress == True: bar.update(i)

                # Finalize decryption (verifies integrity)
                decryptor.finalize()
            out_file.close()
        self.stats['outfile_size'] = os.path.getsize(output_file)
        if self.showprogress == True: bar.finish()
        in_file.close()
        if self.debug: self.log.debug('{}'.format(self._print_stats()))
        return



#=============================================================================#
# END
#=============================================================================#
