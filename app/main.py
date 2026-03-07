from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import news, audio

app = FastAPI(title="IndustryEar API")

# ---------- CORS (VERY IMPORTANT for Next.js) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#fd
# ---------- Routes ----------
app.include_router(news.router, tags=["News"])
app.include_router(audio.router, tags=["Audio"])

# ---------- Health Check ----------
@app.get("/", tags=["Health"])
def read_root():
    return {"status": "FastAPI backend running (Restructured)"}
