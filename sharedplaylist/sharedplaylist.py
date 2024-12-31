from flask import Blueprint, request, jsonify
import logging
from models import db, SharedPlaylist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

shared_playlist = Blueprint("shared_playlist", __name__)

@shared_playlist.get('/api/v1/shared_playlists')
def list_shared_playlists():
    """
    List all shared playlists.
    ---
    tags:
        - Shared Playlist
    get:
        description: Retrieve a list of all shared playlists.
        responses:
            200:
                description: A list of all shared playlists.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/SharedPlaylist'
    """
    try:
        shared_playlist_list = SharedPlaylist.query.all()
        playlists_dict = [playlist.to_dict() for playlist in shared_playlist_list]
        return jsonify({'status': 'success', 'message': 'Retrieved all shared playlists', 'data': playlists_dict}), 200
    except Exception as e:
        logger.error(f"Error retrieving shared playlists: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve shared playlists', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@shared_playlist.post('/api/v1/shared_playlists')
def share_playlist():
    """
    Share a playlist with a user.
    ---
    tags:
        - Shared Playlist
    post:
        description: Share a playlist with a specific user.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user sharing the playlist.
              required: true
            - name: playlist_id
              in: body
              type: integer
              description: ID of the playlist to share.
              required: true
        responses:
            200:
                description: Playlist successfully shared.
            400:
                description: Missing required fields or invalid data.
    """
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')

    if not user_id or not playlist_id:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        new_shared_playlist = SharedPlaylist(user_id=user_id, playlist_id=playlist_id)
        db.session.add(new_shared_playlist)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Playlist successfully shared', 'data': new_shared_playlist.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sharing playlist: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to share playlist', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@shared_playlist.delete('/api/v1/shared_playlists')
def unshare_playlist():
    """
    Unshare a playlist from a user.
    ---
    tags:
        - Shared Playlist
    delete:
        description: Remove a shared playlist from a specific user.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user who shared the playlist.
              required: true
            - name: playlist_id
              in: body
              type: integer
              description: ID of the playlist to unshare.
              required: true
        responses:
            200:
                description: Playlist successfully unshared.
            404:
                description: Shared playlist not found.
    """
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')

    if not user_id or not playlist_id:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        shared_playlist_ = SharedPlaylist.query.filter_by(user_id=user_id, playlist_id=playlist_id).first()

        if shared_playlist_:
            db.session.delete(shared_playlist_)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Playlist successfully unshared', 'data': None}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Shared playlist not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error unsharing playlist: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to unshare playlist', 'error_code': 'SERVER_ERROR', 'data': None}), 500
