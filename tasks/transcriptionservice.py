import requests
from dotenv import load_dotenv
import os
from tasks import celery
import logging


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
headers = {"Authorization": f"Bearer {os.getenv('WHISPER_TOKEN')}"}

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def transcribe(self, filename,episode_id,delete_after=True):
    try:
        # Open the file and read the data
        with open(filename, "rb") as f:
            data = f.read()

        logger.info(f"Sending request for file: {filename} (Size: {len(data)} bytes)")

        # Send POST request to the Hugging Face API
        response = requests.post(API_URL, headers=headers, data=data)

        # Check if the request was successful
        if response.status_code == 200:
            logger.info(f"API response successful for file: {filename}")
            data = response.json()
            data['episode_id'] = episode_id
            return data
        else:
            logger.error(f"API request failed with status code: {response.status_code}. Retrying...")
            raise self.retry(exc=Exception(f"Failed API request. Status code: {response.status_code}"), countdown=60)

    except requests.exceptions.RequestException as e:
        # Handle network errors or request issues
        logger.error(f"Network error occurred while sending the request: {str(e)}")
        raise self.retry(exc=e, countdown=60)  # Retry after a delay

    except Exception as e:
        # Handle other unexpected errors
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise self.retry(exc=str(e), countdown=60)  # Retry after a delay

    finally:
        if delete_after and (self.request.retries >= self.max_retries):
            if os.path.exists(filename):
                os.remove(filename)
                logger.info(f"File {filename} removed successfully.")
