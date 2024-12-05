#!/usr/bin/env bash
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create_metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create_metadata/test/test_metadata.sh
#=============================================================================#

set -euf -o pipefail
# -e           : exit immedialy if any command fails
# -u           : fail and exit immediatly on unset variables
# -f           : disble globbing [*, ?, etc]
# -o pipefail  : fail if any part of a pipe fails
#
# Some versions of python "activate" fail if -u is set.

TOP_DIR="$(dirname $(dirname $(realpath ${BASH_SOURCE[0]})))"
if [[ ! -d "${TOP_DIR}/ve3" ]]; then
    pushd ${TOP_DIR} 1>/dev/null 2>/dev/null
    python3 -m venv ve3
    [[ -s requirements.txt ]] && OPTS="-r requirements.txt"
    OPTS="${OPTS:=''}"
    ./ve3/bin/pip3 install --upgrade pip ${OPTS}
    unset OPTS
    popd 1>/dev/null 2>/dev/null
fi

# Prepare path to import python modules from bin
if [[ -z ${PYTHONPATH+x} ]]; then
    export PYTHONPATH="${TOP_DIR}/bin"
else
    export PYTHONPATH="${PYTHONPATH}:${TOP_DIR}/bin"
fi


echo >&2 "Testing create_mdconfig.py"
${TOP_DIR}/bin/create_mdconfig.py --stdout > config.cfg
S3_URL="$(grep ^s3_url_metadata config.cfg | awk '{print $3}')"
if [[ "X${S3_URL}" == "Xs3://BUCKET_NAME/PATH" ]]; then
    echo >&2 "PASSED: Test of create_mdconfig.py"
else
    echo >&2 "FAILED: Test of create_mdconfig.py"
    exit 1
fi
command rm config.cfg

TEST_DIR="${TOP_DIR}/test"

echo >&2 "Testing metadata.MetaData() class."
source ${TOP_DIR}/ve3/bin/activate && ${TEST_DIR}/test_metadata.py

echo >&2 "Testing create_metadata.sh"
${TOP_DIR}/bin/create_metadata.sh --backup_source="work" \
    --encryption_key="a different key" \
    --s3_url="s3://mybucket/path" \
    --s3_url_metadata="s3://anotherbucket/differentpath" \
    --force \
    --debug \
    ${TEST_DIR}/testfile.txt
BACKUP_SOURCE="$(grep backup_source testfile.txt.meta | awk '{print $2}' | sed -e 's/"//g; s/,//g')"

if [[ "X${BACKUP_SOURCE}" == "Xwork" ]]; then
    echo >&2 "PASSED: Test of create_metadata.sh"
else
    echo >&2 "FAILED: Test of create_metadata.sh"
    exit 1
fi
command rm testfile.txt.meta


exit ${?}



#=============================================================================#
# END
#=============================================================================#
