#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import cryptography

from cryptography.fernet import Fernet
key = Fernet.generate_key()[:-1]
print(key.decode())
