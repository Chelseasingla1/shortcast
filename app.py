import os, logging
from datetime import timedelta
from flask import Flask, jsonify, render_template
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flasgger import Swagger
from models import *
from api.auth.auth import auth
from api.oauth.api import oauth
from api.download.download import download
from api.episode.episode import episode
from api.favourite.favourite import favourite
from api.playlist.playlist import playlist
from api.playlistitem.playlistitem import playlistitem
from api.playlist_bridge.playlist_bridge import playlist_item_bp
from api.podcast.podcast import podcast
from api.rating.rating import rating
from api.sharedplaylist.sharedplaylist import shared_playlist
from api.subscription.subscription import subscription
from api.azureops.azureapi import azure_api
from api.users.users import users

from views.view import views_bp

from flask_migrate import Migrate
from flask_login import LoginManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
CORS(app)
csrf = CSRFProtect(app)
swagger = Swagger(app)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
# app.config['SQLALCHEMY_ECHO'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(views_bp)

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





@app.errorhandler(401)
def unauthorized(error):
    logger.info(error)
    return jsonify({'status': 'failed', 'error': 'You need to be logged in to access this resource'}), 401


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/milo2')
def med():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
