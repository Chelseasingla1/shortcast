from flask import Blueprint, request,url_for, redirect, session,jsonify
import logging
from models import User,db
from model_utils import role_check
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users = Blueprint("users", __name__)

@users.get('/api/v1/users')
def list_users() -> list[User]:
    user_list:list[User] = User.query.all()
    return user_list

@users.get('/api/v1/<id>')
def get_user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        return user
    else:
        return

@users.post('/api/v1/users')
def create_user():
    data = request.json
    oauth_provider = data.get('oauth_provider')
    oauth_id = data.get('oauth_id')
    username = data.get('username')
    profile_image_url = data.get('profile_image_url')
    email = data.get('email')
    role = role_check(str(data.get('role')).upper())
    try:
        new_user = User(oauth_provider = oauth_provider,oauth_id = oauth_id,username = username,profile_image_url = profile_image_url,email = email,role=role)
        db.session.add(new_user)

    # Commit the transaction (this makes the changes permanent in the database)
        db.session.commit()
        return jsonify({'msg':'successfully created user'})
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {str(e)}"

@users.put('/api/v1/users/<int:id>')
def update_user(id):
    data = request.json
    username = data.get('username')
    profile_image_url = data.get('profile_image_url')
    email = data.get('email')

    user = User.query.get(id)
    if user:
        if 'username' in data:
            user.username = username
        if 'profile_image_url' in data:
            user.profile_image_url = profile_image_url
        if 'email' in data:
            user.email = email
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error':str(e)})

        return jsonify({
            'message': 'User updated successfully!'
        })
    else:
        return jsonify({'message': 'User not found!'}), 404

@users.delete('/api/v1/users/<int:id>')
def delete_user(id):
    try:
        user = User.query.get(id)

        if user:
            # Mark the user for deletion
            db.session.delete(user)

            # Commit the transaction (this deletes the user from the database)
            db.session.commit()

            return jsonify({'message': f'User {id} deleted successfully!'}), 200
        else:
            return jsonify({'message': 'User not found!'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message':str(e)})