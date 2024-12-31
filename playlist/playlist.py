from flask import Blueprint, request,jsonify
import logging
from models import db,Playlist
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

playlist = Blueprint("playlist", __name__)

@playlist.get('/api/v1/playlists')
def list_playlists() -> list[Playlist]:
    playlist_list:list[Playlist] = Playlist.query.all()
    return playlist_list

@playlist.get('/api/v1/playlists/<playlist_id>')
def get_playlist(playlist_id):
    playlist_ = Playlist.query.filter_by(id=playlist_id).first()
    if playlist_:
        return playlist_
    else:
        return

@playlist.post('/api/v1/playlists')
def create_playlist():
    data = request.json
    title = data.get('title')
    user_id = data.get('user_id')

    try:
        new_playlist = Playlist(title=title,user_id=user_id)
        db.session.add(new_playlist)

        db.session.commit()
        return jsonify({'msg':'successfully created playlist'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"

@playlist.put('/api/v1/playlists/<int:playlist_id>')
def update_playlist(playlist_id):
    data = request.json
    title = data.get('title')
    playlist_id = playlist_id
    playlist_ = Playlist.query.get(playlist_id)
    if playlist_:
        if 'title' in data:
            playlist_.title = title
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error':str(e)})

        return jsonify({
            'message': 'Playlist updated successfully!'
        })
    else:
        return jsonify({'message': 'Playlist not found!'}), 404

@playlist.delete('/api/v1/playlists/<int:playlist_id>')
def delete_playlist(playlist_id):
    try:
        playlist_ = Playlist.query.get(playlist_id)

        if playlist_:

            db.session.delete(playlist_)

            db.session.commit()

            return jsonify({'message': f'Playlist deleted successfully!'}), 200
        else:
            return jsonify({'message': 'Playlist not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message':str(e)})