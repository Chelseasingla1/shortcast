from flask import Blueprint, request, jsonify
import logging
from models import db, Download

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

download = Blueprint("download", __name__)


@download.get('/api/v1/downloads')
def list_downloads() -> list[Download]:
    download_list: list[Download] = Download.query.all()
    return download_list


@download.post('/api/v1/downloads')
def download():
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')
    try:
        new_download = Download(user_id=user_id,podcast_id=podcast_id)
        db.session.add(new_download)
        db.session.commit()
        return jsonify({'msg': 'successfully downloaded'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"


@download.delete('/api/v1/downloads')
def delete_download():
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')
    try:

        download_ = Download.query.filter_by(user_id=user_id, podcast_id=podcast_id).first()

        if download_:
            db.session.delete(download_)

            db.session.commit()

            return jsonify({'message': f'Download deleted successfully!'}), 200
        else:
            return jsonify({'message': 'Download not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)})