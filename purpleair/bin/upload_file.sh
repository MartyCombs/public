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
if [[ "X$(uname -o)" == "XDarwin" ]]; then
    source ${TOP_DIR}/bin/postgres_paths.sh
fi
if [[ ! -d "${TOP_DIR}/ve3" ]]; then
    pushd ${TOP_DIR} 1>/dev/null 2>/dev/null
    python3 -m venv ve3
    [[ -s requirements.txt ]] && OPTS="-r requirements.txt"
    OPTS="${OPTS:=' '}"
    ./ve3/bin/pip3 install --upgrade pip ${OPTS}
    unset OPTS
    popd 1>/dev/null 2>/dev/null
fi
source ${TOP_DIR}/ve3/bin/activate && ${TOP_DIR}/bin/upload_file.py "$@"
exit ${?}



#=============================================================================#
# END
#=============================================================================#

