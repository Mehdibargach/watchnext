"""
Orchestrator — takes a TMDB movie ID and returns ML recommendations.

This is the main entry point for V2 recommendations. It:
1. Calls content-based model → "Similar Movies" (always available)
2. Calls collaborative model → "Viewers Also Liked" (only if the movie is in MovieLens)
3. Applies confidence thresholds — hides a rail if the model isn't confident
4. Enriches each recommended movie with TMDB metadata (title, poster, rating, etc.)

UX decision: 2 rails only (no hybrid rail). The hybrid blend exists as an internal
evaluation tool but is not exposed to users. Each rail has its own value:
- "Similar Movies" = same universe, same genre (content similarity)
- "Viewers Also Liked" = same audience, same taste (behavioral similarity)
"""

import os
import httpx
from .content_based import ContentBasedModel
from .collaborative import CollaborativeModel

_TMDB_BASE = "https://api.themoviedb.org/3"
_IMG_BASE = "https://image.tmdb.org/t/p"

# Confidence thresholds — if the top score is below this, hide the rail
# rather than show weak recommendations
CB_MIN_SCORE = 0.10
CF_MIN_SCORE = 0.15


def _tmdb_headers():
    api_key = os.environ.get("TMDB_API_KEY", "")
    return {"Authorization": f"Bearer {api_key}", "accept": "application/json"}


def _fetch_tmdb_metadata(tmdb_ids):
    """Fetch TMDB metadata for a batch of movie IDs. Returns {tmdb_id: metadata_dict}."""
    cache = {}
    with httpx.Client(headers=_tmdb_headers(), timeout=5) as client:
        for tmdb_id in tmdb_ids:
            if tmdb_id in cache:
                continue
            try:
                resp = client.get(
                    f"{_TMDB_BASE}/movie/{tmdb_id}",
                    params={"language": "en-US"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    cache[tmdb_id] = {
                        "id": tmdb_id,
                        "title": data.get("title", ""),
                        "genres": [g["name"] for g in data.get("genres", [])],
                        "rating": data.get("vote_average", 0),
                        "runtime": data.get("runtime", 0),
                        "release_year": (data.get("release_date") or "")[:4],
                        "overview": data.get("overview", ""),
                        "poster_url": (
                            f"{_IMG_BASE}/w500{data['poster_path']}"
                            if data.get("poster_path")
                            else None
                        ),
                    }
            except Exception:
                continue
    return cache


class SimilarMovies:
    """Main orchestrator for V2 ML recommendations."""

    def __init__(self):
        self.cb_model = ContentBasedModel()
        self.cf_model = CollaborativeModel()
        self._loaded = False

    def load(self):
        """Load both ML models from disk. Call once at API startup."""
        self.cb_model.load()
        self.cf_model.load()
        self._loaded = True

    def get_recommendations(self, tmdb_id, n=5):
        """
        Get ML recommendations for a movie.

        Returns:
        {
            "movie_id": int,
            "similar_movies": [...],       # content-based (empty if below confidence)
            "viewers_also_liked": [...],    # collaborative (empty if not in MovieLens
                                           #   or below confidence)
        }
        """
        if not self._loaded:
            return {"error": "Models not loaded"}

        # Get raw scores from both models
        cb_raw = self.cb_model.get_similar(tmdb_id, n=n)
        cf_raw = self.cf_model.get_also_liked(tmdb_id, n=n)

        # Apply confidence thresholds — hide rail if top score is too low
        if cb_raw and cb_raw[0]["score"] < CB_MIN_SCORE:
            cb_raw = []
        if cf_raw and cf_raw[0]["score"] < CF_MIN_SCORE:
            cf_raw = []

        # Collect all unique TMDB IDs, fetch metadata once
        all_ids = set()
        for rec in cb_raw + cf_raw:
            all_ids.add(rec["tmdb_id"])
        metadata = _fetch_tmdb_metadata(all_ids)

        # Build enriched lists
        similar_movies = []
        for rec in cb_raw:
            meta = metadata.get(rec["tmdb_id"])
            if meta:
                similar_movies.append({**meta, "score": rec["score"], "rec_type": "similar"})

        viewers_also_liked = []
        for rec in cf_raw:
            meta = metadata.get(rec["tmdb_id"])
            if meta:
                viewers_also_liked.append({**meta, "score": rec["score"], "rec_type": "also_liked"})

        return {
            "movie_id": tmdb_id,
            "similar_movies": similar_movies,
            "viewers_also_liked": viewers_also_liked,
        }
