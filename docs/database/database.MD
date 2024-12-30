## Database Models Documentation

### Overview
The database models for the Podcast Management System are defined using SQLAlchemy. These models represent various entities such as users, podcasts, episodes, subscriptions, favorites, ratings, downloads, playlists, and shared playlists.

### Models

#### User
- **id**: Integer, primary key.
- **oauth_provider**: Enum, OAuth provider.
- **oauth_id**: String, unique OAuth ID.
- **username**: String, username.
- **profile_image_url**: String, profile image URL.
- **email**: String, email address.
- **role**: Enum, user role.
- **created_at**: DateTime, creation date.

#### Podcast
- **id**: Integer, primary key.
- **title**: String, podcast title.
- **description**: String, podcast description.
- **category**: Enum, podcast category.
- **publisher**: String, podcast publisher.
- **publish_date**: DateTime, publish date.
- **image_url**: String, image URL.
- **feed_url**: String, feed URL.
- **audio_url**: String, audio URL.
- **duration**: Time, duration.
- **episodes**: Relationship, list of episodes.

#### Episode
- **id**: Integer, primary key.
- **title**: String, episode title.
- **description**: String, episode description.
- **duration**: Time, duration.
- **publish_date**: DateTime, publish date.
- **audio_url**: String, audio URL.
- **podcast_id**: Integer, foreign key to podcast.

#### Subscription
- **user_id**: Integer, foreign key to user, primary key.
- **podcast_id**: Integer, foreign key to podcast, primary key.
- **subscribed_date**: DateTime, subscription date.

#### Favourite
- **user_id**: Integer, foreign key to user, primary key.
- **podcast_id**: Integer, foreign key to podcast, primary key.
- **episode_id**: Integer, foreign key to episode, primary key.
- **added_date**: DateTime, date added to favorites.

#### Rating
- **user_id**: Integer, foreign key to user, primary key.
- **podcast_id**: Integer, foreign key to podcast, primary key.
- **episode_id**: Integer, foreign key to episode, primary key.
- **rating**: Integer, rating value.
- **review_text**: String, review text.
- **review_date**: DateTime, review date.

#### Download
- **user_id**: Integer, foreign key to user, primary key.
- **podcast_id**: Integer, foreign key to podcast, primary key.
- **episode_id**: Integer, foreign key to episode, primary key.
- **download_date**: DateTime, download date.

#### Playlist
- **id**: Integer, primary key.
- **user_id**: Integer, foreign key to user.
- **title**: String, playlist title.
- **created_at**: DateTime, creation date.

#### PlaylistItem
- **id**: Integer, primary key.
- **podcast_id**: Integer, foreign key to podcast.
- **episode_id**: Integer, foreign key to episode.
- **added_date**: DateTime, date added to playlist.

#### SharedPlaylist
- **user_id**: Integer, foreign key to user, primary key.
- **playlist_id**: Integer, foreign key to playlist, primary key.

#### PlaylistPlaylistitem
- **playlist_id**: Integer, foreign key to playlist, primary key.
- **playlist_item_id**: Integer, foreign key to playlist item, primary key.

### Relationships and Constraints
- **User**: Has relationships with subscriptions, favorites, ratings, downloads, playlists, and shared playlists.
- **Podcast**: Has relationships with episodes, subscriptions, favorites, ratings, downloads, and playlist items.
- **Episode**: Has relationships with favorites, ratings, downloads, and playlist items.
- **Subscription**: Links users to podcasts.
- **Favourite**: Links users to either podcasts or episodes.
- **Rating**: Links users to either podcasts or episodes.
- **Download**: Links users to either podcasts or episodes.
- **Playlist**: Links users to playlist items.
- **PlaylistItem**: Links to either podcasts or episodes.
- **SharedPlaylist**: Links users to playlists.
- **PlaylistPlaylistitem**: Links playlists to playlist items.

### Notes
- Ensure that either `feed_url` or `audio_url` is provided for a podcast, but not both.
- Ensure that either `podcast_id` or `episode_id` is provided for favorites, ratings, downloads, and playlist items, but not both.