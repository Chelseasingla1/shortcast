from flask import Blueprint, request, jsonify
import logging
from models import db, Download
from flask_login import current_user
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

download = Blueprint("download", __name__)


@download.get('/api/v1/downloads')
def list_user_downloads():
    """
    List all downloads for the authenticated user.
    ---
    tags:
        - Download
    get:
        description: Retrieve a list of downloads for the current user.
        responses:
            200:
                description: A list of the user's downloads.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Download'
            403:
                description: Forbidden access for unauthenticated users.
    """
    if not current_user.is_authenticated:
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 403

    download_list = Download.query.filter_by(user_id=current_user.id).all()
    download_list_dict=[item.to_dict() for item in download_list]
    return jsonify({'status': 'success', 'message': 'got downloads', 'data': download_list_dict}), 201



@download.post('/api/v1/downloads')
def download_podcast_episode():
    """
    Download a podcast episode.
    ---
    tags:
        - Download
    post:
        description: Create a new download for a podcast episode.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast episode being downloaded.
              required: true
        responses:
            200:
                description: Successfully downloaded the podcast episode.
            400:
                description: Error occurred during the download.
    """
    data = request.json
    podcast_id = data.get('podcast_id')
    episode_id = data.get('episode_id')
    try:
        new_download = None
        if podcast_id:
            new_download = Download(user_id=current_user.id, podcast_id=podcast_id)
        elif episode_id:
            new_download = Download(user_id=current_user.id, episode_id=episode_id)
        db.session.add(new_download)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'downloaded podcast', 'data': None}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'podcast/episode not downloaded', 'error_code': 'SERVER ERROR', 'data': None}), 500


@download.delete('/api/v1/downloads')
def remove_download():
    """
    Remove a podcast episode download.
    ---
    tags:
        - Download
    delete:
        description: Remove a podcast episode download by user_id and podcast_id.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast episode to be deleted.
              required: true
        responses:
            200:
                description: Download deleted successfully.
            404:
                description: Download not found.
            400:
                description: Error occurred during deletion.
    """
    data = request.json
    podcast_id = data.get('podcast_id')
    try:
        download_ = Download.query.filter_by(user_id=current_user.id, podcast_id=podcast_id).first()

        if download_:
            db.session.delete(download_)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'deleted download', 'data':None}), 201

        else:
            return jsonify({'status': 'success', 'message': 'No download found', 'data': None}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status':'error','message':'download not removed','error_code':'SERVER ERROR','data':None}), 500

@download.get('/api/v1/admin/downloads')
def list_downloads():
    """
    List all downloads.
    ---
    tags:
        - Download
    get:
        description: Retrieve a list of all downloads.
        responses:
            200:
                description: A list of all downloads.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Download'
    """
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Forbidden access','data':None}), 403

    download_list: list[Download] = Download.query.all()
    download_list_dict = [item.to_dict() for item in download_list]
    return jsonify({'status': 'success', 'message': 'got downloads', 'data': download_list_dict}), 201
