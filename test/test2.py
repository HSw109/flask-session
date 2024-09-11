import hmac
import hashlib

def derive_key(secret_key: bytes) -> bytes:
    # Create HMAC object
    mac = hmac.new(secret_key, digestmod=hashlib.sha1)
    # Return the derived key (HMAC digest)
    return mac.digest()

# Example Inputs
secret_key = b'supersecretkey'

# Derive the key
derived_key = derive_key(secret_key)

# Print derived key in hexadecimal format
print(derived_key.hex())
