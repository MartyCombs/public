#!/usr/bin/env python3

import sys
import os
import shutil
import hashlib
from mylog import MyLog
from crypt import AESCrypt


def checksum(filename=None):
    hasher = hashlib.sha512()
    with open(filename, 'rb') as f:
        contents = f.read()
        hasher.update(contents)
    f.close()
    return hasher.hexdigest()

l = MyLog(debug=True)
log = l.log
log.debug('Testing encryption class crypt.AESCrypt')

testfile1 = 'testfile.mp4'
testfile2 = 'testfile-copy.mp4'

# Encrypt the test file.
c = AESCrypt(debug=True)
c.set_filename(testfile1)
c.encrypt()

# Copy the encrypted file to a different name and decrypt.
shutil.copyfile(testfile1 + '.enc', testfile2 + '.enc')
c.set_filename(testfile2 + '.enc')
c.decrypt()

# Checksum both files and compare.
testfile1_sum = checksum(testfile1)
testfile2_sum = checksum(testfile2)
rpt = '\n{}\n'.format('='*80)
rpt += '{:<20} {}\n'.format('File Name', 'SHA512 Checksum')
rpt += '{:<20} {}\n'.format('-'*20, '-'*20)
rpt += '{:<20} {}\n\n'.format(testfile1, testfile1_sum)
rpt += '{:<20} {}\n'.format(testfile2, testfile2_sum)
rpt += '\n{}\n'.format('='*80)
log.debug('{}'.format(rpt))
if testfile1_sum == testfile2_sum:
    log.info('Original file contents match after decoding.')
    for f in [testfile1 + '.enc',
              testfile2,
              testfile2 + '.enc']:
        os.remove(f)
else:
    log.error('Original file contents match after decoding.')


sys.exit()
