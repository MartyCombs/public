# Upload files to S3.
Upload files to S3.  Small files use the BOTO3 S3 client.  Large file use the
BOTO3 S3 resource with multipart upload and threading.

Top level scripts pass all options to lower level, sub-scripts.

The top script assumes `create_metadata` was used to generate JSON formatted
metadata files with `.meta` extension before uploading to S3.  
__See documentation regarding create_metadata.__

Given a series of metadata files - ending in `.meta`, the script parses each
JSON formatted file extracting bucket and key where those files will be stored 
in S3 with parameters defining where they will be uploaded.

* `s3_url` - Defines where the file will be uploaded.
* `s3_url_metadata` - Defines where the metadata file will be uploaded.

Both parameters will follow the format `s3://BUCKET/KEY`.

Both the file and metadata file are assumed to be named **exactly** the same 
except that the metadata file will have `.meta` file name extension.

Because this script uses the class `metadata.py` within `create_metadata` to
parse the metadata files.  This other script should be included within the
top level of this code - at the same level as `bin`, `etc`, and `test`.

Wrapper scripts update the python path with this assumption in mind.

# Configuration
* `aws_s3.cfg` - Configuration file with parameters related to multipart upload.
* `aws_s3_creds.cfg` - Stores the AWS region, access key, and secret key with
write permissions to the S3 buckets for the upload.

**Secure access to `aws_s3_creds.cfg` as anyone reading the contents of this
file can write to the S3 buckets.**


# Code
__Running top level scripts with `--help` will list options available.__

* `upload.sh` - Top level script to upload multiple files to S3.
  - `upload.py` - Called by `upload.sh`.
  - `aws_s3.py` - Python class with does all the work.

* `aws_conf.py` - Class used to read the configuration file and pass values
on to python scripts.
* `create_aws_conf.py` - Creates the config file with default settings.
* `mylog.py` - Custom python logger class.
* `create_metadata/bin/metadata.py` - Class used to parse the `.meta` files.
This is a **critical** dependency for the top level script to successfully 
function.


# Testing
`test_aws.sh` - Runs rudimentary tests of scripts associated with the configurtaion
file and tests connectivity to S3 using the credentials in `aws_s3_creds.cfg`.
No uploads are performed.


# ToDo
* Add downloading of files from S3.

