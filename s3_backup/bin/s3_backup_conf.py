#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import os
import configparser
from mylog import MyLog


class S3BackupConf(object):
    '''Manage S3 backup configuration file.

    ATTRIBUTES
        metadata_destination    Local destination for the metadata files.

        manifest_destination    Local destination for the manifest files
                                which list the contents of tar archives.
                                Archives are assumed to be compressed with
                                .tar.gz extension.

        drop_dir                Directory where files to be archived are
                                dropped.

        drop_script             Script to move files from drop directory to
                                begin the process.

        manifest_dir            Directory where manifest files for archives
                                are created.

        manifest_script         Script used to create the archive manifests.

        encrypt_dir             Directory where files are encrypted.

        encrypt_script          Script used to encrypt files.

        metadata_dir            Directory where metadata files are created.

        metadata_script         Script used to create metadata files.

        s3_upload_dir           Directory where files for upload to S3 are
                                placed.

        upload_script           Script used to upload files to S3.


    METHODS
        read                    Read the configuration file.

        print                   Print the configuration of parameters for
                                nice logging.

        build                   Build and return the configuration file for
                                writing.
    '''

    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    DEF_CONFIG_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 's3_backup.cfg'
    DEF_CONFIG = {
        'metadata_destination'     : 'meta',
        'manifest_destination'     : 'manifest',

        'drop_dir'                 : 'work/10-drop',
        'drop_script'              : 'bin/action_drop.py',

        'manifest_dir'             : 'work/20-tar_manifest',
        'manifest_script'          : 'bin/action_manifests.py',

        'encrypt_dir'              : 'work/30-encrypt',
        'encrypt_script'           : 'bin/action_encrypt.py',

        'metadata_dir'             : 'work/40-create_metadata',
        'metadata_script'          : 'bin/action_metadata.py',

        's3_upload_dir'            : 'work/50-s3_upload',
        'upload_script'            : 'bin/action_s3_upload.sh'
    }



    def __init__(self, debug=False, loglevel='WARNING'):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.top_dir = self.TOP_DIR
        self.filename = self.DEF_CONFIG_FILE

        # Config parameters
        self.metadata_destination = self.DEF_CONFIG['metadata_destination']
        self.manifest_destination = self.DEF_CONFIG['manifest_destination']
        self.drop_dir = self.DEF_CONFIG['drop_dir']
        self.drop_script = self.DEF_CONFIG['drop_script']
        self.manifest_dir = self.DEF_CONFIG['manifest_dir']
        self.manifest_script = self.DEF_CONFIG['manifest_script']
        self.encrypt_dir = self.DEF_CONFIG['encrypt_dir']
        self.encrypt_script = self.DEF_CONFIG['encrypt_script']
        self.metadata_dir = self.DEF_CONFIG['metadata_dir']
        self.metadata_script = self.DEF_CONFIG['metadata_script']
        self.s3_upload_dir = self.DEF_CONFIG['s3_upload_dir']
        self.upload_script = self.DEF_CONFIG['upload_script']
        return



    def read(self):
        '''Read the configuration file.
        '''
        self.log.debug('Reading {}'.format(self.DEF_CONFIG_FILE))
        cfg = configparser.RawConfigParser()
        cfg.read(self.DEF_CONFIG_FILE)
        self.metadata_destination = self._add_path(cfg.get(
            'DEFAULT', 'metadata_destination'))
        self.manifest_destination = self._add_path(cfg.get(
            'DEFAULT', 'manifest_destination'))

        self.drop_dir = self._add_path(cfg.get(
            'DEFAULT', 'drop_dir'))
        self.drop_script = self._add_path(cfg.get(
            'DEFAULT', 'drop_script'))

        self.manifest_dir = self._add_path(cfg.get(
            'DEFAULT', 'manifest_dir'))
        self.manifest_script = self._add_path(cfg.get(
            'DEFAULT', 'manifest_script'))

        self.encrypt_dir = self._add_path(cfg.get(
            'DEFAULT', 'encrypt_dir'))
        self.encrypt_script = self._add_path(cfg.get(
            'DEFAULT', 'encrypt_script'))

        self.metadata_dir = self._add_path(cfg.get(
            'DEFAULT', 'metadata_dir'))
        self.metadata_script = self._add_path(cfg.get(
            'DEFAULT', 'metadata_script'))

        self.s3_upload_dir = self._add_path(cfg.get(
            'DEFAULT', 's3_upload_dir'))
        self.upload_script = self._add_path(cfg.get(
            'DEFAULT', 'upload_script'))
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



    def print(self):
        '''Report on the details read from the configuration file.
        '''
        report = '{}\n'.format('='*76)
        report += '{:<25} {}\n'.format('metadata_destination',
                                       self.metadata_destination)
        report += '{:<25} {}\n'.format('manifest_destination',
                                       self.manifest_destination)
        report += '{:<25} {}\n'.format('drop_dir',
                                       self.drop_dir)
        report += '{:<25} {}\n'.format('drop_script',
                                       self.drop_script)

        report += '{:<25} {}\n'.format('manifest_dir',
                                       self.manifest_dir)
        report += '{:<25} {}\n'.format('manifest_script',
                                       self.manifest_script)

        report += '{:<25} {}\n'.format('encrypt_dir',
                                       self.encrypt_dir)
        report += '{:<25} {}\n'.format('encrypt_script',
                                       self.encrypt_script)

        report += '{:<25} {}\n'.format('metadata_dir',
                                       self.metadata_dir)
        report += '{:<25} {}\n'.format('metadata_script',
                                       self.metadata_script)

        report += '{:<25} {}\n'.format('s3_upload_dir',
                                       self.s3_upload_dir)
        report += '{:<25} {}\n'.format('upload_script',
                                       self.upload_script)

        report += '{}\n'.format('='*76)
        return report



    def build(self):
        '''Create the config file with all default values.
        '''
        div = '#{}#'.format('='*76)
        cfg = ''
        cfg += '{}\n'.format(div)
        cfg += '# Read by python ConfigParser\n'
        cfg += '{}'.format(self._conf_header())
        cfg += '\n'
        cfg += '[DEFAULT]\n'
        cfg += 'metadata_destination = {}\n'.format(self.metadata_destination)
        cfg += 'manifest_destination = {}\n'.format(self.manifest_destination)
        cfg += 'drop_dir = {}\n'.format(self.drop_dir)
        cfg += 'drop_script = {}\n'.format(self.drop_script)
        cfg += 'manifest_dir = {}\n'.format(self.manifest_dir)
        cfg += 'manifest_script = {}\n'.format(self.manifest_script)
        cfg += 'encrypt_dir = {}\n'.format(self.encrypt_dir)
        cfg += 'encrypt_script = {}\n'.format(self.encrypt_script)
        cfg += 'metadata_dir = {}\n'.format(self.metadata_dir)
        cfg += 'metadata_script = {}\n'.format(self.metadata_script)
        cfg += 's3_upload_dir = {}\n'.format(self.s3_upload_dir)
        cfg += 'upload_script = {}\n'.format(self.upload_script)
        cfg += '\n{}\n# END\n{}\n'.format(div, div)
        return cfg



    def _conf_header(self):
        header = ''
        header += '''#
# Configuration file for backups to S3.  Please read the documentation
# regarding the standard process for backing up files in the README.
#
# All directory paths which do not start with '/' are relative to the
# top level working directory:
#
#     {}
#       '''.format(self.TOP_DIR)
        header += '''
# metadata_destination         Local destination where metadata files are stored
#                              after the entire process is finished.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['metadata_destination'])
        header += '''
# manifest_destination         Local destination for the manifest files
#                              which list the contents of tar archives.
#
#                              See NOTES section about archives in the README.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['manifest_destination'])
        header += '''
# drop_dir                     Drop directory for files which need to be
#                              processed by the wrapper script.  This is the
#                              initial directory for the start of the backup
#                              process.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['drop_dir'])
        header += '''
# drop_script                  Script used to move files from drop directory.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['drop_script'])
        header += '''
# manifest_dir                 Manifests are created for archives located here.
#                              Once a manifest is successfully created, they
#                              are moved to the next directory.  Files are simply
#                              moved to the next directory in the process.
#
#                              See NOTES section about archives in the README.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['manifest_dir'])
        header += '''
# manifest_script              Script used to create the archive manifests.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['manifest_script'])
        header += '''
# encrypt_dir                  Files, archives, and manifest files - if present
#                              in this directory are encrypted.
#
#                              After successful encryption:
#
#                              * The original, unencrypted file is delete.
#
#                              * Any manifest files are moved to the next
#                                directory in the process.
#
#                              * Encrypted files are moved to the next
#                                directory in the process.
#
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['encrypt_dir'])
        header += '''
# encrypt_script               Script used to encrypt files.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['encrypt_script'])
        header += '''
# metadata_dir                 Files and archives located here will have metadata
#                              files created in JSON format for later locating
#                              the files in S3, determining their size, checksum,
#                              encryption key used, etc. on the file.
#
#                              Only encrypted manifest files will have metadata
#                              files created.  The unencrypted manifest files are
#                              assumed to be stored locally in a secure location.
#
#                              After successful creation of metadata files, all
#                              files are moved to the next directory in the process.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['metadata_dir'])
        header += '''
# metadata_script              Script used to create metadata files.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['metadata_script'])
        header += '''
# s3_upload_dir                Files and archives located here will be uploaded
#                              to the S3 bucket listed in the metadata file for
#                              that file or archive.
#
#                              After successful upload to S3:
#
#                              * The original file or archive will be deleted.
#
#                              * Any pretaining unencrypted manifest - if one
#                                exists - will be moved to the directory defined
#                                in the 'manifest_destination' config variable.
#
#                              * All metadata files are moved to the directory
#                                defined in the 'metadata_destination' config
#                                variable.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['s3_upload_dir'])
        header += '''
# upload_script                Script used to upload files to S3.
#                              [DEFAULT: {}]
#       '''.format(self.DEF_CONFIG['upload_script'])
        return header



#=============================================================================#
# END
#=============================================================================#
