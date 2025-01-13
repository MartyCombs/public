#!/usr/bin/env python3

import sys
import json
import time
from datetime import datetime

'''
{
  "DateTime": "2025/01/04T22:30:00z",
  "response_date": 1736029729,
}
'''

json_file = sys.argv[1]
with open(json_file, 'r') as f:
    sensor_data = json.load(f)
f.close()


epoch = int(sensor_data['response_date'])
printed_time = time.strftime('%Y/%m/%dT%H:%M:%Sz',
                             time.gmtime(epoch))
rpt = '''
File          : "{}"
DateTime      : "{}"
response_date : "{}"
'''.format(json_file,
           sensor_data['DateTime'],
           printed_time)
print(rpt)
