from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

# Constants for AES-GCM
CHUNK_SIZE = 64 * 1024  # 64 KB
KEY_SIZE = 32  # 256-bit key for AES-256
NONCE_SIZE = 12  # 96 bits, recommended for GCM

def generate_key(password: bytes, salt: bytes) -> bytes:
    # Derive a key from a password (use only for demonstration)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password)

def encrypt_file(input_file, output_file, password):
    # Generate a random salt and nonce
    salt = os.urandom(16)
    nonce = os.urandom(NONCE_SIZE)

    # Derive a key from the password and salt
    key = generate_key(password, salt)

    # Initialize cipher for AES-GCM mode
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    ).encryptor()

    # Write salt and nonce to the beginning of the output file
    with open(output_file, 'wb') as out_file:
        out_file.write(salt)
        out_file.write(nonce)

        # Encrypt the file in chunks
        with open(input_file, 'rb') as in_file:
            while chunk := in_file.read(CHUNK_SIZE):
                encrypted_chunk = encryptor.update(chunk)
                out_file.write(encrypted_chunk)

        # Finalize encryption and get the authentication tag
        out_file.write(encryptor.finalize())
        out_file.write(encryptor.tag)

def decrypt_file(input_file, output_file, password):
    with open(input_file, 'rb') as in_file:
        # Read salt, nonce, and tag from the input file
        salt = in_file.read(16)
        nonce = in_file.read(NONCE_SIZE)

        # Derive the same key using the password and salt
        key = generate_key(password, salt)

        # Initialize cipher for AES-GCM mode
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, in_file.read(16)),
            backend=default_backend()
        ).decryptor()

        # Decrypt the file in chunks
        with open(output_file, 'wb') as out_file:
            while chunk := in_file.read(CHUNK_SIZE):
                decrypted_chunk = decryptor.update(chunk)
                out_file.write(decrypted_chunk)

            # Finalize decryption (verifies integrity)
            decryptor.finalize()

# Example usage
password = b'mysecurepassword'  # Securely handle this in a real application
input_file = 'large_file.txt'
encrypted_file = 'encrypted_file.enc'
decrypted_file = 'decrypted_file.txt'

# Encrypt the file
encrypt_file(input_file, encrypted_file, password)
print("File encrypted successfully.")

# Decrypt the file
decrypt_file(encrypted_file, decrypted_file, password)
print("File decrypted successfully.")

