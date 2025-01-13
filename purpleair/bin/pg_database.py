#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import psycopg2
from mylog import MyLog


class PostgresDatabase(object):
    '''Wrapper around psycopg2 for managing data in Postgres for the Purple Air
    Sensor.

    ATTRIBUTES
        debug          Enable debug mode.

        loglevel       Set the python log level.
                       [DEF: 'WARNING']

        mode           ['READ', 'WRITE']
                       Determines whether to add data to the database or
                       only read it.


    METHODS
        set_mode       Set the database mode for reading or writing.
                       Accepts ['READ', 'WRITE']
                       [DEF: 'READ']

        check          Check whether the database is running and that we
                       can connect to it.

        exec           Execute the query aginst the Purple Air database.

        close          Close the database connection.

    '''
    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    READ_CONF_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 'pa_dbread.cfg'
    WRITE_CONF_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 'pa_dbwrite.cfg'
    PERMITTED_MODES = ['READ', 'WRITE']

    def __init__(self, debug=False, loglevel='WARNING', mode=None):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.mode = None
        self._conn = None
        self._cur = None
        self.set_mode(mode)
        return



    def set_mode(self, mode=None):
        '''Set the database mode READ or WRITE.  This setting determines
        the database username/password used to connect.  The user running
        this code will have to have read permissions on the file containing
        this information.
        '''
        if mode == None:
            self.mode = 'READ'
            return
        if mode not in PostgresDatabase.PERMITTED_MODES:
            raise Exception('Unknown mode "{}"'.format(mode))
        self.mode = mode
        self.log.debug('Mode set to {}'.format(self.mode))
        return



    def check(self):
        '''Check that the database is running by attempting to connect to it
        using the read only user.
        '''
        origmode = self.mode
        self.set_mode('READ')
        conf = self._read_config()
        try:
            conn = psycopg2.connect(dbname=conf['dbname'],
                                     user=conf['user'],
                                     password=conf['password'],
                                     host=conf['host'],
                                     port=conf['port'])
        except psycopg2.OperationalError:
            self.log.error('Failed to  connect to database')
            return False
        finally:
            self.log.debug('Connected to database "{}" in {} mode'.format(
                conf['dbname'], self.mode))
            del(conf)
            self.set_mode(origmode)
        return True



    def _connect(self):
        '''Create a database connection using the credentials associated with
        the mode.  Information related to the connection is removed from
        memory immediately following a successful connection.
        '''
        conf = self._read_config()
        try:
            self._conn = psycopg2.connect(dbname=conf['dbname'],
                                         user=conf['user'],
                                         password=conf['password'],
                                         host=conf['host'],
                                         port=conf['port'])
        except psycopg2.Error as e:
            self.log.error('Failed to connect to database\n\n{}'.format(e))
            raise
        finally:
            self.log.info('Connected to database "{}"'.format(conf['dbname']))
            self.log.debug('Connected to database "{}" in {} mode'.format(
                conf['dbname'], self.mode))
            del(conf)
        return



    def _get_cursor(self):
        '''Get a cursor to the database.
        '''
        if not isinstance(self._conn, psycopg2.extensions.connection):
            self._connect()
        self.log.info('Getting cursor')
        self._cur = self._conn.cursor()
        return



    def exec(self, query=None, params=None, fetch=False):
        '''Execute the query with parameters.  Any errors will envoke a
        rollback.

        PARAMETERS
            query      The parameterized SQL to execute.

            params     Values for any parameters in the SQL query.

            fetch      If fetching data, True.
                       [DEF: False]

        '''
        if not isinstance(self._cur, psycopg2.extensions.cursor):
            self._get_cursor()
        self.log.info('Executing {}'.format(query.split(' ', 1)[0]))
        rpt = 'Attempting to execute\n\n'
        rpt += 'QUERY:\n{}\n\n'.format(query)
        rpt += 'PARAMS:\n{}\n'.format(params)
        self.log.debug(rpt)
        try:
            with self._conn.cursor() as cur:
                cur.execute(query, params)
                if fetch == True:
                    resp = cur.fetchall()
                    self._conn.commit()
                    return resp
                self._conn.commit()
        except psycopg2.errors.UniqueViolation:
            self.log.error('Row already exists')
            self._conn.rollback()
            return False
        except psycopg2.Error as e:
            # Rollback transactions on error.
            self._conn.rollback()
            self.log.error('Error on query execution\n\n{}'.format(e))
            raise
        return



    def _read_config(self):
        '''Read PostgreSQL configuration from a simple KEY=VALUE formatted file.
        There are different configuration files for reading versus writing.
        '''
        if self.mode == 'WRITE':
            config_file = PostgresDatabase.WRITE_CONF_FILE
        elif self.mode == 'READ':
            config_file = PostgresDatabase.READ_CONF_FILE
        else:
            raise Exception('Unknown mode')
        self.log.debug('Opening "{}"'.format(config_file))
        with open(config_file, 'r') as f:
            lines = f.readlines()
        f.close()
        config = {}
        for line in lines:
            if line[0] == '#': continue
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
        return config



    def close(self):
        '''Close the database connection.
        '''
        self.log.debug('Closing database connection')
        self._conn.close()
        return



#=============================================================================#
# END
#=============================================================================#
