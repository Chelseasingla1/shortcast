from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Enum, Integer, DateTime, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.sql import func
from app.model_utils import Providers, Roles, Categories, Shared
from flask_login import UserMixin


class Base(DeclarativeBase):
    ...


db = SQLAlchemy(model_class=Base)


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement="auto")
    oauth_provider: Mapped[Providers] = mapped_column(Enum(Providers), nullable=False, default=Providers.GITHUB)
    oauth_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    profile_image_url: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[Roles] = mapped_column(Enum(Roles), nullable=False, default=Roles.USER)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    podcasts: Mapped[list['Podcast']] = db.relationship('Podcast', backref='user', cascade='all, delete-orphan')
    subscriptions: Mapped[list['Subscription']] = db.relationship('Subscription', backref='user',
                                                                  cascade='all, delete-orphan')
    favourites: Mapped[list['Favourite']] = db.relationship('Favourite', backref='user', cascade='all, delete-orphan')
    shared_playlist = db.relationship('SharedPlaylist', backref='user', cascade='all, delete-orphan')
    playlist = db.relationship('Playlist', backref='user', cascade='all ,delete-orphan')
    ratings: Mapped[list['Rating']] = db.relationship('Rating', backref='user', cascade='all, delete-orphan')
    downloads: Mapped[list['Download']] = db.relationship('Download', backref='user', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile_image': self.profile_image_url,
            'role': self.role,
            'created_at': self.created_at.isoformat()  # Convert datetime to ISO format string
        }


class Podcast(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[Categories] = mapped_column(Enum(Categories), nullable=False)
    publisher: Mapped[str] = mapped_column(String, nullable=False)
    publish_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    feed_url: Mapped[str] = mapped_column(String, nullable=True, unique=True, name='uq_podcast_feed_url')
    audio_url: Mapped[str] = mapped_column(String, nullable=True, unique=True, name='uq_podcast_audio_url')
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    episodes: Mapped[list['Episode']] = db.relationship('Episode', backref='podcast', cascade='all, delete-orphan')
    subscriptions: Mapped[list['Subscription']] = db.relationship('Subscription', backref='podcast',
                                                                  cascade='all, delete-orphan')
    favourites: Mapped[list['Favourite']] = db.relationship('Favourite', backref='podcast',
                                                            cascade='all, delete-orphan')
    playlist_items = db.relationship('PlaylistItem', backref='podcast', uselist=False, cascade='all, delete-orphan')
    ratings: Mapped[list['Rating']] = db.relationship('Rating', backref='podcast', cascade='all, delete-orphan')
    downloads: Mapped[list['Download']] = db.relationship('Download', backref='podcast', cascade='all, delete-orphan')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name='fk_user_podcast'), nullable=False)

    __table_args__ = (
        UniqueConstraint('publisher', 'title', name='uix_publisher_title'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate_urls(self):
        """Validates the feed_url and audio_url."""
        if not (self.feed_url or self.audio_url):
            raise ValueError("Either 'feed_url' or 'audio_url' must be provided.")
        if self.feed_url and self.audio_url:
            raise ValueError("'feed_url' and 'audio_url' can't be provided at once.")

    def to_dict(self):

        return {
            'podcast_id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category.name,
            'publisher': self.publisher,
            'publish_date': self.publish_date.isoformat(),
            'image_url': self.image_url,
            'feed_url': self.feed_url,
            'audio_url': self.audio_url,
            'duration': self.duration,
            'subscriptions': len(self.subscriptions)
        }


class Episode(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement="auto")
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    publish_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    audio_url: Mapped[str] = mapped_column(String, nullable=False, unique=True, name='uq_episode_audio_url')
    transcription:Mapped[str] = mapped_column(String,nullable=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id', name='fk_podcast_episode'),
                                            nullable=False)
    favourites: Mapped[list['Favourite']] = db.relationship('Favourite', backref='episode',
                                                            cascade='all, delete-orphan')
    playlist_items = db.relationship('PlaylistItem', backref='episode', uselist=False, cascade='all, delete-orphan')
    ratings: Mapped[list['Rating']] = db.relationship('Rating', backref='episode', cascade='all,delete-orphan')
    downloads: Mapped[list['Download']] = db.relationship('Download', backref='episode', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'episode_id': self.id,
            'podcast_id':self.podcast_id,
            'title': self.title,
            'description': self.description,
            'publish_date': self.publish_date.isoformat(),
            'image_url': self.image_url,
            'audio_url': self.audio_url,
            'duration': self.duration,

        }


class Subscription(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name='fk_user_subscription'), primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id', name='fk_podcast_subscription'),
                                            primary_key=True)
    subscribed_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # podcasts:Mapped[list['Podcast']] = db.relationship('Podcast',backref='subscription')
    # users: Mapped[list['User']] = db.relationship('User', backref='subscription')
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'podcast_id': self.podcast_id,
            'subscribed_date': self.subscribed_date.isoformat()
        }


class Favourite(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name='fk_user_favourite'), nullable=False,
                                         primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id', name='fk_podcast_favourite'),
                                            nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey('episode.id', name='fk_episode_favourite'),
                                            primary_key=True)
    added_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # podcasts:Mapped[list['Podcast']] = db.relationship('Podcast',backref='favourite')
    # episodes:Mapped[list['Episode']] = db.relationship('Episode',backref = 'favourite')
    # users: Mapped[list['User']] = db.relationship('User', backref='favourite')

    def to_dict(self):
        return {
            'added_date': self.added_date.isoformat()
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")


class Rating(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name='fk_user_rating'), nullable=False,
                                         primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id', name='fk_podcast_rating'),
                                             nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey('episode.id', name='fk_episode_rating'),
                                            primary_key=True)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    review_text: Mapped[str] = mapped_column(String, nullable=True)
    review_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # podcasts: Mapped[list['Podcast']] = db.relationship('Podcast', backref='rating')
    # episodes: Mapped[list['Episode']] = db.relationship('Episode', backref='rating')
    # users: Mapped[list['User']] = db.relationship('User', backref='rating')
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'podcast_id': self.podcast_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_date': self.review_date.isoformat()
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Enforce the condition that only one of podcast_id or episode_id should be set
        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        # Ensure that not both podcast_id and episode_id are provided
        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")


class Download(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name='fk_user_download'), nullable=False,
                                         primary_key=True)
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id', name='fk_podcast_download'),
                                         nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey('episode.id', name='fk_episode_download'),
                                            primary_key=True)
    download_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # podcasts: Mapped[list['Podcast']] = db.relationship('Podcast', backref='download')
    # episodes: Mapped[list['Episode']] = db.relationship('Episode', backref='download')
    # users: Mapped[list['User']] = db.relationship('User', backref='download')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'podcast_id': self.podcast_id,
            'episode_id': self.episode_id,
            'download_date': self.download_date.isoformat()
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Enforce the condition that only one of podcast_id or episode_id should be set
        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        # Ensure that not both podcast_id and episode_id are provided
        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")


class Playlist(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement='auto')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name='fk_user_playlist'), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True, name='uq_playlist_title')
    image_url: Mapped[str] = mapped_column(String, nullable=False,default='')
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    shared_playlist: Mapped['SharedPlaylist'] = db.relationship('SharedPlaylist', backref='playlist',
                                                                cascade='all, delete-orphan')
    playlist_playlist_item: Mapped['PlaylistPlaylistitem'] = db.relationship('PlaylistPlaylistitem', backref='playlist',
                                                                             cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url':self.image_url,
            'created_at': self.created_at.isoformat()
        }


class PlaylistItem(db.Model):
    __tablename__ = 'playlistitem'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement='auto')
    podcast_id: Mapped[int] = mapped_column(Integer, ForeignKey('podcast.id', name='fk_podcast_playlist_item'),
                                            nullable=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey('episode.id', name='fk_episode_playlist_item'),
                                            nullable=True)
    added_date: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    playlist_playlist_item: Mapped['PlaylistPlaylistitem'] = db.relationship('PlaylistPlaylistitem',
                                                                             backref='playlistitem',
                                                                             cascade='all, delete-orphan')

    # podcast = db.relationship('Podcast', backref='playlist_item',uselist=False)
    # episodes = db.relationship('Episode', backref='playlist_item',uselist=False)

    def to_dict(self):
        return {
            'id': self.id
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not (self.podcast_id or self.episode_id):
            raise ValueError("Either 'podcast_id' or 'episode_id' must be provided.")

        if self.podcast_id and self.episode_id:
            raise ValueError("You cannot provide both 'podcast_id' and 'episode_id'. Choose one.")


class SharedPlaylist(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name='fk_user_shared_playlist'), nullable=False,
                                         primary_key=True)
    playlist_id: Mapped[int] = mapped_column(Integer, ForeignKey('playlist.id', name='fk_playlist_shared_playlist'),
                                             primary_key=True, nullable=False)
    roles: Mapped[str] = mapped_column(Enum(Shared), nullable=False, default=Shared.CONSUMERS)

    # user:Mapped['User'] = db.relationship('User',backref='shared_playlist')
    # playlist:Mapped['Playlist'] = db.relationship('Playlist',backref='shared_playlist')
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'playlist_id': self.playlist_id,
            'role': self.roles,
            'playlist': self.playlist.to_dict() if self.playlist else None
        }


class PlaylistPlaylistitem(db.Model):
    playlist_id: Mapped[int] = mapped_column(Integer,
                                             ForeignKey('playlist.id', name='fk_playlist_playlist_playlist_item'),
                                             primary_key=True, nullable=False)
    playlist_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('playlistitem.id',
                                                                      name='fk_playlist_item_playlist_playlist_item'),
                                                  primary_key=True, nullable=False)

    # playlist: Mapped['Playlist'] = db.relationship('Playlist', backref='playlist_playlist_items')
    # playlist_item:Mapped['PlaylistItem'] = db.relationship('PlaylistItem',backref = 'playlist_playlist_items')
    def to_dict(self):
        return {
            'playlist_id': self.playlist_id,
            'playlist_item_id': self.playlist_item_id
        }
