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
# usage: print_usage PROGRAM_NAME

function print_usage() {
    _prog=${1}
    cat <<EOF
Usage: ${_prog} 

Blah.

EOF
    unset _prog
    return 0
}



#-----------------------------------------------------------------------------#
# Confirm log level is accepted.  If not, set to WARNING level.
# usage: check_loglevel LOGLEVEL

function check_loglevel() {
    local _level="${1}"
    local _levels="_DEBUG_ _INFO_ _WARNING_ _ERROR_ _CRITICAL_"
    if echo ${_levels} | grep -q _${_level}_ 2>/dev/null; then
        echo ${_level}
    else
        echo "WARNING"
    fi
    unset _level _levels
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
export -f loggit



#-----------------------------------------------------------------------------#
# Wait for a response before proceeding.  Return 0 (SUCCESS) or 1 (FAILURE)
# accordingly.
#
# usage: confirm "MESSAGE"

function confirm() {
    local _msg="${@}"
    local _answer="Unk"
    printf "\n\n"
    echo "${_msg}"
    while [[ "X${_answer}" != "Xy" ]] && \
          [[ "X${_answer}" != "Xn" ]] && \
          [[ "X${_answer}" != "X" ]]; do
        printf "Proceed (y/n) [DEFAULT: n] : "
        read _answer
    done
    [[ "X${_answer}" == "Xy" ]] && return 0
    return 1
}



#-----------------------------------------------------------------------------#
# Main program

# Assumes this wrapper is in TOP_DIR/bin
TOP_DIR="$(dirname $(dirname $(realpath ${BASH_SOURCE[0]})))"
PROG="$(basename ${BASH_SOURCE[0]})"

while getopts "DL:" optchar; do
    case "${optchar}" in
        "D") DEBUG="True" ;;
        "L") LOGLEVEL="${OPTARG}" ;;
    esac
done
shift $((OPTIND-1))
DEBUG=${DEBUG:="False"}
if [ "X${DEBUG}" == "XTrue" ]; then
    LOGLEVEL='DEBUG'
    set -x
fi
LOGLEVEL="$(check_loglevel ${LOGLEVEL:='WARNING'})"

loggit ${PROG} INFO "This is a test log"


#=============================================================================#
# END
#=============================================================================#
