#!/usr/bin/env python3
"""
WatchNext V2 — Walking Skeleton Test
=====================================
Tests the Riskiest Assumption:
  MovieLens coverage + ML recommendation quality + differentiation CB vs CF

Micro-tests:
  WS-1: MovieLens → TMDB mapping count (≥ 40K)
  WS-2: TMDB top 100 popular films in MovieLens (≥ 60%)
  WS-3: Content-based "Similar to The Dark Knight" (≥ 3/5 coherent)
  WS-4: Content-based "Similar to Toy Story" (≥ 3/5 coherent)
  WS-5: Collaborative "Also liked" for Dark Knight (≥ 3/5 plausible)
  WS-6: Collaborative "Also liked" for Toy Story (≥ 3/5 plausible)
  WS-7: CB vs CF different for Dark Knight (≥ 3 different films)
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

# ─── Config ───────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "movielens" / "ml-25m"

load_dotenv(PROJECT_ROOT / ".env")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_HEADERS = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json",
}

# Test films (TMDB IDs)
TEST_FILMS = {
    "The Dark Knight": 155,
    "Toy Story": 862,
    "The Notebook": 11036,
}

# How many of the most-rated MovieLens films to fetch TMDB overviews for
N_OVERVIEW_MOVIES = 2000
# Number of latent factors for the SVD model
N_FACTORS = 100
# Max ratings to load for WS speed (full 25M takes too long for a WS test)
MAX_RATINGS = 5_000_000
# Minimum ratings per movie to include in SVD (filters out noisy/obscure films)
MIN_RATINGS_PER_MOVIE = 50


# ─── Data Loading ─────────────────────────────────────────────────────────────

def load_movielens():
    """Load MovieLens 25M: links, movies, ratings (sampled for WS speed)."""
    print("\n--- Loading MovieLens 25M data ---")

    links = pd.read_csv(DATA_DIR / "links.csv")
    movies = pd.read_csv(DATA_DIR / "movies.csv")

    print(f"  Loading ratings (sampling {MAX_RATINGS // 1_000_000}M for WS speed)...")
    ratings = pd.read_csv(
        DATA_DIR / "ratings.csv",
        usecols=["userId", "movieId", "rating"],
    )
    if len(ratings) > MAX_RATINGS:
        ratings = ratings.sample(n=MAX_RATINGS, random_state=42)

    print(f"  links:   {len(links):,} movies")
    print(f"  movies:  {len(movies):,} movies")
    print(f"  ratings: {len(ratings):,} ratings")

    return links, movies, ratings


def build_mapping(links):
    """Build bidirectional mapping MovieLens ID <-> TMDB ID."""
    valid = links.dropna(subset=["tmdbId"]).copy()
    valid["tmdbId"] = valid["tmdbId"].astype(int)

    ml_to_tmdb = dict(zip(valid["movieId"], valid["tmdbId"]))
    tmdb_to_ml = dict(zip(valid["tmdbId"], valid["movieId"]))

    return ml_to_tmdb, tmdb_to_ml


# ─── TMDB API ─────────────────────────────────────────────────────────────────

def fetch_tmdb_well_known(n_pages=5):
    """
    Fetch the most well-known movies from TMDB (by vote count, not recency).

    We use vote_count.desc because MovieLens covers up to 2019 — testing against
    "currently popular" (= 2025-2026 releases) would artificially deflate coverage.
    The right question is: for established, well-known films, how good is the coverage?
    """
    all_movies = []
    with httpx.Client(headers=TMDB_HEADERS) as client:
        for page in range(1, n_pages + 1):
            resp = client.get(
                f"{TMDB_BASE}/discover/movie",
                params={
                    "sort_by": "vote_count.desc",
                    "vote_count.gte": 500,
                    "page": page,
                    "language": "en-US",
                },
            )
            resp.raise_for_status()
            all_movies.extend(resp.json()["results"])
            time.sleep(0.1)
    return all_movies


def fetch_tmdb_overviews(tmdb_ids):
    """Fetch movie overviews + genres from TMDB API for a list of TMDB IDs."""
    overviews = {}
    with httpx.Client(timeout=10, headers=TMDB_HEADERS) as client:
        for i, tmdb_id in enumerate(tmdb_ids):
            try:
                resp = client.get(
                    f"{TMDB_BASE}/movie/{tmdb_id}",
                    params={"language": "en-US"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    overview = data.get("overview", "")
                    genres = " ".join(g["name"] for g in data.get("genres", []))
                    # Combine overview + genre names as text for TF-IDF
                    overviews[tmdb_id] = f"{overview} {genres}"
                time.sleep(0.03)  # ~30 req/s, well within TMDB limits

                if (i + 1) % 500 == 0:
                    print(f"    fetched {i + 1}/{len(tmdb_ids)} overviews...")
            except Exception:
                continue
    return overviews


# ─── Content-Based Filtering ─────────────────────────────────────────────────

def build_content_based(overviews):
    """
    Build a TF-IDF similarity model from movie overviews.

    TF-IDF (Term Frequency - Inverse Document Frequency) measures how important
    each word is in a movie's description relative to all other descriptions.
    Rare, distinctive words get high scores; common words get low scores.
    This turns each synopsis into a numeric vector that we can compare.
    """
    tmdb_ids = list(overviews.keys())
    texts = [overviews[tid] for tid in tmdb_ids]

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        min_df=2,
    )
    tfidf_matrix = vectorizer.fit_transform(texts)

    tmdb_id_to_idx = {tid: i for i, tid in enumerate(tmdb_ids)}

    print(f"  TF-IDF matrix: {tfidf_matrix.shape[0]} movies x {tfidf_matrix.shape[1]} word features")

    return tfidf_matrix, tmdb_ids, tmdb_id_to_idx


def get_similar_content_based(tmdb_id, tfidf_matrix, tmdb_ids, tmdb_id_to_idx, n=5):
    """
    Find the N most similar movies by comparing their synopsis/genre text vectors.
    Uses cosine similarity: 1.0 = identical text profile, 0.0 = nothing in common.
    """
    if tmdb_id not in tmdb_id_to_idx:
        return []

    idx = tmdb_id_to_idx[tmdb_id]
    sim_scores = cosine_similarity(tfidf_matrix[idx : idx + 1], tfidf_matrix)[0]

    # Top N, excluding the movie itself
    top_indices = sim_scores.argsort()[::-1][1 : n + 1]

    return [
        {"tmdb_id": tmdb_ids[i], "score": float(sim_scores[i])}
        for i in top_indices
    ]


# ─── Collaborative Filtering ─────────────────────────────────────────────────

def train_collaborative_model(ratings, n_factors=100):
    """
    Train a collaborative filtering model using SVD (Singular Value Decomposition).

    The idea: we have a giant table of "user X rated movie Y with score Z".
    SVD decomposes this table into hidden patterns (latent factors).
    Each movie gets a vector of N factors that captures its "taste profile"
    — not based on its synopsis or genre, but on HOW USERS RATE IT.

    Movies with similar taste profiles = movies liked by the same type of people.
    """
    print(f"\n--- Training collaborative model (SVD, {n_factors} factors) ---")
    t0 = time.time()

    # Filter out movies with too few ratings (noisy/obscure films get extreme vectors)
    movie_counts = ratings.groupby("movieId").size()
    popular_movies = movie_counts[movie_counts >= MIN_RATINGS_PER_MOVIE].index
    ratings = ratings[ratings["movieId"].isin(popular_movies)]
    print(f"  Filtered to movies with >= {MIN_RATINGS_PER_MOVIE} ratings: {len(popular_movies):,} movies, {len(ratings):,} ratings")

    # Map user and movie IDs to sequential indices for the matrix
    user_ids = ratings["userId"].unique()
    movie_ids = ratings["movieId"].unique()

    user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
    movie_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
    idx_to_movie = {i: mid for mid, i in movie_to_idx.items()}

    # Build the sparse ratings matrix (most cells are empty — a user rates few movies)
    rows = ratings["userId"].map(user_to_idx).values
    cols = ratings["movieId"].map(movie_to_idx).values
    vals = ratings["rating"].values.astype(np.float32)

    n_users = len(user_ids)
    n_movies = len(movie_ids)

    matrix = csr_matrix((vals, (rows, cols)), shape=(n_users, n_movies))

    # Center ratings by subtracting the global average
    # (so a "3.5" from someone who averages 4.0 is treated as "below average")
    global_mean = float(vals.mean())
    matrix_centered = matrix.copy()
    matrix_centered.data -= global_mean

    # Run SVD — decompose the matrix into latent factors
    k = min(n_factors, min(n_users, n_movies) - 1)
    U, sigma, Vt = svds(matrix_centered, k=k)

    # Item factors: each movie gets a vector of k dimensions
    # that captures its "taste profile" from user behavior
    item_factors = Vt.T  # shape: (n_movies, k)

    elapsed = time.time() - t0
    print(f"  Trained in {elapsed:.1f}s")
    print(f"  {n_users:,} users x {n_movies:,} movies -> {k} latent factors per movie")

    return item_factors, movie_to_idx, idx_to_movie


def get_similar_collaborative(ml_movie_id, item_factors, movie_to_idx, idx_to_movie, n=5):
    """
    Find movies with the most similar "taste profile" in latent factor space.
    These are movies that get similar ratings from similar types of users —
    even if their genre/synopsis is completely different.
    """
    if ml_movie_id not in movie_to_idx:
        return []

    idx = movie_to_idx[ml_movie_id]
    movie_vec = item_factors[idx].reshape(1, -1)

    sims = cosine_similarity(movie_vec, item_factors)[0]

    top_indices = sims.argsort()[::-1][1 : n + 1]

    return [
        {"ml_movie_id": idx_to_movie[i], "score": float(sims[i])}
        for i in top_indices
    ]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_movie_info(ml_id, movies_df):
    """Get title and genres from MovieLens movies.csv."""
    row = movies_df[movies_df["movieId"] == ml_id]
    if len(row) == 0:
        return f"[ML:{ml_id}]", ""
    return row.iloc[0]["title"], row.iloc[0]["genres"]


def tmdb_to_info(tmdb_id, tmdb_to_ml, movies_df):
    """Get title and genres for a TMDB ID via MovieLens mapping."""
    ml_id = tmdb_to_ml.get(tmdb_id)
    if ml_id:
        return get_movie_info(ml_id, movies_df)
    return f"[TMDB:{tmdb_id}]", ""


# ─── Micro-Tests ──────────────────────────────────────────────────────────────

def run_tests():
    results = {}

    # Load data
    links, movies, ratings = load_movielens()
    ml_to_tmdb, tmdb_to_ml = build_mapping(links)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WS-1: Coverage count
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("WS-1: MovieLens -> TMDB mapping count")
    print("=" * 60)
    count = len(ml_to_tmdb)
    passed = count >= 40_000
    results["WS-1"] = ("PASS" if passed else "FAIL", f"{count:,} films mapped")
    print(f"  Films with valid TMDB ID: {count:,}")
    print(f"  Target: >= 40,000")
    print(f"  -> {'PASS' if passed else 'FAIL'}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WS-2: TMDB popular coverage
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("WS-2: TMDB top 100 well-known films -> MovieLens coverage")
    print("  (by vote count, not recency — MovieLens covers up to 2019)")
    print("=" * 60)
    popular = fetch_tmdb_well_known(n_pages=5)
    found = sum(1 for m in popular if m["id"] in tmdb_to_ml)
    pct = found / len(popular) * 100

    missing = [
        f"  {m['title']} ({m.get('release_date', '?')[:4]})"
        for m in popular
        if m["id"] not in tmdb_to_ml
    ]

    print(f"  Found: {found}/{len(popular)} ({pct:.0f}%)")
    print(f"  Target: >= 60%")
    if missing[:5]:
        print(f"  Missing examples:")
        for m in missing[:5]:
            print(f"    {m}")

    passed = pct >= 60
    results["WS-2"] = ("PASS" if passed else "FAIL", f"{found}/{len(popular)} = {pct:.0f}%")
    print(f"  -> {'PASS' if passed else 'FAIL'}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Build Content-Based model
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("Building Content-Based model (TF-IDF on TMDB overviews)")
    print("=" * 60)

    # Pick the most-rated movies in MovieLens (most likely to be relevant)
    rating_counts = ratings.groupby("movieId").size().reset_index(name="count")
    rating_counts = rating_counts.sort_values("count", ascending=False)
    top_ml_ids = rating_counts.head(N_OVERVIEW_MOVIES)["movieId"].tolist()

    # Map to TMDB IDs
    tmdb_ids_to_fetch = [ml_to_tmdb[mid] for mid in top_ml_ids if mid in ml_to_tmdb]

    # Make sure test films are included
    for name, tid in TEST_FILMS.items():
        if tid not in tmdb_ids_to_fetch:
            tmdb_ids_to_fetch.append(tid)

    print(f"  Fetching TMDB overviews for {len(tmdb_ids_to_fetch)} movies...")
    overviews = fetch_tmdb_overviews(tmdb_ids_to_fetch)
    print(f"  Got {len(overviews)} overviews")

    tfidf_matrix, cb_tmdb_ids, tmdb_id_to_idx = build_content_based(overviews)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WS-3: Similar to The Dark Knight (content-based)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("WS-3: Content-Based — Similar to The Dark Knight")
    print("  Expected: action, thriller, crime, drama")
    print("=" * 60)

    dk_cb = get_similar_content_based(155, tfidf_matrix, cb_tmdb_ids, tmdb_id_to_idx, n=5)
    dk_genres_ok = {"Action", "Thriller", "Crime", "Drama", "Sci-Fi", "Mystery", "Adventure"}
    dk_cb_matches = 0

    for i, rec in enumerate(dk_cb):
        title, genres = tmdb_to_info(rec["tmdb_id"], tmdb_to_ml, movies)
        genre_set = set(genres.split("|")) if genres else set()
        match = bool(genre_set & dk_genres_ok)
        if match:
            dk_cb_matches += 1
        print(f"  {i+1}. {title} [{genres}] (score={rec['score']:.3f}) {'OK' if match else '?'}")

    passed = dk_cb_matches >= 3
    results["WS-3"] = ("PASS" if passed else "FAIL", f"{dk_cb_matches}/5 genre-coherent")
    print(f"  -> {dk_cb_matches}/5 coherent — {'PASS' if passed else 'FAIL'}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WS-4: Similar to Toy Story (content-based)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("WS-4: Content-Based — Similar to Toy Story")
    print("  Expected: animation, children, family, comedy")
    print("=" * 60)

    ts_cb = get_similar_content_based(862, tfidf_matrix, cb_tmdb_ids, tmdb_id_to_idx, n=5)
    ts_genres_ok = {"Animation", "Children", "Family", "Comedy", "Adventure", "Fantasy"}
    ts_cb_matches = 0

    for i, rec in enumerate(ts_cb):
        title, genres = tmdb_to_info(rec["tmdb_id"], tmdb_to_ml, movies)
        genre_set = set(genres.split("|")) if genres else set()
        match = bool(genre_set & ts_genres_ok)
        if match:
            ts_cb_matches += 1
        print(f"  {i+1}. {title} [{genres}] (score={rec['score']:.3f}) {'OK' if match else '?'}")

    passed = ts_cb_matches >= 3
    results["WS-4"] = ("PASS" if passed else "FAIL", f"{ts_cb_matches}/5 genre-coherent")
    print(f"  -> {ts_cb_matches}/5 coherent — {'PASS' if passed else 'FAIL'}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Train Collaborative Filtering model
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    item_factors, movie_to_idx, idx_to_movie = train_collaborative_model(
        ratings, N_FACTORS
    )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WS-5: Collaborative — Also liked The Dark Knight
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("WS-5: Collaborative — Viewers who liked The Dark Knight also liked...")
    print("  Expected: films a Dark Knight fan would plausibly enjoy")
    print("=" * 60)

    dk_ml_id = tmdb_to_ml.get(155)
    dk_cf_matches = 0

    if dk_ml_id:
        dk_cf = get_similar_collaborative(
            dk_ml_id, item_factors, movie_to_idx, idx_to_movie, n=5
        )
        # Dark Knight fans plausibly like: action, thriller, crime, sci-fi, drama, adventure
        dk_cf_ok = {"Action", "Thriller", "Crime", "Sci-Fi", "Drama", "Adventure", "Mystery"}

        for i, rec in enumerate(dk_cf):
            title, genres = get_movie_info(rec["ml_movie_id"], movies)
            genre_set = set(genres.split("|")) if genres else set()
            match = bool(genre_set & dk_cf_ok)
            if match:
                dk_cf_matches += 1
            print(f"  {i+1}. {title} [{genres}] (score={rec['score']:.3f}) {'OK' if match else '?'}")
    else:
        print("  ERROR: The Dark Knight not found in MovieLens")
        dk_cf = []

    passed = dk_cf_matches >= 3
    results["WS-5"] = ("PASS" if passed else "FAIL", f"{dk_cf_matches}/5 plausible")
    print(f"  -> {dk_cf_matches}/5 plausible — {'PASS' if passed else 'FAIL'}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WS-6: Collaborative — Also liked Toy Story
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("WS-6: Collaborative — Viewers who liked Toy Story also liked...")
    print("  Expected: films a Toy Story fan would plausibly enjoy")
    print("=" * 60)

    ts_ml_id = tmdb_to_ml.get(862)
    ts_cf_matches = 0

    if ts_ml_id:
        ts_cf = get_similar_collaborative(
            ts_ml_id, item_factors, movie_to_idx, idx_to_movie, n=5
        )
        ts_cf_ok = {"Animation", "Children", "Family", "Comedy", "Adventure", "Fantasy"}

        for i, rec in enumerate(ts_cf):
            title, genres = get_movie_info(rec["ml_movie_id"], movies)
            genre_set = set(genres.split("|")) if genres else set()
            match = bool(genre_set & ts_cf_ok)
            if match:
                ts_cf_matches += 1
            print(f"  {i+1}. {title} [{genres}] (score={rec['score']:.3f}) {'OK' if match else '?'}")
    else:
        print("  ERROR: Toy Story not found in MovieLens")
        ts_cf = []

    passed = ts_cf_matches >= 3
    results["WS-6"] = ("PASS" if passed else "FAIL", f"{ts_cf_matches}/5 plausible")
    print(f"  -> {ts_cf_matches}/5 plausible — {'PASS' if passed else 'FAIL'}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WS-7: CB vs CF differentiation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("WS-7: Are Content-Based and Collaborative results different?")
    print("  (The whole point: they should surface DIFFERENT films)")
    print("=" * 60)

    # Convert both to TMDB IDs for fair comparison
    cb_set = set(r["tmdb_id"] for r in dk_cb)

    cf_set = set()
    if dk_ml_id and dk_cf:
        for rec in dk_cf:
            tmdb_id = ml_to_tmdb.get(rec["ml_movie_id"])
            if tmdb_id:
                cf_set.add(tmdb_id)

    overlap = cb_set & cf_set
    n_different = (len(cb_set) + len(cf_set)) - 2 * len(overlap)

    print(f"  Content-Based recs : {cb_set}")
    print(f"  Collaborative recs : {cf_set}")
    print(f"  Overlap            : {len(overlap)} film(s)")
    print(f"  Different          : {n_different} film(s)")
    print(f"  Target             : >= 3 different")

    passed = n_different >= 3
    results["WS-7"] = ("PASS" if passed else "FAIL", f"{n_different} films different")
    print(f"  -> {'PASS' if passed else 'FAIL'}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SUMMARY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("WALKING SKELETON — RESULTS")
    print("=" * 60)

    pass_count = 0
    for test_id in sorted(results.keys()):
        verdict, detail = results[test_id]
        if verdict == "PASS":
            pass_count += 1
        print(f"  {test_id}: {verdict} — {detail}")

    total = len(results)
    print(f"\n  GATE: {pass_count}/{total}")

    if pass_count == total:
        print("  SKELETON CHECK: Riskiest Assumption HOLDS.")
        print("  -> Continue to Scopes.")
    else:
        print("  SKELETON CHECK: Issues found. Review before continuing.")

    return results


if __name__ == "__main__":
    run_tests()
