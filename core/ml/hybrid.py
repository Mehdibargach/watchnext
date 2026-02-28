"""
Hybrid Blend — combines content-based and collaborative scores.

How it works:
1. Each approach produces scores on different scales
   (content-based uses text similarity, collaborative uses taste-factor similarity)
2. We normalize both to 0-1 range (min-max normalization)
3. We blend with a configurable weight: α × content + (1-α) × collaborative
4. Default α = 0.5 (equal weight). If a movie has no collaborative score,
   we fall back to content-based only (graceful degradation).
"""


def normalize_scores(recs):
    """Normalize scores to 0-1 range using min-max scaling."""
    if not recs:
        return []

    scores = [r["score"] for r in recs]
    min_s = min(scores)
    max_s = max(scores)

    if max_s == min_s:
        return [{"tmdb_id": r["tmdb_id"], "score": 1.0} for r in recs]

    return [
        {
            "tmdb_id": r["tmdb_id"],
            "score": (r["score"] - min_s) / (max_s - min_s),
        }
        for r in recs
    ]


def blend(cb_recs, cf_recs, alpha=0.5, n=5):
    """
    Blend content-based and collaborative recommendations.

    Args:
        cb_recs: list of {"tmdb_id": int, "score": float} from content-based
        cf_recs: list of {"tmdb_id": int, "score": float} from collaborative
        alpha: weight for content-based (1-alpha for collaborative)
        n: number of results to return

    Returns:
        list of {"tmdb_id": int, "score": float, "sources": list}
    """
    # If no collaborative results, return content-based only
    if not cf_recs:
        return [
            {"tmdb_id": r["tmdb_id"], "score": r["score"], "sources": ["similar"]}
            for r in cb_recs[:n]
        ]

    # Normalize both sets to 0-1
    cb_norm = normalize_scores(cb_recs)
    cf_norm = normalize_scores(cf_recs)

    # Build score lookup
    cb_scores = {r["tmdb_id"]: r["score"] for r in cb_norm}
    cf_scores = {r["tmdb_id"]: r["score"] for r in cf_norm}

    # Collect all candidate movie IDs
    all_ids = set(cb_scores.keys()) | set(cf_scores.keys())

    # Blend scores
    blended = []
    for tmdb_id in all_ids:
        cb_s = cb_scores.get(tmdb_id)
        cf_s = cf_scores.get(tmdb_id)

        sources = []
        if cb_s is not None:
            sources.append("similar")
        if cf_s is not None:
            sources.append("also_liked")

        # If only one source, use that score directly
        if cb_s is not None and cf_s is not None:
            score = alpha * cb_s + (1 - alpha) * cf_s
        elif cb_s is not None:
            score = cb_s * alpha  # penalize single-source
        else:
            score = cf_s * (1 - alpha)  # penalize single-source

        blended.append({
            "tmdb_id": tmdb_id,
            "score": round(score, 4),
            "sources": sources,
        })

    # Sort by score descending, return top N
    blended.sort(key=lambda x: x["score"], reverse=True)
    return blended[:n]
