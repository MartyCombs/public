#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import sys
import os
import json
#import boto3
#from botocore.exceptions import ClientError
from datetime import datetime
from aws_s3 import AWSS3
from mylog import MyLog

def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string
    raise TypeError(f"Type {type(obj)} not serializable")
    return
def dump(struct=None):
    '''Dumps a dictionary to the screen.
    '''
    if struct and type(struct) is dict:
        return json.dumps(struct, indent=4, sort_keys=True)
    return  None

s3c_sess = AWSS3(debug=True)
s3 = s3c_sess.get_client()
r1 = s3.list_buckets()

resp = json.dumps(r1, indent=4, default=custom_serializer)
print('{}'.format(r1))
print('{}'.format(resp))

#response = s3_client.upload_file(file_name, bucket, object_name)



#=============================================================================#
# END
#=============================================================================#
