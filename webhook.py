import os
import requests
from functools import wraps
from flask import jsonify, Response
import logging
from webhook_security import generate_signature
from azureops.azureapi import azure_storage_instance

logger = logging.getLogger(__name__)

def handle_webhook_failure(blob_name, container_name):
    """Rollback function to delete blob after webhook failure."""
    blob_client = azure_storage_instance.get_blob_client(container=container_name, blob=blob_name)
    blob_client.delete_blob()
    logger.error(f"Blob {blob_name} in {container_name} deleted due to webhook failure.")

def webhook_decorator(operation):
    """
    A decorator to trigger the webhook after a successful operation.
    This will consume the data returned by the decorated function and pass it to the webhook.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Call the original function to get the result
                result = func(*args, **kwargs)
                webhook_url = result.get('webhook_url')
                webhook_type = result.get('webhook_type')

                if not webhook_url or not webhook_type:
                    return jsonify({'status': 'error', 'message': 'Missing webhook URL or type.'}), 400

                if not isinstance(result, dict):
                    return jsonify({'status': 'error', 'message': 'Invalid result returned from function'}), 400

                # Prepare the data for the webhook call
                webhook_data = None

                if operation.lower() == 'upload':
                    if webhook_type.lower() == 'episode':
                        webhook_data = {
                            'title': result.get('title'),
                            'description': result.get('description'),
                            'duration': result.get('duration'),
                            'audio_url': result.get('file_url'),
                            'image_url': result.get('image_url'),
                            'podcast_id': result.get('podcast_id'),
                        }
                    elif webhook_type.lower() == 'podcast':
                        webhook_data = {
                            'title': result.get('title'),
                            'description': result.get('description'),
                            'category': result.get('category'),
                            'image_url': result.get('image_url'),
                            'feed_url': result.get('file_url'),
                            'duration': result.get('duration'),
                        }

                    # Trigger the webhook
                    webhook_secret = os.environ.get('WEBHOOK_SECRET')
                    signature = generate_signature(webhook_data, webhook_secret)

                    headers = {
                        'X-Signature': signature.decode('utf-8')
                    }
                    response = requests.post(webhook_url, json=webhook_data, headers=headers)

                    # Handle webhook response
                    if response.status_code not in [200, 201]:
                        blob_name = result.get('file_name')
                        container_name = result.get('container_name')
                        handle_webhook_failure(blob_name, container_name)

                        return jsonify({
                            'status': 'error',
                            'message': f'Webhook failed with status {response.status_code}, file rollback completed.'
                        }), 500

                    return Response(
                        response=response.content,
                        status=response.status_code,
                        headers=dict(response.headers)
                    )

                elif operation.lower() == 'delete':
                    response = None

                    # Handle 'delete' operation based on the destination type
                    if webhook_type.lower() == 'episode':
                        episode_id = result.get('episode_id')
                        webhook_secret = os.environ.get('WEBHOOK_SECRET')
                        signature = generate_signature(str(episode_id), webhook_secret)

                        headers = {
                            'X-Signature': signature.decode('utf-8')
                        }
                        response = requests.delete(f"{webhook_url}/{episode_id}", headers=headers)

                    elif webhook_type.lower() == 'podcast':
                        podcast_id = result.get('podcast_id')
                        webhook_secret = os.environ.get('WEBHOOK_SECRET')
                        signature = generate_signature(str(podcast_id), webhook_secret)

                        headers = {
                            'X-Signature': signature.decode('utf-8')
                        }
                        response = requests.delete(f"{webhook_url}/{podcast_id}", headers=headers)

                    if response.status_code not in [200, 201]:
                        logger.error(f"Webhook delete error for {webhook_type} with status {response.status_code}")
                        return jsonify({
                            'status': 'error',
                            'message': f'Webhook failed with status {response.status_code}, file rollback completed.'
                        }), 500

                    return Response(
                        response=response.content,
                        status=response.status_code,
                        headers=dict(response.headers)
                    )

            except Exception as e:
                logger.error(f"Error triggering webhook: {str(e)}")
                return jsonify({'status': 'error', 'message': 'Failed to process the request', 'error_code': 'SERVER_ERROR'}), 500

        return wrapper

    return decorator
