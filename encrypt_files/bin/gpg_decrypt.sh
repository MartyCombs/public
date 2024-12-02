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

function print_usage() {
    _prog=${1}
    cat <<EOF
Usage: ${_prog} [ OPTIONS ] FILE [FILE ...]

Decrypt files using the GPG command line.

OPTIONS

    --help         Print this usage and exit.

    --debug        Enable debug mode.


EOF
    unset _prog
    return 0
}


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


TOP_DIR="$(dirname $(dirname $(realpath ${BASH_SOURCE[0]})))"
PROG="$(basename ${BASH_SOURCE[0]})"

# GPG requirements.
GPG="$(which gpg)"

while [[ "X${1:0:1}" == "X-" ]]; do
    case "${1}" in
        --help)
            print_usage ${PROG}
            exit 0
            ;;
        --debug) 
            DEBUG="True"
            shift
            ;;
        *)
            loggit ${PROG} WARNING "Unknown option \"$1\". Ignoring"
            shift
            ;;
    esac
done
DEBUG=${DEBUG:="False"}

# Check files for proper extension before decrypting.
for _file in $@; do
    if ! echo ${_file} | grep -q '\.asc$'; then
        echo >&2 "FATAL: Not encrypted with GPG"
        exit 1
    fi
done

# Decrypt files
for _file in $@; do
    OUTFILE="${_file%%.asc}"
    ${GPG} --batch --status-fd=2 --decrypt ${_file} > ${OUTFILE}
    [[ "${DEBUG}" == "True" ]] && loggit ${PROG} DEBUG "${_file} -> ${OUTFILE}"
done
exit ${?}



#=============================================================================#
# END
#=============================================================================#
