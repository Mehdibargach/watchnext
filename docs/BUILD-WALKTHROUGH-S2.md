# BUILD Walkthrough — Scope 2: Deploy + Frontend Lovable

> WatchNext — Scope 2
> Date: 2026-02-21/22

---

## What we built

Scope 2 transforms WatchNext from a local terminal tool into a live product anyone can use. Two things happened: (1) the backend went online on Render, and (2) a full React/Tailwind frontend was built in Lovable.

Think of it like a restaurant: Scope 1 perfected the kitchen (the recommendation pipeline). Scope 2 opened the dining room (the frontend) and put the restaurant on Google Maps (the deploy).

---

## The deploy story

### Backend on Render

The FastAPI backend needed two files to go live:

- **Procfile** — tells Render how to start the server: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- **render.yaml** — the blueprint: Python 3.11, starter plan, env vars for API keys

One surprise: the first deployment worked (`/health` returned OK) but `/recommend` returned 500. Why? The OPENAI_API_KEY environment variable wasn't configured in Render's dashboard. A classic "works on my machine" moment.

Then a second surprise: the OpenAI account had run out of credits. The error was `429 insufficient_quota` — but the backend returned a generic "Internal Server Error" with no details. We added a try/catch that returns a clear `502` with the error type. Lesson: **always surface error context to the frontend, even in production.**

### CORS

The backend needed to accept requests from Lovable's preview domains. We used a regex pattern:

```python
allow_origin_regex=r"https://.*\.(lovableproject\.com|lovable\.app)"
```

This covers all Lovable preview URLs without listing each one individually. Plus `localhost:5173` for local Lovable development.

---

## The frontend story

### Design philosophy: "Linear meets cinema"

The UI follows one principle: **the movie posters are the color.** Everything else is monochrome.

- Background: deep navy (#0B0F1A), not pure black — adds depth
- Cards and surfaces: slightly lighter (#151B2B) with subtle borders
- Accent: indigo (#6366F1), used only for the search button and focus states
- Text: white for titles, muted gray for metadata

The posters float on the dark background with subtle shadows. When you look at the results, your eyes go straight to the movies — not the chrome.

### The poster wall

The empty state has a wall of real movie poster thumbnails (Marty Supreme, Zootopia 2, Oppenheimer, Dune 2, Deadpool & Wolverine, Inside Out 2...) faded to near-invisibility behind the search area. Like the posters you see when you walk into a cinema lobby — atmospheric, not distracting.

### Layouts that work

We went through three layout iterations:

1. **3+2 grid** (first attempt) — 3 cards on top, 2 centered below. Looked terrible. The second row had a visual hole.
2. **5-column grid** (improvement) — All 5 in one row. Perfect on desktop.
3. **Final layout** — Desktop: 5 posters in a horizontal row, click to open detail view. Mobile: 2-column grid with bottom sheet for details.

The detail view is split: poster on the left (the star), info on the right (title, rating, runtime, year, "why this movie", streaming badges). On mobile, it's a bottom sheet that slides up — a standard pattern from Netflix and Disney+.

### The loading experience

Users wait 15-20 seconds for results (two LLM calls + TMDB enrichment). Instead of a boring spinner, we built:

1. **Lottie popcorn animation** — matches the popcorn icon in the header, creates brand consistency
2. **Indigo progress bar** — thin, fills to 95% over 20 seconds, slows down near the end
3. **Movie fun facts** — rotate every 4 seconds: "The word 'mafia' is never said in The Godfather." Keeps users engaged during the wait.

### Lovable prompting method

We used 3 iterative prompts — same method as DocuQuery:

1. **Prompt 1** — Structure + API integration + base layout
2. **Prompt 2** — Loading experience (Lottie + progress + facts) + hover states
3. **Prompt 3** — Animations + error states + branding

Key learning: Lovable works best when you describe what exists and what to change, not when you ask it to rebuild from scratch. The best prompts started with "This is what exists (DO NOT rebuild)" + "Apply these specific changes."

---

## What we learned

### 1. Error messages matter in production

A generic "Internal Server Error" tells the frontend nothing. After adding proper error handling, the frontend could show "Couldn't reach our movie engine" instead of "Something went wrong." Small change, big UX difference.

### 2. Design iteration > design specification

The original Lovable prompts described a 3+2 grid, genre pills, and a coral accent color. All three were wrong. The final product has a horizontal poster row, no genre pills, and indigo accent. The design evolved through screenshots, feedback, and iteration — not from a spec written upfront.

### 3. Movie posters ARE the design system

The single best design decision was making the UI invisible. Dark monochrome everywhere, posters provide all the visual interest. This means the app looks beautiful regardless of which movies are shown — because the posters do the work.

### 4. Loading is a feature, not a wait

15-20 seconds of loading could kill the experience. Instead, the fun facts turn the wait into entertainment. Users read about The Godfather while waiting for their recommendations. The loading screen became one of the best parts of the app.

---

## Micro-tests — 8/8 PASS

| # | Type | Result | Verdict |
|---|------|--------|---------|
| S2-1 | Deploy | Health endpoint responds 200 in 0.3s | **PASS** |
| S2-2 | E2E | Full pipeline Lovable → Render → TMDB → response | **PASS** |
| S2-3 | Posters | 5/5 posters load correctly | **PASS** |
| S2-4 | Streaming | Logos visible in detail view | **PASS** |
| S2-5 | Loading | Lottie + progress bar + fun facts | **PASS** |
| S2-6 | Empty state | Headline + chips + input + poster wall | **PASS** |
| S2-7 | Mobile | 2-col grid + bottom sheet | **PASS** |
| S2-8 | Usability | Flow complet sans aide | **PASS** |

---

## Files changed

| File | Action | Why |
|------|--------|-----|
| `Procfile` | Created | Render start command |
| `render.yaml` | Created | Render blueprint (Python 3.11, env vars) |
| `api.py` | Modified | Added error handling (try/catch → 502) |
| `docs/LOVABLE-PROMPTS.md` | Created | 3 iterative Lovable prompts |
| `docs/reference/DOCUQUERY-*.md` | Created | Design system reference from DocuQuery |
| Frontend (Lovable) | Created | Full React/Tailwind app |

---

## What's next

BUILD is complete. All 3 slices pass their gates:
- Walking Skeleton: 5/5
- Scope 1: 6/6
- Scope 2: 8/8

Next step: **EVALUATE** — 10 mood queries across the eval framework to measure recommendation quality, latency, and UX at scale.
