#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import argparse
from mylog import MyLog
from s3_backup_conf import S3BackupConf


class S3BackupCommon(object):
    def __init__(self,
                 src_dir=None,
                 dst_dir=None):
        self.debug = False
        self.loglevel = 'WARNING'
        self.noop = False
        self.showprogress = False
        self.log = None
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        return



    def parse_arguments(self, description=None):
        parser = argparse.ArgumentParser(description=description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('--debug', action='store_true', default=False,
            help='Enable debug mode.')
        parser.add_argument('--loglevel', action='store', default='INFO',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='Log level.')
        parser.add_argument('--showprogress', action='store_true', default=False,
            help='Enable progress bar.')
        parser.add_argument('--noop', action='store_true',
            default=False,
            help='Take no action.  Enables debug.')

        args = parser.parse_args()

        # Adjust parameters based on settings of --noop and --debug.
        if args.noop == True: args.debug = True
        if args.debug == True: args.loglevel = 'DEBUG'

        # Update internal attributes based on arguments passed.
        self.debug = args.debug
        self.loglevel = args.loglevel
        self.noop = args.noop
        self.showprogress = args.showprogress

        program=__class__.__name__
        logclass = MyLog(program=program, debug=args.debug, loglevel=args.loglevel)
        self.log = logclass.log

        return args



    def get_clean_list(self, directory=None, extensions=['all']):
        '''Examine directory for files to process.  Exclude directories and
        special files.

        RETURN
                List of full paths to files.
        '''
        self.log.info('Examining "{}"'.format(directory))

        filelist = os.listdir(directory)
        cleaned_list = []

        report = 'Processing\n\nfrom {}\n'.format(directory)
        for f in filelist:
            ext = os.path.splitext(f)[1]
            fullpath = directory + os.sep + f
            # Exclude special files.
            if f == '.DS_Store':
                self.log.warning('Excluding special file {}'.format(fullpath))
            elif os.path.isfile(fullpath) and (
                'all' in extensions or ext in extensions):
                cleaned_list.append(fullpath)
                report += '        {}\n'.format(f)
            else:
                self.log.warning('Excluding {}'.format(f))
        self.log.debug('{}'.format(report))
        return cleaned_list



    def move_files(self, filelist=None):
        self.log.info('Moving files from "{}" to "{}"'.format(
            self.src_dir, self.dst_dir))
        report = 'Moved files\n\nfrom {}\nto   {}\n\n'.format(
            self.src_dir, self.dst_dir)
        for f in filelist:
            report += '        {}\n'.format(os.path.basename(f))

        if self.noop == True:
            self.log.debug('NO-OP: {}'.format(report))
            return

        self.log.debug('{}'.format(report))
        for f in filelist:
            src=f
            dst=self.dst_dir + os.sep + os.path.basename(f)
            os.rename(src, dst)
        return



    def clean_src(self):
        self.log.info('Purging "{}"'.format(self.src_dir))
        report = 'Purging files\n\nfrom {}\n'.format(self.src_dir)
        for f in os.listdir(self.src_dir):
            report += '        {}\n'.format(f)

        if self.noop == True:
            self.log.debug('NO-OP: {}'.format(report))
            return

        self.log.info('{}'.format(report))
        for f in os.listdir(self.src_dir):
            filename = self.src_dir + os.sep + f
            os.remove(filename)
        return



#=============================================================================#
# END
#=============================================================================#

