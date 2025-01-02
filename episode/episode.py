import os

from flask import Blueprint, request,jsonify
from flask_login import current_user,login_required
import logging
from models import db,Episode,Podcast
from webhook_security import verify_signature
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
episode = Blueprint("episode", __name__)

@login_required
@episode.get('/api/v1/episodes')
def list_episodes():
    """
    List all episodes in a podcast.
    ---
    tags:
        - Episode
    get:
        description: Retrieve a list of all episodes in a podcast.
        parameters:
            - name: podcast_id
              in: body
              type: integer
              description: podcast id.
              required: true
        responses:
            200:
                description: A list of all episodes.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Episode'
    """

    data = request.json
    podcast_id = data.get('podcast_id')
    if not current_user.is_authenticated:
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 403

    episode_list: list[Episode] = Episode.query.filter_by(podcast_id=podcast_id).all()
    if episode_list:
        episode_list_dict = [item.to_dict() for item in episode_list]
        return jsonify({'status': 'success', 'message': 'list of episodes', 'data': episode_list_dict}), 200
    else:
        return jsonify({'status': 'error', 'message': 'episode is empty', 'data': None}), 404

@login_required
@episode.get('/api/v1/episodes/<episode_id>')
def get_episode(episode_id):
    """
    Get a specific episode by ID.
    ---
    tags:
        - Episode
    get:
        description: Retrieve a specific episode by its ID.
        parameters:
            - name: episode_id
              in: path
              type: integer
              description: ID of the episode.
              required: true
        responses:
            200:
                description: Episode found.
                schema:
                    $ref: '#/definitions/Episode'
            404:
                description: Episode not found.
    """
    episode_ = Episode.query.filter_by(id=episode_id).first()
    if episode_:
        episode_list_dict = [item.to_dict() for item in episode_]
        return jsonify({'status': 'success', 'message': 'fetched episode', 'data': episode_list_dict}), 200
    else:
        return jsonify({'status': 'error', 'message': 'episode not found', 'data':None}), 400

@login_required
@episode.post('/api/v1/episodes')
def create_episode():
    """
    Create a new episode.
    ---
    tags:
        - Episode
    post:
        description: Create a new podcast episode.
        parameters:
            - name: title
              in: body
              type: string
              description: Title of the episode.
              required: true
            - name: description
              in: body
              type: string
              description: Description of the episode.
              required: true
            - name: duration
              in: body
              type: integer
              description: Duration of the episode (in seconds).
              required: false
            - name: audio_url
              in: body
              type: string
              description: URL of the audio file for the episode.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast the episode belongs to.
              required: true
        responses:
            200:
                description: Episode created successfully.
            400:
                description: Missing required podcast ID or other fields.
            404:
                description: Podcast not found.
    """
    payload = request.data.decode('utf-8')
    signature = request.headers.get('X-Signature')
    webhook_secret = os.environ.get('WEBHOOK_SECRET')
    if not verify_signature(payload,signature,webhook_secret):
        return jsonify({'status': 'error', 'message': 'Invalid signature'}), 403
    data = request.json
    title = data.get('title')
    description = data.get('description')
    image_url = data.get('image_url')
    duration = data.get('duration')
    audio_url = data.get('audio_url')
    podcast_id = data.get('podcast_id')


    if not podcast_id:
        return jsonify({'status': 'error', 'message': 'podcast id not found','data':None}), 400

    podcast = Podcast.query.get(podcast_id)

    if not podcast:
        return jsonify({'status': 'error', 'message': 'Podcast not found','data':None}), 400

    try:
        new_episode = Episode(title=title, description=description, audio_url=audio_url, podcast=podcast,image_url=image_url)
        db.session.add(new_episode)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'created episode', 'data':None}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify(
            {'status': 'error', 'message': 'episode not created', 'error_code': 'SERVER ERROR', 'data': None}), 500

@login_required
@episode.put('/api/v1/episodes/<int:episode_id>')
def update_episode(episode_id):
    """
    Update an episode.
    ---
    tags:
        - Episode
    put:
        description: Update an existing episode by its ID.
        parameters:
            - name: episode_id
              in: path
              type: integer
              description: ID of the episode.
              required: true
            - name: title
              in: body
              type: string
              description: New title of the episode.
              required: false
            - name: description
              in: body
              type: string
              description: New description of the episode.
              required: false
        responses:
            200:
                description: Episode updated successfully.
            404:
                description: Episode not found.
    """
    payload = request.data.decode('utf-8')
    signature = request.headers.get('X-Signature')
    webhook_secret = os.environ.get('WEBHOOK_SECRET')
    if not verify_signature(payload, signature, webhook_secret):
        return jsonify({'status': 'error', 'message': 'Invalid signature'}), 403
    data = request.json
    title = data.get('title')
    description = data.get('description')
    episode_ = Episode.query.get(episode_id)
    if episode_:
        if episode_.podcast.user_id != current_user.id:
            return jsonify(
                {'status': 'error', 'message': 'You are not authorized to delete this podcast', 'data': None}), 403

        if 'title' in data:
            episode_.title = title
        if 'description' in data:
            episode_.description = description
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(str(e))
            return jsonify({'status': 'error', 'message': 'episode not updated', 'error_code': 'SERVER ERROR',
                            'data': None}), 500

        return jsonify({'status': 'success', 'message': 'episode updated', 'data': None}), 201
    else:
        return jsonify({'status': 'error', 'message': 'episode not found','data':None}), 404

@login_required
@episode.delete('/api/v1/episodes/<int:episode_id>')
def delete_episode(episode_id):
    """
    Delete an episode.
    ---
    tags:
        - Episode
    delete:
        description: Delete an episode by its ID.
        parameters:
            - name: episode_id
              in: path
              type: integer
              description: ID of the episode to delete.
              required: true
        responses:
            200:
                description: Episode deleted successfully.
            404:
                description: Episode not found.
    """
    try:
        episode_ = Episode.query.get(episode_id)

        if episode_:
            if episode_.podcast.user_id != current_user.id:
                return jsonify(
                    {'status': 'error', 'message': 'You are not authorized to delete this podcast', 'data': None}), 403

            db.session.delete(episode_)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Episode deleted', 'data': None}), 201
        else:
            return jsonify({'status': 'error', 'message': 'episode not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'episode not updated', 'error_code': 'SERVER ERROR',
                        'data': None}), 500
