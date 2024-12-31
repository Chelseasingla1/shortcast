from flask import Blueprint, request, jsonify
import logging
from models import db, PlaylistItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

playlistitem = Blueprint("playlistitem", __name__)


@playlistitem.get('/api/v1/playlistitems')
def list_playlist_items() -> list[PlaylistItem]:
    playlist_item_list: list[PlaylistItem] = PlaylistItem.query.all()
    return playlist_item_list


@playlistitem.post('/api/v1/playlistitems')
def add_playlist_item():
    data = request.json
    podcast_id = data.get('podcast_id')
    episode_id = data.get('episode_id')
    try:
        new_playlist_item = None
        if podcast_id:
            new_playlist_item = PlaylistItem(podcast_id=podcast_id)
        elif episode_id:
            new_playlist_item = PlaylistItem(episode_id=episode_id)
        db.session.add(new_playlist_item)

        db.session.commit()
        return jsonify({'msg': 'successfully added playlist item'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"


@playlistitem.delete('/api/v1/playlistitems/<int:playlist_item_id>')
def delete_playlist_item(playlist_item_id):
    try:
        # TODO : find a way to consume ..
        playlist_item_ = PlaylistItem.query.get(playlist_item_id)

        if playlist_item_:
            db.session.delete(playlist_item_)

            db.session.commit()

            return jsonify({'message': f'PlaylistItem {id} deleted successfully!'}), 200
        else:
            return jsonify({'message': 'PlaylistItem not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)})