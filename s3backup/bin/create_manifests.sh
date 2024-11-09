#!/usr/bin/env bash
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create-metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/s3backup/bin/create_manifests.sh
#=============================================================================#

set -euf -o pipefail
# -e           : exit immedialy if any command fails
# -u           : fail and exit immediatly on unset variables
# -f           : disble globbing [*, ?, etc]
# -o pipefail  : fail if any part of a pipe fails
#
# Some versions of python "activate" fail if -u is set.


#-----------------------------------------------------------------------------#
function print_usage() {
    _prog=${1}
    _drop_dir=${1}
    cat <<EOF
Usage: ${_prog} [ OPTIONS ]

Create manifests for any tar archives in the drop directory

    ${_drop_dir}

After completion, all files which have been processed and empty file ending
in '.done' is created for every file examined and manifest created.
 
EOF
    unset _prog _drop_dir
    return 0
}

TOP_DIR="$(dirname $(dirname $(realpath ${BASH_SOURCE[0]})))"
SRC_DIR="${TOP_DIR}/work/
while [[ ${#} -gt 0 ]]; do
    case "${1}" in
        --help) print_usage ${PROG} ${CONFIG}; exit 0; ;;
        --debug) DEBUG="${1}"; shift; ;;
    esac
done
DEBUG=${DEBUG:=" "}
SHOWPROGRESS=${SHOWPROGRESS:=" "}
DROP_DIR="${1}
exit ${?}



#=============================================================================#
# END
#=============================================================================#
