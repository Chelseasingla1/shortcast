from flask import Blueprint, request, jsonify
import logging
from models import db, SharedPlaylist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

shared_playlist = Blueprint("shared_playlist", __name__)


@shared_playlist.get('/api/v1/shared_playlists')
def list_shared_playlists() -> list[SharedPlaylist]:
    shared_playlist_list: list[SharedPlaylist] = SharedPlaylist.query.all()
    return shared_playlist_list


@shared_playlist.post('/api/v1/shared_playlists')
def share_playlist():
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')
    try:
        new_shared_playlist = SharedPlaylist(user_id=user_id,playlist_id=playlist_id)
        db.session.add(new_shared_playlist)
        db.session.commit()
        return jsonify({'msg': 'successfully subscribed'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"


@shared_playlist.delete('/api/v1/shared_playlists')
def unshare_playlist():
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')
    try:
        shared_playlist_ = SharedPlaylist.query.filter_by(user_id=user_id,playlist_id=playlist_id).first()

        if shared_playlist_:
            db.session.delete(shared_playlist_)
            db.session.commit()

            return jsonify({'message': f'SharedPlaylist out successfully!'}), 200
        else:
            return jsonify({'message': 'SharedPlaylist not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)})