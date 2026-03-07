# import requests

import os
from dotenv import load_dotenv

# Load the .env file so os.getenv can read from it
load_dotenv()

from elevenlabs import ElevenLabs

# Initialize ElevenLabs client
client = ElevenLabs(api_key="sk_0e5a27603d28d11bd83e1b01558d344cff0fcca91fa75882")

print("Testing ElevenLabs generation...")

try:
    audio_stream = client.text_to_speech.convert(
        text="Hello. This is a broadcast test.",
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    
    # Check if we can pull bytes from the generator
    first_chunk = next(audio_stream)
    print(f"Success! Received {len(first_chunk)} bytes.")
except Exception as e:
    print(f"Failed: {e}")