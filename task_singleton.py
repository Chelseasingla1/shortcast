import redis
from typing import Any
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
class TaskInfoSingleton:
    """
    A singleton class to handle interactions with Redis.
    Ensures a single instance of the Redis client is shared across the application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, host='localhost', port=6379, db=0):
        """Initialize the Redis client."""
        self._redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        logger.info('redis initialized')
    def set_value(self, key: str, value: Any):
        """Set a key-value pair in Redis."""
        if isinstance(value, (str, int, float, bytes)):
            self._redis_client.set(key, value)
        else:
            raise TypeError("Value must be a str, int, float, or bytes.")

    def get_value(self, key: str) -> Any:
        """Retrieve the value of a given key from Redis."""
        return self._redis_client.get(key)

    def delete_value(self, key: str):
        """Delete a key from Redis."""
        self._redis_client.delete(key)

    def get_task_info(self, task_id: str) -> Any:
        """
        Retrieve task information stored in Redis.

        """

        return self._redis_client.get(task_id)

    def set_task_info(self, task_id: str, task_name: str):
        """
        Store task information in Redis as a hash.
        """
        if not isinstance(task_name, str):
            raise TypeError("Task information must be a string.")
        self._redis_client.set(task_id,task_name)

    def delete_task_info(self,task_id):
        self._redis_client.delete(task_id)
        logger.info('deleted key-value from redis')