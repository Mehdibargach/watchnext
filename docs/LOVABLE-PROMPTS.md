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
