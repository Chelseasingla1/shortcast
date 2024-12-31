from flask import Blueprint, request,jsonify
import logging
from models import db,Episode,Podcast
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

episode = Blueprint("episode", __name__)

@episode.get('/api/v1/episodes')
def list_episodes() -> list[Episode]:
    episode_list:list[Episode] = Episode.query.all()
    return episode_list

@episode.get('/api/v1/episodes/<episode_id>')
def get_episode(episode_id):
    episode_ = Episode.query.filter_by(id=episode_id).first()
    if episode_:
        return episode_
    else:
        return

@episode.post('/api/v1/episodes')
def create_episode():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    duration = data.get('duration')
    audio_url = data.get('audio_url')
    podcast_id = data.get('podcast_id')
    # TODO : correct duration datatype in Episode

    if not podcast_id:
        return jsonify({'msg': 'Podcast ID is required'}), 400

        # Fetch the podcast by ID
    podcast = Podcast.query.get(podcast_id)

    # If no podcast is found, return an error
    if not podcast:
        return jsonify({'msg': 'Podcast not found'}), 404

    try:
        new_episode = Episode(title=title,description = description,audio_url = audio_url,podcast=podcast)
        db.session.add(new_episode)

    # Commit the transaction (this makes the changes permanent in the database)
        db.session.commit()
        return jsonify({'msg':'successfully created episode'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"

@episode.put('/api/v1/episodes/<int:episode_id>')
def update_episode(episode_id):
    data = request.json
    title = data.get('title')
    description = data.get('description')
    episode_ = Episode.query.get(episode_id)
    if episode_:
        if 'title' in data:
            episode_.title = title
        if 'description' in data:
            episode_.description = description
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error':str(e)})

        return jsonify({
            'message': 'Episode updated successfully!'
        })
    else:
        return jsonify({'message': 'Episode not found!'}), 404

@episode.delete('/api/v1/episodes/<int:episode_id>')
def delete_episode(episode_id):
    try:
        episode_ = Episode.query.get(episode_id)

        if episode_:
            # Mark the user for deletion
            db.session.delete(episode_)

            # Commit the transaction (this deletes the user from the database)
            db.session.commit()

            return jsonify({'message': f'Episode {episode_id} deleted successfully!'}), 200
        else:
            return jsonify({'message': 'Episode not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message':str(e)})