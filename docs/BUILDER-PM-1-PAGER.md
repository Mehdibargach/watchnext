# Builder PM 1-Pager

**Project Name:** WatchNext
**One-liner:** Tell me your mood, I'll tell you what to watch and where.
**Date:** 2026-02-19
**Builder PM Method Phase:** BUILD (Recommendation / Personalization — TMDB API + LLM ranking)

---

## Problem

- **Decision fatigue:** 30+ minutes scrolling Netflix, Disney+, Prime without choosing anything. Average household has 4.1 streaming subscriptions (Antenna, 2025). More options = more paralysis.
- **Platform-locked recommendations:** Netflix recommends Netflix. Disney+ recommends Disney+. No tool shows the BEST option across all your platforms. Each algorithm optimizes for THEIR engagement, not YOUR satisfaction.
- **No mood understanding:** Algorithms optimize for "you watched X, so watch Y" (collaborative filtering). They can't understand "I'm exhausted after a long week, I want something light and feel-good, max 90 minutes, for 2 people."
- **What exists today:**
  - JustWatch: cross-platform search, but no natural language, no mood, no explanation of WHY
  - ChatGPT: can understand mood but hallucinates movies that don't exist, no streaming availability, no posters
  - Platform recs: locked to their own catalog, no mood input

## User

- **Primary:** Anyone with 2+ streaming subscriptions who regularly struggles to pick something to watch (couples, roommates, solo viewers)
- **Secondary:** Film enthusiasts who want curated recommendations beyond algorithmic suggestions
- **Context:** Friday/Saturday evening, couch, phone or laptop open, 2-4 streaming apps available. The pain hits EVERY WEEK. It's a recurring, high-frequency problem.

## Solution

| Pain | Feature |
|------|---------|
| 30 min scrolling, can't choose | Natural language input → top 5 personalized recommendations in seconds |
| Platform-locked recs (Netflix only shows Netflix) | Cross-platform results with "where to watch" badges for each pick (Netflix, Disney+, Prime, etc.) |
| Algorithms don't understand mood/context | LLM translates mood ("light and funny, ~90 min") into structured TMDB filters + ranks results with explanations |
| No explanation of WHY a movie is recommended | Each recommendation comes with a 1-line "why this matches your mood" explanation |

## Riskiest Assumption

**"An LLM can translate a vague mood description ('something light and funny for a tired couple, under 2 hours, on Netflix or Disney+') into TMDB Discover API filters that return movies the user actually wants to watch — better than scrolling their platforms."**

If this fails — if the LLM picks wrong genres, misinterprets mood, or returns irrelevant results — the product is worse than just browsing TMDB directly. The recommendation quality is EVERYTHING.

## Scope Scoring

**Criteria:**
- **Pain** (1-3): Does this feature solve the core problem? 1 = nice-to-have, 3 = without it the product is useless.
- **Risk** (1-3): Does building this test our riskiest assumption? 1 = we already know the answer, 3 = this IS the critical test.
- **Effort** (1-3): How hard to build? 1 = a few hours, 2 = 1-2 days, 3 = 3+ days.

**Formula:** Score = Pain + Risk - Effort. **MVP threshold: ≥ 3.**

| Feature | Pain | Risk | Effort | Score | In/Out |
|---------|------|------|--------|-------|--------|
| NL mood → top 5 movie recommendations | 3 | 3 | 2 | **4** | IN |
| "Where to watch" (streaming platform per movie) | 3 | 2 | 1 | **4** | IN |
| Movie cards (poster, rating, runtime, synopsis) | 3 | 1 | 1 | **3** | IN |
| "Why this matches" explanation per rec | 2 | 2 | 1 | **3** | IN |
| TV series support (movies + series) | 2 | 1 | 2 | **1** | OUT |
| Group mode ("2 people, she likes X, he likes Y") | 2 | 2 | 2 | **2** | OUT |
| Country/region selector | 2 | 1 | 1 | **2** | OUT |
| Follow-up ("something darker?", "less romance") | 2 | 2 | 2 | **2** | OUT |
| User accounts / watch history | 1 | 1 | 3 | **-1** | OUT |
| Genre browsing / manual filters | 1 | 1 | 1 | **1** | OUT |
| Trailers embedded | 1 | 1 | 2 | **0** | OUT |
| Share rec list with friends | 1 | 1 | 2 | **0** | OUT |

### MVP (Score ≥ 3)
- Natural language mood → top 5 movie recommendations
- "Where to watch" (streaming platforms per movie, via TMDB Watch Providers)
- Movie cards with poster, TMDB rating, runtime, synopsis
- "Why this matches your mood" — 1-line explanation per recommendation

### Out of Scope (Score < 3)
- TV series support (v1.1 — TMDB has equivalent TV endpoints, effort = moderate)
- Group mode (v1.1 — high value but doubles prompt complexity)
- Country/region selector (v1 defaults to US — Mehdi is in Austin)
- Conversational follow-up ("darker", "less romance")
- User accounts / history
- Genre browsing
- Trailers
- Sharing

## Success Metrics

> Mood is subjective — but we decompose it into measurable components.

**3 evaluation levels (objective → subjective):**

| Level | Metric | Target | How to Test | Eval Gate |
|-------|--------|--------|-------------|-----------|
| **1. Filter Accuracy** | LLM correctly translates mood → TMDB filters | 100% of explicit constraints parsed correctly | Assert on JSON output: "funny" → genre 35, "< 2h" → runtime_lte 120, "Netflix" → provider 8 | BLOCKING |
| **2. Constraint Compliance** | Returned movies respect all stated filters | 100% of movies comply | Check each movie: runtime ≤ limit? On stated platform? Correct genre? | BLOCKING |
| **3. Recommendation Relevance** | Movies plausibly match the mood (Precision@5) | ≥ 3/5 recs rated 2+ (on 1-3 scale) | Human rates 10 mood queries × 5 recs: 3=clear match, 2=partial, 1=miss | QUALITY |
| **Response time** | End-to-end latency | < 5 seconds | Time from submit to 5 cards displayed | SIGNAL |
| **Usability** | Non-tech person gets useful recs | Zero confusion on main flow | 2-3 people use it cold | QUALITY |

## Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Movie data | TMDB API (free, 40 req/s, 900K+ movies) | Free with attribution. Discover endpoint has 30+ filters. Watch Providers endpoint shows streaming availability. No licensing blocker for non-commercial. |
| LLM | GPT-4o-mini (OpenAI) | ~20x cheaper than Sonnet. Sufficient for mood → filter translation. Same provider as DocuQuery (simplified billing). |
| LLM role | TWO calls: (1) mood → structured filters, (2) rank results + explain | Separation of concerns. Call 1 = structured output (JSON filters). Call 2 = creative (natural language explanations). |
| Backend | FastAPI (Python) | Same as DocuQuery. Proven stack. FastAPI from day 1 (lesson learned: skip Streamlit detour). |
| Frontend | Lovable (React + Tailwind) | Same as DocuQuery. FastAPI backend + Lovable frontend from the start. |
| Deploy | Render (backend) + Lovable (frontend) | Same infra as DocuQuery. Known, proven, $7/mo. |
| Default region | US (country code for watch providers) | Mehdi is in Austin. MVP = US. Region selector is v1.1. |
| Top K results | Fetch 20 from TMDB, LLM ranks top 5 | 20 = enough variety for quality ranking. 5 = digestible for user. LLM explains WHY for each. |
| Image CDN | TMDB image API (`image.tmdb.org/t/p/w500/`) | Free, fast, multiple sizes. Posters at w342 (cards) and w500 (detail). |

## Architecture Flow

```
USER: "Something funny and light, under 2h, Netflix or Disney+"
                    │
                    ▼
         ┌──────────────────┐
         │  GPT-4o-mini     │  CALL 1: Mood → Filters
         │  (structured)    │  → { genres: [35], runtime_lte: 120,
         └────────┬─────────┘    providers: [8, 337], sort: popularity }
                  │
                  ▼
         ┌──────────────────┐
         │  TMDB Discover   │  GET /discover/movie?with_genres=35
         │  API             │  &with_runtime.lte=120
         └────────┬─────────┘  &with_watch_providers=8|337
                  │              &vote_average.gte=6.5
                  │              → 20 movies with metadata
                  ▼
         ┌──────────────────┐
         │  TMDB Watch      │  GET /movie/{id}/watch/providers
         │  Providers API   │  → streaming availability per movie
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  GPT-4o-mini     │  CALL 2: Rank 20 → Top 5 + explain WHY
         │  (creative)      │  → "Light comedy, 98 min, perfect for
         └────────┬─────────┘    unwinding. Strong reviews (7.4/10)."
                  │
                  ▼
         ┌──────────────────┐
         │  Frontend        │  5 movie cards with:
         │  (Lovable)       │  poster, title, rating, runtime,
         └──────────────────┘  "why", streaming badges
```

## Open Questions

- **Mood → filter mapping quality:** Can GPT-4o-mini reliably translate subjective moods ("cozy", "mind-bending", "date night") into the right combination of TMDB genre IDs, rating thresholds, and runtime limits? This is the Walking Skeleton test.
- **TMDB Discover API coverage:** How well does the Discover endpoint cover niche mood combinations? If the user asks for "Korean thriller, slow burn, under-the-radar" — does TMDB have enough filter granularity, or do we need keyword search as fallback?
- **Watch Provider freshness:** TMDB's watch provider data comes from JustWatch. How up-to-date is it? A movie showing "available on Netflix" that isn't actually on Netflix would destroy trust.
