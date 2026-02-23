# Project Dossier — WatchNext

> From The Builder PM Method — SHIP phase

---

## Summary

| | |
|---|---|
| **Project** | WatchNext |
| **Tagline** | Movie recommendations powered by mood |
| **Problem** | Decision fatigue: 200+ options across streaming platforms, 30+ min browsing, still nothing to watch |
| **Solution** | Type how you feel → get 5 movies that match, with where to watch them |
| **Stack** | FastAPI (Python) + GPT-4o-mini + TMDB API + React/Tailwind (Lovable) |
| **Deploy** | Backend: Render ($7/mo) / Frontend: Lovable |
| **Timeline** | 5 days (Feb 19-23, 2026) |
| **Builder** | Mehdi Bargach |
| **Method** | The Builder PM Method (FRAME → BUILD → EVALUATE → SHIP) |

---

## Live URLs

| | |
|---|---|
| **Frontend** | Lovable (demo-ready) |
| **Backend API** | https://watchnext-flta.onrender.com |
| **GitHub** | https://github.com/Mehdibargach/watchnext |
| **Health check** | https://watchnext-flta.onrender.com/health |

---

## What it does

1. User types a mood: "I'm exhausted, something chill" or "Korean drama, emotional" or "action movie with Brad Pitt on Netflix"
2. GPT-4o-mini translates the mood into structured TMDB API filters (genre, language, actor, platform, rating, runtime)
3. TMDB Discover returns 20 candidates
4. Movies are enriched with details (runtime, poster, streaming providers)
5. GPT-4o-mini curates the top 5 with personalized explanations
6. User sees 5 movie cards with posters, ratings, streaming badges, and "why this movie" explanations

---

## AI Product Typology

**Recommendation / Personalization** — one of 5 AI product typologies in The Builder PM Method.

The core challenge: translating unstructured human preferences (mood) into structured API queries (TMDB filters), then using AI to curate and explain results. The LLM acts as both a translator (mood → filters) and a curator (rank → explain).

---

## Architecture

```
User mood (text)
      │
      ▼
┌─────────────────┐
│  mood_parser.py  │  GPT-4o-mini function calling
│  mood → filters  │  (genre, language, actor, platform, rating, runtime)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ tmdb_client.py   │  TMDB Discover API (20 results)
│ + search_person  │  + Movie Details + Watch Providers
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ recommender.py   │  GPT-4o-mini curator
│ rank 20 → top 5  │  + "why this movie" explanations
│ + dedup + genre   │  + genre precision rules
└────────┬────────┘
         │
         ▼
    5 movie cards
    (poster, rating, runtime, providers, explanation)
```

---

## Build Phases

| Phase | Duration | Key Output |
|-------|----------|------------|
| FRAME | Day 1 | 1-Pager + Gameplan (3 slices, 19 micro-tests) |
| BUILD: Walking Skeleton | Day 1 | Mood → filters → 5 movies. 5/5 PASS. Riskiest Assumption validated. |
| BUILD: Scope 1 | Day 3 | Full pipeline: 20→5, ranking, explanations, posters, streaming. 6/6 PASS. |
| BUILD: Scope 2 | Day 3-4 | Deploy Render + Lovable frontend. 8/8 PASS. |
| EVALUATE: Round 1 | Day 5 | 10 golden queries + 3 wild tests. **NO-GO** (5 bugs). |
| BUILD: Micro-loop | Day 5 | 5 fixes: language, cast, dedup, genre precision, null cleanup. |
| EVALUATE: Round 2 | Day 5 | Re-run failed queries. **CONDITIONAL GO**. |
| SHIP | Day 5 | This dossier. |

---

## Eval Results

| Metric | Result | Target |
|--------|--------|--------|
| G1 — Filter Accuracy | 10/10 | 10/10 (100%) |
| G2 — Constraint Compliance | 49/50 | 50/50 (100%) |
| G3 — Avg Relevance Score | 2.78/3.0 | >= 2.0 |
| G4 — Median Latency | ~15-20s | < 30s |
| G5 — Usability | PASS (8/8) | Zero confusion |

**Decision:** CONDITIONAL GO

**Conditions (documented, not blocking):**
1. Animation bias — LLM defaults to animated for vague/family moods (SIGNAL for V2)
2. Language = language, not country — TMDB limitation (French includes Quebec)

---

## Key Bugs Found & Fixed

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| "Korean drama" → 0 Korean films | No `with_original_language` in schema | Added to function calling + TMDB param |
| Duplicate movie in results | Curator LLM returns same ID twice | Dedup by movie_id in recommender |
| Horror movie in thriller results | Genre overlap in TMDB | Strengthened curator prompt |
| "Brad Pitt" → 0 Brad Pitt films | No `with_cast` in schema | Added `with_cast_names` + `search_person()` |
| GPT returns "null" as string | Python `None` vs string `"null"` | Cleanup filter: reject both |

---

## Key Learnings (for the book)

1. **Schema coverage > LLM intelligence** — The LLM understood "Korean drama" perfectly but had no parameter to express it. The bottleneck wasn't AI reasoning, it was the API contract. Lesson: your function calling schema IS your feature set.

2. **Wild tests find what golden datasets miss** — The evaluator's wife found 2 bugs (French, Brad Pitt) that the 10 planned queries didn't catch. Real users don't follow your test plan.

3. **Micro-loop = the method working** — NO-GO isn't failure, it's the eval gate doing its job. 5 bugs identified → 5 fixes → re-test → CONDITIONAL GO. The loop is the feature.

4. **"null" cleanup is a real thing** — GPT-4o-mini sometimes returns the string "null" instead of JSON null. Always filter both.

5. **Poster wall = movie posters ARE the design system** — Dark monochrome UI + colorful posters = the app looks beautiful regardless of which movies appear.

6. **Loading is a feature, not a wait** — Fun facts during 15-20s loading turned the wait into engagement. Users loved it.

7. **Function calling = pre-filled form** — The LLM doesn't "search for movies." It fills out a structured form (genre, language, actor, platform) that maps to an API. Understanding this reframes how you design AI features.

---

## Files

| File | Purpose |
|------|---------|
| `api.py` | FastAPI app (2 endpoints) |
| `core/mood_parser.py` | GPT-4o-mini: mood → structured TMDB filters |
| `core/tmdb_client.py` | TMDB API wrapper (discover, details, providers, person search) |
| `core/recommender.py` | GPT-4o-mini: rank 20 → top 5 with explanations |
| `docs/BUILDER-PM-1-PAGER.md` | Problem/solution/riskiest assumption |
| `docs/BUILD-GAMEPLAN.md` | Slices, micro-tests, DOR/DOD |
| `docs/BUILD-LOG.md` | Chronological build log |
| `docs/BUILD-WALKTHROUGH-*.md` | 3 didactic walkthroughs (WS, S1, S2) |
| `docs/EVAL-REPORT.md` | Full eval (10 golden + 3 wild, R1+R2) |
| `docs/LOVABLE-PROMPTS.md` | 3 iterative Lovable prompts |
| `docs/PROJECT-DOSSIER.md` | This file |

---

## Costs

| Service | Monthly | Notes |
|---------|---------|-------|
| Render (backend) | $7 | Starter plan, auto-deploy from GitHub |
| OpenAI API | ~$2-5 | GPT-4o-mini, ~100 queries/month estimate |
| TMDB API | $0 | Free tier, 40 req/s |
| Lovable (frontend) | $20 | Shared across projects |
| **Total** | **~$30/mo** | |

---

## What's Next (V2 ideas, not committed)

- Genre diversity in curator (reduce animation bias)
- Country of origin filter (beyond language)
- TV series support (TMDB has /discover/tv)
- User accounts + history
- Multi-language UI (French, Arabic)
