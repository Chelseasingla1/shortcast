from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
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
    subscriptions: Mapped[list['Subscription']] = db.relationship('Subscription', backref='user',cascade='all, delete-orphan')
    favourites: Mapped[list['Favourite']] = db.relationship('Favourite', backref='user',cascade='all, delete-orphan')
    shared_playlist = db.relationship('SharedPlaylist', backref='user', cascade='all, delete-orphan')
    playlist = db.relationship('Playlist', backref='user',cascade = 'all ,delete-orphan')
    ratings: Mapped[list['Rating']] = db.relationship('Rating', backref='user',cascade='all, delete-orphan')
    downloads: Mapped[list['Download']] = db.relationship('Download', backref='user', cascade='all, delete-orphan')

    def to_dict(self):

        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role':self.role,
            'created_at': self.created_at.isoformat()  # Convert datetime to ISO format string
        }

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
    episodes:Mapped[list['Episode']] = db.relationship('Episode',backref = 'podcast',cascade='all, delete-orphan')
    subscriptions:Mapped[list['Subscription']] = db.relationship('Subscription',backref = 'podcast',cascade='all, delete-orphan')
    favourites: Mapped[list['Favourite']] = db.relationship('Favourite', backref='podcast',cascade='all, delete-orphan')
    playlist_items = db.relationship('PlaylistItem', backref='podcast', uselist=False, cascade='all, delete-orphan')
    ratings: Mapped[list['Rating']] = db.relationship('Rating', backref='podcast',cascade='all, delete-orphan')
    downloads: Mapped[list['Download']] = db.relationship('Download', backref='pocast', cascade='all, delete-orphan')
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
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id',name='fk_podcast_episode'),nullable=False)
    favourites: Mapped[list['Favourite']] = db.relationship('Favourite', backref='episode',cascade='all, delete-orphan')
    playlist_items = db.relationship('PlaylistItem', backref='episode', uselist=False,cascade='all, delete-orphan')
    ratings: Mapped[list['Rating']] = db.relationship('Rating', backref='episode',cascade = 'all,delete-orphan')
    downloads: Mapped[list['Download']] = db.relationship('Download', backref='episode', cascade='all, delete-orphan')

class Subscription(db.Model):
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey('user.id',name='fk_user_subscription'),primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id',name='fk_podcast_subscription'),primary_key=True)
    subscribed_date:Mapped[DateTime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
    # podcasts:Mapped[list['Podcast']] = db.relationship('Podcast',backref='subscription')
    # users: Mapped[list['User']] = db.relationship('User', backref='subscription')

class Favourite(db.Model):
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey('user.id',name='fk_user_favourite'),nullable=False,primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id',name='fk_podcast_favourite'),primary_key=True,nullable=True)
    episode_id:Mapped[int] = mapped_column(Integer,ForeignKey('episode.id',name='fk_episode_favourite'),primary_key=True,nullable=True)
    added_date:Mapped[DateTime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
    # podcasts:Mapped[list['Podcast']] = db.relationship('Podcast',backref='favourite')
    # episodes:Mapped[list['Episode']] = db.relationship('Episode',backref = 'favourite')
    # users: Mapped[list['User']] = db.relationship('User', backref='favourite')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")

class Rating(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id',name='fk_user_rating'), nullable=False, primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id',name='fk_podcast_rating'), primary_key=True,nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey('episode.id',name='fk_episode_rating'), primary_key=True, nullable=True)
    rating:Mapped[int] = mapped_column(SmallInteger,nullable=False)
    review_text:Mapped[str] = mapped_column(String,nullable=True)
    review_date:Mapped[DateTime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
    # podcasts: Mapped[list['Podcast']] = db.relationship('Podcast', backref='rating')
    # episodes: Mapped[list['Episode']] = db.relationship('Episode', backref='rating')
    # users: Mapped[list['User']] = db.relationship('User', backref='rating')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Enforce the condition that only one of podcast_id or episode_id should be set
        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        # Ensure that not both podcast_id and episode_id are provided
        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")

class Download(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id',name='fk_user_download'), nullable=False, primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id',name='fk_podcast_download'), primary_key=True,nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey('episode.id',name='fk_episode_download'), primary_key=True, nullable=True)
    download_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    # podcasts: Mapped[list['Podcast']] = db.relationship('Podcast', backref='download')
    # episodes: Mapped[list['Episode']] = db.relationship('Episode', backref='download')
    # users: Mapped[list['User']] = db.relationship('User', backref='download')

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
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey('user.id',name='fk_user_playlist'),nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False,unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    shared_playlist:Mapped['SharedPlaylist'] = db.relationship('SharedPlaylist', backref='playlist', cascade='all, delete-orphan')
    playlist_playlist_item:Mapped['PlaylistPlaylistitem'] = db.relationship('PlaylistPlaylistitem', backref='playlist', cascade='all, delete-orphan')
class PlaylistItem(db.Model):
    __tablename__ = 'playlistitem'
    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement='auto')
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id',name='fk_podcast_playlist_item'), nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer,ForeignKey('episode.id',name='fk_episode_playlist_item'),nullable=True)
    added_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    playlist_playlist_item:Mapped['PlaylistPlaylistitem'] = db.relationship('PlaylistPlaylistitem', backref='playlistitem', cascade='all, delete-orphan')
    # podcast = db.relationship('Podcast', backref='playlist_item',uselist=False)
    # episodes = db.relationship('Episode', backref='playlist_item',uselist=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")


class SharedPlaylist(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id',name='fk_user_shared_playlist'), nullable=False, primary_key=True)
    playlist_id: Mapped[int] = mapped_column(Integer, ForeignKey('playlist.id',name='fk_playlist_shared_playlist'), primary_key=True, nullable=False)
    # user:Mapped['User'] = db.relationship('User',backref='shared_playlist')
    # playlist:Mapped['Playlist'] = db.relationship('Playlist',backref='shared_playlist')


class PlaylistPlaylistitem(db.Model):
    playlist_id: Mapped[int] = mapped_column(Integer, ForeignKey('playlist.id',name='fk_playlist_playlist_playlist_item'), primary_key=True, nullable=False)
    playlist_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('playlistitem.id',name='fk_playlist_item_playlist_playlist_item'), primary_key=True, nullable=False)
    # playlist: Mapped['Playlist'] = db.relationship('Playlist', backref='playlist_playlist_items')
    # playlist_item:Mapped['PlaylistItem'] = db.relationship('PlaylistItem',backref = 'playlist_playlist_items')

# TODO : filter by , title,user,posted