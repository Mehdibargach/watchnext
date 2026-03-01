# BUILD Gameplan

> Template from The Builder PM Method — BUILD phase (start)
> Fill this AFTER the 1-Pager, BEFORE writing any code.
> Decompose your MVP into vertical slices — NOT horizontal layers (backend, frontend).

---

**Project Name:** WatchNext V2 — ML Recommendations
**Date:** 2026-02-28
**Cycle Appetite:** 1 week (side project)
**MVP Features (from 1-Pager):**
- Mapping MovieLens → TMDB (pont entre les deux bases de films)
- Recommandations par similarité ("Similar Movies") — analyse du synopsis, genres, acteurs
- Recommandations communautaires ("Viewers Also Liked") — modèle entraîné sur 25M de notes
- Blend hybride — combinaison des deux scores normalisés
- Endpoint API `/movie/{id}/similar`
- Évaluation comparative des 3 approches

**Riskiest Assumption (from 1-Pager):**
"MovieLens 25M a une couverture suffisante des films populaires TMDB pour que le modèle communautaire puisse scorer les résultats — et les recommandations ML font découvrir des films que le mood-ranking LLM seul n'aurait pas surfacé."

---

## Context Setup

**Action:** Mettre à jour `CLAUDE.md` à la racine du projet avec le contexte V2 (1-Pager + Gameplan).

**For each slice:** Donner à Claude Code la description de la slice ci-dessous + le contexte CLAUDE.md.

---

## Definition of Ready / Definition of Done

### DOR — Definition of Ready (avant de commencer une slice)

| # | Critère | Variante Walking Skeleton |
|---|---------|--------------------------|
| R1 | Gate de la slice précédente PASSÉE | FRAME Review passée (1-Pager approuvé) |
| R2 | Dépendances identifiées et installées | venv, MovieLens dataset téléchargé, scikit-learn, surprise installés |
| R3 | Données de test définies dans le gameplan | Films seed définis par micro-test |
| R4 | Micro-tests définis comme acceptance criteria AVANT de coder | Idem |
| R5 | CLAUDE.md mis à jour avec la phase et le contexte de la slice | Idem |

### DOD — Definition of Done (avant de clôturer une slice)

| # | Critère | Artefact |
|---|---------|----------|
| D1 | Tous les micro-tests PASS selon le gate | Gameplan → Result line |
| D2 | Entrée BUILD-LOG écrite | `docs/v2/BUILD-LOG.md` |
| D3 | BUILD-WALKTHROUGH écrit + checklist qualité | `docs/v2/BUILD-WALKTHROUGH-{slice}.md` |
| D4 | CLAUDE.md mis à jour avec la phase suivante | `CLAUDE.md` |
| D5 | Commit sur main avec message descriptif | Git log |

### Compliance tracker

| Slice | R1 | R2 | R3 | R4 | R5 | D1 | D2 | D3 | D4 | D5 | Status |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|--------|
| Walking Skeleton | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | **DONE** |
| Scope 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | **DONE** |
| Scope 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | **DONE** |
| Scope 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **DONE** |

---

## Walking Skeleton

> La tranche la plus fine possible qui va de bout en bout et qui teste la Riskiest Assumption.
> C'est TOUJOURS le premier build. Pas d'exception.

**Ce qu'il fait :** Charger le dataset MovieLens → vérifier la couverture des films TMDB populaires → pour UN film (The Dark Knight), calculer les 5 films les plus similaires par caractéristiques (synopsis + genres) ET les 5 films "les spectateurs ont aussi aimé" (modèle communautaire) → vérifier que les résultats sont pertinents et différents entre les deux approches.

**Chemin de bout en bout :** MovieLens links.csv → mapping TMDB IDs → couverture mesurée → TF-IDF sur synopsis TMDB → 5 "Similar" → SVD sur ratings MovieLens → 5 "Also Liked" → résultats affichés

**Ce qui est DANS le Skeleton :**
- Charger MovieLens (links.csv pour le mapping, ratings.csv pour le modèle communautaire, movies.csv pour les métadonnées)
- Mesurer la couverture : combien de films TMDB populaires (top 100) ont un identifiant MovieLens ?
- Récupérer les synopsis TMDB pour les films mappés (via l'API TMDB existante)
- Construire une matrice de similarité textuelle (technique qui mesure l'importance des mots dans chaque synopsis, puis compare les vecteurs entre films)
- Entraîner un modèle de factorisation matricielle sur les 25M de notes MovieLens (décompose le tableau "utilisateurs × films" pour trouver les patterns de goûts)
- Pour 1 film de test → retourner 5 similaires + 5 "also liked"

**Ce qui est HORS du Skeleton (repoussé aux Scopes) :**
- Endpoint API (le WS tourne en script/notebook, pas encore d'API)
- Blend hybride (on teste chaque approche séparément d'abord)
- Multi-films (le WS teste 3 films, pas tous)
- Optimisation latence
- Intégration avec le pipeline V1

**Done when :** Pour 3 films de test (The Dark Knight, Toy Story, The Notebook), le script retourne 5 "Similar Movies" et 5 "Viewers Also Liked" avec des résultats pertinents et différents entre les deux approches.

**Micro-test :**

| # | Type | Test | Expected | Pass Criteria |
|---|------|------|----------|---------------|
| WS-1 | Couverture | Charger links.csv → compter les films avec un tmdb_id valide | ≥ 40 000 films mappés | Count ≥ 40K |
| WS-2 | Couverture | Requêter TMDB top 100 films populaires → vérifier le % présent dans MovieLens | ≥ 60% de couverture | ≥ 60/100 trouvés |
| WS-3 | Similarité | "Similar to The Dark Knight" (action/thriller/crime) | 5 films retournés, majoritairement action/thriller/crime | ≥ 3/5 cohérents avec le genre |
| WS-4 | Similarité | "Similar to Toy Story" (animation/famille) | 5 films retournés, majoritairement animation/famille | ≥ 3/5 cohérents avec le genre |
| WS-5 | Communautaire | "Viewers who liked The Dark Knight also liked…" | 5 films retournés depuis le modèle entraîné sur MovieLens | ≥ 3/5 plausibles (films qu'un fan de Dark Knight aimerait) |
| WS-6 | Communautaire | "Viewers who liked Toy Story also liked…" | 5 films retournés | ≥ 3/5 plausibles (films qu'un fan de Toy Story aimerait) |
| WS-7 | Valeur ajoutée | Comparer les listes similarité vs communautaire pour The Dark Knight | Les deux listes sont différentes | ≥ 3 films différents entre les deux listes |

**Gate:** 7/7 PASS

→ **RITUAL : Skeleton Check** — La Riskiest Assumption tient-elle ?
- Si coverage < 60% → Le modèle communautaire ne couvre pas assez de films TMDB. Options : (1) se rabattre sur la similarité seule (toujours disponible via metadata TMDB), (2) utiliser MovieLens 32M si disponible, (3) combiner avec un autre dataset. Si coverage < 30% → abandonner le communautaire.
- Si les résultats de similarité ET communautaire sont les mêmes que ce que le LLM mood aurait donné → zéro valeur ajoutée. Pivoter ou kill.
- Si coverage ≥ 60% ET les résultats sont pertinents ET différents entre approches → Continue aux Scopes.

---

## Scopes

### Scope 1 : Pipeline de similarité complet + endpoint API

**Ce qu'il ajoute :** La similarité (qui était un script dans le WS) devient un vrai module intégré au backend FastAPI. Fonctionne pour N'IMPORTE QUEL film TMDB (pas seulement ceux dans MovieLens). Le modèle communautaire est aussi intégré avec un fallback propre quand un film n'est pas dans MovieLens.

**Chemin de bout en bout :** `GET /movie/{tmdb_id}/similar` → vérifier si le film est dans MovieLens → calculer les 5 plus similaires par caractéristiques (toujours disponible) → calculer les 5 "also liked" par le modèle communautaire (si coverage) → retourner les deux listes en JSON

**Done when :** `curl GET /movie/155/similar` retourne un JSON avec `similar_movies` (5 films) et `viewers_also_liked` (5 films ou liste vide si pas de couverture). Testé sur 5 genres différents.

**Micro-test :**

| # | Type | Test | Expected | Pass Criteria |
|---|------|------|----------|---------------|
| S1-1 | Endpoint | `GET /movie/155/similar` (The Dark Knight) | JSON avec `similar_movies` (5 films) et `viewers_also_liked` (5 films) | Les deux listes retournées avec 5 films chacune |
| S1-2 | Multi-genre | Tester sur 5 films de genres différents : action (155), comédie (862 — Toy Story), horreur (694 — The Shining), romance (11036 — The Notebook), drame (550 — Fight Club) | Chaque appel retourne des résultats cohérents avec le genre du film seed | ≥ 4/5 films seeds retournent des similaires pertinents |
| S1-3 | Film récent hors MovieLens | Film sorti en 2025 (absent de MovieLens) | La similarité fonctionne (utilise metadata TMDB). Le communautaire retourne une liste vide, pas une erreur | Réponse valide, `viewers_also_liked: []` |
| S1-4 | Film inexistant | `GET /movie/999999999/similar` | Erreur propre (404 ou message clair) | Pas de crash serveur |
| S1-5 | Métadonnées | Chaque film recommandé a : title, genres, rating, release_year, poster_url | Données complètes pour l'affichage | 6 champs présents pour chaque film retourné |
| S1-6 | Latence | Temps de réponse de l'endpoint | < 3 secondes | Benchmark sur 5 requêtes |

**Gate:** 6/6 PASS

---

### Scope 2 : Blend hybride + évaluation comparative

**Ce qu'il ajoute :** Le blend hybride (combinaison des scores similarité + communautaire en un classement unifié). Et surtout : l'évaluation comparative formelle sur un golden dataset de 10 films de référence, qui mesure la pertinence de chaque approche et leur valeur ajoutée par rapport au LLM.

**Chemin de bout en bout :** `GET /movie/{id}/similar` retourne maintenant 3 listes (similarité, communautaire, hybride) → évaluation humaine sur 10 films → rapport comparatif documenté

**Done when :** L'endpoint retourne 3 listes pour chaque film. Le rapport d'évaluation comparative est complété avec les scores de pertinence pour chaque approche sur 10 films de référence.

**Micro-test :**

| # | Type | Test | Expected | Pass Criteria |
|---|------|------|----------|---------------|
| S2-1 | Hybride endpoint | `GET /movie/155/similar` inclut `hybrid_recs` | 3 listes : similarité, communautaire, hybride (5 films chacune) | Les 3 listes présentes |
| S2-2 | Hybride qualité | Les 5 films hybrides pour The Dark Knight | Mix de films des deux approches, pas juste une copie de l'une | ≥ 2 films qui viennent de la similarité ET ≥ 2 qui viennent du communautaire |
| S2-3 | Hybride fallback | Film hors MovieLens → pas de score communautaire | Hybride = similarité seule (dégradation gracieuse, pas d'erreur) | Réponse valide, hybride = similarité |
| S2-4 | Eval : pertinence similarité | 10 films seed × 5 recs similarité → évaluation humaine (1-3) | Moyenne ≥ 2.5/3.0 | Critère BLOCKING du 1-Pager |
| S2-5 | Eval : pertinence communautaire | 10 films seed × 5 recs communautaire → évaluation humaine (1-3) | Moyenne ≥ 2.0/3.0 | Critère QUALITY du 1-Pager |
| S2-6 | Eval : valeur ajoutée | Pour 10 moods, comparer les recs ML vs les 5 recs LLM du mood-ranking V1 | ≥ 80% des recs ML sont des films différents de ceux du LLM | Les deux systèmes apportent des choses différentes |
| S2-7 | Eval : hybride vs individuel | Hybride ≥ meilleur des deux approches individuelles | Hybride gagne sur ≥ 6/10 films seed | Critère QUALITY du 1-Pager |
| S2-8 | Latence complète | Temps de réponse avec les 3 listes | < 3 secondes | Benchmark sur 10 requêtes |

**Gate:** 8/8 PASS

---

### Scope 3 : Frontend — page détail film + rails de recommandations

**Ce qu'il ajoute :** Le frontend Lovable (React/Tailwind) affiche une page détail quand on clique sur un film. Cette page montre le poster, les infos du film, et surtout les deux rails de recommandations ML : "Similar Movies" et "Viewers Also Liked". C'est ce qui transforme l'API en produit visible et demo-ready.

**Chemin de bout en bout :** User clique sur un poster dans les résultats V1 → page détail s'ouvre → appel `GET /movie/{tmdb_id}/similar` → affiche le rail "Similar Movies" (toujours) et le rail "Viewers Also Liked" (si disponible) → chaque film dans un rail est cliquable (ouvre sa propre page détail → navigation infinie)

**Done when :** Cliquer sur un film dans les résultats V1 ouvre une page détail avec poster + infos + 2 rails de recos. Chaque film dans les rails est cliquable. Les rails se cachent quand le modèle n'est pas confiant (seuil de confiance côté API). Design cohérent avec la V1 (dark monochrome, indigo accent).

**Micro-test :**

| # | Type | Test | Expected | Pass Criteria |
|---|------|------|----------|---------------|
| S3-1 | Navigation | Cliquer sur un poster dans les résultats V1 | Page détail s'ouvre avec poster grand format, titre, genres, note, année, durée, synopsis | Tous les champs affichés |
| S3-2 | Rail "Similar Movies" | Page détail de The Dark Knight (TMDB 155) | Rail horizontal avec 5 posters cliquables, label "Similar Movies" | 5 posters affichés avec titre et année |
| S3-3 | Rail "Viewers Also Liked" | Page détail de The Dark Knight | Rail horizontal avec 5 posters cliquables, label "Viewers Also Liked" | 5 posters affichés |
| S3-4 | Rail masqué | Film récent hors MovieLens (Oppenheimer) OU film avec score trop bas | Pas de rail "Viewers Also Liked" affiché (pas de rail vide, pas d'erreur) | Rail absent, pas d'espace vide |
| S3-5 | Navigation chaînée | Cliquer sur un film dans un rail → sa propre page détail avec ses propres rails | Navigation infinie entre films | Au moins 3 clics de navigation fonctionnels |
| S3-6 | Retour | Bouton retour depuis la page détail | Retour aux résultats V1 | Les résultats V1 sont toujours là |
| S3-7 | Responsive | Page détail sur mobile (< 768px) | Layout adapté : poster en haut, infos en dessous, rails en scroll horizontal | Pas de débordement, tout lisible |

**Gate:** 7/7 PASS

---

## Architecture — Structure des modules V2

```
watchnext/
├── (fichiers V1 inchangés)
├── api.py                     ← V1 + nouveau endpoint /movie/{id}/similar
├── core/
│   ├── mood_parser.py         ← V1 (inchangé)
│   ├── tmdb_client.py         ← V1 (inchangé, déjà les fonctions d'enrichissement)
│   ├── recommender.py         ← V1 (inchangé)
│   └── ml/                    ← NOUVEAU — tout le ML est ici
│       ├── __init__.py
│       ├── data_loader.py     ← Charge MovieLens (links.csv, ratings.csv, movies.csv)
│       │                         et construit le mapping MovieLens ↔ TMDB
│       ├── content_based.py   ← Construit la matrice de similarité textuelle
│       │                         (analyse des synopsis + genres + acteurs)
│       │                         et retourne les N films les plus proches
│       ├── collaborative.py   ← Entraîne/charge le modèle communautaire
│       │                         (factorisation matricielle sur les notes MovieLens)
│       │                         et prédit les films aimés par des spectateurs similaires
│       ├── hybrid.py          ← Combine les scores des deux approches
│       │                         (normalisation + blend pondéré)
│       └── similar.py         ← Orchestrateur : prend un TMDB ID → appelle
│                                 similarité + communautaire + hybride → retourne les 3 listes
├── data/
│   └── movielens/             ← Dataset MovieLens 25M (téléchargé, pas committé)
│       ├── links.csv          ← Pont movieId → imdbId → tmdbId
│       ├── ratings.csv        ← 25M de notes (userId, movieId, rating, timestamp)
│       └── movies.csv         ← Titres et genres MovieLens
├── models/                    ← Modèles pré-entraînés (sauvegardés après entraînement)
│   ├── svd_model.pkl          ← Modèle communautaire entraîné
│   └── tfidf_matrix.pkl       ← Matrice de similarité textuelle pré-calculée
└── scripts/
    └── train_models.py        ← Script d'entraînement offline
                                  (à lancer 1 fois, sauvegarde dans models/)
```

| Module | Responsabilité | WS | S1 | S2 | S3 |
|--------|---------------|:--:|:--:|:--:|:--:|
| `data_loader.py` | Charger MovieLens + mapping TMDB | ✓ | — | — | — |
| `content_based.py` | Matrice similarité + requête "Similar Movies" | ✓ (script) | ✓ (module) | — | — |
| `collaborative.py` | Modèle communautaire + requête "Also Liked" | ✓ (script) | ✓ (module) | — | — |
| `hybrid.py` | Blend des deux scores normalisés (interne, pas exposé) | — | — | ✓ | — |
| `similar.py` | Orchestrateur : TMDB ID → 2 listes + seuils de confiance | — | ✓ | ✓ | — |
| `api.py` | Nouveau endpoint `/movie/{id}/similar` | — | ✓ | — | — |
| `train_models.py` | Script d'entraînement offline | ✓ | — | — | — |
| Frontend (Lovable) | Page détail film + 2 rails de recos | — | — | — | ✓ |

---

## Exit Criteria (BUILD → EVALUATE)

- [x] Riskiest Assumption testée (Skeleton Check passé — 98% couverture, 7/7 PASS)
- [x] Open Questions du 1-Pager résolues (UX = 2 rails, seuils de confiance, hybride = interne)
- [x] Build Log à jour (WS + S1 + S2)
- [x] Évaluation formelle complétée (Hit Rate sur 10 seeds : 22% similarité, 28% communautaire)
- [x] Frontend demo-ready (Scope 3 — page détail + 2 rails, 7/7 PASS)
- [x] Toutes les features MVP visibles de bout en bout (user clique → voit les recos)
