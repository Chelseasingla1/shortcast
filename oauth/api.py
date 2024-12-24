import logging
from flask import Blueprint, request, session, jsonify
from oauth.oauth import TwitchUserService, extract_twitch_info,GithubUserService,extract_github_info, OauthFacade
from auth.auth import _login_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth = Blueprint("oauth", __name__, template_folder='templates/oauth')


@oauth.route('/callback')
def callback():
    """
       OAuth callback for handling the authentication response
       ---
       description: This endpoint processes the OAuth callback, handling the returned code or error, and managing user authentication and getting the access token.
       parameters:
         - name: code
           in: query
           description: The OAuth authorization code received from the OAuth provider.
           required: false
           schema:
             type: string
         - name: state
           in: query
           description: The state parameter returned from the OAuth provider, to ensure the request is valid.
           required: false
           schema:
             type: string
         - name: scope
           in: query
           description: The scope of access requested during OAuth authentication.
           required: false
           schema:
             type: string
         - name: error
           in: query
           description: Error message if the authentication fails.
           required: false
           schema:
             type: string
         - name: error_description
           in: query
           description: Description of the error returned by the OAuth provider.
           required: false
           schema:
             type: string
       responses:
         301:
           description: Successfully authenticated and logged in the user and redirects to the home page.
           content:
             text/html:
               schema:
                 type: string
                 example: "Redirecting to the homepage..."
         401:
           description: Authentication failed due to invalid or missing data.
           content:
             text/html:
               schema:
                 type: string
                 example: "Authentication failed"
         400:
           description: Invalid callback request with no valid parameters.
           content:
             text/html:
               schema:
                 type: string
                 example: "Invalid request"
       """

    code = request.args.get('code', default=None)
    state = request.args.get('state', default=None)
    scope = request.args.get('scope', default=None)
    client = request.args.get('client',default=None)
    error = request.args.get('error', default=None)
    error_description = request.args.get('error_description', default=None)
    logger.info(f'this is : {client}')
    if code:
        data = {'code': code, 'state': state, 'scope': scope}
        try:
            if client == 'twitch':
                oauth_obj = OauthFacade(client=client,response_type="code",
                                        scope=["user:read:email", "user:read:broadcast", "moderator:read:followers",
                                               "user:read:follows"])

                access_token = oauth_obj.get_access_token(data=data)
                session['oauth_token_data'] = access_token
                logger.info(f'saved token:{access_token}')
                return _login_user()
            elif client == 'github':
                oauth_obj = OauthFacade(client=client, response_type="code",
                                        scope=["user:read:email"])

                access_token = oauth_obj.get_access_token(data=data)
                access_data = {'access_token':access_token,'client':client}
                session['oauth_token_data'] = access_data
                logger.info(f'saved token:{access_token}')
                return _login_user()
        except Exception as e:
            logger.error(f'failed token handling: {e}')
            return jsonify('Failed Authentication'), 401

    elif error:
        data = {'error': error, 'error_description': error_description, 'state': state}
        try:
            if client == 'twitch':
                oauth_obj = OauthFacade(client=client,response_type="code",
                                        scope=["user:read:email", "user:read:broadcast"])
                oauth_obj.get_access_token(**data)
                return jsonify('Failed Authentication'), 401
            elif client == 'github':
                oauth_obj = OauthFacade(client=client, response_type="code",
                                        scope=["user:read:email"])
                oauth_obj.get_access_token(**data)
                return jsonify('Failed Authentication'), 401

        except Exception as e:
            logger.error(e)
            return jsonify('error'), 400
    else:
        return jsonify('invalid'), 401
