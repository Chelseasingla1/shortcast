import unittest
from app.models import db, User,Podcast,Episode,Subscription,Favourite,Rating,Download,Playlist,PlaylistItem, \
    PlaylistPlaylistitem
from sqlalchemy import create_engine,func
from sqlalchemy.orm import sessionmaker
from app.model_utils import Providers, Roles, Categories

class TestModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)
        db.metadata.create_all(cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_create_user(self):
        user = User(
            oauth_provider=Providers.GITHUB,
            oauth_id='12345',
            username='testuser',
            profile_image_url='http://example.com/image.png',
            email='testuser@example.com',
            role=Roles.USER

        )
        self.session.add(user)
        self.session.commit()
        retrieved_user = self.session.query(User).filter_by(username='testuser').one()
        print(retrieved_user.id)
        self.assertEqual(retrieved_user.username, 'testuser')
        self.assertEqual(retrieved_user.email, 'testuser@example.com')


    def test_create_podcast(self):
        podcast = Podcast(
            title='Test Podcast',
            description='A test podcast',
            category=Categories.COMEDY,
            publisher='Test Publisher',
            image_url='http://example.com/image.png',
            feed_url='http://example.com/feed'
        )
        self.session.add(podcast)
        self.session.commit()
        retrieved_podcast = self.session.query(Podcast).filter_by(title='Test Podcast').one()
        self.assertEqual(retrieved_podcast.title, 'Test Podcast')
        self.assertEqual(retrieved_podcast.publisher, 'Test Publisher')


    def test_create_episode(self):
        podcast = Podcast(
            title='Test Podcast',
            description='A test podcast',
            category=Categories.COMEDY,
            publisher='Test Publisher',
            image_url='http://example.com/image.png',
            feed_url='http://example.com/feed'
        )
        self.session.add(podcast)
        self.session.commit()
        episode = Episode(
            title='Test Episode',
            description='A test episode',
            duration=3,
            publish_date=func.now(),
            audio_url='http://example.com/audio.mp3',
            podcast_id=podcast.id
        )
        self.session.add(episode)
        self.session.commit()
        retrieved_episode = self.session.query(Episode).filter_by(title='Test Episode').one()
        print(retrieved_episode.podcast)
        self.assertEqual(retrieved_episode.title, 'Test Episode')
        self.assertEqual(retrieved_episode.podcast_id, podcast.id)


    def test_create_subscription(self):
        user = User(
            oauth_provider=Providers.GITHUB,
            oauth_id='12345',
            username='testuser',
            profile_image_url='http://example.com/image.png',
            email='testuser@example.com',
            role=Roles.USER
        )
        self.session.add(user)
        self.session.commit()
        podcast = Podcast(
            title='Test Podcast',
            description='A test podcast',
            category=Categories.COMEDY,
            publisher='Test Publisher',
            publish_date=func.now(),
            image_url='http://example.com/image.png',
            feed_url='http://example.com/feed'
        )
        self.session.add(podcast)
        self.session.commit()
        subscription = Subscription(
            user_id=user.id,
            podcast_id=podcast.id,
            subscribed_date=func.now()
        )
        self.session.add(subscription)
        self.session.commit()
        retrieved_subscription = self.session.query(Subscription).filter_by(user_id=user.id, podcast_id=podcast.id).one()
        print(type(retrieved_subscription.subscribed_date))
        self.assertEqual(retrieved_subscription.user_id, user.id)
        self.assertEqual(retrieved_subscription.podcast_id, podcast.id)

    def test_create_favourite(self):
        user = User(
            oauth_provider=Providers.GITHUB,
            oauth_id='12345',
            username='testuser',
            profile_image_url='http://example.com/image.png',
            email='testuser@example.com',
            role=Roles.USER
        )
        self.session.add(user)
        self.session.commit()
        podcast = Podcast(
            title='Test Podcast',
            description='A test podcast',
            category=Categories.COMEDY,
            publisher='Test Publisher',
            image_url='http://example.com/image.png',
            feed_url='http://example.com/feed'
        )
        self.session.add(podcast)
        self.session.commit()
        favourite = Favourite(
            user_id=user.id,
            podcast_id=podcast.id,
        )
        self.session.add(favourite)
        self.session.commit()
        retrieved_favourite = self.session.query(Favourite).filter_by(user_id=user.id, podcast_id=podcast.id).one()
        self.assertEqual(retrieved_favourite.user_id, user.id)
        self.assertEqual(retrieved_favourite.podcast_id, podcast.id)


    def test_create_rating(self):
        user = User(
            oauth_provider=Providers.GITHUB,
            oauth_id='12345',
            username='testuser',
            profile_image_url='http://example.com/image.png',
            email='testuser@example.com',
            role=Roles.USER
        )
        self.session.add(user)
        self.session.commit()
        podcast = Podcast(
            title='Test Podcast',
            description='A test podcast',
            category=Categories.COMEDY,
            publisher='Test Publisher',
            id = '222',
            publish_date=func.now(),
            image_url='http://example.com/image.png',
            feed_url='http://example.com/feed'
        )
        self.session.add(podcast)
        self.session.commit()
        rating = Rating(
            user_id=user.id,
            podcast_id=podcast.id,
            rating=5,
            review_text='Great podcast!',
            review_date=func.now()
        )
        self.session.add(rating)
        self.session.commit()
        retrieved_rating = self.session.query(Rating).filter_by(user_id=user.id, podcast_id=podcast.id).one()
        self.assertEqual(retrieved_rating.user_id, user.id)
        self.assertEqual(retrieved_rating.podcast_id, podcast.id)
        self.assertEqual(retrieved_rating.rating, 5)
        self.assertEqual(retrieved_rating.review_text, 'Great podcast!')



    def test_create_download(self):
        user = User(
            oauth_provider=Providers.GITHUB,
            oauth_id='12345',
            username='testuser',
            profile_image_url='http://example.com/image.png',
            email='testuser@example.com',
            role=Roles.USER
        )
        self.session.add(user)
        self.session.commit()
        podcast = Podcast(
            title='Test Podcast',
            description='A test podcast',
            category=Categories.COMEDY,
            publisher='Test Publisher',
            publish_date=func.now(),
            image_url='http://example.com/image.png',
            feed_url='http://example.com/feed'
        )
        self.session.add(podcast)
        self.session.commit()
        download = Download(
            user_id=user.id,
            podcast_id=podcast.id,
            download_date=func.now()
        )
        self.session.add(download)
        self.session.commit()
        retrieved_download = self.session.query(Download).filter_by(user_id=user.id, podcast_id=podcast.id).one()
        self.assertEqual(retrieved_download.user_id, user.id)
        self.assertEqual(retrieved_download.podcast_id, podcast.id)

    def test_create_playlist(self):
        user = User(
            oauth_provider=Providers.GITHUB,
            oauth_id='12345',
            username='testuser',
            profile_image_url='http://example.com/image.png',
            email='testuser@example.com',
            role=Roles.USER
        )
        self.session.add(user)
        self.session.commit()
        playlist = Playlist(
            user_id=user.id,
            title='Test Playlist',
            created_at=func.now()
        )
        self.session.add(playlist)
        self.session.commit()
        retrieved_playlist = self.session.query(Playlist).filter_by(title='Test Playlist').one()
        self.assertEqual(retrieved_playlist.title, 'Test Playlist')
        self.assertEqual(retrieved_playlist.user_id, user.id)



    def test_create_playlist_item(self):
        podcast = Podcast(
            title='Test Podcast',
            description='A test podcast',
            category=Categories.COMEDY,
            publisher='Test Publisher',
            publish_date=func.now(),
            image_url='http://example.com/image.png',
            feed_url='http://example.com/feed'
        )
        self.session.add(podcast)
        self.session.commit()
        playlist_item = PlaylistItem(
            podcast_id=podcast.id,
            added_date=func.now()
        )
        self.session.add(playlist_item)
        self.session.commit()
        retrieved_playlist_item = self.session.query(PlaylistItem).filter_by(podcast_id=podcast.id).one()
        self.assertEqual(retrieved_playlist_item.podcast_id, podcast.id)

    def test_create_playlist_playlistitem(self):
        user = User(
            oauth_provider='GITHUB',
            oauth_id='12345',
            username='testuser',
            profile_image_url='http://example.com/image.png',
            email='testuser@example.com',
            role='USER'
        )
        self.session.add(user)
        self.session.commit()

        playlist = Playlist(
            user_id=user.id,
            title='Test Playlist',
            created_at=func.now()
        )
        self.session.add(playlist)
        self.session.commit()

        podcast = Podcast(
            title='Test Podcast',
            description='A test podcast',
            category='COMEDY',
            publisher='Test Publisher',
            image_url='http://example.com/image.png',
            feed_url='http://example.com/feed'
        )
        self.session.add(podcast)
        self.session.commit()

        playlist_item = PlaylistItem(
            podcast_id=podcast.id,
            added_date=func.now()
        )
        self.session.add(playlist_item)
        self.session.commit()

        playlist_playlistitem = PlaylistPlaylistitem(
            playlist_id=playlist.id,
            playlist_item_id=playlist_item.id
        )
        self.session.add(playlist_playlistitem)
        self.session.commit()

        retrieved_playlist_playlistitem = self.session.query(PlaylistPlaylistitem).filter_by(
            playlist_id=playlist.id, playlist_item_id=playlist_item.id).one()
        self.assertEqual(retrieved_playlist_playlistitem.playlist_id, playlist.id)
        self.assertEqual(retrieved_playlist_playlistitem.playlist_item_id, playlist_item.id)
if __name__ == '__main__':
    unittest.main()