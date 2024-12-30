## Podcast Management System API Documentation

### Overview
This API provides a comprehensive system for managing podcasts, episodes, user subscriptions, favorites, ratings, downloads, playlists, and shared playlists. It is built using Flask and SQLAlchemy.

### Endpoints

#### Authentication
- **POST /auth/login**: Log in a user.
- **POST /auth/logout**: Log out a user.

#### OAuth
- **GET /oauth/authorize**: Authorize a user via OAuth.
- **GET /oauth/callback**: Handle OAuth callback.

#### Users
- **GET /users**: Retrieve a list of users.
- **GET /users/{id}**: Retrieve a specific user by ID.
- **POST /users**: Create a new user.
- **PUT /users/{id}**: Update a specific user by ID.
- **DELETE /users/{id}**: Delete a specific user by ID.

#### Podcasts
- **GET /podcasts**: Retrieve a list of podcasts.
- **GET /podcasts/{id}**: Retrieve a specific podcast by ID.
- **POST /podcasts**: Create a new podcast.
- **PUT /podcasts/{id}**: Update a specific podcast by ID.
- **DELETE /podcasts/{id}**: Delete a specific podcast by ID.

#### Episodes
- **GET /episodes**: Retrieve a list of episodes.
- **GET /episodes/{id}**: Retrieve a specific episode by ID.
- **POST /episodes**: Create a new episode.
- **PUT /episodes/{id}**: Update a specific episode by ID.
- **DELETE /episodes/{id}**: Delete a specific episode by ID.

#### Subscriptions
- **GET /subscriptions**: Retrieve a list of subscriptions.
- **POST /subscriptions**: Subscribe a user to a podcast.
- **DELETE /subscriptions**: Unsubscribe a user from a podcast.

#### Favorites
- **GET /favorites**: Retrieve a list of favorites.
- **POST /favorites**: Add a podcast or episode to favorites.
- **DELETE /favorites**: Remove a podcast or episode from favorites.

#### Ratings
- **GET /ratings**: Retrieve a list of ratings.
- **POST /ratings**: Add a rating to a podcast or episode.
- **DELETE /ratings**: Remove a rating from a podcast or episode.

#### Downloads
- **GET /downloads**: Retrieve a list of downloads.
- **POST /downloads**: Add a download for a podcast or episode.
- **DELETE /downloads**: Remove a download for a podcast or episode.

#### Playlists
- **GET /playlists**: Retrieve a list of playlists.
- **GET /playlists/{id}**: Retrieve a specific playlist by ID.
- **POST /playlists**: Create a new playlist.
- **PUT /playlists/{id}**: Update a specific playlist by ID.
- **DELETE /playlists/{id}**: Delete a specific playlist by ID.

#### Playlist Items
- **GET /playlist-items**: Retrieve a list of playlist items.
- **POST /playlist-items**: Add an item to a playlist.
- **DELETE /playlist-items**: Remove an item from a playlist.

#### Shared Playlists
- **GET /shared-playlists**: Retrieve a list of shared playlists.
- **POST /shared-playlists**: Share a playlist with a user.
- **DELETE /shared-playlists**: Unshare a playlist with a user.

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

### Error Handling
- **401 Unauthorized**: Returned when a user is not logged in and tries to access a protected resource.

### Initialization
- The database is initialized and all tables are created if they do not exist when the application starts.

### Configuration
- **SECRET_KEY**: Secret key for the Flask application.
- **SQLALCHEMY_DATABASE_URI**: Database URI for SQLAlchemy.
- **PERMANENT_SESSION_LIFETIME**: Session lifetime configuration.

### Running the Application
To run the application, use the following command:
```bash
python main.py
```

### Dependencies
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-CORS
- Flask-Login
- Flasgger

### Notes
- Ensure that either `feed_url` or `audio_url` is provided for a podcast, but not both.
- Ensure that either `podcast_id` or `episode_id` is provided for favorites, ratings, downloads, and playlist items, but not both.