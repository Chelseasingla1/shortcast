import os
from http.client import responses

from flask import Blueprint,request,url_for,jsonify,send_file,Response
from werkzeug.utils import secure_filename
from flask_login import login_required
from azureops.azureclass import AzureBlobStorage
from dotenv import load_dotenv
load_dotenv()
connection_string = os.getenv('AZURE_CONNECTION_STRING')
azure_api = Blueprint('azure_api',__name__)

azure_storage_instance = AzureBlobStorage(connection_string)

@azure_api.post('/create-container')
def create_container():
    data = request.json
    container_name = data.get('container_name')
    if not container_name:
        return jsonify({
            'error':'Container name is required'
        }),400
    try:

        azure_storage_instance.create_container(container_name)
        return jsonify({
            "message":"Container created successfully"
        }),201
    except Exception as e:
        return jsonify({
            'error':str(e)
        }),500

@azure_api.delete('/delete-container/<container_name>')
def delete_container(container_name):
    try:
        azure_storage_instance.delete_container(container_name)
        return jsonify({
            'message':"container deleted successfully"
        })
    except Exception as e:
        return jsonify({'error':str(e)}),500

@azure_api.get('/list-blobs/<container_name>')
def list_blobs(container_name):
    try:
        blobs = azure_storage_instance.list_blobs(container_name)
        return jsonify({'blobs':blobs}),200
    except Exception as e:
        return jsonify({'error':str(e)}),200

@azure_api.post('upload-blob/<container_name>/<blob_name>')
def upload_blob(container_name,blob_name):
    if 'file' not in request.files:
        return jsonify({'error':'No file part'}),400
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'error':'No selected file'
        }),400
    filename = secure_filename(file.filename)
    file_path = os.path.join('/tmp',filename)
    file.save(file_path)
    try:
        azure_storage_instance.upload_blob(container_name, blob_name, file_path)
        os.remove(file_path)
        return jsonify({'message':'blov uploaded successfully'}),201
    except Exception as e:
        return jsonify({'error':str(e)}),500


@azure_api.get('download-blob/<container_name>/<blob_name>')
def download_blob(container_name,blob_name):
    download_path = f'/tmp/{blob_name}'
    try:
        azure_storage_instance.download_blob(container_name, blob_name, download_path)
        return send_file(download_path,as_attachment=True,download_name=blob_name)
    except Exception as e:
        return jsonify({'error':str(e)}),500

@azure_api.delete('delete-blob/<container_name>/<blob_name>')
def delete_blob(container_name,blob_name):
    try:
        azure_storage_instance.delete_blob(container_name, blob_name)
        return jsonify({'message':'Blob deleted successfully'}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@azure_api.get('blob-exists/<container_name>/<blob_name>')
def blob_exists(container_name,blob_name):
    try:
        exists = azure_storage_instance.blob_exists(container_name, blob_name)
        return jsonify({'exists':exists}),200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@azure_api.get('blob-properties/<container_name>/<blob_name>')
def blob_properties(container_name,blob_name):
    try:
        properties = azure_storage_instance.get_blob_properties(container_name, blob_name)
        return jsonify({'properties':properties}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@azure_api.post('set-metadata/<container_name>/<blob_name>')
def set_metadata(container_name,blob_name):
    try:
        metadata = request.json.get('metadata')
        if not metadata:
            return jsonify({'error':'metadata is required'}),400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@azure_api.get('/stream-blob/<container_name>/<blob_name>')
def stream_blob(container_name,blob_name):
    try:
        properties = azure_storage_instance.get_blob_properties(container_name, blob_name)
        blob_size = properties.get('size')
        range_header = request.headers.get('Range')

        if range_header:
            byte_range = range_header.replace('bytes=', '').split('-')
            start_byte = int(byte_range[0])
            end_byte = int(byte_range[1]) if byte_range[1] else blob_size - 1

            if start_byte >= blob_size:
                return jsonify({
                    'error':'Range out of bounds'
                }),416

            byte_data = azure_storage_instance.stream_blob_part(container_name, blob_name, start_byte, end_byte)
            data = byte_data

            response = Response(data,status=206,content_type='audio/mpeg')
            response.headers['Content-Range'] = f'bytes {start_byte}-{end_byte}/{blob_size}'
            return response
        else:
            byte_data = azure_storage_instance.stream_blob_full(container_name, blob_name)
            data = byte_data
            response = Response(data,content_type='audio/mpeg')
            return response
    except Exception as e:
        return jsonify({'error':str(e)}),500
