#!/usr/bin/env python3
"""
WatchNext V2 — Offline Model Training

Trains both ML models and saves them to models/ for the API to load at startup.

1. Content-Based: fetches TMDB data (synopsis + genres + cast) for top N movies,
   builds TF-IDF matrix, saves to disk.
2. Collaborative: loads MovieLens ratings, trains SVD (scipy), saves item factors.

Run this ONCE before starting the API, or whenever you want to retrain.

Usage: python scripts/train_models.py
"""

import os
import sys
import json
import time
import pickle
import numpy as np
import pandas as pd
import httpx
from pathlib import Path
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

# ─── Config ───────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "movielens" / "ml-25m"
MODELS_DIR = PROJECT_ROOT / "models"
CACHE_FILE = PROJECT_ROOT / "data" / "tmdb_cache.json"

load_dotenv(PROJECT_ROOT / ".env")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_HEADERS = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json",
}

# Content-based: how many of the most-rated movies to include
N_CB_MOVIES = 3000
# Content-based: how many times to repeat genre words (gives genres more weight)
GENRE_REPEAT = 3
# Collaborative: minimum ratings per movie (filters noisy/obscure films)
MIN_RATINGS = 50
# Collaborative: number of latent factors for SVD
N_FACTORS = 100
# Collaborative: max ratings to use (None = all 25M)
MAX_RATINGS = 10_000_000


# ─── TMDB Data Fetching ──────────────────────────────────────────────────────

def load_tmdb_cache():
    """Load cached TMDB metadata if available."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            # JSON keys are strings, convert back to int
            return {int(k): v for k, v in json.load(f).items()}
    return {}


def save_tmdb_cache(cache):
    """Save TMDB metadata cache to disk."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def fetch_tmdb_data(tmdb_ids, cache):
    """
    Fetch movie data from TMDB: overview, genres, top 5 cast members.
    Uses append_to_response=credits to get cast in a single API call.
    Skips movies already in cache.
    """
    to_fetch = [tid for tid in tmdb_ids if tid not in cache]
    print(f"  TMDB: {len(cache)} cached, {len(to_fetch)} to fetch")

    with httpx.Client(headers=TMDB_HEADERS, timeout=10) as client:
        for i, tmdb_id in enumerate(to_fetch):
            try:
                resp = client.get(
                    f"{TMDB_BASE}/movie/{tmdb_id}",
                    params={
                        "language": "en-US",
                        "append_to_response": "credits",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    genres = [g["name"] for g in data.get("genres", [])]
                    cast = []
                    credits = data.get("credits", {})
                    for actor in credits.get("cast", [])[:5]:
                        cast.append(actor["name"])

                    cache[tmdb_id] = {
                        "overview": data.get("overview", ""),
                        "genres": genres,
                        "cast": cast,
                        "title": data.get("title", ""),
                    }
                time.sleep(0.03)

                if (i + 1) % 500 == 0:
                    print(f"    fetched {i + 1}/{len(to_fetch)}...")
                    save_tmdb_cache(cache)  # checkpoint

            except Exception as e:
                print(f"    error fetching {tmdb_id}: {e}")
                continue

    save_tmdb_cache(cache)
    return cache


# ─── Content-Based Training ──────────────────────────────────────────────────

def build_text_profile(movie_data):
    """
    Build a text profile for a movie that TF-IDF can process.

    Structure: "synopsis text  GENRE_action GENRE_action GENRE_action  ACTOR_christian_bale"

    - Genres are repeated 3x so they weigh more than random synopsis words
    - GENRE_ and ACTOR_ prefixes prevent collisions with synopsis words
      (the word "action" in a synopsis shouldn't match the genre "Action")
    """
    parts = []

    overview = movie_data.get("overview", "")
    if overview:
        parts.append(overview)

    for genre in movie_data.get("genres", []):
        tag = f"GENRE_{genre.lower().replace(' ', '_')}"
        parts.extend([tag] * GENRE_REPEAT)

    for actor in movie_data.get("cast", []):
        tag = f"ACTOR_{actor.lower().replace(' ', '_')}"
        parts.append(tag)

    return " ".join(parts)


def train_content_based(tmdb_ids, cache):
    """Build TF-IDF matrix from movie text profiles."""
    print("\n--- Training Content-Based model ---")

    # Build text profiles for movies that have TMDB data
    valid_ids = [tid for tid in tmdb_ids if tid in cache and cache[tid].get("overview")]
    texts = [build_text_profile(cache[tid]) for tid in valid_ids]

    print(f"  Movies with text profiles: {len(valid_ids)}")

    vectorizer = TfidfVectorizer(
        max_features=8000,
        stop_words="english",
        min_df=2,
    )
    tfidf_matrix = vectorizer.fit_transform(texts)

    print(f"  TF-IDF matrix: {tfidf_matrix.shape[0]} movies x {tfidf_matrix.shape[1]} features")

    # Save
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODELS_DIR / "cb_tfidf_matrix.pkl", "wb") as f:
        pickle.dump(tfidf_matrix, f)
    with open(MODELS_DIR / "cb_tmdb_ids.pkl", "wb") as f:
        pickle.dump(valid_ids, f)

    print("  Saved to models/cb_tfidf_matrix.pkl + cb_tmdb_ids.pkl")
    return tfidf_matrix, valid_ids


# ─── Collaborative Filtering Training ────────────────────────────────────────

def train_collaborative(ratings, ml_to_tmdb, tmdb_to_ml):
    """Train SVD model on MovieLens ratings."""
    print("\n--- Training Collaborative model ---")
    t0 = time.time()

    # Filter movies with too few ratings
    movie_counts = ratings.groupby("movieId").size()
    popular_movies = movie_counts[movie_counts >= MIN_RATINGS].index
    ratings = ratings[ratings["movieId"].isin(popular_movies)]
    print(f"  Movies with >= {MIN_RATINGS} ratings: {len(popular_movies):,}")
    print(f"  Ratings after filter: {len(ratings):,}")

    # Build sparse matrix
    user_ids = ratings["userId"].unique()
    movie_ids = ratings["movieId"].unique()

    user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
    movie_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
    idx_to_movie = {i: mid for mid, i in movie_to_idx.items()}

    rows = ratings["userId"].map(user_to_idx).values
    cols = ratings["movieId"].map(movie_to_idx).values
    vals = ratings["rating"].values.astype(np.float32)

    n_users = len(user_ids)
    n_movies = len(movie_ids)

    matrix = csr_matrix((vals, (rows, cols)), shape=(n_users, n_movies))

    # Center ratings
    global_mean = float(vals.mean())
    matrix_centered = matrix.copy()
    matrix_centered.data -= global_mean

    # SVD
    k = min(N_FACTORS, min(n_users, n_movies) - 1)
    U, sigma, Vt = svds(matrix_centered, k=k)
    item_factors = Vt.T  # (n_movies, k)

    elapsed = time.time() - t0
    print(f"  SVD trained in {elapsed:.1f}s — {n_users:,} users x {n_movies:,} movies -> {k} factors")

    # Save
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODELS_DIR / "cf_item_factors.pkl", "wb") as f:
        pickle.dump(item_factors, f)
    with open(MODELS_DIR / "cf_movie_to_idx.pkl", "wb") as f:
        pickle.dump(movie_to_idx, f)
    with open(MODELS_DIR / "cf_idx_to_movie.pkl", "wb") as f:
        pickle.dump(idx_to_movie, f)
    with open(MODELS_DIR / "ml_to_tmdb.pkl", "wb") as f:
        pickle.dump(ml_to_tmdb, f)
    with open(MODELS_DIR / "tmdb_to_ml.pkl", "wb") as f:
        pickle.dump(tmdb_to_ml, f)

    print("  Saved to models/cf_*.pkl + ml_to_tmdb.pkl + tmdb_to_ml.pkl")
    return item_factors, movie_to_idx, idx_to_movie


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("WatchNext V2 — Model Training")
    print("=" * 60)

    # Load MovieLens data
    print("\n--- Loading MovieLens data ---")
    from core.ml.data_loader import load_links, load_movies, load_ratings, build_mapping

    links = load_links()
    movies = load_movies()
    ml_to_tmdb, tmdb_to_ml = build_mapping(links)
    print(f"  Mapping: {len(ml_to_tmdb):,} MovieLens -> TMDB")

    ratings = load_ratings(max_rows=MAX_RATINGS)
    print(f"  Ratings: {len(ratings):,}")

    # Identify top N most-rated movies for content-based corpus
    rating_counts = ratings.groupby("movieId").size().reset_index(name="count")
    rating_counts = rating_counts.sort_values("count", ascending=False)
    top_ml_ids = rating_counts.head(N_CB_MOVIES)["movieId"].tolist()
    tmdb_ids = [ml_to_tmdb[mid] for mid in top_ml_ids if mid in ml_to_tmdb]
    print(f"  Top {N_CB_MOVIES} most-rated -> {len(tmdb_ids)} with TMDB mapping")

    # Fetch TMDB data (with cache)
    print("\n--- Fetching TMDB data (overview + genres + cast) ---")
    cache = load_tmdb_cache()
    cache = fetch_tmdb_data(tmdb_ids, cache)

    # Train content-based
    train_content_based(tmdb_ids, cache)

    # Train collaborative
    train_collaborative(ratings, ml_to_tmdb, tmdb_to_ml)

    print("\n" + "=" * 60)
    print("Training complete. Models saved to models/")
    print("=" * 60)


if __name__ == "__main__":
    # Add project root to path so we can import core.ml
    sys.path.insert(0, str(PROJECT_ROOT))
    main()
