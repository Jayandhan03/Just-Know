import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    RAPID_API_KEY: str = os.getenv("RAPID_API_KEY", "")

settings = Settings()