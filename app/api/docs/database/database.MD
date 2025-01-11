# Database Models Documentation

## Overview
The database models for the Podcast Management System are defined using SQLAlchemy. These models represent various entities such as users, podcasts, episodes, subscriptions, favorites, ratings, downloads, playlists, and shared playlists.

## Models

### User
- **id**: Integer, Primary Key, Auto Increment
- **oauth_provider**: Enum (Providers), Not Null, Default: Providers.GITHUB
- **oauth_id**: String, Unique, Not Null
- **username**: String, Not Null
- **profile_image_url**: String, Not Null
- **email**: String, Nullable
- **role**: Enum (Roles), Not Null, Default: Roles.USER
- **created_at**: DateTime, Not Null, Default: `func.now()`

### Podcast
- **id**: Integer, Primary Key, Auto Increment
- **title**: String, Not Null
- **description**: String, Not Null
- **category**: Enum (Categories), Not Null
- **publisher**: String, Not Null
- **publish_date**: DateTime, Not Null, Default: `func.now()`
- **image_url**: String, Nullable
- **feed_url**: String, Nullable
- **audio_url**: String, Nullable
- **duration**: Integer, Nullable
- **episodes**: Relationship with `Episode`, Backref: 'podcast'

### Episode
- **id**: Integer, Primary Key, Auto Increment
- **title**: String, Not Null
- **description**: String, Not Null
- **duration**: Integer, Nullable
- **publish_date**: DateTime, Not Null, Default: `func.now()`
- **audio_url**: String, Not Null
- **podcast_id**: Integer, Foreign Key (`podcast.id`), Not Null

### Subscription
- **user_id**: Integer, Foreign Key (`user.id`), Primary Key
- **podcast_id**: Integer, Foreign Key (`podcast.id`), Primary Key
- **subscribed_date**: DateTime, Not Null, Default: `func.now()`
- **podcasts**: Relationship with `Podcast`, Backref: 'subscription'
- **users**: Relationship with `User`, Backref: 'subscription'

### Favourite
- **user_id**: Integer, Foreign Key (`user.id`), Primary Key
- **podcast_id**: Integer, Foreign Key (`podcast.id`), Primary Key, Nullable
- **episode_id**: Integer, Foreign Key (`episode.id`), Primary Key, Nullable
- **added_date**: DateTime, Not Null, Default: `func.now()`
- **podcasts**: Relationship with `Podcast`, Backref: 'favourite'
- **episodes**: Relationship with `Episode`, Backref: 'favourite'
- **users**: Relationship with `User`, Backref: 'favourite'

### Rating
- **user_id**: Integer, Foreign Key (`user.id`), Primary Key
- **podcast_id**: Integer, Foreign Key (`podcast.id`), Primary Key, Nullable
- **episode_id**: Integer, Foreign Key (`episode.id`), Primary Key, Nullable
- **rating**: SmallInteger, Not Null
- **review_text**: String, Nullable
- **review_date**: DateTime, Not Null, Default: `func.now()`
- **podcasts**: Relationship with `Podcast`, Backref: 'rating'
- **episodes**: Relationship with `Episode`, Backref: 'rating'
- **users**: Relationship with `User`, Backref: 'rating'

### Download
- **user_id**: Integer, Foreign Key (`user.id`), Primary Key
- **podcast_id**: Integer, Foreign Key (`podcast.id`), Primary Key, Nullable
- **episode_id**: Integer, Foreign Key (`episode.id`), Primary Key, Nullable
- **download_date**: DateTime, Not Null, Default: `func.now()`
- **podcasts**: Relationship with `Podcast`, Backref: 'download'
- **episodes**: Relationship with `Episode`, Backref: 'download'
- **users**: Relationship with `User`, Backref: 'download'

### Playlist
- **id**: Integer, Primary Key, Auto Increment
- **user_id**: Integer, Foreign Key (`user.id`), Not Null
- **title**: String, Not Null, Unique
- **created_at**: DateTime, Not Null, Default: `func.now()`
- **user**: Relationship with `User`, Backref: 'playlist'

### PlaylistItem
- **id**: Integer, Primary Key, Auto Increment
- **podcast_id**: Integer, Foreign Key (`podcast.id`), Nullable
- **episode_id**: Integer, Foreign Key (`episode.id`), Nullable
- **added_date**: DateTime, Not Null, Default: `func.now()`
- **podcast**: Relationship with `Podcast`, Backref: 'playlist_item', uselist=False
- **episodes**: Relationship with `Episode`, Backref: 'playlist_item', uselist=False

### SharedPlaylist
- **user_id**: Integer, Foreign Key (`user.id`), Primary Key
- **playlist_id**: Integer, Foreign Key (`playlist.id`), Primary Key, Not Null
- **user**: Relationship with `User`, Backref: 'shared_playlist'
- **playlist**: Relationship with `Playlist`, Backref: 'shared_playlist'

### PlaylistPlaylistitem
- **playlist_id**: Integer, Foreign Key (`playlist.id`), Primary Key, Not Null
- **playlist_item_id**: Integer, Foreign Key (`playlistitem.id`), Primary Key, Not Null
- **playlist**: Relationship with `Playlist`, Backref: 'playlist_playlist_items'
- **playlist_item**: Relationship with `PlaylistItem`, Backref: 'playlist_playlist_items'