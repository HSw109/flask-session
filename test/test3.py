import hmac
import hashlib

def verify_derived_key(secret_key: bytes, expected_key: bytes) -> bool:
    # Create HMAC object
    mac = hmac.new(secret_key, digestmod=hashlib.sha1)
    # Calculate the derived key
    derived_key = mac.digest()
    # Compare the calculated derived key with the expected key
    return hmac.compare_digest(derived_key, expected_key)

# Example Inputs
secret_key = b'supersecretkey'

# Given derived key (HMAC output) that we want to verify
expected_key_str = '7f68c3050b559db30623ebef6c43454f6fc535b6'
expected_key = bytes.fromhex(expected_key_str)

# Verify if the given derived key matches
is_valid = verify_derived_key(secret_key, expected_key)

print(f"Is the derived key valid? {is_valid}")
