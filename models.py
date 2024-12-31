from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, backref
from sqlalchemy import String, Enum,Integer, DateTime, ForeignKey, SmallInteger
from sqlalchemy.sql import func
from model_utils import Providers, Roles, Categories
from flask_login import UserMixin


class Base(DeclarativeBase):
    ...


db = SQLAlchemy(model_class=Base)


class User(db.Model,UserMixin):
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement="auto")
    oauth_provider:Mapped[Providers] = mapped_column(Enum(Providers),nullable=False,default=Providers.GITHUB)
    oauth_id:Mapped[str] = mapped_column(String,unique=True,nullable=False)
    username: Mapped[str] = mapped_column(String,nullable=False)
    profile_image_url: Mapped[str] = mapped_column(String,nullable=False)
    email: Mapped[str] = mapped_column(String,nullable=True)
    role:Mapped[Roles] = mapped_column(Enum(Roles),nullable=False,default=Roles.USER)
    created_at:Mapped[DateTime] = mapped_column(DateTime,server_default=func.now(),nullable=False)

class Podcast(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    title: Mapped[str] = mapped_column(String,nullable=False)
    description:Mapped[str] = mapped_column(String,nullable=False)
    category:Mapped[Categories] = mapped_column(Enum(Categories),nullable=False)
    publisher:Mapped[str] = mapped_column(String,nullable=False)
    publish_date:Mapped[DateTime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
    image_url:Mapped[str] = mapped_column(String,nullable=True)
    feed_url: Mapped[str] = mapped_column(String,nullable=True)
    audio_url:Mapped[str] = mapped_column(String,nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    episodes:Mapped[list['Episode']] = db.relationship('Episode',backref = 'podcast')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not (self.feed_url or self.audio_url):
            raise ValueError("Either 'feed_url' or 'audio_url' must be provided.")
        if self.feed_url and self.audio_url:
            raise ValueError("'feed_url' and 'audio_url' can't be provided at once.")
class Episode(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement="auto")
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    duration:Mapped[int] = mapped_column(Integer,nullable=True)
    publish_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    audio_url:Mapped[str] = mapped_column(String,nullable=False)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id'),nullable=False)


class Subscription(db.Model):
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey('user.id'),primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id'),primary_key=True)
    subscribed_date:Mapped[DateTime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
    podcasts:Mapped[list['Podcast']] = db.relationship('Podcast',backref='subscription')
    users: Mapped[list['User']] = db.relationship('User', backref='subscription')

class Favourite(db.Model):
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey('user.id'),nullable=False,primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id'),primary_key=True,nullable=True)
    episode_id:Mapped[int] = mapped_column(Integer,ForeignKey('episode.id'),primary_key=True,nullable=True)
    added_date:Mapped[DateTime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
    podcasts:Mapped[list['Podcast']] = db.relationship('Podcast',backref='favourite')
    episodes:Mapped[list['Episode']] = db.relationship('Episode',backref = 'favourite')
    users: Mapped[list['User']] = db.relationship('User', backref='favourite')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")

class Rating(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id'), primary_key=True,nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey('episode.id'), primary_key=True, nullable=True)
    rating:Mapped[int] = mapped_column(SmallInteger,nullable=False)
    review_text:Mapped[str] = mapped_column(String,nullable=True)
    review_date:Mapped[DateTime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
    podcasts: Mapped[list['Podcast']] = db.relationship('Podcast', backref='rating')
    episodes: Mapped[list['Episode']] = db.relationship('Episode', backref='rating')
    users: Mapped[list['User']] = db.relationship('User', backref='rating')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Enforce the condition that only one of podcast_id or episode_id should be set
        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        # Ensure that not both podcast_id and episode_id are provided
        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")

class Download(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id'), primary_key=True,nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey('episode.id'), primary_key=True, nullable=True)
    download_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    podcasts: Mapped[list['Podcast']] = db.relationship('Podcast', backref='download')
    episodes: Mapped[list['Episode']] = db.relationship('Episode', backref='download')
    users: Mapped[list['User']] = db.relationship('User', backref='download')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Enforce the condition that only one of podcast_id or episode_id should be set
        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        # Ensure that not both podcast_id and episode_id are provided
        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")



class Playlist(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement='auto')
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey('user.id'),nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False,unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    user = db.relationship('User',backref = 'playlist')

class PlaylistItem(db.Model):
    __tablename__ = 'playlistitem'
    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement='auto')
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id'), nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer,ForeignKey('episode.id'),nullable=True)
    added_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    podcast = db.relationship('Podcast', backref='playlist_item',uselist=False)
    episodes = db.relationship('Episode', backref='playlist_item',uselist=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")


class SharedPlaylist(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, primary_key=True)
    playlist_id: Mapped[int] = mapped_column(Integer, ForeignKey('playlist.id'), primary_key=True, nullable=False)
    user:Mapped['User'] = db.relationship('User',backref='shared_playlist')
    playlist:Mapped['Playlist'] = db.relationship('Playlist',backref='shared_playlist')


class PlaylistPlaylistitem(db.Model):
    playlist_id: Mapped[int] = mapped_column(Integer, ForeignKey('playlist.id'), primary_key=True, nullable=False)
    playlist_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('playlistitem.id'), primary_key=True, nullable=False)
    playlist: Mapped['Playlist'] = db.relationship('Playlist', backref='playlist_playlist_items')
    playlist_item:Mapped['PlaylistItem'] = db.relationship('PlaylistItem',backref = 'playlist_playlist_items')

# TODO : filter by , title,user,posted