# Prompts Lovable — WatchNext Frontend

> 3 prompts iteratifs. Le Prompt 1 documente la base actuelle + ajustements mineurs.
> Les Prompts 2 et 3 sont additifs — ils ameliorent ce qui existe sans le casser.
> Backend URL: https://watchnext-flta.onrender.com

---

## Prompt 1 — Base actuelle + Ajustements

> Ce prompt documente ce que Mehdi a deja construit dans Lovable + les corrections de finition a appliquer.

```
This is WatchNext, a movie recommendation app. The app is already built and working. Apply these specific refinements without breaking anything:

## What already exists (DO NOT rebuild — just adjust)

- Empty state: headline "What are you in the mood for?", search input, 5 mood chips, poster wall background
- Results: 5 movie posters in a horizontal row (desktop), 2-column grid (mobile), rank badges
- Movie detail: click a poster to see detail (desktop: full page with poster left + info right, mobile: bottom sheet)
- Loading: spinner + "Curating your picks..."
- API: POST https://watchnext-flta.onrender.com/recommend with { "mood": "text" }

## Adjustments to apply

### 1. Poster wall — Increase fade
The poster wall on the empty state is too visible and competes with the content. Reduce opacity to 0.08 (from current level). Add a stronger radial gradient overlay: from transparent at center to #0B0F1A at edges, covering 70% of the posters. The posters should be a barely-there atmospheric hint, not distracting.

### 2. Movie detail — Remove genre pills
Remove the genre pills/tags (Action, Crime, Thriller) from the movie detail view. The "why this movie" explanation already conveys the genre naturally. Genre pills add visual noise without value.

### 3. Movie detail — Fix language
Change "Disponible sur" to "Stream on" (the app is in English). Or better: remove the label entirely and just show the streaming platform logos directly. The logos are self-explanatory.

### 4. Results row (desktop) — Consistent info display
On the results row, make sure ALL 5 poster cards show the title and star rating below the poster consistently (not just some of them). Each card in the row should show:
- Poster (with rank badge #1-#5 in top-left)
- Title below (white, font-medium, text-sm, 1 line, truncate if too long)
- Star icon + rating + dot + year (muted gray, text-xs)

On hover: scale(1.02) with transition 200ms ease.

### 5. Movie detail (mobile bottom sheet) — Larger poster
The poster in the mobile bottom sheet is too small. Make it at least 140px wide (keep 2:3 ratio). The poster should be immediately recognizable.

### 6. Streaming logos
Make sure streaming logos in the detail view are ~28px height, rounded-sm (4px), with 8px gap between them. They should be crisp and recognizable.

### 7. Keep everything else exactly as-is
- Keep the popcorn icon in header
- Keep the search bar style
- Keep the chips style and texts
- Keep the horizontal poster row layout (desktop)
- Keep the 2-column grid layout (mobile)
- Keep the detail view layout (poster left + info right on desktop, bottom sheet on mobile)
- Keep all current colors and typography
```

---

## Prompt 2 — Loading Experience + Lottie + Movie Facts

```
Upgrade the loading experience for WatchNext. Users wait 15-20 seconds for results — this is the most important screen to get right.

## Replace the current loading

Replace the current spinner + "Curating your picks..." with a richer experience. The loading screen replaces the main content area while waiting (header stays visible).

Centered vertically, 3 elements stacked with generous spacing:

1. **Lottie animation** — a cinema clapperboard animation, ~80px, looping smoothly. Use the `lottie-react` package. Here is a free Lottie JSON URL you can use: https://lottie.host/embed/fd4e394b-3583-4727-9ef5-39fc835e4885/VxLLBFnehZ.lottie
   If that URL doesn't work or the animation doesn't look good, use any clean, minimal film/cinema Lottie from lottiefiles.com (clapperboard, film reel, or projector — must be line-art style, monochrome/white, NOT cartoon or colorful). The animation should feel premium, not childish.

2. **Progress bar** — thin (2-3px height), max-width 400px, centered. Fills from 0% to ~95% over 20 seconds with an easing curve that slows down after 70% (cubic-bezier or similar). Color: indigo (#6366F1) on a dark track (#1E293B). Rounded ends. Subtle, not distracting.

3. **Movie fun facts** — a single line of text that changes every 4 seconds with a smooth crossfade transition (fade out old text over 400ms, fade in new text over 400ms). Small text (text-sm), muted gray (#94A3B8). These are real cinema facts, randomly shuffled each time:
   - "The word 'mafia' is never said in The Godfather."
   - "The Lion King was almost called 'King of the Jungle'."
   - "Shrek was originally voiced by Chris Farley."
   - "The sound of E.T. walking was made by squishing jelly."
   - "Toy Story was the first fully computer-animated feature film."
   - "The Dark Knight's pencil trick was done in one take."
   - "Psycho was the first American film to show a toilet flushing."
   - "Sean Connery turned down the role of Gandalf in Lord of the Rings."
   - "The carpet in The Shining and the one in Toy Story are the same pattern."
   - "It took 4 years to render the hair in Brave."
   - "Jim Carrey spent 2.5 hours in makeup every day for the Grinch."
   - "The snow in The Wizard of Oz was made of asbestos."

ONLY these 3 elements. No step indicators ("Analyzing mood...", "Searching..."). No extra text. No "Curating your picks...". Clean.

## After results — Search again

When results are displayed, the user should be able to search again easily:
- Show the search input above the results (same position as the results page currently has it)
- Placeholder: "Try another mood..."
- Submitting a new search shows the loading screen again, then new results replace the old ones

## Card hover refinement

When hovering a movie poster card in the results row:
- Scale: 1.03 (slightly more than 1.02 for a noticeable but elegant effect)
- The card rises slightly: transform translateY(-4px)
- Border brightens from #1E293B to #334155
- Transition: all 200ms ease
- Other cards in the row do NOT dim or change — only the hovered card transforms

## Keep everything else
Do not change the empty state, poster wall, detail views, mobile layouts, or any other existing functionality.
```

---

## Prompt 3 — Polish + Animations + Error States + Branding

```
Final polish for WatchNext. These are refinements, not redesigns — do not break anything that currently works.

## Results animation

When movie results appear (after loading), the 5 poster cards should animate in with a staggered entrance:
- Card 1 appears at 0ms
- Card 2 at 80ms
- Card 3 at 160ms
- Card 4 at 240ms
- Card 5 at 320ms
Each card: fade from opacity 0 to 1 + translate up from 20px to 0. Duration: 400ms. Easing: ease-out.
This creates a smooth "wave" effect as the results appear.

## Detail view animation

- Desktop: the detail view should fade in (opacity 0 to 1, 200ms ease)
- Mobile: the bottom sheet should slide up smoothly from below (already likely works, just ensure it's smooth)

## Error states

Handle these 3 error scenarios with centered, clean error cards (same dark style as the app):

1. **API error (500/502)**: Show message "Couldn't reach our movie engine. Try again in a moment." + an indigo "Try Again" button below.
2. **Zero results** (movies array is empty): Show "No movies found for this mood. Try a different description!" + "Try Again" button.
3. **Network timeout** (no response after 45 seconds): Show "This is taking longer than usual. Please try again." + "Try Again" button.

All error cards: centered vertically, max-width 400px, muted gray text (#94A3B8), no icons, no illustrations. Clean and minimal. The "Try Again" button returns to the empty state (with input cleared).

IMPORTANT: Do NOT show a timeout error before 45 seconds. The API legitimately takes 15-20 seconds (sometimes up to 30 on cold start). Only show timeout after 45 seconds.

## Small details

- **Latency badge**: After results load, show "Found 5 movies in 18.2s" as small muted text (#64748B, text-xs) below the search bar on the results page. Use the `latency` value from the API response and `count` for the number.
- **Poster fallback**: If a movie's `poster_url` is null or the image fails to load, show the movie title centered on a dark gradient card (#151B2B to #0F172A), same 2:3 aspect ratio as other posters.
- **Image alt text**: All poster images should have alt text: "{movie title} ({year}) poster".
- **Page title**: Set the HTML page title to "WatchNext — Movie Recommendations by Mood".
- **Smooth scroll**: When results appear, smoothly scroll to show them (if needed on smaller viewports).

## Branding

Add a small footer text at the very bottom of the page: "Built with The Builder PM Method" in very muted gray (#475569, text-xs). Static text, not a link. It should only be visible when scrolled to the absolute bottom — it's subtle branding, not a feature.

## What NOT to change

- Do NOT add a light mode toggle. Dark only.
- Do NOT add genre pills to the results cards (they're OK in the detail view... actually, remove them from the detail view too if they're still there).
- Do NOT add emojis anywhere in the UI.
- Do NOT change the poster wall, empty state layout, results layout, or detail view layout.
- Do NOT change any colors or typography that currently works.
```

---

## Notes pour Mehdi

**Sequence :**
1. Prompt 1 → ajustements mineurs sur ta base actuelle (poster wall fade, genre pills, langue, consistency)
2. Prompt 2 → upgrade loading (Lottie + progress bar + movie facts) + card hover
3. Prompt 3 → animations d'entree + error states + branding footer + details

**Si Lovable ne trouve pas le Lottie :**
- Va sur lottiefiles.com, cherche "clapperboard" ou "film reel"
- Telecharge le JSON
- Upload-le dans le projet Lovable
- Dis a Lovable d'utiliser le fichier local

**Ce qui a change vs les anciens prompts :**
- Prompt 1 est maintenant un patch sur l'existant (pas un rebuild from scratch)
- Layout results = ta version (horizontal row desktop + 2-col mobile + detail on click)
- Le 3+2 grid est mort et enterre
- Genre pills retires du detail view
- Poster wall plus fade
- Mobile bottom sheet preserve et ameliore

**Design philosophy (inchangee) :**
- L'UI est invisible. Les posters sont les stars.
- Accent indigo uniquement sur les boutons et focus states.
- La touche cinema vient du Lottie + des movie facts + du poster wall, pas des couleurs.
- Linear meets cinema.

---

## Prompt 4 — About Page (Portfolio Case Study)

```
Add a new /about page to WatchNext. This page is a portfolio case study — not documentation. It shows a hiring manager how the product was built, what decisions were made, and what was learned.

## Navigation

Add a small "About" link in the header bar, next to the WatchNext logo. Muted gray (#94A3B8), text-sm. On hover, white. Clicking it navigates to /about. On the About page, the WatchNext logo in the header links back to / (the main app).

## About Page Layout

Dark background (#0B0F1A) consistent with the rest of the app. Content centered, max-width 720px, generous vertical spacing (py-16 px-6). No sidebar, no poster wall. Clean reading experience.

### Section 1 — Hero

Large title: "How WatchNext Works" in white, font-bold, text-3xl.
Subtitle below: "A mood-powered movie recommendation engine — designed, built, tested and shipped in 5 days." in muted gray (#94A3B8), text-lg.

### Section 2 — The Problem

Section heading: "The Problem" — white, font-semibold, text-xl, with a thin top border (#1E293B) as separator.

Text (muted gray, text-base, leading-relaxed):
"Tens of thousands of movies across streaming platforms. Netflix alone has 10,000+. You open it, scroll for 20 minutes, switch to Disney+, scroll some more, and end up rewatching The Office. The problem isn't too few options — it's too many, with no way to search by how you actually feel."

### Section 3 — How It Works

Section heading: "How It Works"

Show a vertical pipeline with 4 steps. Each step is a card (#151B2B background, rounded-xl, p-6, border #1E293B):

Step 1: "You describe your mood"
"'I'm exhausted, something chill and not too long' or 'Korean drama, emotional' or 'action movie with Brad Pitt on Netflix'"

Step 2: "AI translates mood → search filters"
"GPT-4o-mini extracts structured parameters: genre, language, actor, streaming platform, rating threshold, runtime. Like filling out a search form — but the AI does it from natural language."

Step 3: "TMDB finds 20 candidates"
"The TMDB Discover API returns 20 movies matching those filters. Each is enriched with runtime, poster, rating, and streaming availability."

Step 4: "AI curates the top 5"
"A second AI call ranks the 20 candidates and picks the 5 best matches — with a personalized explanation of why each movie fits your mood."

Between each card, show a small downward arrow icon (Lucide ArrowDown, muted gray, centered).

### Section 4 — Key Decisions

Section heading: "Key Decisions"

Show as a clean table or alternating rows (no actual table border — just alternating subtle backgrounds):

| Decision | Choice | Why |
|----------|--------|-----|
| Data source | TMDB API (not IMDb) | Free, 900K+ movies, watch providers by country, 40 req/s |
| LLM | GPT-4o-mini (not GPT-4) | Fast enough for real-time (2-3s), cheap ($0.15/1M tokens), structured output via function calling |
| Architecture | 2 LLM calls, not 1 | Separation of concerns: first call extracts filters (deterministic), second call curates results (creative). Easier to debug and evaluate independently. |
| Frontend | Lovable (not custom React) | Ship in hours, not days. Focus effort on the AI pipeline, not the UI scaffolding. |
| Deploy | Render $7/mo | Auto-deploy from GitHub, good enough for demo. Cold start (30-60s) is acceptable. |

Use white for the "Decision" and "Choice" columns, muted gray for "Why". Keep it scannable.

### Section 5 — Evaluation Results

Section heading: "Evaluation Results"

Text intro: "Every build goes through an Eval Gate — a structured evaluation before shipping. WatchNext was tested with a golden dataset of mood queries covering every category (genre, language, actor, platform, vague moods, specific moods), plus unscripted 'wild tests' from a non-tech user who had never seen the app before."

Show metrics as 4 stat cards in a 2x2 grid (each card: #151B2B, rounded-xl, p-5, border #1E293B):

Card 1: "10/10" (large, indigo #6366F1, font-bold) + "Filter Accuracy" (small, muted gray)
Card 2: "49/50" (large, indigo) + "Movies Comply" (small, muted gray)
Card 3: "2.78 / 3" (large, indigo) + "Relevance Score" (small, muted gray)
Card 4: "~17s" (large, indigo) + "Avg Latency" (small, muted gray)

Below the grid: "Decision: Conditional GO — shipped with 2 known limitations documented below." in muted gray, text-sm.

### Section 6 — Bugs Found & What We Learned

Section heading: "What Broke (and What We Learned)"

Text intro: "The first evaluation round returned NO-GO. Five bugs were identified, fixed, and re-evaluated — plus two limitations we documented and shipped with."

Show as a list of 7 items. Each item has:
- A short bold title (white)
- A description (muted gray)

**Bugs fixed:**

1. **"Korean drama" returned zero Korean films**
"The AI understood 'Korean' perfectly but had no way to tell the movie database to filter by language. We added a language parameter — and suddenly an entire category of queries started working."

2. **"Brad Pitt" returned zero Brad Pitt films**
"Same pattern: the AI knew who Brad Pitt was, but the search form it was filling out had no 'actor' field. We added one, along with a step to look up actor names before searching."

3. **Duplicate movie in results**
"The AI curator returned The Conjuring twice in the same list. A simple check to skip movies already picked fixed it."

4. **Horror movie in 'thriller' results**
"A horror film showed up when someone asked for thrillers. We made the AI's instructions stricter about not mixing genres that feel very different to the viewer."

5. **The AI sometimes returns "null" as text**
"Instead of leaving a field empty, the AI would write the word 'null' — which the system treated as a real value. A small but real production bug."

**Known limitations (shipped with):**

6. **Light and family moods tend to return animated films**
"When you ask for something 'chill' or 'family-friendly,' you'll often get animated movies. That's because the most popular, highest-rated films in those categories genuinely are animated (Toy Story, Shrek, Spirited Away). The AI isn't broken — the data reflects what people love most in those moods. We documented it and moved on."

7. **Abstract or very specific moods can miss the mark**
"Moods like 'mind-bending' or very niche descriptions are harder for the AI to translate into search filters, because they don't map neatly to genres or keywords. The results are usually interesting, but not always exactly what you had in mind."

### Section 7 — Key Learnings

Section heading: "What I Learned"

Show as 4 insight cards (#151B2B, rounded-xl, p-6, border-left 3px solid #6366F1):

Card 1 title (white, font-semibold): "The AI is only as good as the form it fills out"
Card 1 text (muted gray): "The AI understood 'Korean drama' perfectly — but the search form it was filling out had no 'language' field. It's like asking a travel agent to book a beach vacation, but the booking system only has a 'city' dropdown. The intelligence was there. The options weren't."

Card 2 title: "Real users break what test plans don't"
Card 2 text (muted gray): "I tested with 10 carefully designed queries. Then I gave the app to someone who had never seen it. In 3 random tries, she found 2 bugs I completely missed. Lesson: your test plan reflects YOUR assumptions. Real users have their own."

Card 3 title: "Failing the first test is the system working"
Card 3 text (muted gray): "The first evaluation returned 'not ready to ship.' That sounds bad — but that's the whole point of testing before you ship. Five bugs found, five bugs fixed, re-tested in 2 hours. The test caught what I would have shipped broken."

Card 4 title: "15 seconds of waiting can be a feature"
Card 4 text (muted gray): "The app takes 15-20 seconds to respond — it's making two AI calls plus a movie database search. Instead of hiding the wait, we turned it into a movie trivia experience. Users loved the fun facts so much they wanted more. Sometimes the 'flaw' is an opportunity."

### Section 8 — Footer

Centered, generous top margin (mt-16):
Line 1: "Built by Mehdi Bargach" — white, text-sm, font-medium
Line 2: Small GitHub icon linking to https://github.com/Mehdibargach/watchnext — muted gray, 16px

## Style rules

- NO emojis anywhere
- NO images or illustrations (the text IS the content)
- NO light mode — dark only
- Typography: same Inter font as the rest of the app
- All section headings have the thin top border separator
- Smooth scroll behavior
- Page title: "About — WatchNext"
- Mobile: single column, all cards stack, stat grid becomes 2x1

## Do NOT change anything on the main app page. Only add the About page and the header navigation link.
```

---

## Prompt 5 — V2 ML Recommendation Rails (Scope 3)

```
Add ML-powered recommendation rails to the movie detail page. When users click a movie poster, they now see the movie info PLUS two rows of recommended films — powered by a machine learning backend.

## New API endpoint

GET https://watchnext-flta.onrender.com/movie/{tmdb_id}/similar

Response shape:
{
  "movie_id": 155,
  "similar_movies": [
    {
      "id": 49026,
      "title": "The Dark Knight Rises",
      "genres": ["Action", "Crime", "Drama", "Thriller"],
      "rating": 7.792,
      "runtime": 165,
      "release_year": "2012",
      "overview": "...",
      "poster_url": "https://image.tmdb.org/t/p/w500/hr0L2aueqlP2BYUblTTjmtn0hw4.jpg",
      "score": 0.3504,
      "rec_type": "similar"
    }
  ],
  "viewers_also_liked": [
    // same shape, rec_type: "also_liked"
    // CAN BE EMPTY [] if the movie is too recent or confidence is low
  ],
  "latency": 0.5
}

## What to add to the movie detail view

When a movie detail page opens (clicking any poster in results OR in a rail), call GET /movie/{movie.id}/similar and display the recommendation rails below the movie info section.

### Rail layout

Each rail is a horizontal row of poster cards, similar to Netflix/Disney+:

1. **Section label** — left-aligned, white, font-semibold, text-lg
   - First rail: "Similar Movies"
   - Second rail: "Viewers Also Liked"

2. **Poster row** — horizontal scroll on mobile, 5 posters in a row on desktop
   - Each poster card: 2:3 aspect ratio, rounded-lg, w-[140px] on desktop
   - Below each poster: title (white, text-sm, 1 line truncate) + year (muted gray, text-xs)
   - On hover: scale(1.03), translateY(-4px), border brightens from #1E293B to #334155, transition 200ms ease
   - Gap between cards: 12px
   - On mobile (<768px): horizontal scroll with snap, cards are w-[120px]

3. **Rail spacing** — 32px between the movie info and first rail, 24px between rails

### Conditional display rules

- If `similar_movies` is empty → do NOT show the "Similar Movies" rail at all (no label, no empty space)
- If `viewers_also_liked` is empty → do NOT show the "Viewers Also Liked" rail at all
- If BOTH are empty → show nothing below the movie info (same as current behavior)
- While the API is loading → show a subtle skeleton loader (3 gray placeholder cards per rail, pulsing animation)

### Clickable navigation (CRITICAL)

Every poster in a rail is clickable. Clicking it:
1. Opens the detail page for THAT movie (with its full info: poster, title, genres, rating, year, runtime, overview)
2. Calls GET /movie/{clicked_movie.id}/similar to load ITS recommendation rails
3. This creates infinite navigation: Movie A → click rec → Movie B → click rec → Movie C → etc.

The movie info on the detail page should be populated from the data already in the API response (title, genres, rating, runtime, release_year, overview, poster_url). No need for an extra API call for the movie details.

### Back navigation

- A back arrow (Lucide ArrowLeft) in the top-left of the detail view
- If the user came from search results → back goes to search results (preserved)
- If the user came from a rail click → back goes to the previous movie detail
- Browser back button should work naturally (use proper routing/history)

### Desktop layout

The detail page layout stays as-is (poster left + info right). The recommendation rails go BELOW the info section, full width of the content area.

### Mobile layout

The detail page on mobile should be a FULL PAGE (not bottom sheet) when accessed via rail navigation. The bottom sheet is fine for the first click from search results, but chained navigation in a bottom sheet is awkward. So:
- Click from search results → bottom sheet (existing behavior, keep it)
- Click from a recommendation rail → full page with back arrow
- Rails on mobile: horizontal scroll with touch/swipe, cards snap to edges

### Loading state

While GET /movie/{id}/similar is loading:
- Show the movie info immediately (we already have it)
- Below the info, show skeleton loaders for the rails:
  - 2 rows of 3 gray rounded rectangles (same 2:3 ratio as posters)
  - Pulsing animation (opacity 0.3 to 0.6, 1.5s ease-in-out infinite)
  - Each skeleton has a smaller rectangle below it (title placeholder)

### Error handling

If the /similar API call fails (500, timeout, network error):
- Do NOT show any error message — just don't show the rails
- The movie detail page works fine without rails (it's the V1 experience)
- Log the error to console for debugging

## Style consistency

- Same dark background (#0B0F1A)
- Same card backgrounds (#151B2B) with border (#1E293B)
- Same indigo accent (#6366F1) only where needed
- Same Inter font
- NO emojis
- NO genre pills on rail poster cards (just poster + title + year)
- Poster fallback: if poster_url is null or image fails, show movie title centered on dark gradient card (#151B2B to #0F172A), same 2:3 ratio

## What NOT to change

- Do NOT change the search/results page
- Do NOT change the About page
- Do NOT change the empty state or poster wall
- Do NOT change the loading experience (Lottie + facts)
- Do NOT add any new pages besides the movie detail route
- Do NOT change colors, typography, or existing layouts
```
