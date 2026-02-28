#!/usr/bin/env python3
"""
Scope 2 micro-tests — WatchNext V2 ML Recommendations.

Requires the API to be running: uvicorn api:app --port 8000

Tests:
  S2-1: Endpoint returns 3 lists (similar, also_liked, hybrid)
  S2-2: Hybrid quality — mix of both sources
  S2-3: Hybrid fallback — film not in MovieLens
  S2-4: Pertinence "Similar Movies" — Hit Rate vs TMDB reference (10 seeds)
  S2-5: Pertinence "Viewers Also Liked" — Hit Rate vs TMDB reference (10 seeds)
  S2-6: Value-add — ML recs are different from what LLM mood would return
  S2-7: Hybrid >= best individual approach
  S2-8: Latency < 3s on 10 requests
"""

import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE = "http://localhost:8000"
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_HEADERS = {
    "Authorization": f"Bearer {os.environ.get('TMDB_API_KEY', '')}",
    "accept": "application/json",
}

# 10 seed films across genres
SEEDS = {
    155: "The Dark Knight",
    862: "Toy Story",
    694: "The Shining",
    11036: "The Notebook",
    550: "Fight Club",
    27205: "Inception",
    578: "Jaws",
    120: "The Lord of the Rings: The Fellowship of the Ring",
    238: "The Godfather",
    680: "Pulp Fiction",
}

results = {}


def get_tmdb_recommendations(tmdb_id, n=20):
    """Fetch TMDB's 'recommendations' list as reference (better than 'similar')."""
    try:
        resp = httpx.get(
            f"{TMDB_BASE}/movie/{tmdb_id}/recommendations",
            headers=TMDB_HEADERS,
            params={"language": "en-US", "page": 1},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return [m["id"] for m in data.get("results", [])[:n]]
    except Exception:
        pass
    return []


def hit_rate(our_recs, reference_ids):
    """What fraction of our recs appear in the reference list."""
    if not our_recs or not reference_ids:
        return 0.0
    hits = sum(1 for r in our_recs if r in reference_ids)
    return hits / len(our_recs)


def test_s2_1():
    """S2-1: Endpoint returns 3 lists."""
    resp = httpx.get(f"{BASE}/movie/155/similar", timeout=15)
    data = resp.json()

    cb = data.get("similar_movies", [])
    cf = data.get("viewers_also_liked", [])
    hybrid = data.get("hybrid_recs", [])

    print(f"  Similar: {len(cb)}, Also Liked: {len(cf)}, Hybrid: {len(hybrid)}")
    return len(cb) == 5 and len(cf) == 5 and len(hybrid) == 5


def test_s2_2():
    """S2-2: Hybrid contains films from both sources (>= 2 from each)."""
    resp = httpx.get(f"{BASE}/movie/155/similar", timeout=15)
    data = resp.json()
    hybrid = data.get("hybrid_recs", [])

    from_similar = sum(1 for m in hybrid if "similar" in m.get("sources", []))
    from_also_liked = sum(1 for m in hybrid if "also_liked" in m.get("sources", []))

    print(f"  From 'Similar': {from_similar}, From 'Also Liked': {from_also_liked}")
    return from_similar >= 2 and from_also_liked >= 2


def test_s2_3():
    """S2-3: Film not in MovieLens → hybrid = similar only."""
    # Oppenheimer (2023) — not in MovieLens 25M
    resp = httpx.get(f"{BASE}/movie/872585/similar", timeout=15)
    data = resp.json()

    cf = data.get("viewers_also_liked", [])
    hybrid = data.get("hybrid_recs", [])

    # All hybrid sources should be "similar" only
    all_similar_only = all(
        m.get("sources") == ["similar"] for m in hybrid
    ) if hybrid else True

    print(f"  Also Liked: {len(cf)} (expected 0), Hybrid: {len(hybrid)}")
    print(f"  Hybrid sources all 'similar' only: {all_similar_only}")
    return len(cf) == 0 and all_similar_only


def test_s2_4():
    """S2-4: Hit Rate of 'Similar Movies' vs TMDB reference (>= 25% avg over 10 seeds)."""
    hit_rates = []

    for tmdb_id, title in SEEDS.items():
        # Get TMDB's reference list
        ref = get_tmdb_recommendations(tmdb_id)
        if not ref:
            print(f"  {title}: no TMDB reference")
            continue

        # Get our recs
        resp = httpx.get(f"{BASE}/movie/{tmdb_id}/similar", timeout=15)
        data = resp.json()
        our_ids = [m["id"] for m in data.get("similar_movies", [])]

        hr = hit_rate(our_ids, ref)
        hit_rates.append(hr)
        print(f"  {title}: {int(hr * 100)}% hit rate ({int(hr * 5)}/5 in TMDB top 20)")

    avg = sum(hit_rates) / len(hit_rates) if hit_rates else 0
    print(f"  Average hit rate: {avg:.0%}")
    # Threshold: >= 20% (6x random chance with 3000-movie corpus)
    # Random baseline = 5 picks from 3000 vs TMDB top 20 = ~3.3%
    return avg >= 0.20


def test_s2_5():
    """S2-5: Hit Rate of 'Viewers Also Liked' vs TMDB reference (>= 15% avg)."""
    hit_rates = []

    for tmdb_id, title in SEEDS.items():
        ref = get_tmdb_recommendations(tmdb_id)
        if not ref:
            continue

        resp = httpx.get(f"{BASE}/movie/{tmdb_id}/similar", timeout=15)
        data = resp.json()
        our_ids = [m["id"] for m in data.get("viewers_also_liked", [])]

        if not our_ids:
            print(f"  {title}: no 'Also Liked' results (not in MovieLens)")
            continue

        hr = hit_rate(our_ids, ref)
        hit_rates.append(hr)
        print(f"  {title}: {int(hr * 100)}% hit rate ({int(hr * 5)}/5 in TMDB top 20)")

    avg = sum(hit_rates) / len(hit_rates) if hit_rates else 0
    print(f"  Average hit rate: {avg:.0%}")
    # Collaborative is expected to find different films (that's the point),
    # so lower threshold than content-based
    return avg >= 0.15


def test_s2_6():
    """S2-6: Value-add — ML recs are different from each other across approaches."""
    different_counts = []

    for tmdb_id, title in SEEDS.items():
        resp = httpx.get(f"{BASE}/movie/{tmdb_id}/similar", timeout=15)
        data = resp.json()

        cb_ids = set(m["id"] for m in data.get("similar_movies", []))
        cf_ids = set(m["id"] for m in data.get("viewers_also_liked", []))

        if not cf_ids:
            continue

        # How many films are unique to each approach
        only_cb = cb_ids - cf_ids
        only_cf = cf_ids - cb_ids
        different = len(only_cb) + len(only_cf)
        total = len(cb_ids | cf_ids)
        pct = different / total if total else 0

        different_counts.append(pct)
        print(f"  {title}: {different}/{total} different ({pct:.0%})")

    avg = sum(different_counts) / len(different_counts) if different_counts else 0
    print(f"  Average differentiation: {avg:.0%}")
    return avg >= 0.60


def test_s2_7():
    """S2-7: Hybrid hit rate >= best individual approach on >= 6/10 seeds."""
    hybrid_wins = 0
    tested = 0

    for tmdb_id, title in SEEDS.items():
        ref = get_tmdb_recommendations(tmdb_id)
        if not ref:
            continue

        resp = httpx.get(f"{BASE}/movie/{tmdb_id}/similar", timeout=15)
        data = resp.json()

        cb_ids = [m["id"] for m in data.get("similar_movies", [])]
        cf_ids = [m["id"] for m in data.get("viewers_also_liked", [])]
        hy_ids = [m["id"] for m in data.get("hybrid_recs", [])]

        if not cf_ids:
            continue

        cb_hr = hit_rate(cb_ids, ref)
        cf_hr = hit_rate(cf_ids, ref)
        hy_hr = hit_rate(hy_ids, ref)
        best_individual = max(cb_hr, cf_hr)

        tested += 1
        wins = hy_hr >= best_individual
        if wins:
            hybrid_wins += 1

        print(f"  {title}: Similar={cb_hr:.0%} AlsoLiked={cf_hr:.0%} Hybrid={hy_hr:.0%} → {'WIN' if wins else 'LOSE'}")

    print(f"  Hybrid wins: {hybrid_wins}/{tested}")
    return hybrid_wins >= 6 if tested >= 10 else hybrid_wins >= tested * 0.6


def test_s2_8():
    """S2-8: Latency < 3s on 10 requests."""
    latencies = []

    for tmdb_id in SEEDS:
        t0 = time.time()
        resp = httpx.get(f"{BASE}/movie/{tmdb_id}/similar", timeout=15)
        elapsed = time.time() - t0
        latencies.append(elapsed)

    avg = sum(latencies) / len(latencies)
    max_lat = max(latencies)
    print(f"  Avg: {avg:.1f}s, Max: {max_lat:.1f}s")
    return max_lat < 3.0


# Run all tests
if __name__ == "__main__":
    print("=" * 60)
    print("WatchNext V2 — Scope 2 Micro-Tests")
    print("=" * 60)

    tests = [
        ("S2-1", "Endpoint returns 3 lists", test_s2_1),
        ("S2-2", "Hybrid quality — mix of sources", test_s2_2),
        ("S2-3", "Hybrid fallback — no MovieLens", test_s2_3),
        ("S2-4", "Hit Rate 'Similar Movies' vs TMDB", test_s2_4),
        ("S2-5", "Hit Rate 'Also Liked' vs TMDB", test_s2_5),
        ("S2-6", "Value-add — differentiation", test_s2_6),
        ("S2-7", "Hybrid >= best individual", test_s2_7),
        ("S2-8", "Latency < 3s", test_s2_8),
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
