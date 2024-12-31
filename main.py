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
from podcast.podcast import podcast
from rating.rating import rating
from sharedplaylist.sharedplaylist import shared_playlist
from subscription.subscription import subscription
from users.users import users
from flask_migrate import Migrate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)

db.init_app(app)
migrate = Migrate(app,db)
app.register_blueprint(auth)
app.register_blueprint(oauth)
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


@app.errorhandler(401)
def unauthorized(error):
    logger.info(error)
    return jsonify({'status': 'failed', 'error': 'You need to be logged in to access this resource'}), 401




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#TODO: add a streaming functionality