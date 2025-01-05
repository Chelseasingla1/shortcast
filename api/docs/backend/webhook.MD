### Webhook Decorator Documentation

#### Overview

The `webhook_decorator` is designed to wrap Flask route functions and trigger webhooks after a successful operation. It ensures that the data returned by the decorated function is sent to the specified webhook URL, including security headers (via a signature) and the appropriate data format. The decorator supports both **upload** and **delete** operations for podcast-related data, with built-in error handling and rollback functionality for failed uploads.

#### Functionality

- **Upload Operations:** The decorator triggers a webhook after uploading content, passing metadata such as title, description, file URLs, and podcast details.
- **Delete Operations:** The decorator triggers a webhook after deleting content, passing the episode or podcast ID to notify the remote service.

Additionally, the decorator handles errors by:
- Returning a detailed error message if required fields are missing.
- Rolling back the uploaded file (via Azure Blob Storage) if the webhook fails during the upload operation.

#### Dependencies

- **Flask:** The decorator is meant to be used in Flask routes.
- **requests:** For making HTTP requests to the webhook URL.
- **azureops.azureapi:** Used for interacting with Azure Blob Storage to delete blobs in case of upload failures.
- **webhook_security:** Contains the `generate_signature` function used to create the signature for the webhook headers.

#### How to Use the Webhook Decorator

The decorator can be applied to any route function responsible for performing an upload or delete operation. The decorated function should return a dictionary containing the required data for the webhook.

##### 1. Upload Operation

For an upload operation, the decorated function should return a dictionary containing:
- `webhook_url`: The URL where the webhook will be sent.
- `webhook_type`: The type of content (`episode` or `podcast`).
- Metadata relevant to the upload, such as:
  - `title`
  - `description`
  - `duration`
  - `file_url`
  - `image_url`
  - `podcast_id`

Example:
```python
@app.route('/upload-episode', methods=['POST'])
@webhook_decorator(operation='upload')
def upload_episode():
    episode_data = {
        'title': 'My New Episode',
        'description': 'This is a description of the episode.',
        'duration': 120,  # in seconds
        'file_url': 'http://example.com/audio.mp3',
        'image_url': 'http://example.com/episode_image.jpg',
        'podcast_id': 1,
        'webhook_url': 'http://example.com/webhook',
        'webhook_type': 'episode',
        'file_name': 'episode.mp3',  # Optional: used for rollback
        'container_name': 'podcasts'  # Optional: used for rollback
    }
    return jsonify({'status': 'success', 'message': 'Episode uploaded successfully', **episode_data})
```

##### 2. Delete Operation

For a delete operation, the decorated function should return a dictionary containing:
- `webhook_url`: The URL where the webhook will be sent.
- `webhook_type`: The type of content (`episode` or `podcast`).
- The identifier of the content to delete, either:
  - `episode_id` (for episodes)
  - `podcast_id` (for podcasts)

Example:
```python
@app.route('/delete-episode/<int:episode_id>', methods=['DELETE'])
@webhook_decorator(operation='delete')
def delete_episode(episode_id):
    return jsonify({
        'episode_id': episode_id,
        'webhook_url': 'http://example.com/webhook',
        'webhook_type': 'episode'
    })
```

#### Error Handling

If the decorated function does not return a dictionary or if any required fields are missing, the decorator will return an error response:

```json
{
    "status": "error",
    "message": "Missing webhook URL or type."
}
```

If the webhook response is not successful (status codes other than 200 or 201), the decorator will trigger a rollback for upload operations (deleting the blob from Azure). In case of a failure, the response will be:

```json
{
    "status": "error",
    "message": "Webhook failed with status {status_code}, file rollback completed."
}
```

For errors during execution or invalid return types, the decorator will catch exceptions and return a generic server error:

```json
{
    "status": "error",
    "message": "Failed to process the request",
    "error_code": "SERVER_ERROR"
}
```

#### Signature Verification

For security purposes, the webhook signature is generated using the `generate_signature` function, which takes the data being sent to the webhook and a secret (`WEBHOOK_SECRET` environment variable). The signature is included in the request headers (`X-Signature`), ensuring the integrity and authenticity of the webhook request.

#### Rollback Mechanism for Upload Operations

In case of a failed upload operation (when the webhook response status code is not 200 or 201), the decorator will attempt to delete the uploaded blob from Azure Blob Storage as part of a rollback process. This is done using the `handle_webhook_failure` function, which will:
- Retrieve the `blob_name` and `container_name` from the result.
- Delete the blob from Azure Storage.

#### Notes
- The decorator requires that the decorated function return a dictionary containing the necessary information for the webhook operation (either upload or delete).
- The decorator handles both `upload` and `delete` operations, but additional operations can be added if necessary.
- The `handle_webhook_failure` function assumes the use of Azure Blob Storage for storing uploaded content; modify it for other storage solutions as needed.

---

#### Example Use Cases

1. **Upload Episode:**
   - A user uploads a new episode to the podcast system. After the file is uploaded and stored, the webhook is triggered to notify an external system.
   - If the webhook fails, the uploaded blob is deleted from Azure Storage.

2. **Delete Podcast:**
   - A user deletes a podcast from the system. The webhook sends a delete request to notify an external system.
   - If the webhook fails, no rollback is needed as no blob is involved in this case.

3. **Error Handling During Upload:**
   - If the webhook URL or type is missing in the return dictionary, an error is returned to the user with an appropriate message.

---

This decorator helps ensure that external systems are notified about operations like uploads and deletions, while also handling errors gracefully and maintaining system integrity with rollback functionality.