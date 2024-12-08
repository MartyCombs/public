#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os

def prettynum(num):
    '''Given bytes, return a value in KB/MB/GB/TB.
    Only called if showprogress is False for the AWSS3.upload() method.
    '''
    KB = 1024
    MB = 1024 ** 2
    GB = 1024 ** 3
    TB = 1024 ** 4
    if int(num / TB) > 0:
        prettynum = '{:0.3f} TB'.format(num / TB)
    elif int(num / GB) > 0:
        prettynum = '{:0.3f} GB'.format(num / GB)
    elif int(num / MB) > 0:
        prettynum = '{:0.3f} MB'.format(num / MB)
    elif int(num / KB) > 0:
        prettynum = '{:0.3f} KB'.format(num / KB)
    else:
        prettynum = '{} B'.format(num)
    return prettynum

myfile = sys.argv[-1]
print('{}'.format(prettynum(os.path.getsize(myfile))))

#=============================================================================#
# END
#=============================================================================#
