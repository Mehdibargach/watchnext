# BUILD LOG — WatchNext

| Date | Phase | What | Details |
|------|-------|------|---------|
| 2026-02-19 | FRAME | 1-Pager written | Problem: decision fatigue + platform-locked recs. Solution: mood → TMDB filters → 5 movies. Riskiest Assumption: "LLM can translate vague mood into useful TMDB filters." 3-level eval framework defined: Filter Accuracy (deterministic), Constraint Compliance (deterministic), Rec Relevance (semi-subjective). |
| 2026-02-19 | FRAME | BUILD Gameplan written | Walking Skeleton (5 micro-tests) → Scope 1 (watch providers + ranking + explanations, 6 tests) → Scope 2 (deploy + Lovable, 8 tests). DOR/DOD per slice. |
| 2026-02-19 | BUILD | Walking Skeleton — code | Created `api.py` (FastAPI, /health + /recommend), `core/mood_parser.py` (GPT-4o-mini function calling → structured TMDB filters), `core/tmdb_client.py` (Discover + movie details + enrichment). |
| 2026-02-19 | BUILD | Walking Skeleton — micro-tests | **5/5 PASS.** All moods correctly translated to filters. Comedy (35), Horror (27), Action (28), Romance (10749), Sci-Fi\|Thriller (878\|53). Constraints (runtime, sort) respected. Avg latency 2.5s. Skeleton Check: Riskiest Assumption HOLDS. |
| 2026-02-21 | BUILD | Scope 1 — full pipeline | Added watch providers enrichment, GPT-4o-mini ranking (20→5) with "why this matches" explanations, poster URLs. Function calling for structured filters. **6/6 PASS.** |
| 2026-02-21 | BUILD | Scope 2 — deploy backend | Created Procfile + render.yaml. Deployed FastAPI on Render (Python 3.11). Fixed: OpenAI quota error (429), added error handling (try/catch → 502 with message). Backend URL: `https://watchnext-flta.onrender.com` |
| 2026-02-21 | BUILD | Scope 2 — Lovable frontend | Built React/Tailwind frontend in Lovable. 3 prompts iteratifs. Empty state: poster wall background + mood chips. Results: 5 posters horizontal (desktop), 2-col grid (mobile). Detail view: poster + info + streaming badges (desktop: full page, mobile: bottom sheet). Loading: Lottie popcorn + progress bar + movie fun facts. Design: Linear meets cinema — dark monochrome UI, indigo accent, posters = the color. |
| 2026-02-22 | BUILD | Scope 2 — micro-tests | **8/8 PASS.** Deploy OK, E2E OK, posters OK, streaming badges OK, loading OK, empty state OK, mobile OK, usability OK. Produit demo-ready. |
