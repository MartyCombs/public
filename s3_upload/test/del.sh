#!/usr/bin/env bash

aws s3 ls s3://mcombs-backup/test/
echo -n Delete?
read junk
for ii in Benny.jpg.asc \
          Benny.jpg.asc.meta \
          test-archive.tar.gz.asc \
          test-archive.tar.gz.asc.meta \
          test-archive.tar.gz.manifest.asc \
          test-archive.tar.gz.manifest.asc.meta
do
    aws s3 rm s3://mcombs-backup/test/${ii}
done
aws s3 ls s3://mcombs-backup/test/
