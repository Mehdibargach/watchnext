# Eval Report — WatchNext

> From The Builder PM Method — EVALUATE phase

**Project:** WatchNext
**Date:** 2026-02-23
**Evaluator:** Mehdi Bargach
**Build Version:** f8a3a2b
**Golden Dataset Size:** 10 mood queries

---

## Eval Gate Criteria

> Each criterion is classified as BLOCKING, QUALITY, or SIGNAL.
> - **BLOCKING** : non-negotiable. FAIL = NO-GO, return to BUILD.
> - **QUALITY** : configurable threshold. FAIL = Builder decides (GO or CONDITIONAL GO).
> - **SIGNAL** : monitoring only. FAIL = document for V2, not blocking.

| # | Critere | Level | Seuil | Resultat | Status |
|---|---------|-------|-------|----------|--------|
| G1 | Filter Accuracy — LLM correctly translates mood → TMDB filters | BLOCKING | 100% explicit constraints parsed correctly | 9/10 (E8 FAIL) | **FAIL** |
| G2 | Constraint Compliance — returned movies respect all stated filters | BLOCKING | 100% of movies comply with stated constraints | 44/50 (E7 4/5, E8 0/5) | **FAIL** |
| G3 | Recommendation Relevance — movies plausibly match the mood (Precision@5) | QUALITY | >= 3/5 recs rated 2+ per query (1=miss, 2=partial, 3=clear match) | 9/10 queries pass, avg 2.70 | **PASS** |
| G4 | Response Time — end-to-end latency | SIGNAL | < 30s (adjusted from 1-Pager's 5s — includes 2 LLM calls) | ~15-20s | **PASS** |
| G5 | Usability — non-tech person gets useful recs without help | QUALITY | Zero confusion on main flow (tested in S2-8) | **PASS** (8/8 S2) | **PASS** |

### Decision Rules

| Decision | Condition | Action |
|----------|-----------|--------|
| **GO** | 0 BLOCKING fail + 0 QUALITY fail | → SHIP |
| **CONDITIONAL GO** | 0 BLOCKING fail + >=1 QUALITY/SIGNAL fail | → SHIP with documented conditions |
| **NO-GO** | >=1 BLOCKING fail | → Micro-loop BUILD (mandatory) |

---

## Golden Dataset — 10 Mood Queries

> Each query tests a different aspect of the recommendation pipeline.
> Scoring: 3 = clear match, 2 = partial match, 1 = miss.
> For G1 (Filter Accuracy): check the `filters_applied` field.
> For G2 (Constraint Compliance): check each of the 5 movies against the stated constraint.
> For G3 (Rec Relevance): human rates each of the 5 movies 1-3.

| # | Type | Mood Query | Tests What | G1 Check | G2 Check |
|---|------|-----------|------------|----------|----------|
| E1 | Genre explicit | "Something funny and light" | Comedy genre mapping | genres includes 35 (Comedy) | 5/5 are comedies |
| E2 | Genre explicit | "Scary movie for tonight" | Horror genre mapping | genres includes 27 (Horror) | 5/5 are horror |
| E3 | Platform filter | "Action movie on Netflix" | Provider + genre | genres includes 28 + provider Netflix | 5/5 on Netflix + action |
| E4 | Platform filter | "Comedy on Disney+" | Provider + genre | genres includes 35 + provider Disney+ | 5/5 on Disney+ + comedy |
| E5 | Vague mood | "I'm exhausted, something chill and not too long" | Implicit constraints: light genre, short runtime | Light genre + runtime_lte reasonable | 5/5 feel "chill", reasonable runtime |
| E6 | Vague mood | "Date night, something romantic but not cheesy" | Nuanced mood interpretation | Romance-adjacent genre | 5/5 romantic, not purely rom-com |
| E7 | Specific vibe | "Mind-bending thriller like Inception or Shutter Island" | Reference-based mood | Sci-fi/thriller genres | 5/5 are cerebral thrillers |
| E8 | Niche | "Korean drama, emotional" | Language/origin + mood | Korean + drama filters | 5/5 Korean dramas |
| E9 | Multi-constraint | "Animated family movie, well-rated, on any platform" | Multiple genre + quality | Animation + Family + vote_avg high | 5/5 animated, family-friendly, well-rated |
| E10 | Ambiguous | "Something everyone in the family can enjoy tonight" | Fully ambiguous mood | Family-appropriate genre | 5/5 family-friendly |

---

## Golden Dataset Results

> Evaluation run on 2026-02-23 via live Lovable frontend → Render backend.

### E1 — "Something funny and light"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | KPop Demon Hunters | Yes (animated comedy) | 2 |
| 2 | GOAT | Yes (animated comedy) | 2 |
| 3 | SpongeBob Movie | Yes (comedy) | 3 |
| 4 | Shrek | Yes (comedy) | 3 |
| 5 | Inside Out 2 | Yes (comedy) | 3 |

- **G1:** PASS — comedy genre mapped correctly
- **G2:** 5/5 PASS
- **G3:** 2-2-3-3-3, avg **2.6** (5/5 rated 2+ ✓)
- **Pattern:** Animation bias — 5/5 are animated. Funny ≠ animated.

### E2 — "Scary movie for tonight"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | The Conjuring: Last Rites | Yes (horror) | 3 |
| 2 | IT | Yes (horror) | 3 |
| 3 | Dracula | Yes (horror) | 3 |
| 4 | 28 Years Later | Yes (horror) | 3 |
| 5 | The Conjuring: Last Rites | **DUPLICATE of #1** | 3 |

- **G1:** PASS — horror genre mapped correctly
- **G2:** 5/5 comply (all horror), but **DUPLICATE BUG** — film #1 = film #5
- **G3:** 3-3-3-3-3, avg **3.0** (5/5 rated 2+ ✓)
- **Bug:** Deduplication missing in curator LLM or pipeline

### E3 — "Action movie on Netflix"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | The Rip | Yes (action, Netflix) | 3 |
| 2 | Venom: Last Dance | Yes (action, Netflix) | 3 |
| 3 | Bad Boys: Ride or Die | Yes (action, Netflix) | 3 |
| 4 | Casino Royale | Yes (action, Netflix) | 3 |
| 5 | How to Train Your Dragon | Yes (action, Netflix) | 3 |

- **G1:** PASS — action genre + Netflix provider mapped
- **G2:** 5/5 PASS
- **G3:** 3-3-3-3-3, avg **3.0** (5/5 rated 2+ ✓)

### E4 — "Comedy on Disney+"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1-5 | (not captured — user confirmed all good) | Yes | 3 each |

- **G1:** PASS — comedy genre + Disney+ provider mapped
- **G2:** 5/5 PASS
- **G3:** 3-3-3-3-3, avg **3.0** (5/5 rated 2+ ✓)

### E5 — "I'm exhausted, something chill and not too long"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | Shrek | Yes (light, short) | 3 |
| 2 | The Emperor's New Groove | Yes (light, short) | 3 |
| 3 | SpongeBob Movie | Yes (light, short) | 3 |
| 4 | KPop Demon Hunters | Yes (light, short) | 3 |
| 5 | Toy Story | Yes (light, short) | 3 |

- **G1:** PASS — light genre + reasonable runtime mapped
- **G2:** 5/5 PASS
- **G3:** 3-3-3-3-3, avg **3.0** (5/5 rated 2+ ✓)
- **Pattern:** Animation bias — 5/5 animated again (same as E1). LLM equates "chill" with "animated."

### E6 — "Date night, something romantic but not cheesy"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | Hamnet | Yes (romantic drama) | 3 |
| 2 | Pillion | Yes (romantic) | 3 |
| 3 | Your Name | Yes (romantic anime) | 3 |
| 4 | Even If This Love Disappears Tonight | Yes (romantic) | 3 |
| 5 | Wuthering Heights | Yes (romantic drama) | 3 |

- **G1:** PASS — romance-adjacent genre mapped, avoided pure rom-com
- **G2:** 5/5 PASS
- **G3:** 3-3-3-3-3, avg **3.0** (5/5 rated 2+ ✓)
- **Note:** Excellent result. Diverse, not cheesy. Best query performance.

### E7 — "Mind-bending thriller like Inception or Shutter Island"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | The Rip | Yes (thriller) | 3 |
| 2 | The Bone Temple | **NO** — horror, not mind-bending thriller | 1 |
| 3 | Mercy | Yes (thriller) | 3 |
| 4 | The Housemaid | Yes (thriller) | 3 |
| 5 | The Shadow's Edge | Yes (thriller) | 3 |

- **G1:** PASS — thriller genre mapped (TMDB can't capture "mind-bending" nuance in filters)
- **G2:** 4/5 — The Bone Temple is horror, not cerebral thriller
- **G3:** 3-1-3-3-3, avg **2.6** (4/5 rated 2+ ✓)
- **Note:** None are truly "mind-bending" like Inception — they're action/thrillers. Curator LLM didn't capture the nuance.

### E8 — "Korean drama, emotional" — CRITICAL FAILURE

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | My Fault | **NO** — Spanish film | 1 |
| 2 | Wuthering Heights | **NO** — British classic | 1 |
| 3 | Titanic | **NO** — American film | 1 |
| 4 | Hamnet | **NO** — British film | 1 |
| 5 | The Housemaid | **NO** — American film | 1 |

- **G1:** **FAIL** — "Korean" not translated to `with_original_language: "ko"`. LLM ignored the language constraint entirely.
- **G2:** 0/5 **FAIL** — zero Korean films returned
- **G3:** 1-1-1-1-1, avg **1.0** (0/5 rated 2+ ✗)
- **Root cause:** `parse_mood` function calling schema has no `language` or `with_original_language` parameter. The LLM cannot express a language constraint even if it understands the mood. **This is a schema gap, not an LLM reasoning failure.**

### E9 — "Animated family movie, well-rated, on any platform"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | Toy Story | Yes (animated, family, well-rated) | 3 |
| 2 | Zootopia | Yes (animated, family, well-rated) | 3 |
| 3 | David | Yes (animated, family) | 3 |
| 4 | KPop Demon Hunters | Yes (animated) | 3 |
| 5 | Spirited Away | Yes (animated, family, well-rated) | 2 |

- **G1:** PASS — animation + family genres + vote_average mapped
- **G2:** 5/5 PASS
- **G3:** 3-3-3-3-2, avg **2.8** (5/5 rated 2+ ✓)
- **Note:** Animation bias is CORRECT here — the query explicitly asked for animated.

### E10 — "Something everyone in the family can enjoy tonight"

| # | Movie | G2 Comply | G3 Score |
|---|-------|-----------|----------|
| 1 | Zootopia | Yes (family-friendly) | 3 |
| 2 | Toy Story | Yes (family-friendly) | 3 |
| 3 | The Lion King | Yes (family-friendly) | 3 |
| 4 | Coco | Yes (family-friendly) | 3 |
| 5 | Super Mario Bros Movie | Yes (family-friendly) | 3 |

- **G1:** PASS — family-appropriate genre mapped
- **G2:** 5/5 PASS
- **G3:** 3-3-3-3-3, avg **3.0** (5/5 rated 2+ ✓)
- **Pattern:** Animation bias — 5/5 animated again. "Family" = animated in LLM's mind. But results are genuinely good.

---

## Summary Statistics

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| G1 — Filter Accuracy | 9/10 (E8 FAIL) | 10/10 (100%) | **FAIL** |
| G2 — Constraint Compliance | 44/50 movies (E7 4/5, E8 0/5) | 50/50 (100%) | **FAIL** |
| G3 — Avg Relevance Score | 2.70/3.0 | >= 2.0 avg | **PASS** |
| G4 — Median Latency | ~15-20s | < 30s | **PASS** |
| G5 — Usability | PASS (S2-8) | Zero confusion | **PASS** |

### G3 Detail by Query

| Query | Scores | Avg | >=3/5 rated 2+ |
|-------|--------|-----|-----------------|
| E1 | 2-2-3-3-3 | 2.6 | 5/5 ✓ |
| E2 | 3-3-3-3-3 | 3.0 | 5/5 ✓ |
| E3 | 3-3-3-3-3 | 3.0 | 5/5 ✓ |
| E4 | 3-3-3-3-3 | 3.0 | 5/5 ✓ |
| E5 | 3-3-3-3-3 | 3.0 | 5/5 ✓ |
| E6 | 3-3-3-3-3 | 3.0 | 5/5 ✓ |
| E7 | 3-1-3-3-3 | 2.6 | 4/5 ✓ |
| E8 | 1-1-1-1-1 | 1.0 | 0/5 ✗ |
| E9 | 3-3-3-3-2 | 2.8 | 5/5 ✓ |
| E10 | 3-3-3-3-3 | 3.0 | 5/5 ✓ |
| **Total** | | **2.70** | **9/10** |

---

## Eval Gate Decision

**Decision:** NO-GO — return to BUILD (micro-loop)

**Logic:**
- G1 (BLOCKING) = FAIL → E8 "Korean drama" — language constraint not translatable
- G2 (BLOCKING) = FAIL → E8 (0/5 comply) + E7 (4/5 comply)
- >= 1 BLOCKING fail → **NO-GO** per decision rules
- G3, G4, G5 all PASS — the pipeline works well EXCEPT for language/origin constraints

---

## Wild Tests (non-evaluator, unscripted)

> Additional tests run by a non-tech user (evaluator's wife) without the golden dataset. These test real-world usage patterns outside the controlled eval.

### W1 — "a french movie"

| # | Movie | French? | Score |
|---|-------|---------|-------|
| 1 | Hamnet | NO — British | 1 |
| 2 | Wuthering Heights | NO — British | 1 |
| 3 | The Housemaid | NO — American | 1 |
| 4 | The Shadow's Edge | NO — Asian | 1 |
| 5 | Marty Supreme | NO — American | 1 |

- **Result:** 0/5 French films. **Confirms F1** — `with_original_language` missing from schema.
- **Latency:** 8.1s

### W2 — "a fantastic movie for family"

| # | Movie | Family-friendly? | Score |
|---|-------|-----------------|-------|
| 1 | Coco | Yes | 3 |
| 2 | The Lion King | Yes | 3 |
| 3 | Inside Out 2 | Yes | 3 |
| 4 | Zootopia | Yes | 3 |
| 5 | The Emperor's New Groove | Yes | 3 |

- **Result:** 5/5 great picks, but 5/5 animated. **Confirms F4** — animation bias.
- **Latency:** 9.6s

### W3 — "a recent movie with brad pitt"

| # | Movie | Brad Pitt? | Score |
|---|-------|-----------|-------|
| 1 | The Shadow's Edge | NO | 1 |
| 2 | Marty Supreme | NO (Timothee Chalamet) | 1 |
| 3 | The Wrecking Crew | NO (Jason Momoa) | 1 |
| 4 | Mercy | NO | 1 |
| 5 | The Rip | NO | 1 |

- **Result:** 0/5 Brad Pitt films. **New bug F5** — `with_cast` missing from schema. TMDB supports `with_cast` (person ID), but LLM has no parameter to express actor preference.
- **Latency:** 10.4s

### Wild Tests Summary

| Test | Pattern | Bug |
|------|---------|-----|
| W1 "french movie" | Language ignored (same as E8) | F1 (confirmed) |
| W2 "fantastic family" | Animation bias | F4 (confirmed) |
| W3 "brad pitt" | Actor/cast ignored | **F5 (NEW)** |

**Key insight:** The `parse_mood` schema is **systematically too narrow**. It handles genres and streaming providers but cannot express: language/origin, actor/cast, director, or keywords. This is not a collection of individual bugs — it's a **schema coverage gap**.

---

## Failure Analysis

| # | Query | Pattern | Root Cause | Severity | Recommended Fix |
|---|-------|---------|-----------|----------|----------------|
| F1 | E8 + W1 | Language constraint ignored | `parse_mood` schema has NO `with_original_language` parameter. Confirmed on 2 queries (Korean, French). | **CRITICAL** (BLOCKING) | Add `with_original_language` to schema. TMDB supports ISO 639-1 codes (ko, ja, fr, es, etc.). |
| F2 | E2 | Duplicate movie in results | Curator LLM returned same movie twice (Conjuring: Last Rites #1 = #5). No dedup logic in pipeline. | **HIGH** | Add deduplication step after `rank_movies()` — filter by TMDB ID before returning. |
| F3 | E7 | Horror movie in thriller results | Bone Temple = horror, not cerebral thriller. TMDB genre overlap (horror + thriller). Curator didn't filter. | **MEDIUM** | Improve curator prompt to exclude genre mismatches. Or add negative genre filter. |
| F4 | E1, E5, E10, W2 | Animation bias | LLM defaults to Animation genre for vague/light/family moods. 4 queries returned 100% animated. | **LOW** (SIGNAL) | Document for V2. Could add genre diversity constraint in curator prompt. Scores are still good. |
| F5 | W3 | Actor/cast constraint ignored | `parse_mood` schema has NO `with_cast` parameter. LLM cannot express actor preference. | **HIGH** (BLOCKING for actor queries) | Add `with_cast` to schema. Requires TMDB person ID lookup (search person → get ID → pass to discover). More complex than F1. |

---

## Recommendations

### Mandatory fixes (for re-evaluation)

1. **Add `with_original_language` to parse_mood schema** — TMDB supports `with_original_language` (ISO 639-1). Add it as an optional parameter in the function calling spec. Test with E8 "Korean drama" + W1 "French movie" → must return correct language films.

2. **Add deduplication in pipeline** — After `rank_movies()`, filter duplicates by TMDB ID. Return only unique movies.

### Recommended fixes (quality improvement)

3. **Add `with_cast` to parse_mood schema** — TMDB supports `with_cast` (person IDs). Requires a person search step: mood mentions "Brad Pitt" → search TMDB `/search/person?query=Brad Pitt` → get ID → pass to discover. More complex pipeline change but unlocks actor-based queries.

4. **Improve curator prompt for genre precision** — Add instruction: "Exclude movies whose primary genre contradicts the mood. A horror movie is not a mind-bending thriller."

### Document for V2 (not blocking)

5. **Animation bias** — The LLM equates "light/chill/family" with animated. Consider adding genre diversity instruction in curator prompt. Low priority — scores are still good (avg 2.87 across biased queries).

### Re-evaluation plan

After fixes F1 + F2 (mandatory):
- Re-run E2 (verify no duplicate)
- Re-run E8 (verify Korean films returned)
- Re-run W1 (verify French films returned)

After fix F3 (recommended):
- Re-run E7 (verify no horror in thriller results)

After fix F5 (recommended):
- Re-run W3 (verify Brad Pitt films returned)

**Target:** 0 BLOCKING fail → CONDITIONAL GO (animation bias = documented SIGNAL, actor queries = V2)
