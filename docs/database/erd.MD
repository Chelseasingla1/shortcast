### Copy the below and paste it here:  [link](dbdiagram.io) to generate the erd image.

```
Table User {
  id int [pk, increment]
  oauth_provider enum
  oauth_id varchar [unique]
  username varchar
  profile_image_url varchar
  email varchar
  role enum
  created_at datetime
}

Table Podcast {
  id int [pk, increment]
  title varchar
  description varchar
  category enum
  publisher varchar
  publish_date datetime
  image_url varchar
  feed_url varchar
  audio_url varchar
  duration int
}

Table Episode {
  id int [pk, increment]
  title varchar
  description varchar
  duration int
  publish_date datetime
  audio_url varchar
  podcast_id int [ref: > Podcast.id]
}

Table Subscription {
  user_id int [ref: > User.id]
  podcast_id int [ref: > Podcast.id]
  subscribed_date datetime
  primary key (user_id, podcast_id)
}

Table Favourite {
  user_id int [ref: > User.id]
  podcast_id int [ref: > Podcast.id]
  episode_id int [ref: > Episode.id]
  added_date datetime
  primary key (user_id, podcast_id, episode_id)
}

Table Rating {
  user_id int [ref: > User.id]
  podcast_id int [ref: > Podcast.id]
  episode_id int [ref: > Episode.id]
  rating smallint
  review_text varchar
  review_date datetime
  primary key (user_id, podcast_id, episode_id)
}

Table Download {
  user_id int [ref: > User.id]
  podcast_id int [ref: > Podcast.id]
  episode_id int [ref: > Episode.id]
  download_date datetime
  primary key (user_id, podcast_id, episode_id)
}

Table Playlist {
  id int [pk, increment]
  user_id int [ref: > User.id]
  title varchar [unique]
  created_at datetime
}

Table PlaylistItem {
  id int [pk, increment]
  podcast_id int [ref: > Podcast.id]
  episode_id int [ref: > Episode.id]
  added_date datetime
}

Table SharedPlaylist {
  user_id int [ref: > User.id]
  playlist_id int [ref: > Playlist.id]
  primary key (user_id, playlist_id)
}

Table PlaylistPlaylistitem {
  playlist_id int [ref: > Playlist.id]
  playlist_item_id int [ref: > PlaylistItem.id]
  primary key (playlist_id, playlist_item_id)
}
```