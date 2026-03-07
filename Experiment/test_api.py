import httpx
import asyncio

async def test_audio_endpoint():
    async with httpx.AsyncClient() as client:
        print("Sending request to /news-audio")
        response = await client.post(
            "http://127.0.0.1:8000/news-audio",
            json={
                "topic": "artificial intelligence",
                "limit": 1,
                "time_published": "any",
                "voice_id": "en_0",
                "model_id": "v3_en"
            },
            timeout=120.0
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            with open("test_output.wav", "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
            print("Successfully saved to test_output.wav")
            print(f"Headers: {response.headers}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_audio_endpoint())
