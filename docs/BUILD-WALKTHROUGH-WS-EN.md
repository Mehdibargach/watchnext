# BUILD Walkthrough — Walking Skeleton

> WatchNext: tell it how you feel, it recommends 5 movies.

---

## The problem we're solving

It's Friday night. You open Netflix. You scroll. 10 minutes go by. You open Disney+. You scroll some more. You end up rewatching something you've already seen. We've all been there.

The problem is that streaming platforms recommend based on what you've **already watched**. Not based on how you **feel right now**. You're exhausted after a long day? Netflix doesn't know. You want something that'll take your mind off the world for 2 hours? The algorithm doesn't care — it shows you the same carousel as yesterday.

WatchNext solves this. You describe your mood in plain language — "I'm tired, I want something funny and light" — and it gives you 5 movies that fit.

---

## What's a Walking Skeleton?

Before building the full app, we start with the **Walking Skeleton**. It's a term from Alistair Cockburn (a pioneer in software development). The idea is simple:

**Build the thinnest possible version that runs through the entire system end to end.**

Imagine you want to open a restaurant. Before signing the lease, hiring 10 waiters, and printing the menus, you run a test: you cook ONE dish, serve it to ONE customer, see if they like it. If the dish is good, you keep going. If the customer makes a face, you know before spending $100,000.

For WatchNext, the Walking Skeleton is this:

> A mood goes in as text → 5 movies come out.

No user interface. No "where to watch." No pretty cards with posters. Just the core of the system: can an AI turn a vague mood into relevant movie recommendations?

That's our **Riskiest Assumption**. If it doesn't work, nothing else matters. If it works, we build everything else on top.

---

## How it works — the big picture

The system works in 3 steps. To understand it, think of a translator who specializes in movies.

**Step 1 — The translator.** You say "I'm tired, something funny and short." The translator (an AI, GPT-4o-mini) understands you want: genre = Comedy, duration = under 2 hours, and translates that into **search criteria** the movie database understands.

**Step 2 — The catalog.** Those criteria are sent to **TMDB** (The Movie Database) — a massive public database with over 900,000 movies. It's like handing a criteria sheet to a bookseller: "I want a comedy, not too long, well-rated." The bookseller comes back with 5 books that match.

**Step 3 — The enrichment.** The movies come back with basic info (title, rating). But important details are missing — like the exact runtime or the movie poster. So we make an extra round trip for each movie to fill in the complete card.

Here's the full flow:

```
You: "I'm tired, something funny and short"
         │
         ▼
    ┌─────────────┐
    │  Translator  │  ← GPT-4o-mini (OpenAI's AI)
    │  (mood_parser)│     understands your mood
    └──────┬──────┘     and translates it to criteria
           │
           │  criteria: genre=Comedy, runtime<120min
           ▼
    ┌─────────────┐
    │   Catalog    │  ← TMDB (900K+ movie database)
    │  (tmdb_client)│    finds movies that match
    └──────┬──────┘
           │
           │  5 movies with title, rating, poster, runtime
           ▼
    Response: Zootopia 2, SpongeBob, Shrek...
```

**3 files, 3 responsibilities:**
- `mood_parser.py` — the translator: understands your mood, converts it to criteria
- `tmdb_client.py` — the catalog: queries the movie database with those criteria
- `api.py` — the conductor: receives your request, calls the translator then the catalog, sends back the result

---

## The translator: how the AI understands your mood

This is the centerpiece. How do you get an AI to understand "I'm tired, something funny" and turn it into something usable?

### The free-form translation problem

If you ask an AI "give me search criteria for a short comedy," it could respond in any format:
- `"genre: comedy, duration: short"` (free text, unusable by a program)
- `{"genre": "Comedy", "max_runtime": 120}` (JSON, but the field names are made up)
- `Look for funny movies under 2 hours` (a sentence, completely unusable)

It's like asking a translator to fill out a government form — without giving them the form. They'll improvise, and every time the result will be different.

### The solution: the pre-defined form

We use a technique from OpenAI called **function calling**. The idea: instead of asking the AI to generate free text, we give it a **form with specific boxes to fill in**.

Think of a Netflix search form with checkboxes:
- Genre: [ ] Action [ ] Comedy [ ] Horror [ ] Romance ...
- Minimum rating: [____] / 10
- Max runtime: [____] minutes
- Sort by: ( ) Popularity ( ) Highest rated ( ) Most recent

The AI receives this form and can only fill in the boxes. It can't invent new boxes or respond in free text. This guarantees the output is always in the format the catalog expects.

Here are the form's boxes:

| Box | What it contains | Example |
|-----|-----------------|---------|
| Genre(s) | TMDB genre number(s) | `35` = Comedy, `27` = Horror |
| Minimum rating | TMDB rating out of 10 | `6.0` (default, to filter out bad movies) |
| Runtime min/max | In minutes | `90` min, `120` max |
| Sort by | Sorting criteria | Popularity, highest rating, most recent |
| Time period | Release dates | `2020-01-01` to `2026-12-31` for "recent movies" |

### Why numbers for genres?

TMDB doesn't use the words "Comedy" or "Horror." It uses numbers: Comedy = 35, Horror = 27, Science Fiction = 878. It's like zip codes — you can't write "New York," you have to write "10001."

We give the lookup table directly to the AI in its instructions:

```
Action: 28, Comedy: 35, Horror: 27, Romance: 10749,
Science Fiction: 878, Thriller: 53, Drama: 18...
```

So when you say "something funny," the AI knows that's code `35`.

### A concrete example

You: **"Something mind-bending like Inception"**

The AI understands:
- "mind-bending" → Science Fiction or Thriller
- "like Inception" → Inception is a Sci-Fi (878) and Thriller (53) movie
- No mention of duration → leave that box empty
- No mention of "recent" → leave the dates empty

Form result: `genre = 878|53` (Sci-Fi OR Thriller), `minimum rating = 6.0`, `sort = popularity`

The `|` between numbers means "OR" — we want Sci-Fi **or** Thriller movies, not necessarily both at once.

---

## The catalog: how TMDB finds the movies

TMDB (The Movie Database) is a free, open database maintained by volunteers. It contains over 900,000 movies with their details: title, genres, rating, runtime, poster, synopsis. It's the same database that apps like JustWatch and Letterboxd use behind the scenes.

We use a specific TMDB access point called **Discover**. It's like an advanced search engine: you give it criteria (genre, minimum rating, runtime), it returns the movies that match.

### The incomplete card problem

Discover returns movies with basic info: title, rating, genres. But it doesn't return the **runtime** or the **high-quality poster**. That's a problem, because if you said "something short," we need to verify the movies are under 2 hours.

The solution: for each movie, we make an extra call to get the complete card (runtime, poster, full synopsis). It's like the bookseller first giving you a list of 5 titles, then going to the shelf to get each book so you can see the cover and the summary.

In total, for a request with 5 movies, we make 6 calls to TMDB:
- 1 Discover call (the movie list)
- 5 Detail calls (one per movie, to complete the card)

It's fast: TMDB allows 40 calls per second, so these 6 calls take under half a second.

---

## The conductor: how it all fits together

`api.py` is the conductor. It's the entry point — the one that receives your request and coordinates the work.

The flow is linear:

1. You send your mood: `"Something funny and light, under 2 hours"`
2. The conductor calls the translator → receives the criteria
3. The conductor calls the catalog with those criteria → receives 5 movies
4. The conductor enriches each movie with its complete card
5. The conductor sends back everything with the response time

We use **FastAPI**, a Python framework for creating web access points. It's the equivalent of a restaurant host: it receives orders (requests) and routes them to the kitchen (the modules).

---

## The decisions we made (and why)

### Why GPT-4o-mini and not a more powerful model?

GPT-4o-mini is OpenAI's "small, fast model." It costs about $0.15 per million input words — roughly 20 times cheaper than the bigger models. For our use case — understanding a mood and filling in a 7-box form — it's more than enough. No need for a cannon to kill a fly.

### Why TMDB and not IMDB?

IMDB doesn't have a free public API. TMDB is free, well-documented, and offers a catalog of 900K+ movies with streaming info (which platform each movie is available on). Plus, TMDB is used by consumer apps like JustWatch — so it's reliable and up to date.

### Why no frontend for the Skeleton?

The Walking Skeleton's goal isn't to look pretty. It's to test the riskiest assumption as fast as possible. The assumption here: "an AI can turn a vague mood into relevant recommendations." You don't need a user interface to test that — a simple command-line call is enough.

If the assumption doesn't hold, we'd have wasted zero time on design. If it holds, we build the interface on top.

---

## What went wrong (and what we learned)

### My Little Pony in the action results

When we tested "Epic action movie, well-rated," the system returned "My Little Pony: Equestria Girls - Spring Breakdown" as a well-rated action movie. Why? Because TMDB classifies it under the "Action" category and it has an 8.46/10 rating.

The system did exactly what we asked: find well-rated action movies. The problem is it doesn't **understand** what an "epic action movie" is — it just applies mechanical filters.

**What we learned:** Filters alone aren't enough. You need a second step where the AI **re-examines** the results and eliminates the absurdities. That's exactly what we'll build in Scope 1: an intelligent re-ranking module.

### The AI finds a better path than expected

For "Epic action movie, well-rated," we expected the AI to set a minimum rating of 7/10. It did something different: it set the minimum at 6, but sorted by "highest rated first." Result? The top 5 movies all had ratings above 8.4 — better than what we expected.

**What we learned:** The AI doesn't always follow the path you predict, but the result can be better. This is typical behavior in AI-based systems: you define the "what" (find the best action movies), the AI chooses the "how" (sort by rating rather than filter by threshold).

---

## Test results

We defined 5 tests before writing any code. Each test takes a different mood and verifies that the generated filters and returned movies are consistent.

| # | Mood tested | What we expected | What the AI generated | Movies OK? | Time | Verdict |
|---|-----------|-----------------|---------------------|-----------|------|---------|
| 1 | "Funny and light, under 2 hours" | Comedy + runtime < 120 min | Comedy (35) + max 120 min | 5/5 comedies, all < 120 min | 3.0s | **PASS** |
| 2 | "Scary movie for Halloween" | Horror | Horror (27) | 5/5 horror movies | 2.4s | **PASS** |
| 3 | "Epic action, well-rated" | Action + rating > 7.0 | Action (28) + sort by rating | 5/5 action, all > 8.4 | 3.0s | **PASS** |
| 4 | "Romantic date night" | Romance | Romance (10749) | 5/5 romance movies | 2.2s | **PASS** |
| 5 | "Mind-bending like Inception" | Sci-Fi or Thriller | Sci-Fi\|Thriller (878\|53) | 5/5 sci-fi/thriller | 2.1s | **PASS** |

**Gate: 5/5 PASS**

---

## Skeleton Check — does the assumption hold?

**Yes.** The AI reliably translates moods into search criteria. Key findings:

1. **Genre mapping works.** "Funny" → Comedy, "scary" → Horror, "like Inception" → Sci-Fi + Thriller. Zero errors on genre codes.

2. **Constraints are respected.** "Under 2 hours" → max runtime 120 min. "Recent" → movies since 2020. The AI understands implicit constraints.

3. **Movie references work.** "Like Inception" → the AI infers the movie's genres without us programming anything special. It knows movies.

4. **It's fast.** 2 to 3 seconds per request. Well within acceptable user experience (our target was 5 seconds max).

**Conclusion: we continue.** The Riskiest Assumption is validated. We move to Scope 1 to add streaming platforms, intelligent movie ranking, and personalized explanations.
