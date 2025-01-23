from app import app
from app.models import PlaylistPlaylistitem, db, PlaylistItem, Playlist, Episode
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

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


def update_transcription(episode_id: int, transcription_text: str):
    try:
        with app.app_context():
            # Query the episode by ID
            episode = Episode.query.get(episode_id)

            # Check if the episode exists
            if episode:
                # Update the transcription field with the provided transcription text
                episode.transcription = transcription_text

                # Commit the changes to the database
                db.session.commit()
                logger.info(f"Episode {episode_id} transcription updated successfully.")
                return True
            else:
                # If the episode is not found
                logger.error(f"Episode with ID {episode_id} not found.")
                return False
    except Exception as e:
        # Rollback the session in case of any error
        db.session.rollback()
        logger.error(f"Error updating transcription for episode {episode_id}: {e}")
        return False
