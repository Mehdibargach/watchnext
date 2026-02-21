"""Recommender — GPT-4o-mini ranks 20 candidates → top 5 with explanations.

Takes enriched movie data + original mood, asks GPT to pick the best 5
and explain WHY each matches the user's mood.
"""

import json
from openai import OpenAI

_client = None

SYSTEM_PROMPT = """You are a movie recommendation expert. Given a user's mood and a list of candidate movies, select the 5 BEST matches and explain why each one fits.

Rules:
1. Pick exactly 5 movies from the candidates. Return their IDs.
2. Rank them: #1 = best match for the mood, #5 = least strong match (but still good).
3. For each pick, write a 1-2 sentence explanation of WHY it matches the mood. Be specific — reference the movie's plot, tone, or themes, not just its genre.
4. Never mention technical details (TMDB, API, filters, ratings). Write as if recommending to a friend.
5. If the user mentioned a platform ("on Netflix"), prioritize movies available there.
6. Avoid recommending movies that clearly don't fit the mood, even if they match the genre filter (e.g., a kids' cartoon for "intense thriller night").
7. Write explanations in the same language as the user's mood. If the mood is in French, respond in French. If in English, respond in English."""

RANK_FUNCTION = {
    "name": "rank_movies",
    "description": "Select and rank the top 5 movies that best match the user's mood",
    "parameters": {
        "type": "object",
        "properties": {
            "picks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "movie_id": {
                            "type": "integer",
                            "description": "The TMDB movie ID from the candidate list",
                        },
                        "why": {
                            "type": "string",
                            "description": "1-2 sentence explanation of why this movie matches the mood",
                        },
                    },
                    "required": ["movie_id", "why"],
                },
                "minItems": 5,
                "maxItems": 5,
            },
        },
        "required": ["picks"],
    },
}


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def rank_movies(mood: str, candidates: list[dict]) -> list[dict]:
    """Rank candidate movies and pick top 5 with explanations.

    Args:
        mood: Original user mood string.
        candidates: List of enriched movie dicts (from enrich_movies).

    Returns:
        List of 5 movie dicts, each with an added "why" field.
    """
    # Build a concise summary of candidates for the prompt
    candidate_summaries = []
    for m in candidates:
        providers_str = ""
        if m.get("providers"):
            names = [p["name"] for p in m["providers"]]
            providers_str = f" | Streaming: {', '.join(names)}"
        candidate_summaries.append(
            f"- ID {m['id']}: \"{m['title']}\" ({m['release_year']}) — "
            f"{', '.join(m['genres'])} — Rating: {m['rating']}/10 — "
            f"{m['runtime']} min — {m['overview'][:150]}{providers_str}"
        )

    valid_ids = [m["id"] for m in candidates]
    user_message = f"""User's mood: "{mood}"

Candidate movies:
{chr(10).join(candidate_summaries)}

IMPORTANT: You MUST only use movie IDs from this list: {valid_ids}
Do NOT invent or guess movie IDs. Pick exactly 5 from the candidates above."""

    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        functions=[RANK_FUNCTION],
        function_call={"name": "rank_movies"},
    )

    fn_call = response.choices[0].message.function_call
    result = json.loads(fn_call.arguments)

    # Map picks back to full movie data, with fallback for missing IDs
    candidates_by_id = {m["id"]: m for m in candidates}
    picked_ids = set()
    ranked = []
    for pick in result["picks"]:
        movie = candidates_by_id.get(pick["movie_id"])
        if movie:
            ranked.append({**movie, "why": pick["why"]})
            picked_ids.add(pick["movie_id"])

    # Fallback: if GPT returned fewer than 5 valid picks, fill with top candidates
    if len(ranked) < 5:
        for m in candidates:
            if m["id"] not in picked_ids:
                ranked.append({**m, "why": ""})
                if len(ranked) >= 5:
                    break

    return ranked
