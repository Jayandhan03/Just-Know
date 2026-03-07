import io
import logging
from gtts import gTTS

logger = logging.getLogger(__name__)


def generate_audio_stream(script: str, voice_id: str | None = None, model_id: str | None = None):
    """
    Converts text to an MP3 audio bytes iterator using Google TTS (gTTS).

    ``voice_id`` is treated as a BCP-47 language code (default: 'en').
    ``model_id`` is ignored (kept for API compatibility).

    Returns a chunked generator yielding MP3 bytes for use with
    FastAPI's StreamingResponse.
    """
    lang = voice_id if voice_id else "en"
    logger.info("Generating audio using Google TTS (lang=%s)…", lang)

    try:
        tts = gTTS(text=script, lang=lang)

        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)

        def _mp3_iter(buf: io.BytesIO, chunk_size: int = 8192):
            while True:
                chunk = buf.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        return _mp3_iter(buffer)

    except Exception as e:
        logger.error("Google TTS error: %s", e)
        raise

