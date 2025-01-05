import logging

from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, session, jsonify
from flask_login import login_user, logout_user, current_user
from api.oauth.oauth import TwitchUserService, extract_twitch_info, GithubUserService, extract_github_info, OauthFacade
from models import User, db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth = Blueprint("auth", __name__)


def login_user_():
    oauth_data = session.get('oauth_token_data')

    if not oauth_data:
        logger.error("No OAuth data found in session, redirecting to login page")
        # You can return a response with a relevant message for the frontend
        return jsonify({'status': 'error', 'message': 'No session data, please log in again','data':None}), 401

    access_token = oauth_data.get('access_token')
    client = oauth_data.get('client')
    # refresh_token = oauth_data.get('refresh_token')

    try:
        twitch_user = None
        twitch_user_data = None
        user_id = None
        username = None
        email = None
        profile_image_url = None
        if client == 'twitch':
            logger.info('twitch route')
            twitch_user = TwitchUserService(access_token=access_token)
            twitch_user_data = twitch_user.get_user_details()
            user_id = extract_twitch_info(twitch_user_data, 'id')
            username = extract_twitch_info(twitch_user_data, 'display_name')
            email = extract_twitch_info(twitch_user_data, 'email')
            profile_image_url = extract_twitch_info(twitch_user_data, 'profile_image_url')

        elif client == 'github':
            logger.info('github route')
            github_user = GithubUserService(access_token=access_token)
            github_user_data = github_user.get_user_details()
            user_id = extract_github_info(github_user_data, 'id')
            username = extract_github_info(github_user_data, 'name')
            email = extract_github_info(github_user_data, 'email')
            profile_image_url = extract_github_info(github_user_data, 'avatar_url')
        else:
            return jsonify({'status':'error','message':'Invalid client','error_code':'VALIDATION ERROR','data':None}), 400
    except Exception as e:
        logger.error(f"Error fetching user details from Github: {e}")
        return jsonify({'status':'error','message':'Internal Server error','error_code':'SERVER ERROR','data':None}), 500

    logger.info(f"Fetched user details: {username}, {user_id}, {email}, {profile_image_url}")

    existing_user = db.session.execute(db.select(User).filter_by(oauth_id=user_id)).scalar_one_or_none()

    if existing_user:
        login_user(existing_user)
        session.permanent = True
        logger.info(f"User logged in: {existing_user.username}")
        logger.info(f"Current user: {current_user.username}")
        logger.info(f"Is authenticated: {current_user.is_authenticated}")
        user_data = {
            "id": existing_user.id,
            "username": existing_user.username,
            "email": existing_user.email,
            "profile_image_url": existing_user.profile_image_url,  # optional, if you have this
            "role": existing_user.role.value
        }
        return jsonify({'status':'success','message':'user logged in','data':user_data}),201

    new_user = User(
        oauth_id=user_id,
        username=username,
        profile_image_url=profile_image_url,
        email=email,
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        session.permanent = True
    except SQLAlchemyError as e:
        logger.error(f"Database error while adding new user: {e}")
        db.session.rollback()
        jsonify({'status':'error','message':'Internal Server error','error_code':'VALIDATION ERROR','data':None}), 500
    except Exception as e:
        logger.error(f"Unexpected error while adding new user: {e}")
        db.session.rollback()
        return jsonify({'status':'error','message':'Internal Server error','error_code':'VALIDATION ERROR','data':None}), 500

    user_data = {
        "id": existing_user.id,
        "username": existing_user.username,
        "email": existing_user.email,
        "profile_image_url": existing_user.profile_image_url,  # optional, if you have this
        "role": existing_user.role
    }

    return jsonify({'status':'success','message':'user logged in','data':user_data}),201

@auth.get('/api/v1/login')
def login_get():
    """
    Get the OAuth login link
    ---
    tags:
      - Authentication
    description: This endpoint generates an OAuth login link for user authentication via third-party services like Twitch and GitHub.
    responses:
      200:
        description: Returns the OAuth login links for Twitch and GitHub.
        content:
          application/json:
            schema:
              type: array
              items:
                type: string
              example:
                - "https://twitch.tv/oauth/authorize?...credentials"
                - "https://github.com/login/oauth/authorize?...credentials"
    """

    oauth_obj_twitch = OauthFacade('twitch', response_type="code",
                                   scope=["user:read:email", "user:read:broadcast", "moderator:read:followers",
                                          "user:read:follows"])

    oauth_obj_github = OauthFacade('github', response_type="code",
                                   scope=["user:read:email", "user:read:broadcast", "moderator:read:followers",
                                          "user:read:follows"])

    auth_instance_twitch = oauth_obj_twitch
    auth_instance_github = oauth_obj_github
    auth_instances: dict = {'github_link':auth_instance_github.get_auth_link(), 'twitch_link':auth_instance_twitch.get_auth_link()}
    return jsonify({'status':'success','message':'links generated','data':auth_instances}),200


@auth.route('/api/v1/logout')
def logout():
    """
    Logout the current user
    ---
    tags:
      - Authentication
    description: This endpoint logs out the current user by ending their session and redirecting to the login page.
    responses:
      302:
        description: Redirects the user to the login page after logging out.
        content:
          text/html:
            schema:
              type: string
              example: "Redirecting to /login..."
    """
    logout_user()
    return jsonify({'status': 'success', 'message': 'user logged out'}), 200
