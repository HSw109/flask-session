import hmac
import hashlib

class SignatureGenerator:
    def __init__(self, digest_method=hashlib.1):
        self.digest_method = digest_method

    def get_signature(self, key: bytes, value: bytes) -> bytes:
        mac = hmac.new(key, msg=value, digestmod=self.digest_method)
        return mac.digest()

# Example usage
secret_key = b'supersecretkey'  # The key used for HMAC
data_value = b'important_data'  # The data to be signed

# Create an instance of SignatureGenerator with SHA256 as the digest method
sig_gen = SignatureGenerator()

# Generate the HMAC signature
signature = sig_gen.get_signature(secret_key, data_value)

# Print the generated signature in hexadecimal format
print("Generated Signature (hex):", signature.hex())
