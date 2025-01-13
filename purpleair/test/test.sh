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

TEST_DIR="${TOP_DIR}/test"
source ${TOP_DIR}/ve3/bin/activate && ${TEST_DIR}/test.py
exit ${?}



#=============================================================================#
# END
#=============================================================================#

