import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import AudioRequest
from app.services.news_service import fetch_news
from app.services.llm_service import summarize_news
from app.services.audio_service import generate_audio_stream

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/news-audio")
async def news_audio_endpoint(data: AudioRequest):
    """
    Full pipeline in one call:
      1. Fetch fresh articles via RapidAPI
      2. Summarize with xAI Grok LLM (broadcast-style script)
      3. Convert the script to speech using Google TTS (gTTS)
      4. Stream MP3 bytes directly back to the client
    """
    # --- Step 1: Fetch articles ---
    try:
        news_data = fetch_news(
            query=data.topic,
            limit=data.limit,
            time_published=data.time_published,
        )
        articles = news_data.get("data", []) if news_data else []
    except Exception as e:
        logger.error("news-audio fetch error: %s", e)
        raise HTTPException(status_code=502, detail=f"News fetch failed: {e}")

    # --- Step 2: Summarize ---
    try:
        script = summarize_news(topic=data.topic, articles=articles)
    except Exception as e:
        logger.error("news-audio summarize error: %s", e)
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {e}")

    # --- Step 3 + 4: Convert to speech and stream ---
    try:
        audio_stream_generator = generate_audio_stream(
            script=script,
            voice_id=data.voice_id,
            model_id=data.model_id
        )

        filename = data.topic.replace(" ", "_")[:40] + "_news.mp3"
        return StreamingResponse(
            audio_stream_generator,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Topic": data.topic,
                "X-Article-Count": str(len(articles)),
            },
        )

    except ValueError as ve:
        logger.error("news-audio configuration error: %s", ve)
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error("news-audio TTS error: %s", e)
        raise HTTPException(status_code=500, detail=f"Google TTS failed: {e}")