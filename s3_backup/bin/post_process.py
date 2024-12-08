#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import os
from mylog import MyLog
from metadata import MetaData

class PostProcess(object):
    '''After successful upload to S3, manifest files and metadata files are
    moved to a subdirectory on the local filesystem based on settings of
    'manifest_destination' and 'metadata_destination' in the configuration file.

    The local filesystem location mirrors the values of 's3_url' for manifest
    files and 's3_url_metadata' for metadata files.

    MANIFEST FILES
        manifest_destination = /path/to/manifests
        s3_url = s3://BUCKET/long/path/archive.tar.gz.manifest.enc

        Results in a final location on the local filesystem of

        /path/to/manifests/BUCKET/long/path/archive.tar.gz.manifest

        Where the original, unencrypted manifest file is stored (note the
        missing '.enc').


    METADATA
        metadata_destination = /path/to/metadata
        s3_url_metadata = s3://BUCKET/long/path/archive.tar.gz.enc.meta

        Results in a final location on the local filesystem of

        /path/to/metadata/BUCKET/long/path/archive.tar.gz.enc.meta

    '''
    ACCEPTED_TYPES = ['metadata', 'manifest']
    def __init__(self,
                 debug=False,
                 loglevel='WARNING',
                 manifest_src_files=None,
                 metadata_src_files=None,
                 manifest_destination=None,
                 metadata_destination=None):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log

        self.mani_dest = manifest_destination
        self.meta_dest = metadata_destination

        # Dictionary of source_fullpath.meta -> dest_fullpath.meta
        # where dest_fullpath.meta matches the S3 BUCKET/KEY
        self.meta_files = {}
        for f in metadata_src_files:
            self.meta_files[f] = None

        # Dictionary of source_fullpath.manifest -> dest_fullpath.manifest
        # where dest_fullpath.manifest matches the S3 BUCKET/KEY
        self.mani_files = {}
        for f in manifest_src_files:
            self.mani_files[f] = None

        rpt = 'Initialized\n'
        rpt += '    {:<25} {}\n'.format('File Type', 'Count')
        rpt += '    {:<25} {}\n'.format('-'*25, '-'*10)
        rpt += '    {:<25} {}\n'.format('manifest files',
                                        len(self.mani_files.keys()))

        rpt += '    {:<25} {}\n'.format('metadata files',
                                        len(self.meta_files.keys()))
        self.log.debug(rpt)
        return



    def build(self):
        '''Build the list of final locations where manifest and metadata files
        will be stored on the local filesystem.
        '''
        for mdf in self.meta_files.keys():
            md = MetaData(debug=self.debug, loglevel=self.loglevel)
            md.load(mdf)

            # Determining placement of the metadata file is easier.
            # Final location for the metadata file will mirror the path
            # in S3 minus the leading 's3://' - BUCKET/KEY.
            sub_path = str(os.sep).join(md.s3_url_metadata.split('/')[2:])
            self.meta_files[mdf] = self.meta_dest + os.sep + sub_path

            # Then check whether this metadata file refers to a manifest file
            # which is also stored locally.
            self._check_for_manifest_file(md)


    def _check_for_manifest_file(self, md):
        '''If this loaded metadata file refers to a manifest file, extract
        the filesystem destination of the manifest file from 's3_url' without
        the encryption extension and add that to the list of manifest files
        to be relocated.
        '''
        if 'manifest' not in md.filename.split('.'): return
        # Split along the '/' first to drop 's3://'.
        sub_path = str(os.sep).join(md.s3_url.split('/')[2:])

        # Then split along the '.' to drop the encryption extension at the end
        # of the manifest file.
        sub_path = '.'.join(sub_path.split('.')[:-1])

        # Look for the file within the manifest files to move and add
        # the destination.
        for f in self.mani_files.keys():
            if os.path.basename(sub_path) == os.path.basename(f):
                self.mani_files[f] = self.mani_dest + os.sep + sub_path
        return



    def prep(self, noop):
        '''Create the destination directories if necessary.  Use dictionary
        keys to avoid duplicates.
        '''
        dest_dirs = {}
        for f in self.meta_files.keys():
            dest_dirs[os.path.dirname(self.meta_files[f])] = None
        for f in self.mani_files.keys():
            dest_dirs[os.path.dirname(self.mani_files[f])] = None

        for d in dest_dirs.keys():
            if not os.path.exists(d):
                if noop == True:
                    self.log.debug(
                        'NO-OP: Would create directory\n\n    "{}"\n'.format(d))
                else:
                    os.makedirs(d)
        return



    def process(self, noop):
        '''Move both manifest files and metadata files to their final locations.
        '''
        src_dir = os.path.dirname(list(self.mani_files.keys())[0])
        self.log.info('Moving manifest files from "{}" to "{}"'.format(
            src_dir, self.mani_dest))
        report = 'Moved files\n\nfrom {}\nto   {}\n\n'.format(
            src_dir, self.mani_dest)
        for f in self.mani_files.keys():
            report += '        {}\n'.format(os.path.basename(f))
        if noop == True:
            self.log.debug('NO-OP: {}'.format(report))
        else:
            self.log.debug('{}'.format(report))
            for f in self.mani_files.keys():
                os.rename(f, self.mani_files[f])

        src_dir = os.path.dirname(list(self.meta_files.keys())[0])
        self.log.info('Moving metadata files from "{}" to "{}"'.format(
            src_dir, self.meta_dest))
        report = 'Moved files\n\nfrom {}\nto   {}\n\n'.format(
            src_dir, self.meta_dest)
        for f in self.meta_files.keys():
            report += '        {}\n'.format(os.path.basename(f))
        if noop == True:
            self.log.debug('NO-OP: {}'.format(report))
        else:
            self.log.debug('{}'.format(report))
            for f in self.meta_files.keys():
                os.rename(f, self.meta_files[f])
        return



#=============================================================================#
# END
#=============================================================================#
