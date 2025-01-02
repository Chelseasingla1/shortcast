from flask import Blueprint, request,jsonify
import logging
from models import db,Playlist
from flask_login import current_user


playlist = Blueprint("playlist", __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@playlist.get('/api/v1/playlists')
def list_playlists():
    """
    List all playlists.
    ---
    tags:
        - Playlist
    get:
        description: Retrieve a list of all playlists.
        responses:
            200:
                description: A list of all playlists.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Playlist'
    """
    playlist_list: list[Playlist] = Playlist.query.filter_by(user_id=current_user.id).all()

    if playlist_list:
        playlist_list_dict = [item.to_dict() for item in playlist_list]
        return jsonify({'status': 'success', 'message': 'got user private playlists', 'data': playlist_list_dict}), 200
    else:
        return jsonify({'status': 'error', 'message': 'playlist is empty', 'data': None}), 404

@playlist.get('/api/v1/playlists/<playlist_id>')
def get_playlist(playlist_id):
    """
    Get a specific playlist by ID.
    ---
    tags:
        - Playlist
    get:
        description: Retrieve a specific playlist by its ID.
        parameters:
            - name: playlist_id
              in: path
              type: integer
              description: ID of the playlist.
              required: true
        responses:
            200:
                description: The playlist details.
                schema:
                    $ref: '#/definitions/Playlist'
            404:
                description: Playlist not found.
    """
    playlist_ = Playlist.query.filter_by(id=playlist_id).first()
    if playlist_:
        return jsonify({'status': 'success', 'message': 'got downloads', 'data': playlist_}), 201
    else:
        return jsonify({'status': 'error', 'message': 'playlist not found','data':None}), 404


@playlist.post('/api/v1/playlists')
def create_playlist():
    """
    Create a new playlist.
    ---
    tags:
        - Playlist
    post:
        description: Create a new playlist for a user.
        parameters:
            - name: title
              in: body
              type: string
              description: Title of the new playlist.
              required: true
            - name: user_id
              in: body
              type: integer
              description: ID of the user creating the playlist.
              required: true
        responses:
            200:
                description: Successfully created the playlist.
            400:
                description: Missing required fields or invalid data.
    """
    data = request.json
    title = data.get('title')

    try:
        new_playlist = Playlist(title=title, user_id=current_user.id)
        db.session.add(new_playlist)

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'playlist created', 'data': None}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'playlist not created', 'error_code': 'SERVER ERROR',
                        'data': None}), 500


@playlist.put('/api/v1/playlists/<int:playlist_id>')
def update_playlist(playlist_id):
    """
    Update an existing playlist.
    ---
    tags:
        - Playlist
    put:
        description: Update the details of an existing playlist.
        parameters:
            - name: playlist_id
              in: path
              type: integer
              description: ID of the playlist to update.
              required: true
            - name: title
              in: body
              type: string
              description: The new title for the playlist.
              required: false
        responses:
            200:
                description: Playlist updated successfully.
            404:
                description: Playlist not found.
    """
    data = request.json
    title = data.get('title')
    playlist_ = Playlist.query.get(playlist_id)
    if playlist_:
        if playlist_.user_id != current_user.id:
            return jsonify(
                {'status': 'error', 'message': 'You are not authorized to delete this podcast', 'data': None}), 403
        if 'title' in data:
            playlist_.title = title
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)})

        return jsonify({'status': 'success', 'message': 'playlist updated', 'data': None}), 201
    else:
        return jsonify({'status': 'error', 'message': 'playlist not found', 'data': None}), 404


@playlist.delete('/api/v1/playlists/<int:playlist_id>')
def delete_playlist(playlist_id):
    """
    Delete a playlist.
    ---
    tags:
        - Playlist
    delete:
        description: Delete an existing playlist by its ID.
        parameters:
            - name: playlist_id
              in: path
              type: integer
              description: ID of the playlist to delete.
              required: true
        responses:
            200:
                description: Playlist deleted successfully.
            404:
                description: Playlist not found.
    """
    try:
        playlist_ = Playlist.query.get(playlist_id)

        if playlist_:
            if playlist_.user_id != current_user.id:
                return jsonify(
                    {'status': 'error', 'message': 'You are not authorized to delete this podcast', 'data': None}), 403
            db.session.delete(playlist_)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'playlist deleted', 'data': None}), 201
        else:
            return jsonify({'status': 'error', 'message': 'playlist not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'playlist not deleted', 'error_code': 'SERVER ERROR',
                        'data': None}), 500


