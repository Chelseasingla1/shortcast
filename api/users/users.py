from flask import Blueprint, request, jsonify
import logging
from models import User, db
from model_utils import role_check
from  flask_login import current_user,login_required
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users = Blueprint("users", __name__)

@login_required
@users.get('/api/v1/users')
def list_users():
    """
    Retrieve a list of all users.
    ---
    tags:
        - User
    summary: Returns a list of all users in the system.
    description: This endpoint retrieves all users from the database and returns them as a JSON array.
    responses:
        200:
            description: Successfully retrieved the list of users.
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            status:
                                type: string
                                example: 'success'
                            message:
                                type: string
                                example: 'Retrieved all users'
                            data:
                                type: array
                                items:
                                    $ref: '#/components/schemas/User'
        500:
            description: Internal server error occurred while retrieving users.
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            status:
                                type: string
                                example: 'error'
                            message:
                                type: string
                                example: 'Failed to retrieve users'
                            error_code:
                                type: string
                                example: 'SERVER_ERROR'
                            data:
                                type: 'null'
    """
    try:
        user_list = User.query.all()
        users_dict = [user.to_dict() for user in user_list]
        return jsonify({'status': 'success', 'message': 'Retrieved all users', 'data': users_dict}), 200
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve users', 'error_code': 'SERVER_ERROR', 'data': None}), 500

@login_required
@users.get('/api/v1/users')
def get_user():
    """
    Retrieve a user by their ID.
    ---
    tags:
        - User
    get:
        description: Retrieve a user from the system by their unique user ID.
        parameters:
            - name: user_id
              in: path
              type: integer
              description: The unique ID of the user to retrieve.
              required: true
        responses:
            200:
                description: Successfully retrieved the user information.
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                status:
                                    type: string
                                    example: 'success'
                                message:
                                    type: string
                                    example: 'User found'
                                data:
                                    type: array
                                    items:
                                        $ref: '#/components/schemas/User'

            404:
                description: User not found with the given ID.
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                status:
                                    type: string
                                    example: 'error'
                                message:
                                    type: string
                                    example: 'User not found'
                                data:
                                    type: null
            500:
                description: Internal server error while retrieving user data.
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                status:
                                    type: string
                                    example: 'error'
                                message:
                                    type: string
                                    example: 'Failed to retrieve user'
                                error_code:
                                    type: string
                                    example: 'SERVER_ERROR'
                                data:
                                    type: null
    """
    try:
        user = User.query.filter_by(id=current_user.id).first()
        print(user.to_dict())
        if user:
            return jsonify({'status': 'success', 'message': 'User found', 'data': user.to_dict()}), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found', 'data': None}), 404
    except Exception as e:
        logger.error(f"Error retrieving user {current_user.id}: {str(e)}")
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

@login_required
@users.put('/api/v1/users')
def update_user():
    """
    Update user information.
    ---
    tags:
        - User
    put:
        description: Update a user's information in the system by their unique user ID. You can update the username, profile image URL, and email.
        parameters:
            - name: user_id
              in: path
              type: integer
              description: The unique ID of the user to update.
              required: true
            - name: username
              in: body
              type: string
              description: New username to update.
              required: false
            - name: profile_image_url
              in: body
              type: string
              description: New profile image URL to update.
              required: false
            - name: email
              in: body
              type: string
              description: New email to update.
              required: false
        responses:
            200:
                description: User updated successfully with the new information.
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                status:
                                    type: string
                                    example: 'success'
                                message:
                                    type: string
                                    example: 'User updated successfully'
                                data:
                                    type: object
                                    properties:
                                        id:
                                            type: integer
                                            description: The unique ID of the user.
                                        username:
                                            type: string
                                            description: The updated username of the user.
                                        email:
                                            type: string
                                            description: The updated email of the user.
                                        profile_image_url:
                                            type: string
                                            description: The updated profile image URL of the user.
            404:
                description: User not found with the given ID.
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                status:
                                    type: string
                                    example: 'error'
                                message:
                                    type: string
                                    example: 'User not found'
                                data:
                                    type: null
            500:
                description: Internal server error while updating the user data.
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                status:
                                    type: string
                                    example: 'error'
                                message:
                                    type: string
                                    example: 'Failed to update user'
                                error_code:
                                    type: string
                                    example: 'SERVER_ERROR'
                                data:
                                    type: null
    """
    data = request.json
    username = data.get('username')
    profile_image_url = data.get('profile_image_url')
    email = data.get('email')

    try:
        user = User.query.get(current_user.id)
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
        logger.error(f"Error updating user {current_user.id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to update user', 'error_code': 'SERVER_ERROR', 'data': None}), 500


@users.delete('/api/v1/users')
def delete_user():
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
        user = User.query.get(current_user.id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'User {current_user.id} deleted successfully', 'data': None}), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found', 'data': None}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user {current_user.id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to delete user', 'error_code': 'SERVER_ERROR', 'data': None}), 500
