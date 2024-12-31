from flask import Blueprint, request, jsonify
import logging
from models import db, Rating

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rating = Blueprint("rating", __name__)

@rating.get('/api/v1/ratings')
def list_ratings():
    """
    List all ratings.
    ---
    tags:
        - Rating
    get:
        description: Retrieve a list of all ratings.
        responses:
            200:
                description: A list of all ratings.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Rating'
    """
    try:
        rating_list = Rating.query.all()
        ratings_dict = [rating.to_dict() for rating in rating_list]
        return jsonify({'status': 'success', 'message': 'Retrieved all ratings', 'data': ratings_dict}), 200
    except Exception as e:
        logger.error(f"Error retrieving ratings: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve ratings', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@rating.post('/api/v1/ratings')
def rate_podcast_episode():
    """
    Rate a podcast episode.
    ---
    tags:
        - Rating
    post:
        description: Submit a rating for a podcast episode.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user submitting the rating.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast being rated.
              required: true
        responses:
            200:
                description: Successfully rated the podcast episode.
            400:
                description: Missing required fields or invalid data.
    """
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')

    if not user_id or not podcast_id:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        new_rating = Rating(user_id=user_id, podcast_id=podcast_id)
        db.session.add(new_rating)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Successfully rated the podcast episode', 'data': new_rating.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rating podcast: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to rate podcast', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@rating.delete('/api/v1/ratings')
def remove_rating():
    """
    Remove a rating for a podcast episode.
    ---
    tags:
        - Rating
    delete:
        description: Remove a rating for a podcast episode by a specific user.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user who rated the podcast.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast that was rated.
              required: true
        responses:
            200:
                description: Rating removed successfully.
            404:
                description: Rating not found.
    """
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')

    if not user_id or not podcast_id:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        rating_ = Rating.query.filter_by(user_id=user_id, podcast_id=podcast_id).first()

        if rating_:
            db.session.delete(rating_)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Rating removed successfully', 'data': None}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Rating not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing rating: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to remove rating', 'error_code': 'SERVER_ERROR', 'data': None}), 500
