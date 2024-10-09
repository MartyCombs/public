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
    [[ -s requirements.txt ]] && ./ve3/bin/pip3 install -r requirements.txt
    popd 1>/dev/null 2>/dev/null
fi
set +u
source ${TOP_DIR}/ve3/bin/activate && ${TOP_DIR}/bin/create_config.py ${*}
exit ${?}



#=============================================================================#
# END
#=============================================================================#
