# Encrypt or decrypt files
Encrypt or decrypt files using the top level wrapper scripts `encrypt_files.sh`
or `decrypt_files.sh` respectively.

Configuration settings for all encryption / decryption methods are managed by 
`encryption_config.cfg`.

Wrapper scripts pass all options to lower level, sub-scripts.  If the 
sub-script does not understand a given option, it is ignored with a 
warning message.  For example, scripts around GPG ignore options 
`--showprogress` and `--loglevel`.

The `--help` option is available for all sub-scripts.


# Encryption / Decryption workflow
## AES-GCM
For AES-GCM encryption, a master key is read from a file, a salt and nonce 
are generated, and the file is read in chunks, encrypted, and written back 
into the same directory.  The encrypted file has `.enc` appended to the end 
of the name.  After encryption, a tag is included in the file to ensure
file authenticity.

For decryption, the file is expected to have a `.enc` extension in the name.
The necessary information - tag, salt, nonce - are read from the file, the
encrypted file is read in chunks, decrypted, and written back into the 
same directory.  The decrypted will is assumed to be the same name as the
encrypted file, but without the `.enc` name extension.


## GPG
The GPG wrappers scripts are a minimal wrapper around the `gpg` executable.
During encryption, only `gpg_key` is read from the configuration file 
`encryption_config.cfg` to retrieve the name of the GPG key to use to 
pass on to `gpg` to do the encryption.

During decryption, the path to the encrypted file is passed on to `gpg`
which does the prompting for the passphrase associated with the 
encryption key on the terminal.  Because of this prompt dependency at the
terminal, decryption through GPG **cannot easily be enclosed in a script.**

The user is expected to handle key creation and management through the 
`gpg` executable.


# Configuration
All configuration files are located in the `./etc` subdirectory.

* `encryption_config.cfg` - All settings impact AES-GCM encryption / decryption
**except** `gpg_key` which is used for GPG encryption only.  A file with
default values can be generated using `create_conf.py`.

* `mykey` - File containing the master key used in AES-GCM encryption /
decryption.  The helper script `gen_new_key.py` will echo a random key to 
standard output (STDOUT) which the user can put into the file. **Please
CAREFULLY read the Precautions section regarding this file.**


# Code
__Running top level scripts with `--help` will list options available.__

## AES
* `aes_encrypt.sh` - Top level script to run for encrypting multiple files 
with AES-GCM.  The script passes all options to lower level scripts.
  - `aes_encrypt.py` - Called by `aes_encrypt.sh`.
  - `aes_crypt.py` - Python class which does all the work.
* `aes_decrypt.sh` - Top level script to run for decrypting multiple files 
with AES-GCM.  The script passes all options to lower level scripts.
  - `aes_decrypt.py` - Called by `aes_decrypt.sh`.
  - `aes_crypt.py` - Python class which does all the work.

## GPG
* `gpg_encrypt.sh` - Wrapper for `gpg` to encrypt files.
* `gpg_decrypt.sh` - Wrapper for `gpg` to decrypt files.


## Helper scripts
* `enc_conf.py` - Class used to read the configuration file and pass values
on to python scripts.
* `create_conf.py` - Creates the config file with default settings.
* `mylog.py` - Custom python logger class.
* `gen_new_key.py` - Generates a 32-bit random key which can be used as the 
master key for AES-GCM encryption in lieu of one created by the user.  **Read
the Precautions section carefully.**

# Precautions
**Proper management of the file `mykey` is critical.**
Anyone reading the `mykey` file will be able to decrypt files encrypted with it.
Ensure that the file has minimal access permissions.  The key contained 
in the file is the single point of failure for properly decrypting any files
where it was used to encrypt.

The key should also be backed up.  **Encrypted files cannot be decrypted** if 
the master key stored in this file is ever altered or lost.  If the user 
chooses to rotate the key, they will be **unable** to decrypt any files 
encrypted with the old key without having a backup copy of the original key
stored somewhere safely.

# Testing
`test_encrypt.sh` - Runs some rudimentary tests of AES-GCM encryption
and decryption.
  - `test_encrypt.py` - Called by `test_encrypt.sh`.

No explicit testing of GPG encryption is done.
