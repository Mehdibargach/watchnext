"""
Loads MovieLens data and builds the mapping between MovieLens IDs and TMDB IDs.

MovieLens 25M provides:
- links.csv: movieId -> imdbId -> tmdbId (the bridge between the two databases)
- movies.csv: movieId -> title, genres
- ratings.csv: userId, movieId, rating (25 million ratings from 162K users)
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "movielens" / "ml-25m"
# Fallback for iCloud-synced environments where large files may not be locally available
_FALLBACK_DIR = Path("/tmp/ml-25m")


def _csv_path(filename):
    """Return the best available path for a CSV file (local fallback if iCloud fails)."""
    primary = DATA_DIR / filename
    fallback = _FALLBACK_DIR / filename
    if fallback.exists():
        return fallback
    return primary


def load_links():
    """Load the MovieLens -> TMDB ID mapping."""
    links = pd.read_csv(_csv_path("links.csv"))
    valid = links.dropna(subset=["tmdbId"]).copy()
    valid["tmdbId"] = valid["tmdbId"].astype(int)
    return valid


def load_movies():
    """Load MovieLens movie metadata (titles + genres)."""
    return pd.read_csv(_csv_path("movies.csv"))


def load_ratings(max_rows=None):
    """Load MovieLens ratings. Optionally limit to max_rows for speed."""
    df = pd.read_csv(
        _csv_path("ratings.csv"),
        usecols=["userId", "movieId", "rating"],
    )
    if max_rows and len(df) > max_rows:
        df = df.sample(n=max_rows, random_state=42)
    return df


def build_mapping(links_df=None):
    """Build bidirectional mapping MovieLens ID <-> TMDB ID."""
    if links_df is None:
        links_df = load_links()

    ml_to_tmdb = dict(zip(links_df["movieId"], links_df["tmdbId"]))
    tmdb_to_ml = dict(zip(links_df["tmdbId"], links_df["movieId"]))

    return ml_to_tmdb, tmdb_to_ml
