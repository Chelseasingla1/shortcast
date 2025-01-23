from flask_wtf.file import FileAllowed, FileSize
from wtforms.fields.choices import RadioField

from app.api.oauth.oauth import OauthFacade
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired, Optional, Length
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_authentication_links():
    oauth_obj_twitch = OauthFacade('twitch', response_type="code",
                                   scope=["user:read:email", "user:read:broadcast", "moderator:read:followers",
                                          "user:read:follows"])

    oauth_obj_github = OauthFacade('github', response_type="code",
                                   scope=["user:read:email", "user:read:broadcast", "moderator:read:followers",
                                          "user:read:follows"])

    auth_instance_twitch = oauth_obj_twitch
    auth_instance_github = oauth_obj_github
    auth_instances: dict = {'github_link': auth_instance_github.get_auth_link(),
                            'twitch_link': auth_instance_twitch.get_auth_link()}

    return auth_instances


class PlaylistForm(FlaskForm):
    title = StringField('Playlist Name', validators=[DataRequired()])
    image = FileField('Upload your playlist image', validators=[DataRequired()])


class EpisodeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=100)])
    duration = IntegerField('Duration (in seconds)', validators=[Optional()])
    podcast_id = SelectField('Select Podcast', coerce=int,
                             validators=[DataRequired()])  # Using SelectField for dropdown
    image_file = FileField('Upload Image File', validators=[Optional()])
    audio_file = FileField('Upload Audio File', validators=[DataRequired(),
                                                            FileAllowed(['mp3', 'wav', 'ogg'], 'Audio files only!'),
                                                            FileSize(
                                                                     max_size=50 * 1024 * 1024,
                                                                     message='File size must be under 10MB! or above 1MB!')
                                                            ])
    publish_date = StringField('Publish Date', default=datetime.now().isoformat(), validators=[Optional()])


class PodcastForm(FlaskForm):
    image_file = FileField('Upload Image File', validators=[Optional()])
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=1, max=500)])

    category = RadioField(
        'Select Categories',
    )
    duration = IntegerField('Duration (in seconds)', validators=[Optional()])


class AddToPlaylistForm(FlaskForm):
    episode_id = HiddenField('Episode ID', validators=[DataRequired()])
    playlist_id = HiddenField('Playlist ID', validators=[DataRequired()])


class EmailForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Length(min=1, max=500)])

class PreferencesForm(FlaskForm):
    avatar = FileField('Upload Avatar',validators=[Optional()])
    username = StringField('Username',validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(), Length(min=1, max=500)])




#TODO : configure celery to run the transcription service and the email service
#TODO : add pages and routes for creators to update their podcast and episodes
#TODO : get images from freepik