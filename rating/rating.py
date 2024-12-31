from flask import Blueprint, request, jsonify
import logging
from models import db, Rating

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rating = Blueprint("rating", __name__)


@rating.get('/api/v1/ratings')
def list_ratings() -> list[Rating]:
    rating_list: list[Rating] = Rating.query.all()
    return rating_list


@rating.post('/api/v1/ratings')
def rate_podcast_episode():
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')
    try:
        new_rating = Rating(user_id=user_id,podcast_id=podcast_id)
        db.session.add(new_rating)

        db.session.commit()
        return jsonify({'msg': 'successfully rated'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"


@rating.delete('/api/v1/ratings')
def remove_rating():
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')


    try:
        rating_ = Rating.query.filter_by(user_id=user_id, podcast_id=podcast_id).first()

        if rating_:
            # Mark the user for deletion
            db.session.delete(rating_)

            # Commit the transaction (this deletes the user from the database)
            db.session.commit()

            return jsonify({'message': f'Rating removed successfully!'}), 200
        else:
            return jsonify({'message': 'Rating not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)})