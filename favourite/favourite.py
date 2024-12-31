from flask import Blueprint, request, jsonify
import logging
from models import db, Favourite

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

favourite = Blueprint("favourite", __name__)


@favourite.get('/api/v1/favourites')
def list_favourites() -> list[Favourite]:
    favourite_list: list[Favourite] = Favourite.query.all()
    return favourite_list


@favourite.post('/api/v1/favourites')
def add_podcast_to_favourite():
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')
    episode_id = data.get('episode_id')

    try:
        new_favourite = Favourite(user_id=user_id,podcast_id=podcast_id,episode_id=episode_id)
        db.session.add(new_favourite)

        # Commit the transaction (this makes the changes permanent in the database)
        db.session.commit()
        return jsonify({'msg': 'successfully added to favourite'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"


@favourite.delete('/api/v1/favourites')
def remove_from_favourite():
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')
    episode_id = data.get('episode_id')

    try:
        favourite_= None
        if podcast_id:
            favourite_ = Favourite.query.filter_by(user_id=user_id, podcast_id=podcast_id).first()
        elif episode_id:
            favourite_ = Favourite.query.filter_by(user_id=user_id, episode_id=episode_id).first()

        if favourite_:
            # Mark the user for deletion
            db.session.delete(favourite_)
            db.session.commit()

            return jsonify({'message': f'Favourite {id} deleted successfully!'}), 200
        else:
            return jsonify({'message': 'Favourite not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)})