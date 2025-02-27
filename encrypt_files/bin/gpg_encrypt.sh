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
    _config=${2}
    cat <<EOF
Usage: ${_prog} [ OPTIONS ] FILE [FILE ...]

Encrypt files using the GPG command line using the key as specfied in the
'gpg_key' setting in the configuration file:

    ${_config}

This script is a wrapper around GPG and expects the user to have a GPG
keyring which they manage separately.  The 'gpg' executible is also expected
to be in the user execution path.


OPTIONS
    --help         Print this usage and exit.

    --debug        Enable debug mode.

The '--showprogress' and '--loglevel' are not implemented and will be 
ignored with a warning message.

EOF
    unset _prog _config
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
CONFIG="etc/encryption_config.cfg"
RECIPIENT="$(egrep ^gpg_key ${TOP_DIR}/${CONFIG} | awk '{print $3}')"

while [[ "X${1:0:1}" == "X-" ]]; do
    case "${1}" in
        --help) 
            print_usage ${PROG} "$(basename ${TOP_DIR})/${CONFIG}"
            exit 0
            ;;
        --debug) 
            DEBUG="True"
            shift
            ;;
        *)
            loggit ${PROG} WARNING "Option not implemented. Ignoring \"$1\"."
            shift
            ;;
    esac
done
DEBUG=${DEBUG:="False"}
GPG_OPTS="--batch --armor --encrypt --recipient ${RECIPIENT}"

# If --debug is requested, add some extra.
if [[ "X${DEBUG}" == "XTrue" ]]; then
    GPG_OPTS="${GPG_OPTS} --status-fd=2"
fi

# Cannot do anything if no files are passed.
if [[ ${#} -eq 0 ]]; then
    loggit ${PROG} FATAL "No files passed."
    exit 1
fi

# Confirm that target files will not be overwritten.
for _file in $@; do
    if [[ -e ${_file}.asc ]]; then
        loggit ${PROG} FATAL "Cannot encrypt!  Target file already exists \"${_file}.asc\""
        exit 1
    fi
done

# Encrypt files.
for _file in $@; do
    _filesize="$(${TOP_DIR}/bin/prettyprint.py ${_file})"
    loggit ${PROG} INFO "Encrypting ${_file} (${_filesize}) to ${_file}.asc"
    loggit ${PROG} DEBUG "Using recipient key ${RECIPIENT}"
    ${GPG} ${GPG_OPTS} ${_file}
done
exit ${?}



#=============================================================================#
# END
#=============================================================================#
