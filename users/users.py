from flask import Blueprint, request, jsonify
import logging
from models import User, db
from model_utils import role_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users = Blueprint("users", __name__)

@users.get('/api/v1/users')
def list_users():
    """
    List all users.
    ---
    tags:
        - User
    get:
        description: Retrieve a list of all users.
        responses:
            200:
                description: A list of all users.
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/User'
    """
    try:
        user_list = User.query.all()
        users_dict = [user.to_dict() for user in user_list]
        return jsonify({'status': 'success', 'message': 'Retrieved all users', 'data': users_dict}), 200
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve users', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@users.get('/api/v1/users/<int:user_id>')
def get_user(user_id):
    """
    Retrieve a user by their ID.
    ---
    tags:
        - User
    get:
        description: Retrieve a user by their unique ID.
        parameters:
            - name: user_id
              in: path
              type: integer
              description: ID of the user to retrieve.
              required: true
        responses:
            200:
                description: A user object.
                schema:
                    $ref: '#/definitions/User'
            404:
                description: User not found.
    """
    try:
        user = User.query.filter_by(id=user_id).first()
        if user:
            return jsonify({'status': 'success', 'message': 'User found', 'data': user.to_dict()}), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found', 'data': None}), 404
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve user', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@users.post('/api/v1/users')
def create_user():
    """
    Create a new user.
    ---
    tags:
        - User
    post:
        description: Create a new user in the system.
        parameters:
            - name: oauth_provider
              in: body
              type: string
              description: OAuth provider name (e.g., Google, Facebook).
              required: true
            - name: oauth_id
              in: body
              type: string
              description: OAuth ID of the user.
              required: true
            - name: username
              in: body
              type: string
              description: Username of the user.
              required: true
            - name: profile_image_url
              in: body
              type: string
              description: URL for the user's profile image.
              required: false
            - name: email
              in: body
              type: string
              description: User's email address.
              required: true
            - name: role
              in: body
              type: string
              description: Role of the user (e.g., admin, user).
              required: true
        responses:
            200:
                description: User successfully created.
            400:
                description: Missing or invalid parameters.
    """
    data = request.json
    oauth_provider = data.get('oauth_provider')
    oauth_id = data.get('oauth_id')
    username = data.get('username')
    profile_image_url = data.get('profile_image_url')
    email = data.get('email')
    role = role_check(str(data.get('role')).upper())

    if not oauth_provider or not oauth_id or not username or not email or not role:
        return jsonify({'status': 'error', 'message': 'Missing required fields', 'data': None}), 400

    try:
        new_user = User(
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            username=username,
            profile_image_url=profile_image_url,
            email=email,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User {username} successfully created.")
        return jsonify({'status': 'success', 'message': 'User successfully created', 'data': new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to add user: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to create user', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@users.put('/api/v1/users/<int:user_id>')
def update_user(user_id):
    """
    Update user information.
    ---
    tags:
        - User
    put:
        description: Update a user's information.
        parameters:
            - name: user_id
              in: path
              type: integer
              description: ID of the user to update.
              required: true
            - name: username
              in: body
              type: string
              description: New username.
              required: false
            - name: profile_image_url
              in: body
              type: string
              description: New profile image URL.
              required: false
            - name: email
              in: body
              type: string
              description: New email.
              required: false
        responses:
            200:
                description: User updated successfully.
            404:
                description: User not found.
    """
    data = request.json
    username = data.get('username')
    profile_image_url = data.get('profile_image_url')
    email = data.get('email')

    try:
        user = User.query.get(user_id)
        if user:
            if 'username' in data:
                user.username = username
            if 'profile_image_url' in data:
                user.profile_image_url = profile_image_url
            if 'email' in data:
                user.email = email

            db.session.commit()
            return jsonify({'status': 'success', 'message': 'User updated successfully', 'data': user.to_dict()}), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to update user', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@users.delete('/api/v1/users/<int:user_id>')
def delete_user(user_id):
    """
    Delete a user by their ID.
    ---
    tags:
        - User
    delete:
        description: Delete a user from the system by their unique ID.
        parameters:
            - name: user_id
              in: path
              type: integer
              description: ID of the user to delete.
              required: true
        responses:
            200:
                description: User deleted successfully.
            404:
                description: User not found.
    """
    try:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'User {user_id} deleted successfully', 'data': None}), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to delete user', 'error_code': 'SERVER_ERROR', 'data': None}), 500
