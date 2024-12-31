from flask import Blueprint,jsonify,request
import logging
from models import db,Subscription
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

subscription = Blueprint("subscription", __name__)

@subscription.get('/api/v1/subscriptions')
def list_subscriptions() -> list[Subscription]:
    subscription_list:list[Subscription] = Subscription.query.all()
    return subscription_list


@subscription.post('/api/v1/subscriptions')
def subscribe_to_podcast():
    data = request.json
    user_id = data.get('user_id')
    podcast_id = data.get('podcast_id')
    try:
        new_subscription = Subscription(user_id = user_id,podcast_id=podcast_id)
        db.session.add(new_subscription)
        db.session.commit()
        return jsonify({'msg':'successfully subscribed'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"

@subscription.delete('/api/v1/subscriptions')
def unsubscribe():
    try:
        data = request.json
        user_id = data.get('user_id')
        podcast_id = data.get('podcast_id')
        subscription_ = Subscription.query.filter_by(user_id=user_id, podcast_id=podcast_id).first()


        if subscription_:

            db.session.delete(subscription_)

            db.session.commit()

            return jsonify({'message': f'unsubscribed successfully!'}), 200
        else:
            return jsonify({'message': 'Subscription not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message':str(e)})