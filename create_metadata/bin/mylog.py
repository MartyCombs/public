#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create_metadata/bin/mylog.py
#=============================================================================#
import sys
import logging
import platform

# Subclass logging.Filter to include the platform hostname within log
# lines.  This is necessary in a centralized logging environment.
class HostnameFilter(logging.Filter):
    def filter(self, record):
        record.hostname = platform.node()
        return True


# Create my own formatted logger.
class MyLog(object):
    '''Template for doing logging through python modules.

    ATTRIBUTES
        debug      : Enable more verbose logging for debug mode.
                     This automatically sets attribute loglevel='DEBUG'
                     [DEFAULT: False]

        loglevel   : Permits passing a different logger.
                     [DEFAULT: 'WARNING']
    '''

    FORMATTER_BASIC = logging.Formatter(
        fmt='[%(asctime)s] %(hostname)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z')
    FORMATTER_DEBUG = logging.Formatter(
        fmt='DEBUG: [%(asctime)s] %(hostname)s %(filename)s(%(process)d) %(levelname)s [%(name)s.%(funcName)s()] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z')

    def __init__(self, program=None, debug=False, loglevel='WARNING'):
        loglevel = loglevel.upper()
        if loglevel == 'DEBUG': debug=True
        if debug == True: loglevel = 'DEBUG'
        if not program: program=__class__.__name__
        self.program = program
        self.debug = debug
        self.loglevel = loglevel
        self.log = logging.getLogger(program)

        if not self.log.hasHandlers():
            stderrh = logging.StreamHandler(stream=sys.stderr)
            stderrh.addFilter(HostnameFilter())
            if self.debug == True:
                stderrh.setFormatter(MyLog.FORMATTER_DEBUG)
            else:
                stderrh.setFormatter(MyLog.FORMATTER_BASIC)
            self.log.setLevel(getattr(logging, self.loglevel))
            self.log.addHandler(stderrh)
        return



#=============================================================================#
# END
#=============================================================================#
