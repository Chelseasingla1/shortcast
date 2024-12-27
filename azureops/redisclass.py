import redis

redis_client = redis.StrictRedis(host='localhost',port=6379,db=0)

def get_playback_position(user_id):
    """
    Get the user's last playback position from Redis.
    :param user_id: The unique ID of the user.
    :return: The last known position in the media file.
    """
    position = redis_client.get(f"user:{user_id}:position")
    if position:
        return int(position)
    return 0  # Default to the beginning of the file


def save_playback_position(user_id, position):
    """
    Save the user's playback position in Redis.
    :param user_id: The unique ID of the user.
    :param position: The current position in the media file.
    """
    redis_client.set(f"user:{user_id}:position", position)