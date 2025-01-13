#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
from datetime import datetime
import json
from mylog import MyLog


class PAData(object):
    '''Process the JSON formatted data from the Purple Air sensor.

    ATTRIBUTES
        debug          Enable debug mode.

        loglevel       Set the python log level.
                       [DEF: 'warning']

        epoch          Epoch seconds stored as datetime.timestamp().

        datetime       Date time within the file.

        data_dir       Top level directory where backup copy of JSON
                       data files are stored.

        data_filename  Full path to the JSON data file.

        data_struct    Dictionary of JSON formatted data.

    METHODS
        process        Process the JSON formatted data structure creating
                       the full path to the data file (PAData.data_filename),
                       epoch timestamp (PAData.epoch), and storing the
                       dictionary in memory (PAData.data_struct).

        write          Write the processed data to a file.

        load           Load the JSON formatted data file and process it with
                       process().

    '''
    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    def __init__(self, debug=False, loglevel='WARNING'):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log

        self.epoch = None
        self.datetime = None
        self.data_dir = PAData.TOP_DIR + os.sep + 'sensor_data'
        self.data_filename = None
        self.data_struct = {}
        return



    def process(self, struct=None):
        '''Read and store the JSON formatted data from the Purple Air sensor.
        The name of the JSON data file to write will be based on "DateTime"
        field within the JSON data.

        Epoch seconds are also extracted from "DateTime" and will be used
        as a unique key within a database store to avoid duplicate data.

        The path to the JSON data file will be:

            ${DATA_DIR}/YYYY/mm/dd/YYYYmmddTHHhMMmSSsUTC.json

        '''
        if struct == None or not isinstance(struct, dict):
            raise Exception('No structure passed.')

        self.log.info('Processing dictionary')
        self.log.debug('Processing\n\n{}\n'.format(struct))
        self.data_struct = struct

        poll_date = datetime.strptime(struct['DateTime'], '%Y/%m/%dT%H:%M:%Sz')
        self.datetime = poll_date
        self.epoch = int(poll_date.timestamp())

        year = poll_date.strftime("%Y")
        month = poll_date.strftime("%m")
        day = poll_date.strftime("%d")
        mytime = poll_date.strftime("%Y-%m-%d-%Hh%Mm%SsUTC")
        self.data_filename = self.data_dir + os.sep + (
            year + os.sep + month + os.sep + day) + (
            os.sep + mytime + '.json')
        return



    def write(self):
        '''Write the processed JSON data to the backup data file.
        '''
        if (
            self.data_filename == None
            or self.epoch == None
            or len(self.data_struct.keys()) == 0
        ):
            raise Exception('No data to write.  Did you run process() first?')

        self.log.info('Writing "{}"'.format(self.data_filename))
        prepath = os.path.dirname(self.data_filename)
        if not os.path.exists(prepath):
            self.log.debug('Creating directories "{}"'.format(prepath))
            os.makedirs(prepath)
        with open(self.data_filename, 'w') as f:
            f.write(json.dumps(self.data_struct, indent=4))
        f.close()
        return



    def load(self, filename=None):
        '''Load the JSON formatted backup data file into the internal data
        structure.
        '''
        if filename == None:
            raise Exception('No filename to read!')

        self.log.info('Loading "{}"'.format(filename))
        with open(filename, 'rb') as f:
            self.process(json.load(f))
        f.close()

        # Warn if the file loaded is outside the standard storage location
        # for the JSON data files from the Purple Air sensor.
        if os.path.realpath(filename) != self.data_filename:
            msg = 'File being uploaded is outside the normal data directory\n'
            msg += '    {:<15} : {}\n'.format('Datafile Name',
                                              self.data_filename)
            msg += '    {:<15} : {}'.format('Loaded File',
                                            os.path.realpath(filename))
            self.log.warning(msg)
        return



#=============================================================================#
# END
#=============================================================================#
