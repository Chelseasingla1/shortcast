from flask import Blueprint, request, jsonify
import logging
from models import db, PlaylistItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

playlistitem = Blueprint("playlistitem", __name__)

@playlistitem.get('/api/v1/playlistitems')
def list_playlist_items():
    """
    List all playlist items.
    ---
    tags:
        - PlaylistItem
    get:
        description: Retrieve a list of all playlist items.
        responses:
            200:
                description: A list of all playlist items.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/PlaylistItem'
    """
    playlist_item_list = PlaylistItem.query.all()
    playlist_item_list_dict = [item.to_dict() for item in playlist_item_list]
    return jsonify({'status': 'success', 'message': 'retrieved all playlist items', 'data': playlist_item_list_dict}), 200


@playlistitem.post('/api/v1/playlistitems')
def add_playlist_item():
    """
    Add a new item to a playlist.
    ---
    tags:
        - PlaylistItem
    post:
        description: Add a new podcast or episode to the playlist.
        parameters:
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast to add to the playlist.
              required: false
            - name: episode_id
              in: body
              type: integer
              description: ID of the episode to add to the playlist.
              required: false
        responses:
            200:
                description: Successfully added the playlist item.
            400:
                description: Missing podcast_id or episode_id in the request body.
    """
    data = request.json
    podcast_id = data.get('podcast_id')
    episode_id = data.get('episode_id')

    if not podcast_id and not episode_id:
        return jsonify({'status': 'error', 'message': 'missing podcast_id or episode_id', 'data': None}), 400

    try:
        new_playlist_item = None
        if podcast_id:
            new_playlist_item = PlaylistItem(podcast_id=podcast_id)
        elif episode_id:
            new_playlist_item = PlaylistItem(episode_id=episode_id)

        db.session.add(new_playlist_item)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'playlist item added', 'data': new_playlist_item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding playlist item: {str(e)}")
        return jsonify({'status': 'error', 'message': 'playlist item not added', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@playlistitem.delete('/api/v1/playlistitems/<int:playlist_item_id>')
def delete_playlist_item(playlist_item_id):
    """
    Delete a playlist item.
    ---
    tags:
        - PlaylistItem
    delete:
        description: Remove a playlist item from the playlist by its ID.
        parameters:
            - name: playlist_item_id
              in: path
              type: integer
              description: ID of the playlist item to delete.
              required: true
        responses:
            200:
                description: Playlist item deleted successfully.
            404:
                description: Playlist item not found.
    """
    try:
        playlist_item = PlaylistItem.query.get(playlist_item_id)

        if playlist_item:
            db.session.delete(playlist_item)
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'playlist item {playlist_item_id} deleted', 'data': None}), 200
        else:
            return jsonify({'status': 'error', 'message': 'playlist item not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting playlist item: {str(e)}")
        return jsonify({'status': 'error', 'message': 'playlist item not deleted', 'error_code': 'SERVER_ERROR', 'data': None}), 500
