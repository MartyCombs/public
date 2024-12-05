# Create metadata files
Create JSON formatted metadata files for files and archives backed up to S3.
The information stored in the files ensures authenticity of the file when 
downloaded later.

**Metadata file contents**
```
{
    "testfile.txt": {
        "backup_date": "2024-12-05 01:52:16 -0600",
        "backup_source": "personal",
        "encryption_key": "GPG",
        "file_checksum": "bf9bac8036ea00445c04e3630148fdec15aa91e20b753349d9771f4e25a4f68c82f9bd52f0a72ceaff5415a673dfebc91f365f8114009386c001f0d56c7015de",
        "file_checksum_method": "sha512",
        "file_size_bytes": 21,
        "s3_url": "s3://BUCKET_NAME/PATH/testfile.txt",
        "s3_url_metadata": "s3://BUCKET_NAME/PATH/testfile.txt.meta"
    }
}
```

# Configuration
A configuration file - `metadata.cfg` - allows for configuration of several values
within the metadata file such as:

* backup_source
* encryption_key
* s3_url
* s3_url_metadata

The top level script - `create_metadata.sh` - also takes options which allow
overriding of settings in the configuration file.


# Code
__Running top level scripts with `--help` will list options available.__

* `create_metadata.sh` - Top level script to create the metadata files.
  - `create_metadata.py` - Called by `create_metadata.sh`.
  - `metadata_conf.py` - Python class which reads the configuration file.
  - `metadata.py` - Python class which does all the work.
* `create_mdconfig.py` - Creates the config file with default settings.
* `mylog.py` - Custom python logger class.


# Testing
`test_metadata.sh` - Runs tests of configuration file creation, and creation of 
a metadata file from a sample both with direct interaction with the class in
`metadata.py` and through options in `create_metadata.py` by passing options 
to the top level script `create_metadata.sh`.


