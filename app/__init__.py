import os
import logging
from datetime import timedelta
from flask import Flask, jsonify, render_template
from celerysetup import make_celery


from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from flasgger import Swagger

from app.models import db, User
from app.model_utils import *

from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask Configuration
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.getenv('FLASK_SECRET_KEY'))
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI_SHORTCAST', 'sqlite:///default.db')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)








# Extensions Initialization
celery = make_celery(app)

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)
CSRFProtect(app)
Swagger(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'views.login'


import tasks
# Import Blueprints
from app.views.view import views_bp
from app.api.auth.auth import auth
from app.api.oauth.api import oauth
from app.api.download.download import download
from app.api.episode.episode import episode
from app.api.favourite.favourite import favourite
from app.api.playlist.playlist import playlist
from app.api.playlistitem.playlistitem import playlistitem
from app.api.playlist_bridge.playlist_bridge import playlist_item_bp
from app.api.podcast.podcast import podcast
from app.api.rating.rating import rating
from app.api.sharedplaylist.sharedplaylist import shared_playlist
from app.api.subscription.subscription import subscription
from app.api.azureops.azureapi import azure_api
from app.api.users.users import users

# Register Blueprints
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



# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Error Handlers
@app.errorhandler(401)
def unauthorized(error):
    logger.info(error)
    return jsonify({'status': 'failed', 'error': 'You need to be logged in to access this resource'}), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# @celery.task
# def add_numbers(a, b):
#     return a + b

# @app.route('/add/<int:a>/<int:b>')
# def add(a, b):
#     from tasks.testlongtask import add_numbers
#     # Call the Celery task
#     task = add_numbers.delay(a, b)
#     return f"Task ID: {task.id}, Check status later!"

# @app.route('/result/<task_id>')
# def result(task_id):
#     task = add_numbers.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         return "Task is still processing..."
#     elif task.state == 'SUCCESS':
#         return f"Task result: {task.result}"
#     else:
#         return f"Task failed or is in {task.state} state."
#

if __name__ == '__main__':
    with app.app_context():
        from app.models import db
        db.create_all()
    app.run()
