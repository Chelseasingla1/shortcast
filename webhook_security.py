import hmac
import hashlib
import base64

def generate_signature(payload, secret):
    return base64.b64encode(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())


def verify_signature(payload, signature, secret):
    # Verify the HMAC signature using the same secret
    expected_signature = base64.b64encode(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())
    return signature == expected_signature.decode('utf-8')

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.data.decode('utf-8')  # Get raw payload
    signature = request.headers.get('X-Signature')  # Get signature from header
    secret = 'your_shared_secret_key'  # Shared secret between producer and consumer

    if not verify_signature(payload, signature, secret):
        return jsonify({'status': 'error', 'message': 'Invalid signature'}), 403

    # Proceed with handling the valid payload
    data = request.json
    return jsonify({'status': 'success', 'message': 'Webhook received successfully'}), 200
