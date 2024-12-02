#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import boto3
import os
import math
from tqdm import tqdm
import threading
#from threading import Thread

class MultipartUpload:
    def __init__(self,
                 file_path,
                 bucket_name,
                 s3_key,
                 part_size=50 * 1024 * 1024,
                 num_threads=4):
        self.file_path = file_path
        self.bucket_name = bucket_name
        self.s3_key = s3_key
        self.part_size = part_size
        self.num_threads = num_threads

        self.s3 = boto3.client('s3')
        self.upload_id = None
        self.parts = []
        self.lock = threading.Lock()

    def initiate_multipart_upload(self):
        response = self.s3.create_multipart_upload(
            Bucket=self.bucket_name,
            Key=self.s3_key)
        self.upload_id = response['UploadId']
        print(f"Multipart upload initiated with UploadId: {self.upload_id}")

    def upload_part(self, part_number, data):
        try:
            response = self.s3.upload_part(
                Bucket=self.bucket_name,
                Key=self.s3_key,
                PartNumber=part_number,
                UploadId=self.upload_id,
                Body=data
            )
            with self.lock:
                self.parts.append({'PartNumber': part_number,
                                   'ETag': response['ETag']})
        except Exception as e:
            print(f"Error uploading part {part_number}: {e}")

    def complete_multipart_upload(self):
        self.parts.sort(key=lambda x: x['PartNumber'])
        self.s3.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=self.s3_key,
            UploadId=self.upload_id,
            MultipartUpload={'Parts': self.parts}
        )
        print(f"Upload completed successfully: s3://{self.bucket_name}/{self.s3_key}")

    def abort_multipart_upload(self):
        self.s3.abort_multipart_upload(
            Bucket=self.bucket_name,
            Key=self.s3_key,
            UploadId=self.upload_id)
        print(f"Multipart upload aborted.")

    def upload(self):
        file_size = os.path.getsize(self.file_path)
        total_parts = math.ceil(file_size / self.part_size)

        # Initialize progress bar
        progress_bar = tqdm(total=file_size,
                            unit='B',
                            unit_scale=True,
                            desc=self.file_path)

        # Initiate multipart upload
        self.initiate_multipart_upload()

        try:
            with open(self.file_path, 'rb') as file:
                threads = []
                for part_number in range(1, total_parts + 1):
                    data = file.read(self.part_size)
                    thread = threading.Thread(target=self.upload_part,
                                              args=(part_number, data))
                    threads.append(thread)
                    thread.start()

                    # Manage the thread pool size
                    if len(threads) >= self.num_threads:
                        for t in threads:
                            t.join()
                        threads = []

                    progress_bar.update(len(data))

                # Join any remaining threads
                for t in threads:
                    t.join()

            # Complete the multipart upload
            self.complete_multipart_upload()
        except Exception as e:
            self.abort_multipart_upload()
            print(f"Error occurred during upload: {e}")
        finally:
            progress_bar.close()

# Usage
file_path = '/Users/marty/srcbin/s3_upload/upload/test-archive.tar.gz.asc'
bucket_name = 'mcombs-backup'
s3_key = 'test/test-archive.tar.gz.asc'

uploader = MultipartUpload(file_path,
                           bucket_name,
                           s3_key,
                           part_size=50 * 1024 * 1024,
                           num_threads=4)
uploader.upload()

