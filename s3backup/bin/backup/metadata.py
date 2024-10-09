#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import re
import time
import datetime
import hashlib
import progressbar
import json
from .mylog import MyLog

class MetaData(object):
    '''Manages the internal meta-data structure around backups of files to S3.

    ATTRIBUTES
        debug       (OPT: bool)    : Enable debug mode.
        logger      (OPT: inst)    : Instance of a logging class.
        loglevel    (OPT: str)     : Log level.
        progress    (OPT: bool)    : Enable progress bar.
        stats                      : Data structure of stats for filename.

    Data Structure for stats attribute:
        'filename_base' {
            'backup_source'        : Backup source.
            'backup_date'          : Date of last backup as 'Y-M-D H:M:S TZ'.
            'file_size_bytes'      : File size in bytes.
            'file_checksum'        : Checksum of backup file.
            'file_checksum_method' : Checksum method (SHA256, MD5, etc)
            's3_url'               : S3 URL of backup.
            's3_url_metadata'      : S3 URL of this meta-data structure.
        }

    METHODS
        init_file_stats            : Initialize file statistics.
        set_source                 : Set backup source.
        set_date                   : Set date for backup.
        add_file_stats             : Add file size and checksum.
        set_s3_url                 : Set S3 URL for backup file.
        set_s3_url_metadata        : Set S3 URL for metadata file.
        format                     : Return string with metadata file.
        load_file                  : Load a metadata file into memory.

    '''

    MDINIT = {
        'backup_source' : 'unknown',    # Backup source ('jira', ...).
        'backup_date' : None,           # Date of last backup as 'Y-M-D H:M:S TZ'.
        'file_size_bytes' : None,       # File size in bytes.
        'file_checksum' : None,         # Checksum of backup file.
        'file_checksum_method' : None,  # Checksum method (SHA256, MD5, etc)
        's3_url' : None,                # S3 URL of backup.
        's3_url_metadata' : None        # S3 URL of this meta-data structure.
    }
    BACKUP_SOURCES = [ 'personal', 'work' ]
    DEFAULT_SOURCE = 'personal'
    FILENAME = re.compile(r'^"([^"].*)"\s+\{')
    DATAPOINT = re.compile(r'^    "([^"].*)"\s+\:\s+"([^"].*)",{,1}$')
    SHOWPROGRESS = False



    def __init__(self, debug=None, loglevel='INFO', progress=False):
        self.debug = debug
        l = MyLog(program=__name__, debug=debug, loglevel=loglevel)
        self.log = l.log
        MetaData.SHOWPROGRESS = progress
        self.today = datetime.datetime.utcnow()
        self.stats = {}
        self.backup_regex = re.compile(r'.*_export_(\d{8})_(\d{6})_(\S+)\.zip')
        return



    def init_file_stats(self, filename=None, force=False):
        '''Initilize data structure for the file using the absolute
        file path as the key. Any relative path passed is converted to
        an absolute path.

        Args:
            filename       (REQ: str)  : File name. Absolute path not required.
            force          (OPT: bool) : Force initialization [DEF: False].
        '''
        if not filename:
            raise Exception('Filename not defined. Nothing to init.')
            return
        fullpath = os.path.abspath(filename)
        basename = os.path.basename(fullpath)
        if not os.path.isfile(fullpath):
            raise Exception('File not found "{}". Nothing to init.'.format(fullpath))
        if basename in self.stats.keys() and not force:
            self.log.warning('Stats for "{}" already initialized!  Use "force=True" to force reset of stats.'.format(basename))
            return
        self.stats[basename] = {}
        self.log.info('Initializing file stats for "{}".'.format(basename))
        for k in MetaData.MDINIT.keys():
            self.stats[basename][k] = MetaData.MDINIT[k]
        return



    def set_source(self, filename=None, backup_source=DEFAULT_SOURCE):
        '''Set the backup source for the filename.

        Args:
            filename       (REQ: str)  : File name. Absolute path not required.
            backup_source  (REQ: str)  : Source data. Value must be one of:
                                 {}

        '''.format(MetaData.BACKUP_SOURCES)
        if not filename:
            self.log.error('Filename not defined. Returning.')
            return
        if backup_source not in MetaData.BACKUP_SOURCES:
            self.log.warning('Source passed "{}" not located in list of known backup sources "{}".'.format(backup_source, MetaData.BACKUP_SOURCES))
        fullpath = os.path.abspath(filename)
        basename = os.path.basename(fullpath)
        self.log.debug('Setting "backup_source" for "{}" to "{}"'.format(basename,
                                                                         backup_source))
        self.stats[basename]['backup_source'] = backup_source
        return



    def set_date(self, filename=None, backup_date=None):
        '''Set the backup date for the filename.

        Args:
            filename       (REQ: str)  : File name. Absolute path not required.
            backup_date    (REQ: str)  : Date in the format 'YYYY-MM-DD HH:MM:SS TZ'

        '''
        if not filename:
            self.log.error('Filename not defined. Returning.')
            return
        if not backup_date:
            self.log.error('Filename not defined. Returning.')
            return
        fullpath = os.path.abspath(filename)
        basename = os.path.basename(fullpath)
        self.log.debug('Setting "backup_date" for "{}" to "{}"'.format(basename,
                                                                       backup_date))

        self.stats[basename]['backup_date'] = backup_date
        return



    def add_file_stats(self, filename=None):
        '''Add file stats - size, checksum, etc. - to the filename.

        Args:
            filename       (REQ: str)  : File name. Absolute path not required.
        '''
        fullpath = os.path.abspath(filename)
        if not os.path.isfile(fullpath):
            raise IOError('File not found "{}".'.format(filename))
        basename = os.path.basename(fullpath)
        if self.stats[basename] and self.stats[basename]['file_checksum']:
            self.log.error('File stats already seem to exist for "{}".'.format(basename))
            return
        self.log.debug('Adding file stats for "{}".'.format(basename))
        m = re.match(self.backup_regex, basename)
        if m:
            (d, t, tz) = m.group(1,2,3)
            (yr, mth, day) = re.match(r'^(\d\d\d\d)(\d\d)(\d\d)', d).group(1,2,3)
            (hr, min, sec) = re.match(r'^(\d\d)(\d\d)(\d\d)', t).group(1,2,3)
            self.stats[basename]['backup_date'] = '{}-{}-{} {}:{}:{} {}'.format(yr, mth, day, hr, min, sec, tz)
        else:
            self.log.debug('Filename "{}" failed to match a date.'.format(basename))
        self.stats[basename]['file_size_bytes'] = os.stat(os.path.abspath(filename)).st_size
        self.stats[basename]['file_checksum_method'] = 'sha512'
        self._calculate_checksum(fullpath=fullpath)
        return



    def _calculate_checksum(self, fullpath=None):
        basename = os.path.basename(fullpath)
        self.log.info('Calculating SHA512 sum of "{}".'.format(basename))
        readbuff = 65536
        hasher = hashlib.sha512()
        # Set up a progress bar to let the user know we're still doing something.
        progressmax = self.stats[basename]['file_size_bytes'] / readbuff
        if self.stats[basename]['file_size_bytes'] % readbuff > 0:
            progressmax += 1
        if MetaData.SHOWPROGRESS == True:
            widgets = [progressbar.ETA(),
                       ' ',
                       progressbar.Bar('=', '[', ']', ' '), ' ',
                                       progressbar.Percentage()]
            bar = progressbar.ProgressBar(widgets=widgets,
                                          maxval=progressmax,
                                          term_width=80).start()
        with open(fullpath, 'rb') as f:
            i = 0
            while True:
                buff = f.read(readbuff)
                if not buff: break
                hasher.update(buff)
                i = i + 1
                if MetaData.SHOWPROGRESS == True: bar.update(i)
        if MetaData.SHOWPROGRESS == True: bar.finish()
        self.stats[basename]['file_checksum'] = '{}'.format(hasher.hexdigest())
        return



    def set_s3_url(self, filename=None, s3_url=None):
        '''Set the S3 URL where the data is stored.

        Args:
           filename      (REQ: str): Filename.
           s3_url        (REQ: str): Full S3 URL to data.

        '''
        fullpath = os.path.abspath(filename)
        basename = os.path.basename(fullpath)
        self.log.debug('Setting "s3_url" for "{}" to "{}"'.format(basename,
                                                                  s3_url))

        self.stats[basename]['s3_url'] = s3_url
        return



    def set_s3_url_metadata(self, filename=None, s3_url_metadata=None):
        '''Set the S3 URL where the data is stored.

        Args:
           filename        (REQ: str): Filename.
           s3_url_metadata (REQ: str): Full S3 URL to metadata.

        '''
        fullpath = os.path.abspath(filename)
        basename = os.path.basename(fullpath)
        self.log.debug('Setting "s3_url_metadata" for "{}" to "{}"'.format(basename,
                                                                           s3_url_metadata))
        self.stats[basename]['s3_url_metadata'] = s3_url_metadata
        return



    def format(self, filename=None):
        '''Format the stats in JSON format for the file.  If
        filename is not specified, the stats for all files in the
        dictionary are returned.

        Args:
           filename      (OPT: str): Filename.

        '''
        if filename:
            fullpath = os.path.abspath(filename)
            basename = os.path.basename(fullpath)
            if basename not in self.stats.keys(): return
            basestats = { basename : self.stats[basename] }
            return(json.dumps(basestats, indent=4, sort_keys=True))
        else:
            return(json.dumps(self.stats, indent=4, sort_keys=True))
        return



    def load_file(self, filename=None, force=False):
        '''Load data from the referenced stats file.

        Args:
           filename     (REQ:  str): Filename.
           force        (OPT: bool): Force loading even if record exists.

        '''
        if not os.path.isfile(filename):
            self.log.error('File not found "{}".'.format(filename))
            return
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if re.match(MetaData.FILENAME, line):
                    name = re.match(MetaData.FILENAME, line).group(1)
                    if name not in self.stats.keys():
                        self.stats[name] = {}
                        continue
                    self.log.warning('In-memory dictionary already exists for file "{}" and force="{}".'.format(name,force))
                    if force == True:
                        self.log.warning('Overwriting with contents from "{}".'.format(filename))
                        self.stats[name] = {}
                    else:
                        self.log.info('Skipping file "{}".'.format(filename))
                if re.match(MetaData.DATAPOINT, line):
                    (k,v) = re.match(MetaData.DATAPOINT, line).group(1,2)
                    self.stats[name][k] = v
            f.close()
        return




#=============================================================================#
# END
#=============================================================================#
