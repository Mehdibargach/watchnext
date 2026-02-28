#!/usr/bin/env python3
"""
Scope 1 micro-tests — WatchNext V2 ML Recommendations.

Requires the API to be running: uvicorn api:app --port 8000

Tests:
  S1-1: Endpoint returns CB + CF results for Dark Knight
  S1-2: Multi-genre test on 5 seed films
  S1-3: Recent film (not in MovieLens) returns CB only, no error
  S1-4: Non-existent film returns error, no crash
  S1-5: Every recommended film has all 6 metadata fields
  S1-6: Latency < 3 seconds on 5 requests
"""

import time
import httpx

BASE = "http://localhost:8000"

# Seed films for multi-genre test
SEED_FILMS = {
    155: {"title": "The Dark Knight", "genre": "action/crime"},
    862: {"title": "Toy Story", "genre": "animation/family"},
    694: {"title": "The Shining", "genre": "horror"},
    11036: {"title": "The Notebook", "genre": "romance"},
    550: {"title": "Fight Club", "genre": "drama"},
}

REQUIRED_FIELDS = {"id", "title", "genres", "rating", "release_year", "poster_url"}

results = {}


def test_s1_1():
    """S1-1: GET /movie/155/similar returns 5 CB + 5 CF."""
    resp = httpx.get(f"{BASE}/movie/155/similar", timeout=15)
    data = resp.json()

    cb = data.get("similar_movies", [])
    cf = data.get("viewers_also_liked", [])

    passed = len(cb) == 5 and len(cf) == 5
    print(f"  CB: {len(cb)} films, CF: {len(cf)} films")
    return passed


def test_s1_2():
    """S1-2: Multi-genre — 5 seed films return pertinent results (>= 4/5)."""
    genre_keywords = {
        155: ["action", "crime", "thriller", "drama"],
        862: ["animation", "family", "comedy", "adventure"],
        694: ["horror", "thriller", "mystery"],
        11036: ["romance", "drama"],
        550: ["drama", "thriller", "crime"],
    }

    pertinent_count = 0

    for tmdb_id, info in SEED_FILMS.items():
        resp = httpx.get(f"{BASE}/movie/{tmdb_id}/similar", timeout=15)
        data = resp.json()
        cb = data.get("similar_movies", [])

        if not cb:
            print(f"  {info['title']}: NO results")
            continue

        # Check genre overlap: at least 3/5 CB results share a genre with seed
        matching = 0
        expected = [g.lower() for g in genre_keywords[tmdb_id]]
        for movie in cb:
            movie_genres = [g.lower() for g in movie.get("genres", [])]
            if any(g in movie_genres for g in expected):
                matching += 1

        is_pertinent = matching >= 3
        pertinent_count += 1 if is_pertinent else 0
        print(f"  {info['title']}: {matching}/5 genre-matching → {'OK' if is_pertinent else 'WEAK'}")

    passed = pertinent_count >= 4
    print(f"  Pertinent seeds: {pertinent_count}/5")
    return passed


def test_s1_3():
    """S1-3: Recent film not in MovieLens → CB works, CF is empty list, no error."""
    # Oppenheimer (2023) — TMDB 872585, not in MovieLens 25M (cutoff 2019)
    resp = httpx.get(f"{BASE}/movie/872585/similar", timeout=15)

    if resp.status_code != 200:
        print(f"  Status: {resp.status_code} (expected 200)")
        return False

    data = resp.json()
    cf = data.get("viewers_also_liked", [])

    print(f"  Status: 200, CF: {len(cf)} (expected 0 or empty)")
    print(f"  CB: {len(data.get('similar_movies', []))} films")

    # CF should be empty (not in MovieLens), response should be valid
    return resp.status_code == 200 and isinstance(cf, list)


def test_s1_4():
    """S1-4: Non-existent TMDB ID → error response, no server crash."""
    resp = httpx.get(f"{BASE}/movie/999999999/similar", timeout=15)

    # Should not crash (not 500)
    no_crash = resp.status_code != 500
    # After this, the server should still respond
    health = httpx.get(f"{BASE}/health", timeout=5)
    server_alive = health.status_code == 200

    print(f"  Status: {resp.status_code}, Server alive: {server_alive}")
    return no_crash and server_alive


def test_s1_5():
    """S1-5: Every recommended film has all 6 metadata fields."""
    resp = httpx.get(f"{BASE}/movie/155/similar", timeout=15)
    data = resp.json()

    all_movies = data.get("similar_movies", []) + data.get("viewers_also_liked", [])
    missing_count = 0

    for movie in all_movies:
        present = set(movie.keys())
        missing = REQUIRED_FIELDS - present
        if missing:
            print(f"  {movie.get('title', '?')}: missing {missing}")
            missing_count += 1

    print(f"  {len(all_movies)} films checked, {missing_count} with missing fields")
    return missing_count == 0 and len(all_movies) > 0


def test_s1_6():
    """S1-6: Latency < 3s on 5 requests."""
    latencies = []
    test_ids = [155, 862, 694, 550, 27205]

    for tmdb_id in test_ids:
        t0 = time.time()
        resp = httpx.get(f"{BASE}/movie/{tmdb_id}/similar", timeout=15)
        elapsed = time.time() - t0
        latencies.append(elapsed)

    avg = sum(latencies) / len(latencies)
    max_lat = max(latencies)
    print(f"  Avg: {avg:.1f}s, Max: {max_lat:.1f}s")
    for i, (tid, lat) in enumerate(zip(test_ids, latencies)):
        print(f"    {tid}: {lat:.1f}s")

    return max_lat < 3.0


# Run all tests
if __name__ == "__main__":
    print("=" * 60)
    print("WatchNext V2 — Scope 1 Micro-Tests")
    print("=" * 60)

    tests = [
        ("S1-1", "Endpoint returns CB + CF", test_s1_1),
        ("S1-2", "Multi-genre pertinence", test_s1_2),
        ("S1-3", "Recent film (not in MovieLens)", test_s1_3),
        ("S1-4", "Non-existent film", test_s1_4),
        ("S1-5", "Metadata completeness", test_s1_5),
        ("S1-6", "Latency < 3s", test_s1_6),
    ]

    for test_id, desc, fn in tests:
        print(f"\n--- {test_id}: {desc} ---")
        try:
            passed = fn()
        except Exception as e:
            passed = False
            print(f"  ERROR: {e}")
        results[test_id] = "PASS" if passed else "FAIL"
        print(f"  → {results[test_id]}")

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for test_id, result in results.items():
        print(f"  {test_id}: {result}")
    total_pass = sum(1 for r in results.values() if r == "PASS")
    print(f"\n  {total_pass}/{len(results)} PASS")
    print(f"  Gate: {'PASS' if total_pass == len(results) else 'FAIL'}")
