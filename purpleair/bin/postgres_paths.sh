#!/usr/bin/env bash
#=============================================================================#
# Project Docs : 
# Ticket       :
# Source Ctl   : 
#=============================================================================#
# Specific hack for my installation of PostgreSQL on Mac OSX.

if [[ "X$(which psql)" == "X" ]] && \
   [[ -d "/opt/homebrew/Cellar/postgresql@16/16.6" ]]; then
    export POSTGRES_HOME="/opt/homebrew/Cellar/postgresql@16/16.6"
    export PATH=${PATH}:${POSTGRES_HOME}/bin
fi



#=============================================================================#
# END
#=============================================================================#

