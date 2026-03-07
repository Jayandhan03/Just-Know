import os
import requests
from dotenv import load_dotenv

load_dotenv()

def txt2speech(text):
  API_URL = "https://router.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
  api_token = os.getenv("HF_TOKEN")
  headers = {"Authorization": f"Bearer {api_token}"}
  payloads = {'inputs': text}

  response = requests.post(API_URL, headers=headers, json=payloads)
  
  with open('audio_answer.mp3', 'wb') as file:
      file.write(response.content)

text = "Hello, how are you?"
txt2speech(text)    