"""Mood Parser — translates natural language mood into TMDB Discover API filters.

GPT-4o-mini receives the user's mood description and returns structured JSON
filters that map directly to TMDB Discover API parameters.
Uses OpenAI function calling for reliable structured output.
"""

import json
from openai import OpenAI

_client = None

GENRE_MAP = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35,
    "Crime": 80, "Documentary": 99, "Drama": 18, "Family": 10751,
    "Fantasy": 14, "History": 36, "Horror": 27, "Music": 10402,
    "Mystery": 9648, "Romance": 10749, "Science Fiction": 878,
    "Thriller": 53, "War": 10752, "Western": 37,
}

PROVIDER_MAP = {
    "Netflix": 8, "Amazon Prime Video": 9, "Disney+": 337,
    "Hulu": 15, "Max": 1899, "Apple TV+": 350,
    "Paramount+": 531, "Peacock": 386,
}

GENRE_IDS_STR = ", ".join(f"{name}: {gid}" for name, gid in GENRE_MAP.items())
PROVIDER_IDS_STR = ", ".join(f"{name}: {pid}" for name, pid in PROVIDER_MAP.items())

SYSTEM_PROMPT = f"""You are a movie recommendation filter generator. Given a user's mood description, extract structured filters for the TMDB Discover API.

Available genre IDs:
{GENRE_IDS_STR}

Available streaming platform IDs:
{PROVIDER_IDS_STR}

Rules:
1. Map the user's mood to the most relevant genre(s). Return genre IDs as a pipe-separated string for OR (e.g. "35|10749" for Comedy OR Romance).
2. Only set filters the user explicitly or implicitly mentioned. Leave others as null.
3. If the user mentions a specific movie ("like Inception"), infer its genres (Sci-Fi, Thriller → "878|53").
4. Default sort_by to "popularity.desc" unless user asks for "highest rated" (use "vote_average.desc") or "newest" (use "primary_release_date.desc").
5. If the user mentions a time period ("recent" → last 3 years, "90s" → 1990-1999), set release_date_gte/lte.
6. Default vote_average_gte to 6.0 to filter out poorly-rated movies.
7. For runtime: "short" = under 100 min, "long" = over 150 min. Only set if user mentions duration.
8. Never hallucinate genre IDs or provider IDs. Only use the IDs listed above.
9. If the user mentions a streaming platform ("on Netflix", "available on Disney+"), set with_watch_providers to the matching provider ID. Only set if explicitly mentioned."""

FILTER_FUNCTION = {
    "name": "set_movie_filters",
    "description": "Set TMDB Discover API filters based on the user's mood",
    "parameters": {
        "type": "object",
        "properties": {
            "with_genres": {
                "type": "string",
                "description": "Pipe-separated genre IDs (e.g. '35|10749' for Comedy OR Romance). Use IDs from the provided list only.",
            },
            "vote_average_gte": {
                "type": "number",
                "description": "Minimum TMDB rating (0-10). Default 6.0.",
            },
            "with_runtime_gte": {
                "type": "integer",
                "description": "Minimum runtime in minutes. Only set if user mentions duration.",
                "nullable": True,
            },
            "with_runtime_lte": {
                "type": "integer",
                "description": "Maximum runtime in minutes. Only set if user mentions duration.",
                "nullable": True,
            },
            "sort_by": {
                "type": "string",
                "description": "Sort order. Default: popularity.desc",
                "enum": ["popularity.desc", "vote_average.desc", "primary_release_date.desc"],
            },
            "release_date_gte": {
                "type": "string",
                "description": "Minimum release date (YYYY-MM-DD). Only set if user mentions time period.",
                "nullable": True,
            },
            "release_date_lte": {
                "type": "string",
                "description": "Maximum release date (YYYY-MM-DD). Only set if user mentions time period.",
                "nullable": True,
            },
            "with_watch_providers": {
                "type": "string",
                "description": "Pipe-separated streaming provider IDs (e.g. '8' for Netflix). Only set if user mentions a specific platform.",
                "nullable": True,
            },
        },
        "required": ["with_genres", "vote_average_gte", "sort_by"],
    },
}


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def parse_mood(mood: str) -> dict:
    """Translate a mood description into TMDB Discover API filters.

    Returns a dict like:
        {
            "with_genres": "35",
            "vote_average_gte": 6.0,
            "sort_by": "popularity.desc",
            "with_runtime_lte": 120,
            ...
        }
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mood},
        ],
        functions=[FILTER_FUNCTION],
        function_call={"name": "set_movie_filters"},
    )

    fn_call = response.choices[0].message.function_call
    filters = json.loads(fn_call.arguments)

    # Clean up null values
    return {k: v for k, v in filters.items() if v is not None}
