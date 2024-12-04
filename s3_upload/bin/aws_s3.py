#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import os
import math
from aws_conf import AWSConf
import boto3
from botocore.exceptions import ClientError
from tqdm import tqdm
from mylog import MyLog

# Extras for multipart upload.
import threading
from boto3.s3.transfer import TransferConfig



class ProgressPercentage(object):
    '''Class called by "Callback" parameter in the BOTO3 S3 client.  The tqdm
    class is used to display a simple upload bar if the showprogress
    parameter is True when calling the AWSS3.upload() method.
    '''
    def __init__(self, filename):
        self._filename = os.path.basename(filename)
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._tqdm = tqdm(total=self._size,
                          ascii=" >>>>>>>>>=",
                          unit='B',
                          unit_scale=True,
                          desc=self._filename)
        # Thread locking only needed with multipart upload.
        self._lock = threading.Lock()
        return

    def __call__(self, bytes_amount):
        ''' Update progress bar.  Thread locking only needed with
        multipart upload.
        '''
        with self._lock:
            self._seen_so_far += bytes_amount
            self._tqdm.update(bytes_amount)
        return

    def close(self):
        self._tqdm.close()



class AWSS3(object):
    '''Create AWS BOTO3 S3 connections - both client and resoure.

    S3 client connections are used for files smaller than MP_THRESHOLD
    as defined in the configuration file - AWSS3.DEF_CREDS_FILE.

    S3 resource connections with multipart upload and threading are
    used for files larger than MP_THRESHOLD.

    ATTRIBUTES
        debug              Debug mode.

        loglevel           Log level.

    METHODS
        get_client         Return the BOTO3 S3 client.

        get_resource       Return the BOTO3 S3 resource.

        connect            Connect to S3 both client and resource.

        bucket_exists      Return True if bucket exists.
                           False otherwise.

        prettyprint        Return a formatted number.

        upload             Upload a file to S3.

    '''

    TOP_DIR = str(os.sep).join(os.path.realpath(__file__).split(os.sep)[:-2])
    DEF_CREDS_FILE = TOP_DIR + os.sep + 'etc' + os.sep + 'aws_s3_creds.cfg'

    def __init__(self, debug=None, loglevel='WARNING'):
        self.debug = debug
        self.loglevel = loglevel
        program=__class__.__name__
        l = MyLog(program=program, debug=self.debug, loglevel=self.loglevel)
        self.log = l.log

        # Config settings.
        self.cfg = AWSConf(debug=self.debug, loglevel=self.loglevel)
        self.cfg.read()

        self.client = None
        self.resource = None
        self._bucketlist = None
        return



    def get_client(self):
        '''Return the BOTO S3 client.  If one does not exist, connect first.
        '''
        if self.client == None: self.connect()
        return self.client



    def get_resource(self):
        '''Return the BOTO S3 resource.  If one does not exist, connect first.
        '''
        if self.resource == None: self.connect()
        return self.resource



    def connect(self):
        '''Connect to S3 using credentials stored in a separate file.
        Immediately clear the values for the access and secret keys as
        soon as a client and resource are obtained.
        '''
        creds = self._read_credentials()
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                region_name=creds['aws_region_name']
                )

            self.resource = boto3.resource(
                's3',
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                region_name=creds['aws_region_name']
                )
        finally:
            # Clear out the information about the keys as soon as a
            # connection to AWS is made.
            region = creds['aws_region_name']
            access_key = '...' + creds['aws_access_key_id'][-5:-1]
            secret_key = '...' + creds['aws_secret_access_key'][-5:-1]
            del(creds)
        self.log.debug(
            'Connected to S3 region {} using key "{}" and secret "{}"'.format(
            region, access_key, secret_key))
        self.log.debug('Multipart uploads settings:\n{}'.format(self.cfg.print()))
        return

    def _read_credentials(self):
        '''Read S3 information from a simple KEY=VALUE formatted file.
        '''
        with open(self.DEF_CREDS_FILE, 'r') as f:
            lines = f.readlines()
        f.close()
        credentials = {}
        for line in lines:
            if line[0] == '#': continue
            key, value = line.strip().split('=')
            credentials[key.strip()] = value.strip()
        return credentials



    def bucket_exists(self, bucket_name=None):
        '''Return True if the bucket exists, otherwise return False.
        '''
        self.log.debug('Checking for bucket {}'.format(bucket_name))
        if self._bucketlist == None: self._build_bucket_list()
        if bucket_name in self._bucketlist: return True
        return False

    def _build_bucket_list(self):
        if self.client == None: self.connect()
        resp = self.client.list_buckets()
        self._bucketlist = []
        for bucket in resp['Buckets']:
            self._bucketlist.append(bucket['Name'])
        return



    def prettyprint(self, num=None):
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




    def upload(self, srcfile=None, bucket=None, key=None, showprogress=False):
        '''Upload a file to S3 through a single stream.  Show progress if requested
        (i.e. showprogress=True) using the ProgressPercentage class.
        '''

        # If file size is larger than 'mp_threshold' in the config, use
        # multipart upload with threading instead.
        if os.path.getsize(srcfile) > self.cfg.mp_threshold:
            response = self._mp_upload(srcfile=srcfile,
                                       bucket=bucket,
                                       key=key,
                                       showprogress=showprogress)
            return response

        if self.client == None: self.connect()
        size_bytes = os.path.getsize(srcfile)
        s3_url = 's3://{}/{}'.format(bucket, key)

        if showprogress == True:
            progress = ProgressPercentage(srcfile)
        else:
            self.log.info('Uploading\n    {} ({}) --> {}'.format(
                os.path.basename(srcfile),
                self.prettyprint(size_bytes),
                s3_url))

        try:
            if showprogress == True:
                response = self.client.upload_file(srcfile,
                                                   bucket,
                                                   key,
                                                   Callback=progress)
            else:
                response = self.client.upload_file(srcfile,
                                                   bucket,
                                                   key)
        except ClientError as e:
            raise Exception(e)
        finally:
            if showprogress == True:
                progress.close()
            else:
                self.log.debug('Successfully uploaded {} to {}'.format(
                    os.path.basename(srcfile), s3_url))
        return



    def _mp_upload(self, srcfile=None, bucket=None, key=None, showprogress=False):
        '''Upload a file to S3 using multipart upload with threading.

        Show progress using tqdm if requested (i.e. showprogress=True).
        '''
        if self.resource == None: self.connect()
        size_bytes = os.path.getsize(srcfile)
        config = TransferConfig(multipart_threshold=self.cfg.mp_threshold,
                                max_concurrency=self.cfg.max_concurrency,
                                multipart_chunksize=self.cfg.mp_chunksize,
                                use_threads=True)
        s3_url = 's3://{}/{}'.format(bucket, key)

        if showprogress == True:
            progress = ProgressPercentage(srcfile)
        else:
            self.log.info(
                'Uploading via multipart upload\n    {} ({}) --> {}'.format(
                os.path.basename(srcfile),
                self.prettyprint(size_bytes),
                s3_url))

        try:
            if showprogress == True:
                response = self.resource.meta.client.upload_file(
                    srcfile,
                    bucket,
                    key,
                    Config=config,
                    Callback=progress)
            else:
                response = self.resource.meta.client.upload_file(
                    srcfile,
                    bucket,
                    key,
                    Config=config)
        except ClientError as e:
            raise Exception(e)
        finally:
            if showprogress == True:
                progress.close()
            else:
                self.log.debug('Successfully uploaded {} to {}'.format(
                    os.path.basename(srcfile), s3_url))
        return



#=============================================================================#
# END
#=============================================================================#
