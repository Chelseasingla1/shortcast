import os
import uuid

import requests
from flask import Blueprint, render_template, request, url_for, session, redirect, flash, jsonify
import logging
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from app.api.auth import login_user_
from app.api.azureops.azureapi import azure_storage_instance
from app.api.oauth.oauth import OauthFacade
from app.model_utils import Categories
from app.views.helpers import get_authentication_links, PlaylistForm, EpisodeForm, AddToPlaylistForm, PodcastForm
from flask_login import current_user, logout_user
from flask_login import login_required
from app.models import Podcast, Episode, SharedPlaylist, db, Playlist, PlaylistItem, PlaylistPlaylistitem
from app.api.azureops.azureclass import AzureBlobStorage
from app.views.dbfuncs import add_episode_to_playlist

load_dotenv()

GITHUB_CLIENT_ID = os.getenv('GITHUB_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_SECRET_KEY')
connection_string = os.getenv('AZURE_CONNECTION_STRING')
container_name = os.getenv('AZURE_CONTAINER_NAME')
github_client_id = os.getenv('GITHUB_ID')
azure_storage_instance = AzureBlobStorage(connection_string)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

views_bp = Blueprint('views', __name__, static_folder='static', template_folder='templates')


@views_bp.route('/', methods=['GET'])
def index():
    nav_links = [
        {'text': 'Home', 'url': url_for('views.index'), 'active': True},
        {'text': 'Create', 'url': '#', 'active': False, 'submenu': [
            {'text': 'Podcast', 'url': url_for('views.create_podcast')},
            {'text': 'Episode', 'url': url_for('views.create_episode')}
        ]},
        {'text': 'About', 'url': url_for('views.about'), 'active': False},
        {'text': 'Contact', 'url': url_for('views.contact'), 'active': False},
        {'text': 'Login / Register', 'url': url_for('views.login'), 'active': False}
    ]

    top_podcasts = []
    latest_episodes = []
    shared_playlists = []
    try:
        top_podcasts = Podcast.query.limit(10).all()
        filter_top_podcasts = sorted(top_podcasts, key=lambda top: len(top.subscriptions), reverse=True)

        latest_episodes = Episode.query.order_by(Episode.publish_date.desc()).limit(8).all()
        shared_playlists = SharedPlaylist.query.all()

        latest_episodes = [episode.to_dict() for episode in latest_episodes]
        top_podcasts = [podcast.to_dict() for podcast in filter_top_podcasts]

        shared_playlists = [shared_playlists.to_dict() for shared_playlist in shared_playlists]
    except Exception as e:
        logger.error(f"Failed to retrieve top podcasts: {str(e)}")

    return render_template(
        'index.html',
        logo_text="ShortCast",
        nav_links=nav_links,
        top_podcast=top_podcasts,
        latest_episodes=latest_episodes,
        shared_playlist=shared_playlists
    )


@views_bp.route('/create-podcast')
@login_required
def create_podcast():
    form = PodcastForm()

    if form.validate_on_submit():
        logging.info("Form is valid, processing data")
        title = form.title.data
        description = form.description.data
        category = form.category.data
        duration = form.duration.data
        feed_url = form.feed_url.data
        if form.image_file.data:
            image_file = form.image_file.data
            original_filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join('/tmp', unique_filename)

            image_file.save(file_path)

            blob_name = f"images/{unique_filename}"
            try:
                image_url = azure_storage_instance.upload_blob(container_name, blob_name, file_path)
            except Exception as e:
                flash(f"Error uploading image: {e}", "error")
                return render_template('createpodcast.html', form=form)

            if os.path.exists(file_path):
                os.remove(file_path)

            new_podcast = Podcast(
                title=title,
                description=description,
                image_url=image_url if image_url else None,
                category=category,
                duration=duration if duration else None,
                feed_url=feed_url
            )

            try:
                db.session.add(new_podcast)
                db.session.commit()
                logging.info("Podcast created successfully!")
                flash('Podcast created successfully!', 'success')
                return redirect(url_for('views.podcasts'))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error saving episode: {e} rolled database ")
                azure_storage_instance.delete_blob(container_name, blob_name)
                logger.error('deleted data from azure')
                flash(f"Error saving episode: {e}", "error")
                return render_template('createpodcast.html', form=form)

    return render_template('createpodcast.html', form=form)


@views_bp.route('/create_episode', methods=['GET', 'POST'])
@login_required
def create_episode():
    form = EpisodeForm()

    # Fetch the list of podcasts that belong to the current user
    podcasts = Podcast.query.filter_by(user_id=current_user.id).all()

    # Populate the podcast dropdown with podcast titles and IDs
    form.podcast_id.choices = [(podcast.id, podcast.title) for podcast in podcasts]

    if form.validate_on_submit():

        logging.info("Form is valid, processing data")
        title = form.title.data
        description = form.description.data
        podcast_id = form.podcast_id.data
        publish_date = datetime.utcnow()

        # Process the image file upload (if any)
        if form.image_file.data:
            image_file = form.image_file.data
            original_filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join('/tmp', unique_filename)

            image_file.save(file_path)  # Save the file temporarily

            # Upload the image to Azure Blob Storage
            blob_name = f"images/{unique_filename}"
            try:
                image_url = azure_storage_instance.upload_blob(container_name, blob_name, file_path)
            except Exception as e:
                flash(f"Error uploading image: {e}", "error")
                return render_template('createepisodes.html', form=form, podcasts=podcasts)

            # Clean up the temporary file after upload
            if os.path.exists(file_path):
                os.remove(file_path)

        if form.audio_file.data:
            audio_file = form.audio_file.data
            original_filename = secure_filename(audio_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join('/tmp', unique_filename)

            audio_file.save(file_path)

            blob_name = f"audio/{unique_filename}"
            try:
                audio_url = azure_storage_instance.upload_blob(container_name, blob_name, file_path)
                logging.info(f"Audio uploaded successfully: {audio_url}")
            except Exception as e:
                flash(f"Error uploading audio: {e}", "error")
                logging.error(f"Error uploading audio: {e}")
                return render_template('createepisodes.html', form=form, podcasts=podcasts)

            if os.path.exists(file_path):
                os.remove(file_path)
        # Create a new episode record
        new_episode = Episode(
            title=title,
            description=description,
            image_url=image_url if image_url else None,
            audio_url=audio_url,
            podcast_id=podcast_id,
            publish_date=publish_date
        )

        try:
            db.session.add(new_episode)
            db.session.commit()
            logging.info("Episode created successfully!")
            flash('Episode created successfully!', 'success')
            return redirect(url_for('views.episode_list'))
        except Exception as e:
            db.session.rollback()
            azure_storage_instance.delete_blob(container_name,blob_name)
            logging.error(f"Error saving episode: {e}")
            flash(f"Error saving episode: {e}", "error")
            return render_template('createepisodes.html', form=form, podcasts=podcasts)

    return render_template('createepisodes.html', form=form, podcasts=podcasts)


@views_bp.route('/about')
def about():
    about_shortcast_message = "At ShortCast, we’re redefining the podcast experience with a focus on short-form, " \
                              "impactful content tailored for your busy lifestyle. Whether you’re commuting, " \
                              "taking a quick break, or simply looking to absorb valuable insights in bite-sized " \
                              "episodes, we’ve got you covered. Our platform brings together creators and listeners " \
                              "in a dynamic space where every moment counts and every story matters. From " \
                              "thought-provoking discussions to entertaining narratives, ShortCast keeps you " \
                              "informed, inspired, and entertained—no matter where you are. Join our growing " \
                              "community of podcast enthusiasts and discover fresh, engaging content right at your " \
                              "fingertips. With ShortCast, every second is an opportunity to learn, laugh, " \
                              "and connect. "
    return render_template('about.html', about_shortcast_message=about_shortcast_message)


@views_bp.route('/contact')
def contact():
    return render_template('contact.html')


@views_bp.route('/login')
def login():
    auth_link = get_authentication_links()

    return render_template("login-register.html", auth_links=auth_link)


@views_bp.route('/callback')
def callback_route():
    code = request.args.get('code')
    state = request.args.get('state')
    scope = request.args.get('scope')
    client = request.args.get('client')
    error = request.args.get('error')
    error_description = request.args.get('error_description')

    logger.info(f'This is client: {client}')

    if error:
        logger.error(f'Error during OAuth callback: {error_description}')
        flash(f'Error: {error_description}', 'error')
        return redirect(url_for('views.login'))

    if code:
        data = {'code': code, 'state': state, 'scope': scope}
        try:
            oauth_obj = OauthFacade(client=client, response_type="code", scope=["user:read:email"])
            access_token = oauth_obj.get_access_token(data=data)
            access_data = {'access_token': access_token, 'client': client}
            session['oauth_token_data'] = access_data
            logger.info(f'Saved token: {access_token}')

            response = login_user_()
            status_code = response[1] if isinstance(response, tuple) else response
            logger.info(response)
            if status_code == 201:
                flash('Logged in successfully!', 'success')
                return redirect(url_for('views.podcast'))
            elif hasattr(response, 'status') and response.status == 'error':
                flash('Failed to log in.', 'error')
                return redirect(url_for('views.login'))

            else:
                logger.warning('Unexpected login response.')
                flash('An unexpected error occurred during login.', 'error')
                return redirect(url_for('views.login'))

        except Exception as e:
            logger.exception('Failed during token handling.')
            flash('An error occurred during authentication.', 'error')
            return redirect(url_for('views.login'))

    # Fallback for any unexpected scenario
    flash('Invalid or missing code parameter.', 'error')
    return redirect(url_for('views.login'))


@views_bp.route('/podcasts')
@login_required
def podcast():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10

        category = request.args.get('category')
        publisher = request.args.get('publisher')
        min_duration = request.args.get('min_duration', type=int)
        max_duration = request.args.get('max_duration', type=int)
        title_search = request.args.get('title')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Podcast.query
        playlists = Playlist.query.filter_by(user_id=current_user.id).all()
        if category:
            print(Podcast.category.name)
            query = query.filter(Podcast.category.name == category.lower())
        if publisher:
            query = query.filter(Podcast.publisher.ilike(f"%{publisher}%"))
        if min_duration is not None:
            query = query.filter(Podcast.duration >= min_duration)
        if max_duration is not None:
            query = query.filter(Podcast.duration <= max_duration)
        if title_search:
            query = query.filter(Podcast.title.ilike(f"%{title_search}%"))
        if start_date and end_date:
            query = query.filter(Podcast.publish_date.between(start_date, end_date))

        # Apply pagination to the filtered query
        pagination = query.order_by(Podcast.publish_date.desc()).paginate(page=page, per_page=per_page)
        podcasts = pagination.items  # This is the list of podcast items

        category_names = [category.name for category in Categories]

        return render_template('podcastlist.html', pagination=pagination, podcasts=podcasts, playlists=playlists,
                               categories=category_names)

    except Exception as e:
        logger.error(f'Failed to retrieve paginated podcasts: {str(e)}')
        return render_template('podcastlist.html', pagination=None, podcasts=[], playlists=playlists)


@views_bp.route('/episodes')
@login_required
def episode():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10

        # Mandatory podcast_id filter
        podcast_id = request.args.get('podcast_id', type=int)
        if not podcast_id:
            flash("Podcast ID is required to view episodes.", "danger")
            return redirect(url_for('views.podcast'))

        # Base query filtered by podcast_id
        query = Episode.query.filter_by(podcast_id=podcast_id)

        # Optional filters
        publisher = request.args.get('publisher')
        min_duration = request.args.get('min_duration', type=int)
        max_duration = request.args.get('max_duration', type=int)
        title_search = request.args.get('title')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if publisher:
            query = query.filter(Episode.publisher.ilike(f"%{publisher}%"))
        if min_duration is not None:
            query = query.filter(Episode.duration >= min_duration)
        if max_duration is not None:
            query = query.filter(Episode.duration <= max_duration)
        if title_search:
            query = query.filter(Episode.title.ilike(f"%{title_search}%"))
        if start_date and end_date:
            query = query.filter(Episode.publish_date.between(start_date, end_date))

        # Pagination
        pagination = query.order_by(Episode.publish_date.desc()).paginate(page=page, per_page=per_page)
        episodes = pagination.items

        playlists = Playlist.query.filter_by(user_id=current_user.id).all()

        return render_template(
            'episodeslist.html',
            pagination=pagination,
            episodes=episodes,
            playlists=playlists,
            podcast_id=podcast_id
        )

    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('views.podcast'))

    except Exception as e:
        logger.error(f'Failed to retrieve paginated episodes: {str(e)}')
        return render_template('episodeslist.html', pagination=None, episodes=[], playlists=playlists)


@views_bp.route('/live-podcasts')
@login_required
def live_podcast():
    return


@views_bp.route('/createplaylist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()  # Initialize the form
    if form.validate_on_submit():
        # Handle form submission
        playlist_title = form.title.data  # Get the playlist title from form
        file = form.image.data  # Get the file from form

        if not file:
            flash('No image file provided.', 'error')
            return render_template('createplaylist.html', form=form)

        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join('/tmp', unique_filename)

        try:
            file.save(file_path)  # Save the file temporarily

            blob_name = f"images/{unique_filename}"

            image_url = azure_storage_instance.upload_blob(container_name, blob_name, file_path)

            # Create a new playlist
            new_playlist = Playlist(
                user_id=current_user.id,  # Ensure `current_user` is accessible via Flask-Login
                title=playlist_title,
                image_url=image_url
            )
            db.session.add(new_playlist)
            db.session.commit()

            flash('Playlist created and saved successfully!', 'success')
            return render_template(
                'createplaylist.html',
                form=form,
                title=playlist_title,
                image_url=image_url
            )

        except SQLAlchemyError as db_err:
            db.session.rollback()
            print(f"Database Error: {str(db_err)}")
            flash('A database error occurred. Please try again.', 'error')

        except Exception as e:
            print(f"General Error: {str(e)}")
            flash('An error occurred while creating the playlist. Please try again.', 'error')

        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

    # For GET request or if validation fails
    return render_template('createplaylist.html', form=form)


@views_bp.route('/removeplaylist/<int:playlist_id>', methods=['POST'])
@login_required
def remove_playlist(playlist_id):
    try:
        # Fetch the playlist to be deleted
        playlist = Playlist.query.get(playlist_id)

        if not playlist:
            flash('Playlist not found.', 'error')
            return redirect(url_for('views.user_playlists'))

        # Ensure the playlist belongs to the current user
        if playlist.user_id != current_user.id:
            flash('You do not have permission to delete this playlist.', 'error')
            return redirect(url_for('views.user_playlists'))

        # Delete the image from Azure storage
        if playlist.image_url:
            blob_name = playlist.image_url.split('/')[-1]  # Extract the blob name
            azure_storage_instance.delete_blob(container_name, f"images/{blob_name}")

        # Remove the playlist from the database
        db.session.delete(playlist)
        db.session.commit()

        flash('Playlist removed successfully!', 'success')
        return redirect(url_for('views.user_playlists'))

    except SQLAlchemyError as db_err:
        db.session.rollback()
        print(f"Database Error: {str(db_err)}")
        flash('A database error occurred. Please try again.', 'error')

    except Exception as e:
        print(f"General Error: {str(e)}")
        flash('An error occurred while removing the playlist. Please try again.', 'error')

    return redirect(url_for('views.user_playlists'))


@views_bp.get('/playlists')
@login_required
def user_playlists():
    # Fetch all playlists belonging to the current user
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()

    return render_template('viewplaylist.html', playlists=playlists)


@views_bp.get('/open_playlist/<int:playlist_id>')
def open_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        flash('Playlist not found.', 'error')
        return redirect(url_for('views_bp.user_playlists'))

    return render_template('open_playlist.html', playlist=playlist)


@views_bp.route('/add_to_playlist', methods=['POST'])
@login_required
def add_to_playlist():
    try:
        # Parse JSON data from the request
        data = request.json

        if not data:
            return jsonify({'msg': 'No data provided'}), 400

        episode_id = data.get('episode_id')
        playlist_id = data.get('playlist_id')

        if not episode_id or not playlist_id:
            return jsonify({'msg': 'episode_id and playlist_id are required'}), 400

        # Query the database for the playlist and episode
        playlist = Playlist.query.get(playlist_id)
        episode = Episode.query.get(episode_id)

        if not playlist or not episode:
            return jsonify({'msg': 'playlist or episode not found'}), 404

        if episode.playlist_items:
            # Check if the playlist already contains the item
            existing_item = PlaylistPlaylistitem.query.filter_by(
                playlist_item_id=episode.playlist_items.id,
                playlist_id=playlist_id
            ).first()

            if existing_item:
                return jsonify({'msg': 'Episode already exists in playlist'}), 200

            # Add the existing playlist item to the playlist
            playlist_bridge = PlaylistPlaylistitem(
                playlist_id=playlist_id,
                playlist_item_id=episode.playlist_items.id
            )
            db.session.add(playlist_bridge)
            db.session.commit()
            return jsonify({'msg': 'Episode added to playlist successfully'}), 201
        else:
            # Create a new playlist item for the episode
            new_playlist_item = PlaylistItem(episode_id=episode_id)
            db.session.add(new_playlist_item)
            db.session.flush()

            # Add the new playlist item to the playlist
            playlist_bridge = PlaylistPlaylistitem(
                playlist_id=playlist_id,
                playlist_item_id=new_playlist_item.id
            )
            db.session.add(playlist_bridge)
            db.session.commit()

            return jsonify({'msg': 'Episode added to playlist successfully'}), 201

    except KeyError as e:
        # Handle missing keys in the data
        return jsonify({'msg': f'Missing key: {str(e)}'}), 400

    except ValueError as e:
        # Handle value-related errors
        return jsonify({'msg': f'Value error: {str(e)}'}), 400

    except Exception as e:
        # Catch all other exceptions
        return jsonify({'msg': f'An unexpected error occurred: {str(e)}'}), 500


@views_bp.route('/remove_from_playlist', methods=['POST'])
@login_required
def remove_from_playlist():
    try:
        # Parse JSON data from the request
        data = request.json

        if not data:
            return jsonify({'msg': 'No data provided'}), 400

        episode_id = data.get('episode_id')
        playlist_id = data.get('playlist_id')

        if not episode_id or not playlist_id:
            return jsonify({'msg': 'episode_id and playlist_id are required'}), 400

        # Query the database for the playlist and episode
        playlist = Playlist.query.get(playlist_id)
        episode = Episode.query.get(episode_id)

        if not playlist or not episode:
            return jsonify({'msg': 'playlist or episode not found'}), 404

        # Query the association table to check if the item exists
        playlist_item_association = PlaylistPlaylistitem.query.filter_by(
            playlist_id=playlist_id,
            playlist_item_id=episode.playlist_items.id
        ).first()

        if not playlist_item_association:
            return jsonify({'msg': 'Episode not found in the playlist'}), 404

        # Remove the playlist item from the playlist
        db.session.delete(playlist_item_association)

        # If there are no other references to the playlist item, delete the playlist item itself
        # You may need to add logic to ensure it's safe to delete (e.g., no other playlist associations exist)
        if not PlaylistPlaylistitem.query.filter_by(playlist_item_id=episode.playlist_items.id).first():
            db.session.delete(episode.playlist_items)

        db.session.commit()

        return jsonify({'msg': 'Episode removed from playlist successfully'}), 200

    except KeyError as e:
        # Handle missing keys in the data
        return jsonify({'msg': f'Missing key: {str(e)}'}), 400

    except ValueError as e:
        # Handle value-related errors
        return jsonify({'msg': f'Value error: {str(e)}'}), 400

    except Exception as e:
        # Catch all other exceptions
        return jsonify({'msg': f'An unexpected error occurred: {str(e)}'}), 500


@views_bp.route('/playlist/<int:playlist_id>/episodes', methods=['GET'])
@login_required
def playlist_episodes(playlist_id):
    # Fetch the playlist by its ID
    playlist = Playlist.query.get(playlist_id)

    # Check if the playlist exists
    if playlist:
        # Get all episodes in the playlist by joining PlaylistItem and Episode
        episodes = db.session.query(Episode).join(PlaylistItem).filter(PlaylistItem.playlist_id == playlist.id).all()

        # Render the episodes (you can pass this to a template)
        return render_template('playlist_episodes.html', playlist=playlist, episodes=episodes)

    else:
        return "Playlist not found", 404


@views_bp.route('/delete_playlist/<int:playlist_id>', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    # Deleting associated PlaylistItems from PlaylistPlaylistitem relationship
    PlaylistPlaylistitem.query.filter_by(playlist_id=playlist_id).delete()

    # Deleting the playlist itself
    db.session.delete(playlist)
    db.session.commit()

    return redirect(url_for('views.podcasts'))  # Redirect to the list of podcasts or playlists


@views_bp.route('/logout')
def logout():
    logger.info('User initiated logout.')

    flash('You have been logged out successfully.', 'success')

    access_data = session.pop('oauth_token_data', None)
    if access_data and 'access_token' in access_data:
        try:
            token = access_data['access_token']

            response = requests.delete(
                f'https://api.github.com/applications/{GITHUB_CLIENT_ID}/grant',
                auth=(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET),
                json={"access_token": token}
            )

            if response.status_code == 204:
                logger.info('GitHub OAuth token successfully invalidated.')
            else:
                logger.warning(
                    f'Failed to invalidate GitHub OAuth token. Status: {response.status_code}, Response: {response.text}'
                )

        except Exception as e:
            logger.exception('Error while invalidating GitHub OAuth token.')

    logout_user()
    session.clear()

    return redirect(url_for('views.index'))
#
#
# @views_bp.route('/login')
# def login_route():
#     oauth_obj_twitch = OauthFacade('twitch', response_type="code",
#                                    scope=["user:read:email", "user:read:broadcast", "moderator:read:followers",
#                                           "user:read:follows"])
#
#     oauth_obj_github = OauthFacade('github', response_type="code",
#                                    scope=["user:read:email", "user:read:broadcast", "moderator:read:followers",
#                                           "user:read:follows"])
#
#     auth_instance_twitch = oauth_obj_twitch
#     auth_instance_github = oauth_obj_github
#     auth_instances: dict = {'github_link': auth_instance_github.get_auth_link(),
#                             'twitch_link': auth_instance_twitch.get_auth_link()}
#
#     return render_template('login-register.html', auth_links=auth_instances)
#
#
# @views_bp.route('/singlepost')
# def single_post():
#     return render_template('single-post.html')
#


# @views_bp.route('/podcasts')
# def pocast():
#     return render_template('podcastlist.html')
#
#
# @views_bp.route('/episodes')
# def episodes():
#     return render_template('episodeslist.html')
#
#
# @views_bp.route('/user')
# def users():
#     return render_template('profile.html')
#
# @views_bp.route('/createpodcast')
# def create_podcast():
#     return render_template('createpodcast.html')
#
#
# @views_bp.route('/createepisode')
# def create_episode():
#     return render_template('createepisodes.html')
#
#
# @views_bp.route('/uploads')
# def upload():
#     return render_template('user_uploads.html')
#

#
# @views_bp.route('/playlist')
# def view_playlist():
#     return render_template('viewplaylist.html')
