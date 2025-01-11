import osfrom app.api.azureops.redisclass import save_playback_position, get_playback_position, redis_clientfrom flask import Blueprint, request, jsonify, send_file, Response, sessionfrom werkzeug.utils import secure_filenamefrom flask_login import login_requiredfrom app.api.azureops.azureclass import AzureBlobStoragefrom dotenv import load_dotenvimport logginglogging.basicConfig(level=logging.INFO)logger = logging.getLogger(__name__)load_dotenv()connection_string = os.getenv('AZURE_CONNECTION_STRING')azure_api = Blueprint('azure_api', __name__)azure_storage_instance = AzureBlobStorage(connection_string)from app.api.webhook import webhook_decorator@login_required@azure_api.post('/create-container')def create_container():    """    Create a new container in Azure Blob Storage.    ---    tags:      - Azure Blob Storage    parameters:      - in: body        name: container_name        description: The name of the container to create.        required: true        schema:          type: object          properties:            container_name:              type: string    responses:      201:        description: Container created successfully.      400:        description: Container name is required.      500:        description: Internal server error.    """    data = request.json    container_name = data.get('container_name')    if not container_name:        return jsonify({'status': 'error', 'message': 'container name required', 'error_code': 'VALIDATION ERROR',                        'data': None}), 401    try:        azure_storage_instance.create_container(container_name)        logger.info('created container')        return jsonify({'status': 'success', 'message': 'container created'}), 201    except Exception as e:        logger.error(str(e))        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500@login_required@azure_api.delete('/delete-container/<container_name>')def delete_container(container_name):    """    Delete a container from Azure Blob Storage.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container to delete.        required: true        type: string    responses:      200:        description: Container deleted successfully.      500:        description: Internal server error.    """    try:        azure_storage_instance.delete_container(container_name)        return jsonify({'status': 'success', 'message': 'container deleted'}), 201    except Exception as e:        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500@login_required@azure_api.get('/list-blobs/<container_name>')def list_blobs(container_name):    """    List all blobs in a container.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container.        required: true        type: string    responses:      200:        description: List of blobs.      500:        description: Internal server error.    """    try:        blobs = azure_storage_instance.list_blobs(container_name)        blob_data = {'blobs': blobs}        return jsonify({'status': 'success', 'message': 'blob list', 'data': blob_data}), 201    except Exception as e:        logger.error(str(e))        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500@login_required@webhook_decorator(operation='upload')@azure_api.post('/upload-blob/<container_name>/<blob_name>')def upload_blob(container_name, blob_name):    """    Upload a blob to a container.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container.        required: true        type: string      - in: path        name: blob_name        description: The name of the blob.        required: true        type: string      - in: formData        name: file        description: The file to upload.        required: true        type: file    responses:      201:        description: Blob uploaded successfully.      400:        description: No file part or no selected file.      500:        description: Internal server error.    """    data = request.json    title = data.get('title')    description = data.get('description'),    category = data.get('category'),    image_url = data.get('image_url'),    duration = data.get('duration')    webhook_url = data.get('webhook_url')    webhook_type = data.get('webhook_type')    if 'file' not in request.files:        return jsonify({'status': 'error', 'message': 'VALIDATION ERROR', 'data': None}), 401    file = request.files['file']    if file.filename == '':        return jsonify({'status': 'error', 'message': 'VALIDATION ERROR', 'data': None}), 401    filename = secure_filename(file.filename)    file_path = os.path.join('/tmp', filename)    file.save(file_path)    try:        url = azure_storage_instance.upload_blob(container_name, blob_name, file_path)        response_data = {            'status': 'success',            'message': 'Blob uploaded successfully',            'container_name': container_name,            'file_name': filename,            'title': title,            'description': description,            'category': category,            'image_url': image_url,            'duration': duration,            'file_url': url,            'webhook_url': webhook_url,            'webhook_type': webhook_type        }        return jsonify(response_data), 201    except Exception as e:        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500    finally:        os.remove(file_path)@login_required@azure_api.get('/download-blob/<container_name>/<blob_name>')def download_blob(container_name, blob_name):    """    Download a blob from a container.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container.        required: true        type: string      - in: path        name: blob_name        description: The name of the blob.        required: true        type: string    responses:      200:        description: Blob downloaded successfully.      500:        description: Internal server error.    """    download_path = f'/tmp/{blob_name}'    try:        azure_storage_instance.download_blob(container_name, blob_name, download_path)        return send_file(download_path, as_attachment=True, download_name=blob_name)    except Exception as e:        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500@login_required@webhook_decorator(operation='delete')@azure_api.delete('/delete-blob/<container_name>/<blob_name>')def delete_blob(container_name, blob_name):    """    Delete a blob from a container.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container.        required: true        type: string      - in: path        name: blob_name        description: The name of the blob.        required: true        type: string    responses:      200:        description: Blob deleted successfully.      500:        description: Internal server error.    """    try:        data = request.json        episode_id = data.get('episode_id')        podcast_id = data.get('podcast_id')        azure_storage_instance.delete_blob(container_name, blob_name)        response_data = {            'status': 'success',            'message': 'Blob uploaded successfully',            'podcast_id': podcast_id,            'episode_id': episode_id,            'webhook_url': webhook_url,            'webhook_type': webhook_type        }        return jsonify(response_data), 201    except Exception as e:        logger.error(str(e))        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500@azure_api.get('/blob-exists/<container_name>/<blob_name>')def blob_exists(container_name, blob_name):    """    Check if a blob exists in a container.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container.        required: true        type: string      - in: path        name: blob_name        description: The name of the blob.        required: true        type: string    responses:      200:        description: Blob existence status.      500:        description: Internal server error.    """    try:        exists = azure_storage_instance.blob_exists(container_name, blob_name)        return jsonify({'status': 'success', 'message': 'blob exists'}), 200    except Exception as e:        logger.error(str(e))        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500@azure_api.get('/blob-properties/<container_name>/<blob_name>')def blob_properties(container_name, blob_name):    """    Get properties of a blob.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container.        required: true        type: string      - in: path        name: blob_name        description: The name of the blob.        required: true        type: string    responses:      200:        description: Blob properties.      500:        description: Internal server error.    """    try:        properties = azure_storage_instance.get_blob_properties(container_name, blob_name)        return jsonify({'status': 'success', 'message': 'blob exists', 'data': properties}), 200    except Exception as e:        logger.error(str(e))        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500@azure_api.post('/set-metadata/<container_name>/<blob_name>')def set_metadata(container_name, blob_name):    """    Set metadata for a blob.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container.        required: true        type: string      - in: path        name: blob_name        description: The name of the blob.        required: true        type: string      - in: body        name: metadata        description: The metadata to set.        required: true        schema:          type: object    responses:      200:        description: Metadata set successfully.      400:        description: Metadata is required.      500:        description: Internal server error.    """    try:        metadata = request.json.get('metadata')        if not metadata:            return jsonify({'status': 'error', 'message': 'VALIDATION ERROR', 'data': None}), 400        return jsonify({'status': 'success', 'message': 'metadata set', 'data': None}), 201    except Exception as e:        logger.error(str(e))        return jsonify(            {'status': 'error', 'message': 'Internal Server error', 'error_code': 'SERVER ERROR', 'data': None}), 500@azure_api.get('/stream-blob/<container_name>/<blob_name>')def stream_blob(container_name, blob_name):    """    Stream a blob from a container.    ---    tags:      - Azure Blob Storage    parameters:      - in: path        name: container_name        description: The name of the container.        required: true        type: string      - in: path        name: blob_name        description: The name of the blob.        required: true        type: string      - in: header        name: Range        description: The byte range to stream.        required: false        type: string    responses:      206:        description: Partial content.      200:        description: Full content.      416:        description: Range out of bounds.      500:        description: Internal server error.    """    try:        properties = azure_storage_instance.get_blob_properties(container_name, blob_name)        blob_size = properties.get('size')        range_header = request.headers.get('Range')        user_id = session.get('user_id')        current_position = get_playback_position(user_id)        if range_header:            byte_range = range_header.replace('bytes=', '').split('-')            start_byte = int(byte_range[0])            end_byte = int(byte_range[1]) if byte_range[1] else blob_size - 1            if start_byte >= blob_size:                return jsonify({                    'error': 'Range out of bounds'                }), 416            cache_key = f"{container_name}:{blob_name}:{start_byte}:{end_byte}"            cached_chunk = redis_client.get(cache_key)            if cached_chunk:                print('Fetching from redis cache')                data = cached_chunk            else:                print("Fetching from Azure Blob Storage")                byte_data = azure_storage_instance.stream_blob_part(container_name, blob_name, start_byte, end_byte)                data = byte_data                redis_client.set(cache_key, data, ex=3600)                print("Cached chunk in Redis")            response = Response(data, status=206, content_type='audio/mpeg')            response.headers['Content-Range'] = f'bytes {start_byte}-{end_byte}/{blob_size}'            save_playback_position(user_id, end_byte + 1)            return response        else:            byte_data = azure_storage_instance.stream_blob_full(container_name, blob_name)            data = byte_data            response = Response(data, content_type='audio/mpeg')            save_playback_position(user_id, current_position + len(data))            return response    except Exception as e:        logger.error(str(e))        return jsonify(            {'status': 'error', 'message': 'Stream not playing', 'error_code': 'SERVER ERROR', 'data': None}), 500