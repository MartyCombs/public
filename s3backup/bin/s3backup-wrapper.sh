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


#-----------------------------------------------------------------------------#
function print_usage() {
    _prog=${1}
    _config=${2}
    cat <<EOF
Usage: ${_prog} [ OPTIONS ] ACTION

Perform a series of steps to back up files, or tar archives in 
the work directory to S3 based on parameters set in the 
configuration file:

  ${_config}

ACTION

    ALL            Performs all actions - manifest, encrypt, 
                   metadata, upload.

    manifest       Generate a sorted manifest of tar archives and
                   store them in the work directory.

    encrypt        Encrypt the files in the work directory.

    metadata       Create metadata files for files in the work 
                   directory.

    upload         Upload encrypted files to the S3 buckets and 
                   move manifests and metadata files to final
                   locations.
    
EOF
    unset _prog _config
    return 0
}



#-----------------------------------------------------------------------------#
# Echo log message of priority to STDERR and syslog.
#
# usage: loggit PROGRAM_NAME PRIORITY "MESSAGE"

function loggit() {
    local _prog=${1}
    shift
    local _big_priority="$(echo ${1} | tr [:lower:] [:upper:])"
    local _small_priority="$(echo ${1} | tr [:upper:] [:lower:])"
    shift
    local _msg="[$(date +"%Y-%m-%d %H:%M:%S %z")] ${_prog}(${$}) ${_big_priority} ${@}"
    echo >&2 "${_msg}"
    logger -p syslog.${_small_priority} -t "${_prog}" "${@}"
    unset _prog _big_priority _small_priority _msg
    return 0
}
# Export to include in xargs loops.
#export -f loggit



#-----------------------------------------------------------------------------#
# Main program

TOP_DIR="$(dirname $(dirname $(realpath ${BASH_SOURCE[0]})))"
PROG="$(basename ${BASH_SOURCE[0]})"
CONFIG="${TOP_DIR}/etc/s3backup.cfg"


while [[ ${#} -gt 0 ]]; do
    case "${1}" in
        --help) print_usage ${PROG} ${CONFIG}; exit 0; ;;
        --debug) DEBUG="${1}"; shift; ;;
        --showprogress) SHOWPROGRESS="${1}"; shift; ;;
        ALL) ACTION="ALL"; shift; ;;
        manifest) ACTION="manifest"; shift; ;;
        encrypt) ACTION="encrypt"; shift; ;;
        metadata) ACTION="metadata"; shift; ;;
        upload) ACTION="upload"; shift; ;;
    esac
done

DEBUG=${DEBUG:=" "}
SHOWPROGRESS=${SHOWPROGRESS:=" "}
ACTION=${ACTION:="NULL"}

if [[ "X${DEBUG}" == "X--debug" ]]; then
    set -x
fi

if [[ "X${ACTION}" == "XNULL" ]]; then
    echo >&2 "Missing action"
    print_usage ${PROG} ${CONFIG}
    exit 1
fi

case "${ACTION}" in
    "ALL") ${TOP_DIR}/bin/create_manifests.sh && \
           ${TOP_DIR}/bin/encrypt.sh ${DEBUG} ${SHOWPROGRESS} && \
           ${TOP_DIR}/bin/create_metadata.sh ${DEBUG} ${SHOWPROGRESS} && \
           ${TOP_DIR}/bin/upload.sh ;;
    "manifest") ${TOP_DIR}/bin/create_manifests.sh ;;
    "encrypt") ${TOP_DIR}/bin/encrypt.sh ${DEBUG} ${SHOWPROGRESS} ;;
    "metadata") ${TOP_DIR}/bin/create_metadata.sh ${DEBUG} ${SHOWPROGRESS} ;;
    "upload") ${TOP_DIR}/bin/upload.sh ;;
esac
exit ${?}


#=============================================================================#
# END
#=============================================================================#

