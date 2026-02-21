"""TMDB API client — wraps Discover, Movie Details, and Watch Providers endpoints.

All calls go through httpx (sync). TMDB API key is read from environment.
Attribution required: "This product uses the TMDB API but is not endorsed or certified by TMDB."
"""

import os
import httpx

_BASE = "https://api.themoviedb.org/3"
_IMG_BASE = "https://image.tmdb.org/t/p"

GENRE_ID_TO_NAME = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    53: "Thriller", 10752: "War", 37: "Western",
}


def _headers() -> dict:
    api_key = os.environ.get("TMDB_API_KEY", "")
    return {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
    }


def discover_movies(filters: dict, limit: int = 5) -> list[dict]:
    """Call TMDB Discover endpoint with parsed filters.

    Args:
        filters: Dict from mood_parser.parse_mood() — keys map to TMDB params.
        limit: Number of movies to return (default 5 for Walking Skeleton).

    Returns:
        List of movie dicts with basic metadata from Discover.
    """
    params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "page": 1,
    }

    # Map our filter keys to TMDB parameter names
    param_mapping = {
        "with_genres": "with_genres",
        "vote_average_gte": "vote_average.gte",
        "with_runtime_gte": "with_runtime.gte",
        "with_runtime_lte": "with_runtime.lte",
        "sort_by": "sort_by",
        "release_date_gte": "primary_release_date.gte",
        "release_date_lte": "primary_release_date.lte",
    }

    for our_key, tmdb_key in param_mapping.items():
        if our_key in filters and filters[our_key] is not None:
            params[tmdb_key] = filters[our_key]

    # Ensure minimum vote count to avoid obscure movies with few ratings
    params["vote_count.gte"] = 50

    resp = httpx.get(f"{_BASE}/discover/movie", params=params, headers=_headers())
    resp.raise_for_status()
    results = resp.json().get("results", [])

    return results[:limit]


def get_movie_details(movie_id: int) -> dict:
    """Fetch full details for a single movie (includes runtime)."""
    resp = httpx.get(
        f"{_BASE}/movie/{movie_id}",
        params={"language": "en-US"},
        headers=_headers(),
    )
    resp.raise_for_status()
    return resp.json()


def enrich_movies(discover_results: list[dict]) -> list[dict]:
    """Enrich Discover results with full details (runtime, etc.).

    For each movie, fetches /movie/{id} to get runtime and full metadata.
    Returns a clean list of movie dicts ready for the API response.
    """
    enriched = []
    for movie in discover_results:
        details = get_movie_details(movie["id"])
        genre_names = [GENRE_ID_TO_NAME.get(gid, "Unknown") for gid in movie.get("genre_ids", [])]

        enriched.append({
            "id": movie["id"],
            "title": details.get("title", movie.get("title", "")),
            "genres": genre_names,
            "rating": details.get("vote_average", 0),
            "runtime": details.get("runtime", 0),
            "release_year": (details.get("release_date") or "")[:4],
            "overview": details.get("overview", ""),
            "poster_url": f"{_IMG_BASE}/w500{details['poster_path']}" if details.get("poster_path") else None,
        })

    return enriched


def poster_url(poster_path: str, size: str = "w500") -> str:
    """Construct a full poster URL from a TMDB poster_path."""
    if not poster_path:
        return ""
    return f"{_IMG_BASE}/{size}{poster_path}"
