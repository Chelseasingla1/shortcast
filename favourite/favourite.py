from flask import Blueprint, request, jsonify
import logging
from models import db, Favourite
from flask_login import current_user,login_required
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

favourite = Blueprint("favourite", __name__)

@login_required
@favourite.get('/api/v1/favourites')
def list_favourites():
    """
    List all favourites.
    ---
    tags:
        - Favourite
    get:
        description: Retrieve a list of all favourites (either podcast or episode).
        responses:
            200:
                description: A list of all favourites.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Favourite'
    """
    if not current_user.is_authenticated:
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 403

    favourite_list: list[Favourite] = Favourite.query.filter_by(user_id=current_user.id).all()
    favourite_list_dict = [item.to_dict() for item in favourite_list]
    return jsonify({'status': 'success', 'message': 'got downloads', 'data': favourite_list_dict}), 201

@login_required
@favourite.get('/api/v1/favourites/podcast')
def favourites_podcast_count():
    data = request.json
    podcast_id = data.get('podcast_id')
    try:
        count = 0
        favourite_list = Favourite.query.filter_by(podcast_id=podcast_id).all()
        count = len(favourite_list)
        return jsonify({'status': 'success', 'message': 'Retrieved number of likes', 'data': count}), 200
    except Exception as e:
        logger.error(f"Error retrieving numeber of likes: {str(e)}")
        return jsonify(
            {'status': 'error', 'message': 'Failed to retrieve number of likes', 'error_code': 'SERVER_ERROR',
             'data': None}), 500

@login_required
@favourite.post('/api/v1/favourites')
def add_podcast_to_favourite():
    """
    Add a podcast or episode to favourites.
    ---
    tags:
        - Favourite
    post:
        description: Add a podcast or episode to the user's favourites.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast (optional, either podcast_id or episode_id should be provided).
              required: false
            - name: episode_id
              in: body
              type: integer
              description: ID of the episode (optional, either podcast_id or episode_id should be provided).
              required: false
        responses:
            200:
                description: Successfully added to favourites.
            400:
                description: Missing required fields or invalid data.
    """
    data = request.json
    podcast_id = data.get('podcast_id')
    episode_id = data.get('episode_id')

    try:
        new_favourite = Favourite(user_id=current_user.id, podcast_id=podcast_id, episode_id=episode_id)
        db.session.add(new_favourite)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'added to favourite', 'data': None}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'favourite action failed', 'error_code': 'SERVER ERROR',
                        'data': None}), 500

@login_required
@favourite.delete('/api/v1/favourites')
def remove_from_favourite():
    """
    Remove a podcast or episode from favourites.
    ---
    tags:
        - Favourite
    delete:
        description: Remove a podcast or episode from the user's favourites.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast (optional, either podcast_id or episode_id should be provided).
              required: false
            - name: episode_id
              in: body
              type: integer
              description: ID of the episode (optional, either podcast_id or episode_id should be provided).
              required: false
        responses:
            200:
                description: Successfully removed from favourites.
            404:
                description: Favourite not found.
    """
    data = request.json
    podcast_id = data.get('podcast_id')
    episode_id = data.get('episode_id')

    try:
        favourite_ = None
        if podcast_id:
            favourite_ = Favourite.query.filter_by(user_id=current_user.id, podcast_id=podcast_id).first()
        elif episode_id:
            favourite_ = Favourite.query.filter_by(user_id=current_user.id, episode_id=episode_id).first()

        if favourite_:
            db.session.delete(favourite_)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'removed from favourite', 'data': None}), 201
        else:
            return jsonify({'status': 'error', 'message': 'Not found','data':None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'favourite not removed', 'error_code': 'SERVER ERROR',
                        'data': None}), 500

