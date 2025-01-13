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
from pa_data import PAData
from pa_database import PADatabase
from mylog import MyLog

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='''
            ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--debug', action='store_true', default=False,
        help='Enable debug mode.')
    parser.add_argument('--loglevel', action='store', default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level.')
    parser.add_argument('--noop', action='store_true', default=False,
        help='Take no action.')
    parser.add_argument('filename', type=str, action='store', default=None,
        help='File to process.')
    return parser.parse_args()



args = parse_arguments()
l = MyLog(program=__name__, debug=args.debug, loglevel=args.loglevel)
log = l.log

# Load the data in the Purple Air JSON file.
log.info('Loading JSON data file.')
pd = PAData(debug=args.debug, loglevel=args.loglevel)
pd.load(args.filename)

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
