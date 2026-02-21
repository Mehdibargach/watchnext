# WatchNext

## What this project is
Movie recommendation engine powered by mood. Tell it what you feel like watching, it finds the best picks across all your streaming platforms.

## Architecture Decisions (from 1-Pager)
- **Data source**: TMDB API (free, 40 req/s, 900K+ movies, watch providers by country)
- **LLM**: GPT-4o-mini (OpenAI) — two calls: (1) mood → structured filters, (2) rank + explain
- **Backend**: FastAPI (Python) — same stack as DocuQuery
- **Frontend**: Lovable (React + Tailwind) — same as DocuQuery
- **Deploy**: Render (backend $7/mo) + Lovable (frontend)
- **Default region**: US (watch providers)
- **Top K**: Fetch 20 from TMDB, LLM ranks top 5 with explanations

## Current Phase
BUILD — Walking Skeleton DONE (5/5 PASS). Scope 1 DONE (6/6 PASS, PM valide). Next: Scope 2 (deploy Render + frontend Lovable).

## Riskiest Assumption
"An LLM can translate a vague mood description into TMDB Discover API filters that return movies the user actually wants to watch."

## Anti-patterns
- NEVER decompose into backend → frontend → integration
- Always vertical slices (Walking Skeleton → Scopes)

## Build Rules (from DocuQuery — applies to all projects)
1. Micro-test = gate, pas une etape. Code → Micro-test PASS → Doc → Commit.
2. Le gameplan fait autorite sur les donnees de test.
3. Checklist qualite walkthrough — audience non-technique (analogies AVANT concepts, zero jargon sans explication, ton conversationnel, FR + EN).
4. Pas de mode batch.
5. Test first, code if needed.
6. UX dans les prompts — no jargon leaked to user.
7. PM Validation Gate — apres micro-tests PASS, AVANT commit : donner les instructions de test au PM, attendre son GO explicite. Zero commit sans feu vert PM.
