import os
import uuid
import requests
from flask import Blueprint, render_template, request, url_for, session, redirect, flash, jsonify
from flask_login import current_user, logout_user,login_required
import logging
from dotenv import load_dotenv
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from datetime import datetime
from difflib import SequenceMatcher

from app.api.auth import login_user_
from app.api.azureops.azureapi import azure_storage_instance
from app.api.oauth.oauth import OauthFacade
from app.model_utils import Categories,categories_details
from app.views.helpers import get_authentication_links, PlaylistForm, EpisodeForm,PodcastForm,EmailForm, PreferencesForm, EpisodeUpdateForm, PodcastUpdateForm

from app.models import Podcast, Episode, SharedPlaylist, db, Playlist, PlaylistItem, PlaylistPlaylistitem, User, \
    Favourite
from app.api.azureops.azureclass import AzureBlobStorage
from task_singleton import TaskInfoSingleton

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

# home page route
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



    most_popular_episodes = []
    latest_episodes = []
    shared_playlists = []
    email_form = EmailForm()
    try:

        top_episodes = (
            db.session.query(
                Favourite.episode_id, func.count(Favourite.user_id).label('favourite_count')
            )
            .group_by(Favourite.episode_id)
            .order_by(func.count(Favourite.user_id).desc())
            .limit(5)  # Get the top 5
            .all()
        )

        # Convert the result to a list of dictionaries
        most_popular_episodes = []
        for episode_id, count in top_episodes:
            episode = Episode.query.filter_by(id=episode_id).first()
            if episode:
                episode_dict = episode.to_dict()
                episode_dict.update({'count': count})
                most_popular_episodes.append(episode_dict)


        latest_episodes = Episode.query.order_by(Episode.publish_date.desc()).limit(8).all()
        shared_playlists = SharedPlaylist.query.all()

        latest_episodes = [episode.to_dict() for episode in latest_episodes]

        shared_playlists = [shared_playlist.to_dict() for shared_playlist in shared_playlists]
    except Exception as e:
        logger.error(f"Failed to retrieve top podcasts: {str(e)}")

    return render_template(
        'index.html',
        logo_text="ShortCast",
        nav_links=nav_links,
        top_episodes=most_popular_episodes,
        latest_episodes=latest_episodes,
        shared_playlist=shared_playlists,
        email_form=email_form,
        categories=categories_details
    )

# Route to create a new podcast
@views_bp.route('/create-podcast',methods=['GET','POST'])
@login_required
def create_podcast():
    form = PodcastForm()
    form.category.choices = [(category.name, category.name.replace('_', ' ').title()) for category in Categories]
    email_form = EmailForm()
    if form.validate_on_submit():
        logging.info("Form is valid, processing data")
        title = form.title.data
        description = form.description.data
        category = form.category.data
        duration = form.duration.data
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
            # Removes uploaded image
            if os.path.exists(file_path):
                os.remove(file_path)



            try:
                new_podcast = Podcast(
                    title=title,
                    description=description,
                    image_url=image_url if image_url else None,
                    category=category,  # find a way to make it accept multi values,probably make a category table
                    publisher=current_user.username,
                    duration=duration if duration else None,
                    user_id = current_user.id

                )

                website_hostname = os.getenv('WEBSITE_HOSTNAME')
                db.session.add(new_podcast)
                db.session.flush()
                new_podcast.feed_url = f"{website_hostname}/podcasts/{new_podcast.id}/feed"
                new_podcast.validate_urls()
                db.session.commit()
                logger.info("Podcast created successfully!")
                flash('Podcast created successfully!', 'success')
                return redirect(url_for('views.podcast'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Error saving episode: {e} rolled database ")
                azure_storage_instance.delete_blob(container_name, blob_name)
                logger.error('deleted data from azure')
                flash(f"Error saving episode: {e}", "error")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error saving episode: {e} rolled database ")
                azure_storage_instance.delete_blob(container_name, blob_name)
                logger.error('deleted data from azure')
                logger.error(f'Encountered error: {e}')
                flash("An unexpected error occurred. Please try again.", "error")
            return render_template('createpodcast.html', form=form,email_form=email_form)

    return render_template('createpodcast.html', form=form,email_form=email_form)


@views_bp.route('/create_episode', methods=['GET', 'POST'])
@login_required
def create_episode():
    from tasks.transcriptionservice import transcribe
    form = EpisodeForm()
    email_form = EmailForm()
    # Fetch the list of podcasts that belong to the current user
    podcasts = Podcast.query.filter_by(user_id=current_user.id).all()

    # Populate the podcast dropdown with podcast titles and IDs
    form.podcast_id.choices = [(podcast.id, podcast.title) for podcast in podcasts]
    image_url = None
    audio_url = None
    audio_file_path = None
    blob_name = None
    # form validation
    if form.validate_on_submit():

        logging.info("Form is valid, processing data")
        title = form.title.data
        description = form.description.data
        podcast_id = form.podcast_id.data
        publish_date = datetime.now()

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
            audio_file_path = os.path.join('/tmp', unique_filename)

            audio_file.save(audio_file_path)

            blob_name = f"audio/{unique_filename}"
            try:
                audio_url = azure_storage_instance.upload_blob(container_name, blob_name, audio_file_path)
                logging.info(f"Audio uploaded successfully: {audio_url}")
            except Exception as e:
                flash(f"Error uploading audio: {e}", "error")
                logging.error(f"Error uploading audio: {e}")
                return render_template('createepisodes.html', form=form, podcasts=podcasts)




        try:
            # Create a new episode record
            new_episode = Episode(
                title=title,
                description=description,
                image_url=image_url if image_url else None,
                audio_url=audio_url,
                podcast_id=podcast_id,
                publish_date=publish_date
            )

            db.session.add(new_episode)
            db.session.commit()
            logging.info("Episode created successfully!")
            flash('Episode created successfully!', 'success')

            # transcription asynchronous
            try:
                if audio_file_path and new_episode.id:
                    task = transcribe.apply_async(args=[audio_file_path,new_episode.id,True])
                    task_id = task.id
                    task_info_singleton = TaskInfoSingleton()
                    task_info_singleton.set_task_info(task_id, 'transcription')
                    logger.info("Transcription started asynchronously.")
            except Exception as e:
                logger.error(f"Failed to start transcription: {e}")

            return redirect(url_for('views.episode',podcast_id=podcast_id))
        except Exception as e:
            db.session.rollback()
            azure_storage_instance.delete_blob(container_name, blob_name)
            logging.error(f"Error saving episode: {e}")
            flash(f"Error saving episode: {e}", "error")
            return render_template('createepisodes.html', form=form, podcasts=podcasts,email_form=email_form)



    return render_template('createepisodes.html', form=form, podcasts=podcasts,email_form=email_form)


@views_bp.route('/about')
def about():
    email_form = EmailForm()
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
    return render_template('about.html', about_shortcast_message=about_shortcast_message,email_form=email_form)


@views_bp.route('/contact')
def contact():
    email_form = EmailForm()
    return render_template('contact.html',email_form=email_form)


@views_bp.route('/login')
def login():
    email_form = EmailForm()
    auth_link = get_authentication_links()

    return render_template("login-register.html", auth_links=auth_link,email_form=email_form)

# route that handles oauth logic
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

# route to view all the published podcasts
@views_bp.route('/podcasts')
@login_required
def podcast():
    email_form = EmailForm()
    podcasts = []
    playlists = []
    category_names = []
    pagination = None
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
                               categories=category_names,email_form=email_form)

    except Exception as e:
        logger.error(f'Failed to retrieve paginated podcasts: {str(e)}')
        return render_template('podcastlist.html', pagination=pagination, podcasts=podcasts, playlists=playlists,email_form=email_form,categories=category_names)


# route to view all the published episodes in a podcast
@views_bp.route('/episodes')
# @login_required
def episode():
    playlists  = []
    episodes = []
    try:
        email_form = EmailForm()
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
        favourite_counts = {i.id: len(i.favourites) for i in episodes}
        favourite_state = {i.id: True if any(fav.user_id == current_user.id for fav in i.favourites) else False for i in
                           episodes}

        return render_template(
            'episodeslist.html',
            pagination=pagination,
            episodes=episodes,
            playlists=playlists,
            podcast_id=podcast_id,
            favourite_counts=favourite_counts,
            favourite_state=favourite_state,
            email_form=email_form

        )

    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        logger.error(f'Failed to retrieve paginated episodes: {str(e)}')
        return render_template('episodeslist.html', pagination=None, episodes=episodes, playlists=playlists,email_form=email_form)


@views_bp.route('/user/podcasts')
@login_required
def user_podcasts():
    email_form = EmailForm()
    form = PodcastUpdateForm()
    podcasts = Podcast.query.filter_by(user_id=current_user.id).all()

    return render_template('viewuserpodcasts.html',form=form, podcasts = podcasts, email_form=email_form)

@views_bp.post('/user/podcasts/<int:podcast_id>')
def user_podcasts_remove(podcast_id):
    try:
        # Fetch the podcast to be deleted
        podcast = Podcast.query.get(podcast_id)

        if not podcast:
            flash('Podcast not found.', 'error')
            return redirect(url_for('views.user_podcasts'))

        # Ensure the playlist belongs to the current user
        if podcast.user_id != current_user.id:
            flash('You do not have permission to delete this podcast.', 'error')
            return redirect(url_for('views.user_podcasts'))

        # Delete the image from Azure storage
        if podcast.image_url:

            blob_name = podcast.image_url.split('/')[-1]  # Extract the blob name
            azure_storage_instance.delete_blob(container_name, f"images/{blob_name}")

        # Remove the podcast from the database
        db.session.delete(podcast)
        db.session.commit()

        flash('Podcast removed successfully!', 'success')
        return redirect(url_for('views.user_podcasts'))

    except SQLAlchemyError as db_err:
        db.session.rollback()
        print(f"Database Error: {str(db_err)}")
        flash('A database error occurred. Please try again.', 'error')

    except Exception as e:
        print(f"General Error: {str(e)}")
        flash('An error occurred while removing the podcast. Please try again.', 'error')

    return redirect(url_for('views.user_podcasts'))

@views_bp.get('/user/episodes/<int:podcast_id>')
def user_episodes(podcast_id):
    try:
        form = EpisodeUpdateForm()
        email_form = EmailForm()
        episodes = Episode.query.filter_by(podcast_id=podcast_id).all()

        return render_template(
            'viewuserepisode.html',
            episodes=episodes,
            form = form,
            email_form=email_form
        )
    except Exception as e:
        logger.error(str(e))
        flash(f'An error occured ')
        return render_template('viewuserepisode.html',
                               email_form=email_form)

@views_bp.post('/user/episodes/<int:podcast_id>/<int:episode_id>')
def user_episodes_remove(podcast_id,episode_id):
    try:
        # Fetch the episode to be deleted

        episode = Episode.query.get(episode_id)
        podcast_id = podcast_id

        if not episode:
            flash('Episode not found.', 'error')
            return redirect(url_for('views.user_episodes',podcast_id=podcast_id))

        # Ensure the playlist belongs to the current user
        if episode.podcast.user_id != current_user.id:
            flash('You do not have permission to delete this episode.', 'error')
            return redirect(url_for('views.user_episodes',podcast_id=podcast_id))

        try:
            # Delete the image from Azure storage if it exists
            if episode.image_url:
                blob_name = episode.image_url.split('/')[-1]  # Extract the blob name
                try:
                    azure_storage_instance.delete_blob(container_name, f"images/{blob_name}")
                except Exception as e:
                    logger.error(f"Failed to delete image blob: {str(e)}")
                    flash('Failed to delete the episode image.', 'error')

            # Delete the audio from Azure storage if it exists
            if episode.audio_url:
                blob_name = episode.audio_url.split('/')[-1]  # Extract the blob name
                try:
                    azure_storage_instance.delete_blob(container_name, f"audio/{blob_name}")
                except Exception as e:
                    logger.error(f"Failed to delete audio blob: {str(e)}")
                    flash('Failed to delete the episode audio.', 'error')

        except Exception as e:
            logger.error(f"Error in Azure blob deletion: {str(e)}")
            flash('An error occurred while deleting media from Azure.', 'error')

        # Remove the episode from the database
        db.session.delete(episode)
        db.session.commit()

        flash('Episode removed successfully!', 'success')
        return redirect(url_for('views.user_episodes',podcast_id=podcast_id))

    except SQLAlchemyError as db_err:
        db.session.rollback()
        logger.error(f"Database Error: {str(db_err)}")
        flash('A database error occurred. Please try again.', 'error')

    except Exception as e:
        logger.error(f"General Error: {str(e)}")
        flash('An error occurred while removing the episode. Please try again.', 'error')

    return redirect(url_for('views.user_episodes'))


@views_bp.post('/update/episode/<int:episode_id>')
def update_episodes(episode_id):
    episode = Episode.query.filter_by(id=episode_id).first()
    if not episode:
        flash("Episode not found.", "error")
        return redirect(url_for('views.user_episodes', podcast_id=episode.podcast.id))

    form = EpisodeUpdateForm()
    if form.validate_on_submit():
        logger.info("Form is valid, processing data.")
        image_url = None
        description = form.description.data

        if form.image_file.data:
            try:
                image_file = form.image_file.data
                original_filename = secure_filename(image_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                file_path = os.path.join('/tmp', unique_filename)

                # Save file temporarily
                image_file.save(file_path)

                # Upload to Azure
                blob_name = f"images/{unique_filename}"
                image_url = azure_storage_instance.upload_blob(container_name, blob_name, file_path)

                # Clean up temporary file
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error uploading image: {e}")
                flash(f"Error uploading image: {e}", "error")
                return redirect(url_for('views.user_episodes', podcast_id=episode.podcast.id))

        try:
            # Delete the previous image from Azure storage if it exists
            if episode.image_url:
                blob_name = episode.image_url.split('/')[-1]  # Extract the blob name
                try:
                    azure_storage_instance.delete_blob(container_name, f"images/{blob_name}")
                except Exception as e:
                    logger.error(f"Failed to delete image blob: {str(e)}")
                    flash('Failed to delete the episode image.', 'error')

            if description:
                episode.description = description
            if image_url:
                episode.image_url = image_url

            db.session.commit()  # Commit changes to the database
            flash("Episode updated successfully.", "success")
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            db.session.rollback()
            flash("Failed to update episode.", "error")

    else:
        logger.warning("Form validation failed.")
        flash("Invalid input, please check the form.", "error")

    return redirect(url_for('views.user_episodes', podcast_id=episode.podcast.id))


@views_bp.post('/update/podcast/<int:podcast_id>')
def update_podcast(podcast_id):
    podcast = Podcast.query.filter_by(id=podcast_id).first()
    if not podcast:
        flash("Podcast not found.", "error")
        return redirect(url_for('views.user_podcasts'))

    form = PodcastUpdateForm()
    if form.validate_on_submit():
        logger.info("Form is valid, processing data.")
        image_url = None
        description = form.description.data

        if form.image_file.data:
            try:
                image_file = form.image_file.data
                original_filename = secure_filename(image_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                file_path = os.path.join('/tmp', unique_filename)

                # Save file temporarily
                image_file.save(file_path)

                # Upload to Azure
                blob_name = f"images/{unique_filename}"
                image_url = azure_storage_instance.upload_blob(container_name, blob_name, file_path)

                # Clean up temporary file
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error uploading image: {e}")
                flash(f"Error uploading image: {e}", "error")
                return redirect(url_for('views.user_podcasts'))

        try:
            # Delete the previous image from Azure storage if it exists
            if image_url:
                if podcast.image_url:
                    blob_name = podcast.image_url.split('/')[-1]  # Extract the blob name
                    try:
                        azure_storage_instance.delete_blob(container_name, f"images/{blob_name}")
                    except Exception as e:
                        logger.error(f"Failed to delete image blob: {str(e)}")
                        flash("Failed to delete the podcast image.", "error")

            # Update podcast details
            if description:
                podcast.description = description
            if image_url:
                podcast.image_url = image_url

            db.session.commit()  # Commit changes to the database
            flash("Podcast updated successfully.", "success")
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            db.session.rollback()
            flash("Failed to update podcast.", "error")

    else:
        logger.warning("Form validation failed.")
        flash("Invalid input, please check the form.", "error")

    return redirect(url_for('views.user_podcasts'))

# route to view live podcasts
@views_bp.route('/live-podcasts')
@login_required
def live_podcast():
    return


# route to create a playlist of current user
@views_bp.route('/createplaylist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    """
    Create a new playlist for the current user.

    This route allows an authenticated user to create a new playlist by providing a title and an image. The image is
    uploaded to Azure Blob Storage, and the playlist is saved in the database.

    ---
    tags:
      - Playlist
    parameters:
      - name: title
        in: formData
        description: The title of the playlist.
        required: true
        type: string
        example: 'My Favorite Episodes'
      - name: image
        in: formData
        description: The image file to represent the playlist.
        required: true
        type: file
    responses:
      200:
        description: Successfully created the playlist with an image uploaded.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'Playlist created and saved successfully!'
            playlist:
              type: object
              properties:
                title:
                  type: string
                  example: 'My Favorite Episodes'
                image_url:
                  type: string
                  example: 'https://azure.blobstorage.url/images/unique_filename.jpg'
      400:
        description: Missing or invalid data provided in the form.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'No image file provided.'
      500:
        description: A database or unexpected error occurred during playlist creation.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'An error occurred while creating the playlist. Please try again.'
    """

    form = PlaylistForm()  # Initialize the form
    email_form = EmailForm()
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
                image_url=image_url,
                email_form=email_form
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
    return render_template('createplaylist.html', form=form,email_form=email_form)

# route to remove a playlist of the current user
@views_bp.route('/removeplaylist/<int:playlist_id>', methods=['POST'])
@login_required
def remove_playlist(playlist_id):
    """
    Remove a playlist created by the current user.

    This route allows the current authenticated user to delete a playlist they created. If the playlist has an associated
    image, it will be deleted from Azure storage before removing the playlist from the database.

    ---
    tags:
      - Playlist
    parameters:
      - name: playlist_id
        in: path
        description: The ID of the playlist to be removed.
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Successfully removed the playlist.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'Playlist removed successfully!'
      400:
        description: Playlist not found or deletion permission denied.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'You do not have permission to delete this playlist.'
      500:
        description: A database error occurred or an unexpected issue during playlist removal.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'An error occurred while removing the playlist. Please try again.'
    """

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

# route to get all playlist of the current user
@views_bp.get('/playlists')
@login_required
def user_playlists():
    """
    Retrieve a list of playlists belonging to the current user.

    This route fetches and displays all playlists created by the currently authenticated user. The playlists are rendered
    on a webpage, where users can view the titles and other details of their playlists.

    ---
    tags:
      - Playlist
    responses:
      200:
        description: Successfully retrieved the list of user playlists.
        schema:
          type: object
          properties:
            playlists:
              type: array
              items:
                type: object
                description: List of playlists belonging to the current user.
            email_form:
              type: object
              description: The email form object to be rendered in the template.
      401:
        description: Unauthorized access, the user needs to be logged in to view playlists.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'User must be logged in to view playlists.'
    """

    # Fetch all playlists belonging to the current user
    email_form = EmailForm()
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()


    return render_template('viewplaylist.html', playlists=playlists,email_form=email_form)


@views_bp.get('/open_playlist/<int:playlist_id>')
def open_playlist(playlist_id):
    """
    Open a specific playlist with its episodes and related information.

    This route allows the user to view the details of a playlist, including episodes in the playlist.
    The user can also search for specific episodes by title. Favourites and their states are also displayed.

    ---
    tags:
      - Playlist
    parameters:
      - name: playlist_id
        in: path
        type: integer
        required: true
        description: The ID of the playlist to be opened.
      - name: title
        in: query
        type: string
        required: false
        description: A search term to filter episodes by title (case-insensitive).
    responses:
      200:
        description: Successfully retrieved the playlist and its episodes.
        schema:
          type: object
          properties:
            playlist_items:
              type: array
              items:
                type: object
                description: List of episodes in the playlist
            playlist:
              type: object
              description: The playlist details (ID, title, user, etc.)
            favourite_counts:
              type: object
              description: Mapping of episode IDs to the number of favourites.
            favourite_state:
              type: object
              description: Mapping of episode IDs to the current user's favourite state (True/False).
      400:
        description: Invalid or missing playlist ID or other request-related issues.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'Playlist not found.'
      500:
        description: An unexpected error occurred.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'An error occurred while retrieving the playlist.'
    """

    try:
        email_form=EmailForm()
        title_search = request.args.get('title')
        print('this is title serar',title_search)


        playlist_items = []
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
        if playlist:
            print(playlist.id)
            playlist_playlist_item=PlaylistPlaylistitem.query.filter_by(playlist_id=playlist.id).all()
            playlist_items_ids = [i.to_dict().get('playlist_item_id') for i in playlist_playlist_item]
            for i in playlist_items_ids:
                playlist_item = PlaylistItem.query.filter_by(id = i).first()
                playlist_items.append(playlist_item)
            if title_search:
                print(title_search)
                playlist_items = [a.episode for a in playlist_items if isinstance(a.episode.title, str) and SequenceMatcher(None, a.episode.title.upper(), title_search.upper()).ratio() > 0.5]
            else:
                playlist_items = [a.episode for a in playlist_items]
            favourite_counts = {i.id:len(i.favourites) for i in playlist_items}
            favourite_state = {i.id: True if any(fav.user_id == current_user.id for fav in i.favourites) else False for i in
                           playlist_items}

        if not playlist:
            flash('Playlist not found.', 'error')
            return redirect(url_for('views_bp.user_playlists'))

        return render_template(
            'open_playlist.html',
            playlist_items=playlist_items,
            playlist=playlist,
            favourite_counts=favourite_counts,
            favourite_state=favourite_state,
            email_form=email_form

        )


    except Exception as e:
        flash(f'An error occured')
        return render_template('open_playlist.html', playlist_items=playlist_items,playlist=playlist,email_form=email_form)
# route to add episode to playlist
@views_bp.route('/add_to_playlist', methods=['POST'])
@login_required
def add_to_playlist():
    """
    Add an episode to a playlist.

    ---
    tags:
      - Playlist
    parameters:
      - name: episode_id
        in: body
        type: integer
        required: true
        description: The ID of the episode to be added to the playlist.
      - name: playlist_id
        in: body
        type: integer
        required: true
        description: The ID of the playlist to which the episode should be added.
    responses:
      201:
        description: Episode successfully added to the playlist.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'Episode added to playlist successfully'
      200:
        description: Episode already exists in the playlist.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'Episode already exists in playlist'
      400:
        description: Missing required data or invalid data provided.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'episode_id and playlist_id are required'
      404:
        description: Playlist or episode not found.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'playlist or episode not found'
      500:
        description: An unexpected error occurred.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'An unexpected error occurred: <error_details>'
    """

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

# route to remove episode from playlist
@views_bp.route('/remove_from_playlist', methods=['GET','DELETE'])
@login_required
def remove_from_playlist():
    """
    Remove an episode from a playlist.

    ---
    tags:
      - Playlist
    parameters:
      - name: episode_id
        in: body
        type: integer
        required: true
        description: The ID of the episode to be removed from the playlist.
      - name: playlist_id
        in: body
        type: integer
        required: true
        description: The ID of the playlist from which the episode is to be removed.
    responses:
      200:
        description: Successfully removed the episode from the playlist.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'Episode removed from playlist successfully'
      400:
        description: Missing required data or invalid data provided.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'episode_id and playlist_id are required'
      404:
        description: Playlist or episode not found, or episode not found in the playlist.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'Episode not found in the playlist'
      500:
        description: An unexpected error occurred.
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 'An unexpected error occurred: <error_details>'
    """

    try:
        # Parse JSON data from the request
        data = request.json

        if not data:
            logger.error('no data provided')
            return jsonify({'msg': 'No data provided'}), 400

        episode_id = data.get('episode_id')
        playlist_id = data.get('playlist_id')

        if not episode_id or not playlist_id:
            return jsonify({'msg': 'episode_id and playlist_id are required'}), 400

        # Query the database for the playlist and episode
        playlist = Playlist.query.get(playlist_id)
        episode = Episode.query.get(episode_id)

        if not playlist or not episode:
            logger.error('episode or playlist not found')
            return jsonify({'msg': 'playlist or episode not found'}), 404

        # Query the association table to check if the item exists
        playlist_item_association = PlaylistPlaylistitem.query.filter_by(
            playlist_id=playlist_id,
            playlist_item_id=episode.playlist_items.id
        ).first()

        if not playlist_item_association:
            logger.error('episode not found in playlist')
            return jsonify({'msg': 'Episode not found in the playlist'}), 404

        # Remove the playlist item from the playlist
        db.session.delete(playlist_item_association)

        # If there are no other references to the playlist item, delete the playlist item itself
        # You may need to add logic to ensure it's safe to delete (e.g., no other playlist associations exist)
        if not PlaylistPlaylistitem.query.filter_by(playlist_item_id=episode.playlist_items.id).first():
            db.session.delete(episode.playlist_items)

        db.session.commit()
        logger.info('episode successfully removed')
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
    """
    Get all episodes in a specific playlist.

    ---
    tags:
      - Playlist
    parameters:
      - name: playlist_id
        in: path
        type: integer
        required: true
        description: The ID of the playlist whose episodes are to be retrieved.
    responses:
      200:
        description: Successfully retrieved the episodes in the playlist.
        schema:
          type: object
          properties:
            playlist:
              type: object
              description: Playlist details
            episodes:
              type: array
              items:
                type: object
                description: Episode details
      404:
        description: Playlist not found.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Playlist not found'
            data:
              type: object
              example: null
    """

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
    """
    Delete a playlist and its associated items.

    ---
    tags:
      - Playlist
    parameters:
      - name: playlist_id
        in: path
        type: integer
        required: true
        description: The ID of the playlist to be deleted.
    responses:
      200:
        description: Successfully deleted the playlist and its associated items.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'success'
            message:
              type: string
              example: 'Playlist deleted successfully'
            data:
              type: object
              example: null
      404:
        description: Playlist not found.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Playlist not found'
            data:
              type: object
              example: null
    """

    playlist = Playlist.query.get_or_404(playlist_id)

    # Deleting associated PlaylistItems from PlaylistPlaylistitem relationship
    PlaylistPlaylistitem.query.filter_by(playlist_id=playlist_id).delete()

    # Deleting the playlist itself
    db.session.delete(playlist)
    db.session.commit()

    return redirect(url_for('views.podcasts'))  # Redirect to the list of podcasts or playlists


@views_bp.post('/favourite')
@login_required
def add_favourite():
    """
    Add an episode to the user's favourites.

    ---
    tags:
      - Favourite
    parameters:
      - name: episode_id
        in: body
        type: string
        required: true
        description: The ID of the episode to add to favourites.
    responses:
      201:
        description: Successfully added the episode to favourites.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'success'
            message:
              type: string
              example: 'Added to favourites'
            data:
              type: object
              example: null
      400:
        description: Missing episode ID in the request.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Episode ID is required'
            data:
              type: object
              example: null
      409:
        description: Episode is already in the user's favourites.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Already in favourites'
            data:
              type: object
              example: null
      500:
        description: Error when adding the episode to favourites.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Favourite action failed'
            error_code:
              type: string
              example: 'SERVER ERROR'
            data:
              type: object
              example: null
    """

    data = request.json
    episode_id = data.get('episode_id')

    # Validate input
    if not episode_id:
        return jsonify({'status': 'error', 'message': 'Episode ID is required', 'data': None}), 400

    try:
        # Check if the episode is already in the user's favorites
        existing_favourite = Favourite.query.filter_by(user_id=current_user.id, episode_id=episode_id).first()

        if existing_favourite:
            return jsonify({'status': 'error', 'message': 'Already in favourites', 'data': None}), 409

        # Add to favourites
        new_favourite = Favourite(user_id=current_user.id, episode_id=episode_id)
        db.session.add(new_favourite)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Added to favourites', 'data': None}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'Favourite action failed', 'error_code': 'SERVER ERROR',
                        'data': None}), 500


@views_bp.delete('/favourite')
@login_required
def remove_favourite():
    """
    Remove an episode from the user's favourites.

    ---
    tags:
      - Favourite
    parameters:
      - name: episode_id
        in: body
        type: string
        required: true
        description: The ID of the episode to remove from favourites.
    responses:
      201:
        description: Successfully removed the episode from favourites.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'success'
            message:
              type: string
              example: 'removed from favourites'
            data:
              type: object
              example: null
      400:
        description: Missing episode ID in the request.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Episode ID is required'
            data:
              type: object
              example: null
      404:
        description: Episode not found in the user's favourites.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'not found'
            data:
              type: object
              example: null
      500:
        description: Error when removing the favourite.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Favourite action failed'
            error_code:
              type: string
              example: 'SERVER ERROR'
            data:
              type: object
              example: null
    """

    data = request.json
    episode_id = data.get('episode_id')

    # Validate input
    if not episode_id:
        return jsonify({'status': 'error', 'message': 'Episode ID is required', 'data': None}), 400

    try:
        # Check if the episode is already in the user's favorites
        existing_favourite = Favourite.query.filter_by(user_id=current_user.id, episode_id=episode_id).first()

        if existing_favourite:
            db.session.delete(existing_favourite)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'removed from favourites', 'data': None}), 201
        else:
            return jsonify({'status': 'error', 'message': 'not found', 'data': None}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'Favourite action failed', 'error_code': 'SERVER ERROR',
                        'data': None}), 500


@views_bp.get('/favourite')
@login_required
def get_episode_favourites():
    """
    Retrieve the number of favourites (likes) for a specific episode.

    ---
    tags:
      - Favourite
    parameters:
      - name: episode_id
        in: query
        type: string
        required: true
        description: The ID of the episode to retrieve the favourite count for.
    responses:
      200:
        description: Successfully retrieved the number of favourites.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'success'
            message:
              type: string
              example: 'Retrieved number of likes'
            data:
              type: integer
              example: 42
      400:
        description: Missing episode ID in the request.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Episode ID is required'
            data:
              type: object
              example: null
      500:
        description: Error when retrieving the favourite count.
        schema:
          type: object
          properties:
            status:
              type: string
              example: 'error'
            message:
              type: string
              example: 'Favourite action failed'
            error_code:
              type: string
              example: 'SERVER ERROR'
            data:
              type: object
              example: null
    """

    # Get episode_id from query parameters
    episode_id = request.args.get('episode_id')

    # Validate input
    if not episode_id:
        return jsonify({'status': 'error', 'message': 'Episode ID is required', 'data': None}), 400

    try:
        # Count favourites for the episode
        favourite_count = Favourite.query.filter_by(episode_id=episode_id).count()

        return jsonify({'status': 'success', 'message': 'Retrieved number of likes', 'data': favourite_count}), 200
    except SQLAlchemyError as e:
        logger.error(str(e))
        return jsonify({'status': 'error', 'message': 'Favourite action failed', 'error_code': 'SERVER ERROR',
                        'data': None}), 500




@views_bp.route('/preferences',methods=['GET','PUT'])
def preferences():

    """
    User preferences update (GET/PUT).

    ---
    tags:
      - Preferences
    parameters:
      - name: username
        in: formData
        type: string
        required: false
        description: The username to update.
      - name: email
        in: formData
        type: string
        required: false
        description: The email address to update.
      - name: avatar
        in: formData
        type: file
        required: false
        description: The avatar image to upload (if provided).
    responses:
      200:
        description: User preferences updated successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Updated preferences'
      400:
        description: Error updating user preferences or file upload failure.
        schema:
          type: object
          properties:
            error:
              type: string
              example: 'Error uploading image: <error_message>'
      500:
        description: Internal server error during database operation.
        schema:
          type: object
          properties:
            error:
              type: string
              example: 'Error updating preferences'
    """

    email_form = EmailForm()
    form = PreferencesForm()
    username= None
    email = None
    blob_name = None

    if form.validate_on_submit():
        logging.info("Form is valid,processing data")
        username = form.username.data
        email = form.email.data
        if form.avatar.data:
            image_file = form.avatar.data
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
                return render_template('profile.html', form=form)

            # Clean up the temporary file after upload
            if os.path.exists(file_path):
                os.remove(file_path)

        try:
            update_user_details = User.query.filter_by(id=current_user.id).first()  # Get the first matching user
            if update_user_details:  # Make sure the user exists
                if username:
                    update_user_details.username = username
                if email:
                    update_user_details.email = email
                db.session.commit()
                flash('updated preferences','success')
                return redirect(url_for('views.preferences'))
        except SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            azure_storage_instance.delete_blob(container_name, blob_name)
            return render_template('profile.html',email_form=email_form,form = form)

    return render_template('profile.html',email_form=email_form,form = form)


@views_bp.route('/email', methods=['POST'])
def email_route():
    referrer = request.referrer
    try:
        from tasks.emailservice import send_verification_email

        form = EmailForm(request.form)

        if form.validate_on_submit():
            logger.info('Form is valid, processing data')
            email = form.email.data
            token = 'd'

            # Send email task
            task = send_verification_email.apply_async(args=[email, token])
            task_id = task.id
            task_info_singleton = TaskInfoSingleton()
            task_info_singleton.set_task_info(task_id, 'send_verification')

            # Flash a success message
            flash('Sent Subscription Message to your Inbox', 'success')

        else:
            # Flash an error message if form validation fails
            flash('Invalid form data. Please try again.', 'danger')

    except Exception as e:
        # Log the error and flash a failure message
        logger.error(f"Error processing email route: {str(e)}")
        flash('An error occurred. Please try again later.', 'danger')

    return redirect(referrer)


@views_bp.route('/categories')
def categories():
    """
    Displays the categories page where users can view different categories and submit their email.

    This route performs the following actions:
    - Retrieves the form for submitting an email (`EmailForm`).
    - Retrieves category details from the `categories_details` variable (or any source it's derived from).
    - Renders the `categories.html` template, passing the email form and category details for display.

    Context Provided to Template:
        - email_form: The form for the user to submit their email.
        - categories: A list or dictionary of category details that will be displayed on the page.

    Returns:
        render_template: Renders the `categories.html` template with the provided context.
    """
    email_form = EmailForm()
    category_details = categories_details
    return render_template('categories.html', email_form=email_form, categories=category_details)


@views_bp.route('/logout')
def logout():
    """
    Logs the user out of the application, invalidates the GitHub OAuth token if it exists,
    and clears the session.

    This route performs the following actions:
    - Logs the user out of the Flask app by calling `logout_user()`.
    - If an OAuth token exists in the session, it attempts to invalidate the token
      by sending a DELETE request to the GitHub OAuth application API.
    - Clears any session data related to the OAuth token.
    - Displays a success message via `flash` indicating that the user has been logged out.
    - Redirects the user to the home page after logout.

    Responses:
        - 200: Successfully logged out and invalidated GitHub OAuth token.
        - 400: Error occurred while invalidating the GitHub OAuth token.

    Returns:
        redirect: Redirects to the home page (`views.index`).
    """
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

#TODO : implement live podcast feature