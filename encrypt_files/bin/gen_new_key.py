#!/usr/bin/env python3
#=============================================================================#
# Project Docs :
# Ticket       :
# Source Ctl   :
#=============================================================================#

import cryptography
from cryptography.fernet import Fernet

# Generates a random, 32-bit master key sent to STDOUT.  This can be
# pasted to the master key file for AES-GCM encryption.

key = Fernet.generate_key()[:-1]
print(key.decode())



#=============================================================================#
# END
#=============================================================================#
