#!/usr/bin/env bash
#=============================================================================#
# Project Docs : https://github.com/MartyCombs/public/blob/main/create-metadata/README.md
# Ticket       :
# Source Ctl   : https://github.com/MartyCombs/public/blob/main/s3backup/bin/common.sh
#=============================================================================#

set -euf -o pipefail
# -e           : exit immedialy if any command fails
# -u           : fail and exit immediatly on unset variables
# -f           : disble globbing [*, ?, etc]
# -o pipefail  : fail if any part of a pipe fails
#
# Some versions of python "activate" fail if -u is set.


# Use a shell logging function across all wrapper scripts.
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


# Set some global shell variables for all scripts.  These may however be
# redefined within a given shell script should that script be run
# independently of the wrapper.
TOP_DIR="$(dirname $(dirname $(realpath ${BASH_SOURCE[0]})))"
PROG="$(basename ${BASH_SOURCE[0]})"


# Test for dependent software.
_egrep="$(which egrep)"
_python="$(which python3)"


# Look for '--debug' while leaving arguments in place to pass to subscripts
# such as python.
if [[ ${#} -gt 0 ]]; then
    for _arg in ${@}; do
        case "_arg" in 
            --debug) DEBUG='True' ;;
        esac
    done
fi
DEBUG="${DEBUG:='False'}"

# Set outer shell to -x and echo information about dependent software used 
# if we are in debug mode.
if [[ "X${DEBUG}" == "XTrue" ]]; then
    set -x
    _message=$(cat<<EOF
Running with:
    TOP_DIR    : ${TOP_DIR}
    PROG       : ${PROG}
    egrep      : ${_egrep}
    python     : ${_python}
EOF
)
loggit ${PROG} DEBUG ${_message}
unset _egrep _python _arg _message



#=============================================================================#
# END
#=============================================================================#
