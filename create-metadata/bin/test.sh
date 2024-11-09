#!/usr/bin/env bash
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create-metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/create-metadata/test.sh
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
echo >&2 "Testing 'create_mdconfig.sh --stdout'"
${TOP_DIR}/bin/create_mdconfig.sh --stdout

cat >${TOP_DIR}/bin/testfile <<EOF
This is a test file.
EOF

echo >&2 "Testing MetaData class."
source ${TOP_DIR}/ve3/bin/activate && ${TOP_DIR}/bin/test.py

OPTIONS='--backup_source=personal --encryption_key=...abcd --s3_url=s3://mybucket/path --s3_url_metadata=s3://anotherbucket/differentpath'
echo >&2 "Testing 'create_metadata.sh"
${TOP_DIR}/bin/create_metadata.sh ${OPTIONS} ${TOP_DIR}/bin/testfile
command rm -v ${TOP_DIR}/bin/testfile.meta ${TOP_DIR}/bin/testfile
exit ${?}



#=============================================================================#
# END
#=============================================================================#
