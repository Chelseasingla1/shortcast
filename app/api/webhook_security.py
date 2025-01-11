import hmac
import hashlib
import base64

def generate_signature(payload, secret):
    return base64.b64encode(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())


def verify_signature(payload, signature, secret):
    # Verify the HMAC signature using the same secret
    expected_signature = base64.b64encode(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())
    return signature == expected_signature.decode('utf-8')
