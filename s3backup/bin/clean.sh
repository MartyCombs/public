#!/usr/bin/env bash
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

TOP_DIR="$(dirname $(dirname $(realpath ${BASH_SOURCE[0]})))"
find ${TOP_DIR} -type d -iname 've3' -exec /bin/rm -rf {} \; 2>/dev/null
find ${TOP_DIR} -type d -iname '__pycache__' -exec /bin/rm -rf {} \; 2>/dev/null
find ${TOP_DIR} -type f -iname '.ds_store' -exec /bin/rm -f {} \; 2>/dev/null


#=============================================================================#
# END
#=============================================================================#
