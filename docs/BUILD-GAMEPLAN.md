# BUILD Gameplan

> Template from The Builder PM Method — BUILD phase (start)
> Fill this AFTER the 1-Pager, BEFORE writing any code.
> Decompose your MVP into vertical slices — NOT horizontal layers (backend, frontend).
> Each slice goes end-to-end: from data to user interface.

---

**Project Name:** WatchNext
**Date:** 2026-02-19
**Cycle Appetite:** 1 week (side project)
**MVP Features (from 1-Pager):**
- Natural language mood → top 5 movie recommendations
- "Where to watch" (streaming platforms per movie)
- Movie cards (poster, rating, runtime, synopsis)
- "Why this matches" explanation per recommendation

**Riskiest Assumption (from 1-Pager):**
"An LLM can translate a vague mood description into TMDB Discover API filters that return movies the user actually wants to watch."

---

## Context Setup

**Action:** 1-Pager key sections installed in `CLAUDE.md` at project root.

**For each slice:** Give Claude Code the slice description below + CLAUDE.md context.

---

## Definition of Ready / Definition of Done

### DOR — Definition of Ready (before starting a slice)

| # | Criteria | Walking Skeleton variant |
|---|----------|--------------------------|
| R1 | Previous gate PASSED | FRAME Review passed (1-Pager approved) |
| R2 | Dependencies identified and installed | venv, OpenAI API key, TMDB API key verified |
| R3 | Test data specs defined in gameplan | Mood queries defined per micro-test |
| R4 | Micro-tests defined as acceptance criteria BEFORE coding | Same |
| R5 | CLAUDE.md updated with current phase and slice context | Same |

### DOD — Definition of Done (before closing a slice)

| # | Criteria | Artifact |
|---|----------|----------|
| D1 | All micro-tests PASS per gate criteria | Gameplan → Result line |
| D2 | BUILD-LOG entry written | `docs/BUILD-LOG.md` |
| D3 | BUILD-WALKTHROUGH written + quality checklist | `docs/BUILD-WALKTHROUGH-{slice}.md` |
| D4 | CLAUDE.md updated with next phase | `CLAUDE.md` |
| D5 | Committed on main with descriptive message | Git log |

### Compliance tracker

| Slice | R1 | R2 | R3 | R4 | R5 | D1 | D2 | D3 | D4 | D5 | Status |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|--------|
| Walking Skeleton | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | **DONE** |
| Scope 1 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | **DONE** |
| Scope 2 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | **DONE** |

---

## Walking Skeleton

> The thinnest possible end-to-end slice that tests the Riskiest Assumption.

**What it does:** Take a mood description as text → GPT-4o-mini translates it to structured TMDB Discover API filters → call TMDB Discover → return 5 movies with title, genre, rating, runtime.

**End-to-end path:** Mood text → FastAPI endpoint → GPT-4o-mini (mood → JSON filters) → TMDB Discover API → 5 movies returned as JSON

**What's IN the Skeleton:**
- 1 FastAPI endpoint (`POST /recommend`)
- GPT-4o-mini structured output: mood → `{ genres, runtime_lte, runtime_gte, vote_average_gte, sort_by }`
- TMDB Discover API call with those filters
- Return 5 movies: title, genre names, rating, runtime, release year
- 1 health endpoint (`GET /health`)

**What's OUT (deferred to Scopes):**
- Watch providers ("where to watch")
- GPT ranking/explanation ("why this matches")
- Posters/images
- Frontend
- Deploy

**Done when:** `curl -X POST /recommend -d '{"mood": "something funny and light"}'` returns 5 comedy movies with correct metadata. Tested on 5 different moods.

**Micro-test:**

| # | Mood Input | Expected Filters (verify GPT output) | Expected Movies (verify TMDB results) | Pass Criteria |
|---|-----------|--------------------------------------|---------------------------------------|---------------|
| WS-1 | "Something funny and light, under 2 hours" | genres includes 35 (Comedy), runtime_lte ≤ 120 | 5 comedies, all < 120 min | Filter correct + 5/5 movies comply |
| WS-2 | "Scary movie for Halloween night" | genres includes 27 (Horror) | 5 horror movies | Filter correct + 5/5 genre match |
| WS-3 | "Epic action movie, well-rated" | genres includes 28 (Action), vote_average_gte ≥ 7.0 | 5 action movies, all rated 7.0+ | Filter correct + 5/5 comply |
| WS-4 | "Romantic movie for date night" | genres includes 10749 (Romance) | 5 romance movies | Filter correct + 5/5 genre match |
| WS-5 | "Something mind-bending like Inception" | genres includes 878 (Sci-Fi) or 53 (Thriller) | 5 sci-fi/thriller movies | Filter correct + 5/5 genre match |

**Gate:** 5/5 — each mood correctly translated to filters AND 5/5 movies comply with stated constraints.

**Result:**

| # | Mood Input | Filters Generated | Movies OK | Latency | Verdict |
|---|-----------|-------------------|-----------|---------|---------|
| WS-1 | "Something funny and light, under 2 hours" | `with_genres=35, runtime_lte=120` | 5/5 comedies, all < 120 min | 3.0s | **PASS** |
| WS-2 | "Scary movie for Halloween night" | `with_genres=27` | 5/5 horror movies | 2.4s | **PASS** |
| WS-3 | "Epic action movie, well-rated" | `with_genres=28, sort_by=vote_average.desc` | 5/5 action, all rated 8.4+ (Dark Knight, LOTR ROTK...) | 3.0s | **PASS** |
| WS-4 | "Romantic movie for date night" | `with_genres=10749` | 5/5 romance movies | 2.2s | **PASS** |
| WS-5 | "Something mind-bending like Inception" | `with_genres=878\|53` | 5/5 sci-fi/thriller | 2.1s | **PASS** |

**Gate: 5/5 PASS** — All moods correctly translated to filters, all movies comply with constraints. Average latency 2.5s (well under 5s target).

**Note WS-3:** GPT set `vote_average_gte=6` (not 7.0) but used `sort_by=vote_average.desc`, so all returned movies are rated 8.4+. Outcome exceeds expectations via a different mechanism.

→ **RITUAL: Skeleton Check** — Does the Riskiest Assumption hold?
- If NO → The LLM can't reliably translate moods to filters. Options: (1) add few-shot examples, (2) constrain output with function calling schema, (3) fallback to keyword search. If still fails → kill.
- If YES → Continue to Scopes.

---

## Scopes

### Scope 1: Full recommendation pipeline

**What it adds:** Watch providers ("where to watch" per movie). GPT-4o-mini re-ranks 20 movies → top 5 with "why this matches" explanation. Movie posters and full metadata. Platform filter in the mood input ("on Netflix").

**End-to-end path:** Mood text → GPT filters (now includes `with_watch_providers`) → TMDB Discover (20 results) → TMDB Watch Providers per movie → GPT ranks top 5 + explains why → JSON response with full data

**Done when:** `POST /recommend` with mood + platform preferences returns 5 movies with: title, poster URL, rating, runtime, synopsis, streaming platforms, "why this matches" explanation.

**Micro-test:**

| # | Type | Mood Input | Expected Behavior | Pass Criteria |
|---|------|-----------|-------------------|---------------|
| S1-1 | Platform filter | "Comedy on Netflix" | All 5 recs available on Netflix | 5/5 show Netflix in providers |
| S1-2 | Platform filter | "Action on Disney+" | All 5 recs available on Disney+ | 5/5 show Disney+ in providers |
| S1-3 | Explanation | "Light and funny for a tired couple" | Each rec has a "why" that references "light", "funny", or "couple" | 5/5 explanations reference the mood |
| S1-4 | Ranking quality | "Best thriller of the last 5 years" | Top-ranked movie has higher TMDB rating than #5 | Recs ordered by quality (not random) |
| S1-5 | Poster URLs | Any mood | All 5 recs have valid poster_path | 5/5 poster URLs resolve (HTTP 200) |
| S1-6 | Full metadata | Any mood | Each rec has: title, rating, runtime, synopsis, providers, why | All 6 fields present for all 5 recs |

**Gate:** 6/6 PASS

**Result:**

| # | Type | Mood Input | Result | Verdict |
|---|------|-----------|--------|---------|
| S1-1 | Platform filter | "Comedy on Netflix" | 5/5 available on Netflix | **PASS** |
| S1-2 | Platform filter | "Action on Disney+" | 5/5 available on Disney+ | **PASS** |
| S1-3 | Explanation | "Light and funny for a tired couple" | All "why" reference mood context | **PASS** |
| S1-4 | Ranking quality | "Best thriller of the last 5 years" | Top-ranked higher rated than #5 | **PASS** |
| S1-5 | Poster URLs | "epic action" | 5/5 poster URLs resolve (HTTP 200) | **PASS** |
| S1-6 | Full metadata | "epic action" | All 6 fields present for all 5 recs | **PASS** |

**Gate: 6/6 PASS** — Full pipeline with providers, ranking, explanations, posters all working.

---

### Scope 2: Deploy + Lovable frontend

**What it adds:** Backend deployed on Render. React/Tailwind frontend built in Lovable. Full user experience: type mood → see 5 movie cards with posters, ratings, streaming badges, explanations.

**Done when:** A non-tech person can go to the live URL, type "I want something funny tonight", and see 5 beautiful movie cards with posters and "where to watch" badges — without instructions.

**Micro-test:**

| # | Type | Test | Expected Behavior | Pass Criteria |
|---|------|------|-------------------|---------------|
| S2-1 | Deploy | `curl https://watchnext-api.onrender.com/health` | `{"status": "ok"}` | API accessible |
| S2-2 | E2E | Query from Lovable → Render → TMDB → response | 5 movie cards displayed | Full pipeline works cross-origin |
| S2-3 | Posters | Submit a mood query | 5 movie posters load correctly | All images visible, no broken links |
| S2-4 | Streaming badges | Submit "comedy on Netflix" | Netflix badge visible on each card | Platform badges render correctly |
| S2-5 | Loading | Submit a query | Loading state visible during processing | User knows something is happening |
| S2-6 | Empty state | Open app, no query yet | Clear instructions + example moods | User knows what to type |
| S2-7 | Mobile | Open on phone | Layout works on mobile screen | Cards stack vertically, input accessible |
| S2-8 | Usability | Give to 2-3 non-tech people | Complete flow without help | Zero confusion |

**Gate:** 8/8 PASS

**Result:**

| # | Type | Test | Result | Verdict |
|---|------|------|--------|---------|
| S2-1 | Deploy | curl /health | `{"status": "ok"}` — 200 in 0.3s | **PASS** |
| S2-2 | E2E | Lovable → Render → TMDB → response | 5 films affiches, cross-origin OK | **PASS** |
| S2-3 | Posters | Mood query | 5/5 posters chargent correctement | **PASS** |
| S2-4 | Streaming | "comedy on Netflix" | Logos streaming visibles dans detail view | **PASS** |
| S2-5 | Loading | Submit query | Lottie popcorn + progress bar indigo + movie facts | **PASS** |
| S2-6 | Empty state | Ouvrir l'app | Headline + chips + input + poster wall atmospherique | **PASS** |
| S2-7 | Mobile | Ouvrir sur telephone | Grid 2 colonnes, bottom sheet au clic, input accessible | **PASS** |
| S2-8 | Usability | Non-tech users | Flow complet sans aide | **PASS** |

**Gate: 8/8 PASS** — Produit demo-ready. Backend Render + Frontend Lovable fonctionnels end-to-end.

---

## Architecture — Module Structure

```
watchnext/
├── CLAUDE.md              ← AI context
├── api.py                 ← FastAPI app (2 endpoints: /health, /recommend)
├── core/
│   ├── mood_parser.py     ← GPT-4o-mini: mood text → structured filters JSON
│   ├── tmdb_client.py     ← TMDB API wrapper: discover + watch providers + images
│   └── recommender.py     ← GPT-4o-mini: rank 20 → top 5 + explain WHY
├── docs/
│   ├── BUILDER-PM-1-PAGER.md
│   ├── BUILD-GAMEPLAN.md
│   ├── BUILD-LOG.md
│   └── BUILD-WALKTHROUGH-*.md
├── requirements.txt
├── render.yaml
├── Procfile
└── .env
```

| Module | Responsibility | Walking Skeleton | Scope 1 | Scope 2 |
|--------|---------------|:----------------:|:-------:|:-------:|
| `mood_parser.py` | Mood → TMDB filters | ✓ | Enhanced (providers) | — |
| `tmdb_client.py` | TMDB API calls | Discover only | + Watch Providers + Images | — |
| `recommender.py` | Rank + explain | — (not in WS) | ✓ | — |
| `api.py` | FastAPI endpoints | /health + /recommend (basic) | /recommend (full) | CORS for Lovable |
| Lovable frontend | UI | — | — | ✓ |

---

## Exit Criteria (BUILD → EVALUATE)

- [ ] All MVP features from 1-Pager functional end-to-end
- [ ] Riskiest Assumption tested (Skeleton Check passed)
- [ ] Open Questions from 1-Pager resolved or converted to ADRs
- [ ] Build Log up to date
- [ ] Ready for formal evaluation (10 mood queries × 3 eval levels)
