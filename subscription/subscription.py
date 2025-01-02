from flask import Blueprint, jsonify, request
import logging
from models import db, Subscription
from flask_login import current_user,login_required
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

subscription = Blueprint("subscription", __name__)

@login_required
@subscription.get('/api/v1/subscriptions')
def list_subscriptions():
    """
    List all subscriptions.
    ---
    tags:
        - Subscription
    get:
        description: Retrieve a list of all subscriptions.
        responses:
            200:
                description: A list of all subscriptions.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Subscription'
    """
    data = request.json

    try:

        subscription_list = Subscription.query.all()
        subscriptions_dict = [subscription.to_dict() for subscription in subscription_list]
        return jsonify({'status': 'success', 'message': 'Retrieved all subscriptions', 'data': subscriptions_dict}), 200
    except Exception as e:
        logger.error(f"Error retrieving subscriptions: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve subscriptions', 'error_code': 'SERVER_ERROR', 'data': None}), 500

@login_required
@subscription.get('/api/v1/subscriptions/podcast')
def list_podcast_subscribers_count():
    data = request.json
    podcast_id = data.get('podcast_id')
    try:
        count = 0
        subscription_list = Subscription.query.filter_by(podcast_id=podcast_id).all()
        count = len(subscription_list)
        return jsonify({'status': 'success', 'message': 'Retrieved podcast subscriber count', 'data': count}), 200
    except Exception as e:
        logger.error(f"Error retrieving podcast subscriber count: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve podcast subscribers count', 'error_code': 'SERVER_ERROR', 'data': None}), 500

@login_required
@subscription.get('/api/v1/subscriptions/subscribed')
def list_subscriber_subscribed():
    data = request.json
    try:
        count = 0
        subscription_list = Subscription.query.filter_by(podcast_id=current_user.id).all()
        subscriptions_dict = [item.podcast.to_dict() for item in subscription_list]
        count = len(subscription_list)
        result = {'podcasts':subscriptions_dict,'count':count}
        return jsonify({'status': 'success', 'message': 'Retrieved podcast subscriber count', 'data': result}), 200
    except Exception as e:
        logger.error(f"Error retrieving podcast subscriber count: {str(e)}")
        return jsonify(
            {'status': 'error', 'message': 'Failed to retrieve podcast subscribers count', 'error_code': 'SERVER_ERROR',
             'data': None}), 500

@login_required
@subscription.post('/api/v1/subscriptions')
def subscribe_to_podcast():
    """
    Subscribe a user to a podcast.
    ---
    tags:
        - Subscription
    post:
        description: Subscribe a user to a specific podcast.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user subscribing to the podcast.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast to subscribe to.
              required: true
        responses:
            200:
                description: Successfully subscribed to the podcast.
            400:
                description: Missing required fields or invalid data.
    """
    data = request.json
    user_id = current_user.id
    podcast_id = data.get('podcast_id')
    print(user_id,podcast_id)
    if not user_id or not podcast_id:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        new_subscription = Subscription(user_id=user_id, podcast_id=podcast_id)
        db.session.add(new_subscription)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Successfully subscribed to the podcast', 'data': new_subscription.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error subscribing to podcast: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to subscribe to podcast', 'error_code': 'SERVER_ERROR', 'data': None}), 500

@login_required
@subscription.delete('/api/v1/subscriptions')
def unsubscribe():
    """
    Unsubscribe a user from a podcast.
    ---
    tags:
        - Subscription
    delete:
        description: Unsubscribe a user from a specific podcast.
        parameters:
            - name: user_id
              in: body
              type: integer
              description: ID of the user unsubscribing from the podcast.
              required: true
            - name: podcast_id
              in: body
              type: integer
              description: ID of the podcast to unsubscribe from.
              required: true
        responses:
            200:
                description: Successfully unsubscribed from the podcast.
            404:
                description: Subscription not found.
    """
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')

    if not user_id or not podcast_id:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        subscription_ = Subscription.query.filter_by(user_id=user_id, podcast_id=podcast_id).first()

        if subscription_:
            db.session.delete(subscription_)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Successfully unsubscribed from the podcast', 'data': None}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Subscription not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error unsubscribing from podcast: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to unsubscribe from podcast', 'error_code': 'SERVER_ERROR', 'data': None}), 500
