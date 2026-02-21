# BUILD Walkthrough — Scope 1: The full pipeline

> We go from "5 raw movies" to "5 hand-picked movies with explanations and streaming platforms."

---

## What we had, and what was missing

The Walking Skeleton proved the AI can translate a mood into search criteria. But the experience was still rough. Three big gaps:

**1. No "where to watch."** The system tells you "watch Parasite" but doesn't tell you if it's on Netflix, Disney+, or nowhere. You have to go look it up yourself. That's exactly the problem we're trying to solve.

**2. My Little Pony.** The Walking Skeleton returned a My Little Pony cartoon as an "epic action movie." Mechanical filters aren't enough — we need an AI to re-examine the results and eliminate the absurdities.

**3. No explanation.** The system tells you "watch The Dark Knight" but doesn't tell you **why** it matches your mood. It's like a bookseller handing you a book without saying a word. You want to know: "why this one?"

Scope 1 solves all three.

---

## The new architecture — 4 steps instead of 3

The Walking Skeleton had 3 steps: Translator → Catalog → Enrichment. Scope 1 adds a fourth: the **Curator**.

Imagine you walk into a bookstore and say "I want something funny for tonight, available in paperback."

1. **The translator** understands you want: humor, paperback format.
2. **The catalog** pulls 20 books that match the criteria.
3. **The enrichment** fills in the details (summary, cover, store availability).
4. **The curator** — that's the new part — examines all 20 books, picks the 5 best ones for you, and tells you **why** each one will appeal to you: "this one is Monty Python-style absurd humor," "this one is more feel-good, perfect if you're tired."

Here's the new flow:

```
You: "something funny on Netflix"
         │
         ▼
    ┌─────────────┐
    │  Translator  │  ← understands your mood + platform
    └──────┬──────┘
           │  criteria: genre=Comedy, platform=Netflix
           ▼
    ┌─────────────┐
    │   Catalog    │  ← searches 20 movies (instead of 5)
    └──────┬──────┘
           │  20 raw movies
           ▼
    ┌─────────────┐
    │  Enrichment  │ ← fills each card + streaming platforms
    └──────┬──────┘
           │  20 complete movies with Netflix/Disney+/etc.
           ▼
    ┌─────────────┐
    │   Curator    │  ← AI picks the 5 best + explains
    └──────┬──────┘     why each matches your mood
           │
           │  5 ranked movies with "why this movie"
           ▼
    Final response
```

Why 20 movies instead of 5? Because the curator needs choices. If you give it 5 movies, it can't really "choose" — it takes everything. With 20, it can eliminate the My Little Ponies, favor movies that truly fit the mood, and keep only the best.

---

## Change 1: "Where can I watch this?"

### The problem

You say "a funny movie on Netflix." The Walking Skeleton didn't understand "on Netflix" — it ignored that part. And even when it found movies, it didn't know which streaming platforms they were available on.

### The two-part solution

**Part A — The translator learns about platforms.** We add a box to the AI's form: "streaming platform." Like genres, each platform has a number:

| Platform | TMDB Number |
|----------|-------------|
| Netflix | 8 |
| Amazon Prime | 9 |
| Disney+ | 337 |
| Hulu | 15 |
| Max (HBO) | 1899 |
| Apple TV+ | 350 |
| Paramount+ | 531 |

When you say "on Netflix," the AI fills in `platform = 8`. TMDB's catalog then only returns movies available on Netflix in the US.

**Part B — Enrichment includes platforms.** For each movie, we now make an extra call to TMDB to find out which streaming platforms it's available on. TMDB uses data from **JustWatch** (the site that aggregates all streaming catalogs).

The result: each movie comes back with its platform list, including each service's logo. Netflix, Disney+, Amazon Prime — it's all there.

### What it looks like in practice

You: **"Comedy on Netflix"**

The translator generates: `genre = Comedy (35), platform = Netflix (8)`

The catalog finds comedies available on Netflix and returns:
- "Glass Onion: A Knives Out Mystery" — Netflix
- "Don't Look Up" — Netflix
- "The Wolf of Wall Street" — Netflix
- "Forrest Gump" — Netflix + Amazon Prime + Paramount+
- "KPop Demon Hunters" — Netflix

Each movie arrives with the Netflix logo and any other platforms it's also available on.

---

## Change 2: The curator eliminates the absurdities

### The My Little Pony problem

The Walking Skeleton showed a weakness: TMDB filters are **mechanical**. If TMDB classifies My Little Pony under "Action" and that cartoon has a good rating, it passes the filters. The catalog doesn't "understand" that a 44-minute cartoon isn't an "epic action movie."

It's like a Google search that returns technically correct but absurd results. You type "fast jaguar" and get articles about the car AND the animal. Technically correct, practically useless.

### The solution: a second AI that re-examines

We create a new module, the **curator** (`recommender.py`). Its job:

1. Receive all 20 enriched movies + your original mood
2. Read the synopsis, genre, and tone of each movie
3. Eliminate those that clearly don't fit (My Little Pony for "epic action")
4. Choose the 5 best and rank them from most to least relevant
5. Write a personalized explanation for each one

The curator uses the same technique as the translator (function calling) to guarantee a structured format. It receives a form with 5 slots to fill: for each, the movie's ID and the explanation.

### How the curator "chooses"

We give it precise instructions:

- **Prioritize mood coherence.** "Light and funny for a tired couple" → favor soft, funny movies, not dark comedies or satires.
- **If the user mentions a platform,** favor movies available there.
- **Avoid absurdities.** A children's cartoon isn't an "intense thriller night," even if TMDB classifies it as Thriller.
- **Write as if recommending to a friend.** No technical jargon. Not "based on TMDB filters." Just: "this movie is perfect for you because..."
- **Write in the same language as the user.** If the mood is in French, the explanations are in French. In English, respond in English.

### A concrete example

You: **"Light and funny for a tired couple"**

The 20 candidates include a mix of comedies: cartoons, romantic comedies, satires, dark comedies.

The curator picks:
1. **Zootopia** — "A fun animated film full of humor and heart, perfect for a light evening. The story is engaging and the characters are lovable — ideal for winding down after a long day."
2. **Shrek** — "Signature humor and charming characters for a light-hearted good time — exactly what a tired couple needs to take their minds off things."
3. **The SpongeBob Movie** — "A whimsical adventure in a colorful underwater world. Silly, good-natured humor — zero stress."
4. **Eternity** — "A film that blends romance and humor in a light reflection on life choices. Touching without being heavy."
5. **The Naked Gun** — "Absurd comedy with non-stop gags. Guaranteed to make you laugh."

Notice the difference from the Walking Skeleton: movies are sorted by relevance, ultra-childish cartoons no longer dominate, and every recommendation tells you **why it's a match**.

---

## Change 3: The form gets richer

Let's recap the changes to the AI's form:

| What already existed (WS) | What we added (Scope 1) |
|---------------------------|------------------------|
| Genre(s) | Streaming platform |
| Minimum rating | |
| Runtime min/max | |
| Sort (popularity, rating, recency) | |
| Time period (recent, 90s...) | |

Just one field added. The bulk of Scope 1's work isn't in the translator — it's in the curator (new) and the enrichment (improved).

---

## What went wrong (and what we learned)

### The curator hallucinated IDs

First test of the curator: we give it 20 movies and ask it to pick 5. It returns 5 picks... but 2 of them have IDs that don't match any movie on the list. The AI **invented** IDs.

This is a known problem with generative AI: they "hallucinate" — they invent data that doesn't exist. In our case, the AI probably mixed up an ID from the list with one from a movie it knows from its training data.

Result: instead of 5 movies, we only got 3 (the other 2 were ignored because they couldn't be found).

**The fix:** Two measures.
1. We add the exact list of valid IDs to the message sent to the AI: "You MUST only use these IDs: [1084242, 991494, 14874, ...]." This reduces the hallucination risk.
2. We add a safety net: if the AI returns fewer than 5 valid movies, we automatically fill in with the top remaining candidates. The system will never return fewer than 5 movies.

After the fix, the "Comedy on Netflix" test returns 5/5 movies, all on Netflix.

### Latency explodes

The Walking Skeleton responded in 2-3 seconds. Scope 1 responds in **17-23 seconds**. Why?

The math:
- 1 GPT call for the translator (~1-2s)
- 1 TMDB Discover call (~0.3s)
- 20 TMDB Detail calls, one per movie (~3s)
- 20 TMDB Watch Provider calls, one per movie (~3s)
- 1 GPT call for the curator (~2-3s)
- **Total: ~45 sequential calls (one after another)**

It's like making 45 phone calls, one at a time, instead of making them simultaneously. The good news: this is an optimization problem, not a design problem. We can parallelize these calls (run them at the same time) in a future scope. For now, 20 seconds is acceptable for a side project — the user waits once, not every second.

---

## Test results

6 tests defined before coding, each verifying a different aspect of the full pipeline.

| # | What we're testing | Mood / test | Result | Verdict |
|---|-------------------|------------|--------|---------|
| 1 | Netflix filter | "Comedy on Netflix" | 5/5 movies on Netflix (Glass Onion, Don't Look Up, Forrest Gump...) | **PASS** |
| 2 | Disney+ filter | "Action on Disney+" | 5/5 movies on Disney+ (Avengers, Avatar, Iron Man...) | **PASS** |
| 3 | Explanations | "Light and funny for a tired couple" | 5/5 explanations reference "light," "tired," "couple" | **PASS** |
| 4 | Ranking quality | "Best thriller of the last 5 years" | #1 rated higher than #5 (Parasite, Joker in top 5) | **PASS** |
| 5 | Movie posters | Any mood | 5/5 movies have a valid poster | **PASS** |
| 6 | Complete card | "A great drama" | 5/5 movies have: title, rating, runtime, synopsis, platforms, explanation | **PASS** |

**Gate: 6/6 PASS**

---

## Before/after: the difference between the Skeleton and Scope 1

To illustrate the progression, here's the same request processed by the Skeleton then by Scope 1:

**Request:** "Comedy on Netflix"

### Walking Skeleton version (before)

```
Filters: genre = Comedy
(no Netflix filter — the platform is ignored)

Movies:
1. Zootopia 2 — Comedy, 7.6/10, 108 min
2. The Wrecking Crew — Comedy, 6.9/10, 124 min
3. SpongeBob Movie — Comedy, 6.7/10, 89 min
4. Try Seventeen — Comedy, 6.2/10, 96 min
5. Send Help — Comedy, 7.1/10, 113 min

No platform. No explanation. No smart ranking.
```

### Scope 1 version (after)

```
Filters: genre = Comedy, platform = Netflix (8)

Movies:
1. KPop Demon Hunters — Netflix
   "A fun blend of humor and fantasy, light and entertaining."
2. Don't Look Up — Netflix
   "A biting satire with an exceptional cast."
3. Glass Onion: A Knives Out Mystery — Netflix
   "A comedic whodunit that blends humor and suspense."
4. Crazy, Stupid, Love. — Netflix
   "A romantic comedy that explores love with charm."
5. Forrest Gump — Netflix
   "A classic with plenty of humor and emotion."

Every movie on Netflix. Every movie explained. Absurdities eliminated.
```

The difference is clear: Scope 1 is a **usable product**. The Walking Skeleton was a proof of concept.

---

## What's left to do

The full pipeline works. But the product still isn't usable by someone who isn't a developer: you need to type commands in a terminal, read raw JSON. Nobody's doing that on a Friday night.

Scope 2 will transform this into a **real product**:
- A website where you type your mood and see 5 beautiful movie cards with posters
- Streaming badges (Netflix logo, Disney+ logo, etc.) on each card
- A modern design that makes you want to use it
- Deployed on the internet — accessible to everyone, not just locally

That's the transformation from "it works in the terminal" to "my wife can use it without instructions."
