from flask import request,jsonify,Blueprint
from models import db,Playlist,PlaylistItem,PlaylistPlaylistitem
import logging
from  flask_login import login_required
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


playlist_item_bp = Blueprint('playlist_item', __name__)


@login_required
@playlist_item_bp.post('/api/v1/playlists/<int:playlist_id>/playlist_items')
def add_playlist_item_to_playlist(playlist_id):
    """
    Add a PlaylistItem to a Playlist.
    ---
    tags:
        - Playlist
    post:
        description: Add a PlaylistItem to a specific Playlist.
        parameters:
            - name: playlist_id
              in: path
              type: integer
              description: ID of the playlist to add the item to.
              required: true
            - name: playlist_item_id
              in: body
              type: integer
              description: ID of the PlaylistItem to add to the Playlist.
              required: true
        responses:
            200:
                description: PlaylistItem successfully added to the Playlist.
            404:
                description: Playlist or PlaylistItem not found.
            500:
                description: Server error while adding PlaylistItem.
    """
    data = request.json
    playlist_item_id = data.get('playlist_item_id')

    if not playlist_item_id:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        # Ensure the playlist exists
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'status': 'error', 'message': 'Playlist not found', 'data': None}), 404

        # Ensure the playlist item exists
        playlist_item = PlaylistItem.query.get(playlist_item_id)
        if not playlist_item:
            return jsonify({'status': 'error', 'message': 'PlaylistItem not found', 'data': None}), 404

        # Create the relationship entry in PlaylistPlaylistitem table
        new_playlist_item = PlaylistPlaylistitem(playlist_id=playlist_id, playlist_item_id=playlist_item_id)
        db.session.add(new_playlist_item)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'PlaylistItem added to Playlist', 'data': new_playlist_item.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding PlaylistItem to Playlist {playlist_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to add PlaylistItem to Playlist', 'error_code': 'SERVER_ERROR', 'data': None}), 500

@login_required
@playlist_item_bp.delete('/api/v1/playlists/<int:playlist_id>/playlist_items')
def remove_playlist_item_from_playlist(playlist_id):
    """
    Remove a PlaylistItem from a Playlist.
    ---
    tags:
        - Playlist
    delete:
        description: Remove a PlaylistItem from a specific Playlist.
        parameters:
            - name: playlist_id
              in: path
              type: integer
              description: ID of the playlist to remove the item from.
              required: true
            - name: playlist_item_id
              in: body
              type: integer
              description: ID of the PlaylistItem to remove from the Playlist.
              required: true
        responses:
            200:
                description: PlaylistItem successfully removed from the Playlist.
            404:
                description: Playlist or PlaylistItem not found.
            500:
                description: Server error while removing PlaylistItem.
    """
    data = request.json
    playlist_item_id = data.get('playlist_item_id')

    if not playlist_item_id:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        # Ensure the playlist exists
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'status': 'error', 'message': 'Playlist not found', 'data': None}), 404

        # Ensure the playlist item exists
        playlist_item = PlaylistItem.query.get(playlist_item_id)
        if not playlist_item:
            return jsonify({'status': 'error', 'message': 'PlaylistItem not found', 'data': None}), 404

        # Find and delete the relationship entry in PlaylistPlaylistitem table
        playlist_playlist_item = PlaylistPlaylistitem.query.filter_by(playlist_id=playlist_id, playlist_item_id=playlist_item_id).first()
        if not playlist_playlist_item:
            return jsonify({'status': 'error', 'message': 'PlaylistItem not found in Playlist', 'data': None}), 404

        db.session.delete(playlist_playlist_item)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'PlaylistItem removed from Playlist', 'data': None}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing PlaylistItem from Playlist {playlist_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to remove PlaylistItem from Playlist', 'error_code': 'SERVER_ERROR', 'data': None}), 500

@login_required
@playlist_item_bp.get('/api/v1/playlists/<int:playlist_id>/playlist_items')
def list_playlist_items_in_playlist(playlist_id):
    """
    List all PlaylistItems in a Playlist.
    ---
    tags:
        - Playlist
    get:
        description: Retrieve a list of all PlaylistItems in a specific Playlist.
        parameters:
            - name: playlist_id
              in: path
              type: integer
              description: ID of the playlist to retrieve the items from.
              required: true
        responses:
            200:
                description: A list of PlaylistItems in the Playlist.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/PlaylistItem'
            404:
                description: Playlist not found.
            500:
                description: Server error while retrieving PlaylistItems.
    """
    try:
        # Ensure the playlist exists
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'status': 'error', 'message': 'Playlist not found', 'data': None}), 404

        # Get all playlist items associated with this playlist
        playlist_items = PlaylistPlaylistitem.query.filter_by(playlist_id=playlist_id).all()
        if playlist_items:
            items_dict = [item.to_dict() for item in playlist_items]
            return jsonify({'status': 'success', 'message': 'Retrieved PlaylistItems', 'data': items_dict}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No PlaylistItems found for this Playlist', 'data': None}), 404
    except Exception as e:
        logger.error(f"Error retrieving PlaylistItems from Playlist {playlist_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve PlaylistItems', 'error_code': 'SERVER_ERROR', 'data': None}), 500
