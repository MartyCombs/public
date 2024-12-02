#!/usr/bin/env python3
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create_metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create_metadata/bin/metadata.py
#=============================================================================#

import sys
import os
import re
import time
import datetime
import hashlib
from tqdm import tqdm
import json
from mylog import MyLog

class MetaData(object):
    '''Manages the metadata structure of files backed up to S3.

    ATTRIBUTES
        debug             : Enable debug mode.
        loglevel          : Log level.
        showprogress      : Enable progress bar.
        filename          : Basename of the file.
        fullpath          : Full path to the file.
        md_filename       : Basename of the metadata file.
        md_filecontents   : JSON formatted contents of the metadata file.
        stats             : Data structure for metadata file. (See below.)

    DATA STRUCTURE
        This will become the contents of 'FILENAME.meta'

        FILENAME {
            'backup_source'        : Backup source.
            'backup_date'          : Date of last backup as 'Y-M-D H:M:S TZ'.
            'file_size_bytes'      : File size in bytes.
            'file_checksum'        : Checksum of backup file.
            'file_checksum_method' : Checksum method (SHA256, MD5, etc)
            'encryption_key'       : Encryption key used on the file.
            's3_url'               : S3 URL to file.
            's3_url_metadata'      : S3 URL to metadata file.
        }

    METHODS
        set_filename               : Set the file name.
        set_backup_source          : Set backup source.
        set_backup_date            : Set date for backup.
        add_file_stats             : Add file size and checksum.
        set_encryption_key         : Set the value for encryption key used.
        set_s3_url                 : Set S3 URL for backup file.
        set_s3_url_metadata        : Set S3 URL for metadata file.
        format                     : Return JSON formatted contents of
                                     metadata file
        load                       : Load metadata file.

    '''

    MDINIT = {
        'backup_source' : 'personal',   # Backup source note
        'backup_date' : None,           # 'Y-M-D H:M:S TZ'
        'file_size_bytes' : None,       # File size in bytes
        'file_checksum' : None,         # Checksum of backup file
        'file_checksum_method' : None,  # Checksum method (SHA256, MD5, etc)
        'encryption_key' : 'GPG key',   # Encryption key used on the file.
        's3_url' : None,                # S3 URL of file
        's3_url_metadata' : None        # S3 URL of metadata file
    }


    def __init__(self, debug=None, loglevel='INFO', showprogress=False,
                 filename=None):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.showprogress = showprogress
        self.filename = None
        self.fullpath = None
        self.md_filename = None
        self.stats = self.MDINIT
        self.md_filecontents = None

        if filename: self.set_filename(filename)
        return



    def set_filename(self, path=None):
        '''Given a path, set attributes filename, fullpath, md_filename.
        '''
        if not os.path.exists(path): raise Exception('File does not exist')
        if not os.path.isfile(path): raise Exception('Not a file')
        if not os.access(path, os.R_OK): raise Exception('File not readable')
        self.filename = os.path.basename(path)
        self.fullpath = os.path.realpath(path)
        self.md_filename = self.filename + '.meta'
        return



    def set_backup_source(self, backup_source=None):
        '''Set the backup source for the filename.
        '''
        self.log.debug('Setting "backup_source" to "{}"'.format(backup_source))
        self.stats['backup_source'] = backup_source
        return
    def get_backup_source(self):
        return self.stats['backup_source']



    def set_backup_date(self, backup_date=None):
        '''Set the backup date for the filename.
        '''
        if not backup_date:
            self.log.error('Backup date not set')
            return
        self.log.debug('Setting "backup_date" to "{}"'.format(backup_date))
        self.stats['backup_date'] = backup_date
        return
    def get_backup_date(self):
        return self.stats['backup_date']



    def add_file_stats(self):
        '''Add file stats to the metadata file.  These cannot be set manually.
        These include:
            file_size_bytes
            file_checksum
            file_checksum_method
        '''
        self.log.debug('Adding file stats')
        self.stats['file_size_bytes'] = os.path.getsize(self.fullpath)
        self.stats['file_checksum_method'] = 'sha512'
        self._calculate_checksum()
        return
    def get_file_size_bytes(self):
        return self.stats['file_size_bytes']
    def get_file_checksum_method(self):
        return self.stats['file_checksum_method']



    def _calculate_checksum(self):
        self.log.debug('Calculating SHA512 sum of "{}"'.format(self.filename))

        # Set up a progress bar to let the user know we're still doing something.
        readbuff = 64 * 1024  # 64KB
        hasher = hashlib.sha512()
        if self.showprogress == True:
            filesize = os.path.getsize(self.filename)
            progress_bar = tqdm(total=filesize,
                                ascii=" >>>>>>>>>=",
                                unit='B',
                                unit_scale=True,
                                desc=self.filename)

        with open(self.fullpath, 'rb') as f:
            while True:
                buff = f.read(readbuff)
                if not buff: break
                hasher.update(buff)
                if self.showprogress == True: progress_bar.update(len(buff))
        if self.showprogress == True: progress_bar.close()
        self.stats['file_checksum'] = '{}'.format(hasher.hexdigest())
        return
    def get_file_checksum(self):
        return self.stats['file_checksum']



    def set_encryption_key(self, key_used=None):
        '''Set the value of the encryption key used on the file.
        '''
        self.log.debug('Setting "encryption_key" to "{}"'.format(key_used))
        self.stats['encryption_key'] = key_used
        return
    def get_encryption_key(self):
        return self.stats['encryption_key']



    def set_s3_url(self, s3_url=None):
        '''Set the S3 URL for the file.
        '''
        self.log.debug('Setting "s3_url" to "{}"'.format(s3_url))
        self.stats['s3_url'] = s3_url
        return
    def get_s3_url(self):
        return self.stats['s3_url']



    def set_s3_url_metadata(self, s3_url_metadata=None):
        '''Set the S3 URL for the metadata file.
        '''
        self.log.debug('Setting "s3_url_metadata" to "{}"'.format(s3_url_metadata))
        self.stats['s3_url_metadata'] = s3_url_metadata
        return
    def get_s3_url_metadata(self):
        return self.stats['s3_url_metadata']



    def format(self):
        '''Return JSON format of the metadata file.
        '''
        self.md_filecontents = {}
        self.md_filecontents[self.filename] = self.stats
        return(json.dumps(self.md_filecontents, indent=4, sort_keys=True))



    def load(self, path=None):
        '''Load data from the referenced stats file.

        NOTE: The attribute fullpath is not set as only the basename for the
              original file sent to S3 is stored in the metadata file.
        '''
        if not os.path.exists(path): raise Exception('File does not exist')
        if not os.path.isfile(path): raise Exception('No a file.')
        if not os.access(path, os.R_OK): raise Exception('File not readable')
        with open(os.path.realpath(path), 'r') as f:
            self.metadata_file = json.load(f)
        f.close()
        self.md_filename = os.path.basename(path)
        for k in self.metadata_file.keys():
            self.filename = str(k)
            for k2 in self.metadata_file[k].keys():
                self.stats[k2] = self.metadata_file[k][k2]
        return




#=============================================================================#
# END
#=============================================================================#
