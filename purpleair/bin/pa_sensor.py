#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import requests
from mylog import MyLog

class PASensor(object):
    '''Interact with the Purple Air sensor.

    ATTRBUTES
        debug          Enable debug mode.

        loglevel       Set the python log level.
                       [DEF: 'warning']

        sensor        The Purple Air sensor to monitor.

    METHODS
        set_sensor     Set the Purple Air sensor to monitor.

        poll           Poll the Purple Air sensor.

    '''

    DEF_SENSOR='192.168.86.110'

    def __init__(self, debug=False, loglevel='WARNING', sensor=None):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=debug, loglevel=loglevel)
        self.log = l.log
        self.sensor = None
        self.set_sensor(sensor)
        return



    def set_sensor(self, sensor=None):
        '''Set the Purple Air sensor to monitor.  Using a method permits
        tests on the sensor before setting it such as pings.
        '''
        if sensor == None:
            self.sensor = PASensor.DEF_SENSOR
            return
        self.sensor = sensor
        return



    def poll(self, sensor=None):
        '''Poll the Purple Air sensor and return a JSON string for setting
        a python dictionary.
        '''
        if sensor != None:
            self.set_sensor(sensor)
        url = 'http://' + self.sensor + '/json'
        self.log.info('Polling {}'.format(url))
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception('Returned code {}:\n    {}'.format(r.status_code,
                                                               r.text))
        self.log.debug('Returning\n\n{}\n'.format(r.text))
        return r.json()



#=============================================================================#
# END
#=============================================================================#
