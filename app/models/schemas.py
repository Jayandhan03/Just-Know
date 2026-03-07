from pydantic import BaseModel

class NewsRequest(BaseModel):
    topic: str

class SummarizeRequest(BaseModel):
    topic: str
    limit: int = 5           # number of articles to fetch
    time_published: str = "anytime"  # anytime / past_hour / past_day / past_week

class AudioRequest(BaseModel):
    topic: str
    limit: int = 5
    time_published: str = "anytime"
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb"   # ElevenLabs voice – George (news anchor)
    model_id: str = "eleven_multilingual_v2"
