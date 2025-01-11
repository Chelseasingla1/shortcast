from app.models import PlaylistPlaylistitem, db, PlaylistItem, Playlist, Episode


def add_episode_to_playlist(episode_id, playlist_id):
    # Fetch episode and playlist from the database
    episode = Episode.query.get(episode_id)
    playlist = Playlist.query.get(playlist_id)

    # Ensure both episode and playlist exist
    if not episode or not playlist:
        return None, "Episode or Playlist not found"

    # Fetch the podcast associated with the episode
    podcast_id = episode.podcast_id

    # Check if the episode already exists in the playlist
    if episode.playlist_items:
        existing_item = PlaylistPlaylistitem.query.filter_by(episode_id=episode.id, playlist_id=playlist.id).first()
        if existing_item:
            return None, "Episode already exists in this playlist"

    # Add the episode to the playlist
    new_playlist_item = PlaylistItem(podcast_id=podcast_id, episode_id=episode_id)
    db.session.add(new_playlist_item)

    playlist_bridge = PlaylistPlaylistitem(playlist_id=playlist.id, playlist_item_id=new_playlist_item.id)
    db.session.add(playlist_bridge)
    db.session.commit()

    return new_playlist_item, None