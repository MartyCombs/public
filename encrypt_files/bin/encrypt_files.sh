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
CONFIG="etc/encryption_config.cfg"
ENCRYPTION_METHOD="$(egrep ^encryption_method "${TOP_DIR}/${CONFIG}" | awk '{print $3}')"

case "${ENCRYPTION_METHOD}" in
    GPG) 
        "${TOP_DIR}/bin/gpg_encrypt.sh" "$@"
        ;;
    AES-GCM)
        "${TOP_DIR}/bin/aes_encrypt.sh" "$@"
        ;;
    *)
         cat >&2 <<EOF
FATAL: Unknown encrypt method "${ENCRYPTION_METHOD}" specified in
       ${CONFIG}
EOF
esac

exit ${?}



#=============================================================================#
# END
#=============================================================================#
