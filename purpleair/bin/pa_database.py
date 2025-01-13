#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import json
from psycopg2.extras import Json
from mylog import MyLog
from pg_database import PostgresDatabase


class PADatabase(object):
    '''
    '''
    def __init__(self, debug=False, loglevel='WARNING', noop=False):
        self.debug = debug
        self.loglevel = loglevel
        self.noop = noop
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log

        self.postgres = PostgresDatabase(debug=self.debug,
                                         loglevel=self.loglevel)
        self.insert_query = None
        return



    def check(self):
        '''Check that the database is running.
        '''
        return self.postgres.check()



    def add_purpleair_data(self, purpleair_data=None):
        '''Upload the parsed JSON file to the database.
        '''
        # Set mode to write.
        self.postgres.set_mode('WRITE')
        sql = '''INSERT INTO purple_air_1 (event_time, sensor_response) \n'''
        sql += '''VALUES (TO_TIMESTAMP(%s) AT TIME ZONE 'UTC', %s) \n'''
        sql += '''RETURNING id;'''
        self.insert_query = sql

        if self.noop == True:
            self.log.info('NO-OP set.  No action taken.')
            sys.stderr.write(
                'NO-OP: Would execute\n\n{}\n    with\n({},\n\n{})\n\n'.format(
                sql, purpleair_data.epoch, purpleair_data.data_struct))
            return

        new_id = self.postgres.exec(
            sql,
            (purpleair_data.epoch, Json(purpleair_data.data_struct)),
            fetch=True)
        if isinstance(new_id, list):
            self.log.info('Inserted row with ID {}'.format(new_id[0][0]))
        elif isinstance(new_id, bool) and new_id == False:
            self.log.error('Failed to insert')
            return False
        else:
            self.log.error('Unknown error')
            return False
        return



#=============================================================================#
# END
#=============================================================================#
