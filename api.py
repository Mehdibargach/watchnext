"""FastAPI backend for WatchNext — mood-based movie recommendations."""

import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

from core.mood_parser import parse_mood
from core.tmdb_client import discover_movies, enrich_movies

load_dotenv()

app = FastAPI(title="WatchNext", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://.*\.(lovableproject\.com|lovable\.app)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    mood: str


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/recommend")
def recommend(req: RecommendRequest):
    t0 = time.time()

    # Step 1: GPT-4o-mini translates mood → TMDB filters
    filters = parse_mood(req.mood)

    # Step 2: TMDB Discover API returns movies matching filters
    raw_movies = discover_movies(filters, limit=5)

    # Step 3: Enrich with full details (runtime, poster, etc.)
    movies = enrich_movies(raw_movies)

    latency = time.time() - t0

    return {
        "mood": req.mood,
        "filters_applied": filters,
        "movies": movies,
        "count": len(movies),
        "latency": round(latency, 1),
    }
