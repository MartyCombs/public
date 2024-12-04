# Encrypt or decrypt files
Encrypt or decrypt files using the top level wrapper scripts `encrypt_files.sh`
or `decrypt_files.sh` respectively.

Encryption/Decryption methods used - as well as subscripts called - are
determined by a configuration file `etc/encryption_config.cfg`

All options are passed on to lower level, sub-scripts.  If the sub-script does
not understand a given option, it is ignored with a warning message.  While 
the scripts around AES-GCM encryption include options `--showprogress` and 
`--loglevel=`, scripts around GPG encryption do not currently offer these
options.

The `--help` option is available for all sub-scripts.

Specific encryption/decryption schemes follow their own path of sub-scripts and
wrapper scripts.  Those workflows are outlined below.

# Encryption / Decryption Methods
## AES-GCM
Encryption using AES-GCM reads, encrypts or decrypts, and writes an output file
in chunks.  A salt and nonce are generated.  The master key/password is read
and used with the salt to generate the encryption key.

The encryption key and nonce are used to encrypt the file in chunks.  Once the
file is encrypted, a tag is generated to ensure authenticity.

The tag, salt, and nonce are all included within the encrypted file for
decrypting.

## Precautions
**Proper management of the master key file `mykey` is critical.**
Minimal permissions should be set on this file so that its contents are not
compromised.  It should also be backed up.  Encrypted files cannot be
decrypted if this key is ever lost or changed.


### AES-GCM Scripts
* `aes_encrypt.sh` - Wrapper to ensure python virtual environment with dependencies
is created and used.
  - `aes_encrypt.py` - Called by `aes_encrypt.sh`.  Encrypts multiple files.
  - `aes_crypt.py` - Class used to encrypt or decrypt the file.

* `aes_decrypt.sh` - Wrapper to ensure python virtual environment with dependencies
is created and used.
  - `aes_decrypt.py` - Called by `aes_decrypt.sh`.  Decrypts multiple files.
  - `aes_crypt.py` - Class used to encrypt or decrypt the file.


## GPG
GPG wrappers scripts only store the recipient key used in encrypting or
decrypting files.  The wrappers are very simple and assumes the user has
gpg installed.  

Key creation and management is assumed to be done by the user through gpg.

### GPG Scripts
* `gpg_encrypt.sh` - Wrapper for `gpg` to encrypt files.

* `gpg_decrypt.sh` - Wrapper for `gpg` to decrypt files.

# Configuration Files
* `encryption_config.cfg` - Configuration file for AES-GCM and GPG 
parameters.  A configuration file with default settings can be 
generated using the `create_conf.py` helper script.

* `mykey` - File for the master key used in AES-GCM encryption.  A random
key can be generated using the `gen_new_key.py` helper script.

# Helper Scripts / Code
* `create_conf.py` - Creates the config file with default settings.

* `enc_conf.py` - Class used to manage the configuration file.

* `gen_new_key.py` - Generates a 32-bit random key which can be used as the 
master key for AES-GCM encryption in lieu of one created by the user.  See
the warnings about the master key in the AES-GCM section.

* `mylog.py` - Custom python logger.

# Testing
Run `test/test_encrypt.sh` to test AES-GCM encryption.  After making a backup 
copy of the key file containing the master key, a random key is generated.
The test file is encrypted, copied to a different name, and decrypted.
If the sum of both files matches, the test passes.

No explicit testing of GPG encryption is done.  The user can run the
encryption and decryption wrapper scripts and test.
