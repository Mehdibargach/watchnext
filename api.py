"""FastAPI backend for WatchNext — mood-based movie recommendations."""

import time
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from core.mood_parser import parse_mood, _parse_mood_cached
from core.tmdb_client import discover_movies, enrich_movies
from core.recommender import rank_movies
from core.ml.similar import SimilarMovies

load_dotenv()

app = FastAPI(title="WatchNext", version="0.2.0")

# V2 ML models — loaded once at startup
_ml_recommender = SimilarMovies()

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


@app.on_event("startup")
def load_ml_models():
    """Load ML models at startup (content-based + collaborative)."""
    try:
        _ml_recommender.load()
        logger.info("ML models loaded successfully")
    except Exception as e:
        logger.warning(f"ML models not available: {e}")


@app.get("/health")
def health():
    cache_info = _parse_mood_cached.cache_info()
    return {
        "status": "ok",
        "version": "0.2.0",
        "cache": {
            "hits": cache_info.hits,
            "misses": cache_info.misses,
            "size": cache_info.currsize,
            "maxsize": cache_info.maxsize,
        },
    }


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


@app.get("/movie/{tmdb_id}/similar")
def get_similar_movies(tmdb_id: int, n: int = 5):
    """V2 ML endpoint — returns content-based + collaborative recommendations."""
    t0 = time.time()
    result = _ml_recommender.get_recommendations(tmdb_id, n=n)

    if "error" in result:
        raise HTTPException(status_code=503, detail=result["error"])

    result["latency"] = round(time.time() - t0, 1)
    return result
