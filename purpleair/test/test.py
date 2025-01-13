#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
from pa_data import PAData
from pg_database import PostgresDatabase
from pa_database import PADatabase
from mylog import MyLog

TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
l = MyLog(program=__name__, debug=True)
log = l.log

log.debug('Testing class PAData')
pd = PAData(debug=True)
f = TOP_DIR + os.sep + 'test' + os.sep + '2024-12-29-05h05m09sUTC.json'
pd.load(f)
rpt = '{:<30} : {}\n'.format('DateTime', pd.datetime)
rpt += '{:<30} : {}\n'.format('Epoch', pd.epoch)
rpt += '{:<30} : {}\n'.format('Data Filename', pd.data_filename)
log.debug('Test result:\n{}'.format(rpt))

log.debug('Testing class PostgresDatabase')
pg = PostgresDatabase(debug=True, mode='READ')
rpt = '{:<30} : {}'.format('Database Mode', pg.mode)
log.debug('Test result:\n{}'.format(rpt))

log.debug('Testing select to database "purpleair"')
r1 = pg.exec(query='SELECT * FROM purple_air_1 LIMIT 2;', fetch=True)
rpt = '{:<30}\n{}'.format('QUERY RESULT', r1)
log.debug('Test result:\n{}'.format(rpt))
pg.close()

log.debug('Testing class PADatabase')
padb = PADatabase(debug=True)
r2 = padb.check()
rpt = '{:<30} : {}'.format('Database Check Result', r2)
log.debug('Test result:\n{}'.format(rpt))

sys.exit(0)



#=============================================================================#
# END
#=============================================================================#
