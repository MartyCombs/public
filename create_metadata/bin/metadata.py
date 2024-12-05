#!/usr/bin/env python3
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create_metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create_metadata/bin/metadata.py
#=============================================================================#

import sys
import os
import time
import datetime
import hashlib
from tqdm import tqdm
import json
from mylog import MyLog

class MetaData(object):
    '''Manages the metadata structure of files backed up to S3.

    ATTRIBUTES
        debug                    Enable debug mode.

        loglevel                 Set the python log level.

        showprogress             Show progress via tqdm.

        filename                 File name.

        metadata_filename        Metadata file name.

        metadata_filecontents    JSON formatted contents of the metatdata file.
                                 after loading a metadata file or after setting
                                 all metadata file attributes and running the
                                 format() method.


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
        set_filename             Set the file name.

        set_backup_source        Set backup source.

        set_backup_date          Set date for backup.

        add_file_stats           Add file information such as 'file_size_bytes',
                                 'file_checksum_method', and 'file_checksum'.

        set_encryption_key       Set the encryption key used.

        set_s3_url               Set S3 URL for the file.

        set_s3_url_metadata      Set S3 URL for the metadata file.
                                 (This file.)

        format                   Return JSON formatted contents of metadata file.

        load                     Load metadata file.

    '''

    DEFAULT_SETTINGS = {
        'backup_source' : None      ,   # Backup source note
        'backup_date' : None,           # 'Y-M-D H:M:S TZ'
        'file_size_bytes' : None,       # File size in bytes
        'file_checksum' : None,         # Checksum of backup file
        'file_checksum_method' : None,  # Checksum method (SHA256, MD5, etc)
        'encryption_key' : None,        # Encryption key used on the file.
        's3_url' : None,                # S3 URL of file
        's3_url_metadata' : None        # S3 URL of metadata file
    }


    def __init__(self,
                 debug=None,
                 loglevel='INFO',
                 showprogress=False,
                 filename=None):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.showprogress = showprogress

        if filename != None:
            self.set_filename(filename)
        else:
            self.filename = None
            self.metadata_filename = None
            self.fullpath = None
        self.backup_source = self.DEFAULT_SETTINGS['backup_source']
        self.backup_date = self.DEFAULT_SETTINGS['backup_date']
        self.file_size_bytes = self.DEFAULT_SETTINGS['file_size_bytes']
        self.file_checksum = self.DEFAULT_SETTINGS['file_checksum']
        self.file_checksum_method = self.DEFAULT_SETTINGS['file_checksum_method']
        self.encryption_key = self.DEFAULT_SETTINGS['encryption_key']
        self.s3_url = self.DEFAULT_SETTINGS['s3_url']
        self.s3_url_metadata = self.DEFAULT_SETTINGS['s3_url_metadata']
        self.metadata_filecontents = None
        return



    def set_filename(self, path=None):
        '''Given a path, set attributes filename, fullpath, md_filename.
        '''
        if path == None: return
        self.filename = os.path.basename(path)
        self.fullpath = os.path.realpath(path)
        self.metadata_filename = self.filename + '.meta'
        return



    def set_backup_source(self, backup_source=None):
        '''Set the backup source for the filename.
        '''
        self.log.debug('Setting "backup_source" to "{}"'.format(backup_source))
        self.backup_source = backup_source
        return



    def set_backup_date(self, backup_date=None):
        '''Set the backup date for the filename.
        '''
        if not backup_date:
            self.log.error('Backup date not set')
            return
        self.log.debug('Setting "backup_date" to "{}"'.format(backup_date))
        self.backup_date = backup_date
        return



    def add_file_stats(self):
        '''Add file stats to the metadata file.  These cannot be set manually.
        These include:
            file_size_bytes
            file_checksum
            file_checksum_method
        '''
        if not os.path.isfile(self.filename):
            raise Exception('File does not exist "{}"'.format(self.filename))
        self.log.debug('Adding file stats')
        self.file_size_bytes = os.path.getsize(self.fullpath)
        self.file_checksum_method = 'sha512'
        self._calculate_checksum()
        return



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
        self.file_checksum = '{}'.format(hasher.hexdigest())
        return



    def set_encryption_key(self, key_used=None):
        '''Set the value of the encryption key used on the file.
        '''
        self.log.debug('Setting "encryption_key" to "{}"'.format(key_used))
        self.encryption_key = key_used
        return



    def set_s3_url(self, url=None):
        '''Set the S3 URL for the file.
        '''
        self.log.debug('Setting "s3_url" to "{}"'.format(url))
        self.s3_url = url
        return



    def set_s3_url_metadata(self, url=None):
        '''Set the S3 URL for the metadata file.
        '''
        self.log.debug('Setting "s3_url_metadata" to "{}"'.format(url))
        self.s3_url_metadata = url
        return



    def format(self):
        '''Return JSON format of the metadata file.
        '''
        if self.filename == None: raise Exception('Filename not set')

        # Build the JSON file from the nested python dictionary.
        self.metadata_filecontents = {}

        stats = self.DEFAULT_SETTINGS
        stats['backup_source'] = self.backup_source
        stats['backup_date'] = self.backup_date
        stats['file_size_bytes'] = self.file_size_bytes
        stats['file_checksum'] = self.file_checksum
        stats['file_checksum_method'] = self.file_checksum_method
        stats['encryption_key'] = self.encryption_key
        stats['s3_url'] = self.s3_url
        stats['s3_url_metadata'] = self.s3_url_metadata

        self.metadata_filecontents[self.filename] = stats
        json_file_contents = json.dumps(self.metadata_filecontents,
                                        indent=4,
                                        sort_keys=True)
        return json_file_contents



    def write(self):
        full_md_filename = os.path.dirname(self.fullpath) + os.sep + (
            os.path.basename(self.metadata_filename))
        self.log.debug('Writing "{}"'.format(self.metadata_filename))
        with open(full_md_filename, 'w') as f:
            f.write(self.format())
        f.close()
        return



    def load(self, path=None):
        '''Load data from the referenced metadata file.  File format should match
        the DATA STRUCTURE in the class comments above.

        NOTE: The attribute fullpath is not set as only the basename for the
              original file sent to S3 is stored in the metadata file.
        '''
        with open(os.path.realpath(path), 'r') as f:
            md_contents = json.load(f)
        f.close()
        self.metadata_filename = os.path.basename(path)
        # Top level key is the filename.
        for k1 in md_contents.keys():
            self.set_filename(str(k1))
            for k2 in md_contents[k1].keys():
                if k2 == 'backup_source':
                    self.set_backup_source(md_contents[k1][k2])
                elif k2 == 'backup_date':
                    self.set_backup_date(md_contents[k1][k2])
                elif k2 == 'file_size_bytes':
                    self.file_size_bytes = int(md_contents[k1][k2])
                elif k2 == 'file_checksum':
                    self.file_checksum = md_contents[k1][k2]
                elif k2 == 'file_checksum_method':
                    self.file_checksum_method = md_contents[k1][k2]
                elif k2 == 'encryption_key':
                    self.set_encryption_key(md_contents[k1][k2])
                elif k2 == 's3_url':
                    self.set_s3_url(md_contents[k1][k2])
                elif k2 == 's3_url_metadata':
                    self.set_s3_url_metadata(md_contents[k1][k2])
        return




#=============================================================================#
# END
#=============================================================================#
