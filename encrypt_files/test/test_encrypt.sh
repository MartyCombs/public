#!/usr/bin/env bash
#=============================================================================#
# Project Docs : 
# Ticket       :
# Source Ctl   : 
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

echo >&2 ""
echo >&2 "Testing AES-GCM encryption."

# Fail if a backed up key already exists.
if [[ -e ${TOP_DIR}/etc/mykey.bak ]]; then
    echo >&2 "FATAL: Backup key exists ${TOP_DIR}/etc/mykey.bak"
    exit 1
fi

echo >&2 ""
if [[ -s ${TOP_DIR}/etc/mykey ]]; then
    echo >&2 "Backing up existing encrypt key and testing with a new key."
    command mv -v ${TOP_DIR}/etc/mykey  ${TOP_DIR}/etc/mykey.bak
fi

echo >&2 ""
echo >&2 "Creating encryption key."
${TOP_DIR}/bin/gen_new_key.py > ${TOP_DIR}/etc/mykey

source ${TOP_DIR}/ve3/bin/activate && ${TOP_DIR}/test/test_encrypt.py

if [[ -s ${TOP_DIR}/etc/mykey.bak ]]; then
    echo >&2 ""
    echo >&2 "Restoring backup of original encryption key."
    command mv -v ${TOP_DIR}/etc/mykey.bak ${TOP_DIR}/etc/mykey
else
    echo >&2 "Nullifying encryption key."
    cat /dev/null > ${TOP_DIR}/etc/mykey
fi
exit ${?}



#=============================================================================#
# END
#=============================================================================#
