import os
import logging
from datetime import timedelta
from flask import Flask, jsonify, render_template
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from flasgger import Swagger
from celery_utils import make_celery
from app.models import db, User
from app.model_utils import *
from celery.result import AsyncResult


def create_app():
    app = Flask(__name__)

    # Logging setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Flask Configuration
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI_SHORTCAST', 'sqlite:///default.db')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)

    # Extensions Initialization
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    CSRFProtect(app)
    Swagger(app)
    celery = make_celery(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'views.login'

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

    # Import and Register Blueprints
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

    # Routes
    @app.route('/milo2')
    def med():
        return render_template('index.html')

    # Celery Task
    @celery.task
    def add_numbers(a, b):
        return a + b

    @app.route('/add/<int:a>/<int:b>')
    def add(a, b):
        task = add_numbers.delay(a, b)
        return jsonify({"task_id": task.id, "status": "Task submitted"})

    @app.route('/status/<task_id>')
    def task_status(task_id):
        task_result = AsyncResult(task_id, app=celery)
        return jsonify({"task_id": task_id, "status": task_result.status, "result": task_result.result})

    return app, celery
