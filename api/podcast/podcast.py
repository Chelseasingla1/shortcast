from flask import Blueprint, request, jsonify
import logging
from api.webhook_security import verify_signature
from flask_login import current_user,login_required
import os
from models import db, Podcast
from model_utils import provider_check


podcast = Blueprint("podcast", __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_required
@podcast.get('/api/v1/podcasts')
def list_podcasts():
    """
    List all podcasts.
    ---
    tags:
        - Podcast
    get:
        description: Retrieve a list of all podcasts.
        responses:
            200:
                description: A list of all podcasts.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Podcast'
    """
    try:
        podcast_list = Podcast.query.all()
        if podcast_list:
            podcast_list_dict = [item.to_dict() for item in podcast_list]
            return jsonify({'status': 'success', 'message': 'retrieved all podcasts', 'data': podcast_list_dict}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Podcast is empty', 'data': None}), 404
    except Exception as e:
        logger.error(str(e))
        return jsonify(
            {'status': 'error', 'message': 'Failed to retrieve podcasts', 'error_code': 'SERVER_ERROR', 'data': None}), 500

@login_required
@podcast.get('/api/v1/podcasts/<int:podcast_id>')
def get_podcast(podcast_id):
    """
    Get a podcast by its ID.
    ---
    tags:
        - Podcast
    get:
        description: Retrieve details of a specific podcast by its ID.
        parameters:
            - name: podcast_id
              in: path
              type: integer
              description: ID of the podcast to retrieve.
              required: true
        responses:
            200:
                description: Details of the podcast.
                schema:
                    $ref: '#/definitions/Podcast'
            404:
                description: Podcast not found.
    """
    podcast_ = Podcast.query.filter_by(id=podcast_id).first()
    if podcast_:
        return jsonify({'status': 'success', 'message': 'retrieved podcast details', 'data': podcast_.to_dict()}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Podcast not found!', 'data': None}), 404

@login_required
@podcast.post('/api/v1/podcasts')
def create_podcast():
    """
    Create a new podcast.
    ---
    tags:
        - Podcast
    post:
        description: Create a new podcast with the provided data.
        parameters:
            - name: title
              in: body
              type: string
              description: Title of the podcast.
              required: true
            - name: description
              in: body
              type: string
              description: Description of the podcast.
              required: true
            - name: category
              in: body
              type: string
              description: Category of the podcast.
              required: true
            - name: publisher
              in: body
              type: string
              description: Publisher of the podcast.
              required: true
            - name: image_url
              in: body
              type: string
              description: Image URL for the podcast cover.
              required: false
            - name: feed_url
              in: body
              type: string
              description: RSS Feed URL for the podcast.
              required: false
            - name: audio_url
              in: body
              type: string
              description: Audio URL for the podcast.
              required: true
            - name: duration
              in: body
              type: string
              description: Duration of the podcast episode.
              required: false
        responses:
            200:
                description: Successfully created the podcast.
            400:
                description: Missing required fields or invalid data.
    """
    data = request.json
    title = data.get('title')
    description = data.get('description')
    category = str(data.get('category')).upper()
    publisher = current_user.username
    image_url = data.get('image_url')
    feed_url = data.get('feed_url')
    audio_url = data.get('audio_url')
    duration = data.get('duration')

    if not title or not description or not category or not publisher:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400
    if feed_url and audio_url:
        return jsonify({'status': 'error', 'message': 'Provide either feed_url or audio_url not both', 'data': None}), 400

    try:
        new_podcast = None
        if audio_url:
            payload = request.data.decode('utf-8')
            signature = request.headers.get('X-Signature')
            webhook_secret = os.environ.get('WEBHOOK_SECRET')
            if not verify_signature(payload, signature, webhook_secret):
                return jsonify({'status': 'error', 'message': 'Invalid signature'}), 403
            new_podcast = Podcast(title=title, description=description, category=category, publisher=publisher,
                              image_url=image_url, audio_url=audio_url, duration=duration,user_id=current_user.id)
        if feed_url:
            new_podcast = Podcast(title=title, description=description, category=category, publisher=publisher,
                                  image_url=image_url, feed_url=feed_url, duration=duration,user_id=current_user.id)

        db.session.add(new_podcast)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Podcast created successfully', 'data': new_podcast.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating podcast: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Podcast not created', 'error_code': 'SERVER_ERROR', 'data': None}), 500

@login_required
@podcast.put('/api/v1/podcasts/<int:podcast_id>')
def update_podcast(podcast_id):
    """
    Update an existing podcast.
    ---
    tags:
        - Podcast
    put:
        description: Update a podcast's details by its ID.
        parameters:
            - name: podcast_id
              in: path
              type: integer
              description: ID of the podcast to update.
              required: true
            - name: title
              in: body
              type: string
              description: New title of the podcast.
              required: false
            - name: description
              in: body
              type: string
              description: New description of the podcast.
              required: false
            - name: category
              in: body
              type: string
              description: New category of the podcast.
              required: false
            - name: image_url
              in: body
              type: string
              description: New image URL for the podcast cover.
              required: false
        responses:
            200:
                description: Podcast updated successfully.
            404:
                description: Podcast not found.
    """

    data = request.json
    title = data.get('title')
    description = data.get('description')
    category = provider_check(str(data.get('category')).upper())
    image_url = data.get('image_url')

    podcast_ = Podcast.query.get(podcast_id)
    if podcast_:
        if podcast_.user_id != current_user.id:
            return jsonify(
                {'status': 'error', 'message': 'You are not authorized to update this podcast', 'data': None}), 403

        if 'title' in data:
            podcast_.title = title
        if 'description' in data:
            podcast_.description = description
        if 'category' in data:
            podcast_.category = category
        if 'image_url' in data:
            podcast_.image_url = image_url

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e), 'data': None}), 500

        return jsonify({'status': 'success', 'message': 'Podcast updated successfully!', 'data': podcast_.to_dict()}), 201
    else:
        return jsonify({'status': 'error', 'message': 'Podcast not found!', 'data': None}), 404

@login_required
@podcast.delete('/api/v1/podcasts/<int:podcast_id>')
def delete_podcast(podcast_id):
    """
    Delete a podcast by its ID.
    ---
    tags:
        - Podcast
    delete:
        description: Delete a podcast by its ID.
        parameters:
            - name: podcast_id
              in: path
              type: integer
              description: ID of the podcast to delete.
              required: true
        responses:
            200:
                description: Podcast deleted successfully.
            404:
                description: Podcast not found.
    """
    try:
        podcast_ = Podcast.query.get(podcast_id)

        if podcast_:
            if podcast_.audio_url:
                payload = request.data.decode('utf-8')
                signature = request.headers.get('X-Signature')
                webhook_secret = os.environ.get('WEBHOOK_SECRET')

                if not verify_signature(payload, signature, webhook_secret):
                    return jsonify({'status': 'error', 'message': 'Invalid signature'}), 403

            if podcast_.user_id != current_user.id:
                return jsonify(
                    {'status': 'error', 'message': 'You are not authorized to delete this podcast', 'data': None}), 403

            db.session.delete(podcast_)
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'Podcast {podcast_id} deleted successfully!', 'data': None}), 201
        else:
            return jsonify({'status': 'error', 'message': 'Podcast not found!', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting podcast: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Podcast not deleted', 'error_code': 'SERVER_ERROR', 'data': None}), 500
