"""FastAPI backend for WatchNext — mood-based movie recommendations."""

import time
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from core.mood_parser import parse_mood
from core.tmdb_client import discover_movies, enrich_movies
from core.recommender import rank_movies

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

    try:
        # Step 1: GPT-4o-mini translates mood → TMDB filters
        filters = parse_mood(req.mood)

        # Step 2: TMDB Discover API returns 20 candidates
        raw_movies = discover_movies(filters, limit=20)

        # Step 3: Enrich with full details + streaming providers
        candidates = enrich_movies(raw_movies, include_providers=True)

        # Step 4: GPT-4o-mini ranks 20 → top 5 with explanations
        movies = rank_movies(req.mood, candidates)

    except Exception as e:
        logger.error(f"Recommendation failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=502, detail=f"Recommendation engine error: {type(e).__name__}")

    latency = time.time() - t0

    return {
        "mood": req.mood,
        "filters_applied": filters,
        "movies": movies,
        "count": len(movies),
        "latency": round(latency, 1),
    }
