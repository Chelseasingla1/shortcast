import os,logging
from datetime import timedelta
from flask import Flask,jsonify
from flask_cors import CORS
from flasgger import Swagger
from models import *
from auth.auth import auth
from oauth.api import oauth
from download.download import download
from episode.episode import episode
from favourite.favourite import favourite
from playlist.playlist import playlist
from playlistitem.playlistitem import playlistitem
from playlist_bridge.playlist_bridge import playlist_item_bp
from podcast.podcast import podcast
from rating.rating import rating
from sharedplaylist.sharedplaylist import shared_playlist
from subscription.subscription import subscription
from azureops.azureapi import azure_api
from users.users import users
from flask_migrate import Migrate
from flask_login import LoginManager,login_required

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
CORS(app)
swagger = Swagger(app)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
# app.config['SQLALCHEMY_ECHO'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)

db.init_app(app)
migrate = Migrate(app,db)
app.register_blueprint(auth)
app.register_blueprint(oauth)
app.register_blueprint(azure_api)
app.register_blueprint(download)
app.register_blueprint(episode)
app.register_blueprint(favourite)
app.register_blueprint(playlist)
app.register_blueprint(playlistitem)
app.register_blueprint(podcast)
app.register_blueprint(rating)
app.register_blueprint(shared_playlist)
app.register_blueprint(subscription)
app.register_blueprint(users)
app.register_blueprint(playlist_item_bp)


@app.route('/')
def home():
    return jsonify({'msg':'success'})

@app.errorhandler(401)
def unauthorized(error):
    logger.info(error)
    return jsonify({'status': 'failed', 'error': 'You need to be logged in to access this resource'}), 401

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#TODO : test the different azureapi with postman
#TODO : test the different database api with postman
#TODO: integrate the azureapi with the database as well as the authentication api
#TODO : properly handle session and roles
#TODO: add a streaming functionality