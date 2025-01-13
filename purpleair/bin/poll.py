#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import json
import argparse
from pa_sensor import PASensor
from pa_data import PAData
from pa_database import PADatabase
from mylog import MyLog

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='''Poll the Purple Air sensor and write out the data
            to a JSON formatted file.
            ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--debug', action='store_true', default=False,
        help='Enable debug mode.')
    parser.add_argument('--loglevel', action='store', default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--noop', action='store_true', default=False,
        help='Take no action.')
    return parser.parse_args()


args = parse_arguments()
l = MyLog(program=__name__, debug=args.debug, loglevel=args.loglevel)
log = l.log

log.info('Polling Purple Air sensor')
sensor = PASensor(debug=args.debug, loglevel=args.loglevel)
pd = PAData(debug=args.debug, loglevel=args.loglevel)
pd.process(sensor.poll())


if args.noop == True:
    log.info('NO-OP: Would write to "{}"\n\n{}\n\n'.format(pd.data_filename,
                                                           pd.data_struct))
else:
    pd.write()
log.info('Wrote datafile')

# Write the data to a database.
padb = PADatabase(debug=args.debug, loglevel=args.loglevel, noop=args.noop)
if padb.check() == False:
    log.error('Could not connect to database')
    sys.exit(1)

result = padb.add_purpleair_data(pd)
if result == False:
    log.error('Failed to upload file data to database')
    sys.exit(1)
log.info('Uploaded data to database')
sys.exit(0)



#=============================================================================#
# END
#=============================================================================#
