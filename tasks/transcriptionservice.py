import requests
from dotenv import load_dotenv
import os
load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
headers = {"Authorization": f"Bearer {os.getenv('WHISPER_TOKEN')}"}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()