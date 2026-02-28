# Builder PM 1-Pager

**Project Name:** WatchNext V2 — ML Recommendations
**One-liner:** Keep the LLM for mood. Add ML for "similar" and "also liked."
**Date:** 2026-02-28
**Builder PM Method Phase:** BUILD (Recommendation / Personalization — recommandations par similarité et par comportement communautaire, cohabitant avec le LLM existant)

---

## Problem

- **L'expérience s'arrête aux 5 résultats.** WatchNext V1 donne 5 films par mood. L'utilisateur clique sur un film, regarde la fiche… et c'est fini. Pas de "si tu aimes celui-là, regarde aussi…". Pas d'exploration. Le funnel est : mood → 5 films → mur. Chaque plateforme streaming a des couches de recommandations (films similaires, spectateurs ont aussi aimé, tendances). WatchNext n'en a qu'une.
- **Zéro notion de similarité entre films.** Le LLM comprend le mood mais ne sait pas que Rocky est similaire à Creed, Warrior, Million Dollar Baby. Il n'a pas de notion de "proximité" entre films basée sur leurs caractéristiques (genre, acteurs, synopsis). Si l'utilisateur voit Rocky dans ses 5 résultats et veut explorer cette direction → impasse.
- **Zéro signal communautaire.** "Les spectateurs qui ont aimé Rocky ont aussi aimé…" — ce signal n'existe pas dans V1. C'est pourtant le moteur de 80% des recommandations Netflix/Spotify/TF1+ : exploiter les goûts de millions d'utilisateurs pour prédire ce qui va plaire à quelqu'un. C'est le skill ML #1 attendu d'un AI PM dans la recommandation.
- **"LLM for everything" = gap crédibilité.** En 2026, un AI PM qui ne sait qu'appeler des APIs LLM manque le machine learning fondamental. Les hiring managers US (surtout streaming/e-commerce) veulent voir que tu comprends les différentes techniques de recommandation et surtout **quand utiliser laquelle**.

- **Ce qui existe (V1) :**
  - Pipeline : mood → GPT function calling → TMDB Discover (20 candidats) → GPT curator (top 5 + explications)
  - Forces : filter accuracy 100%, pertinence des recommandations 2.78/3.0, CONDITIONAL GO
  - Architecture : stateless, 2 appels GPT, TMDB API, FastAPI + Lovable
  - **Ce qui manque :** similarité entre films, signal communautaire, page détail film, exploration post-résultats

## User

- **Primary:** Même que V1 — anyone with 2+ streaming subscriptions. Nouveau comportement : "j'ai vu Rocky dans mes 5 résultats, montre-moi des films dans cette direction"
- **Secondary:** Hiring managers et ML engineers qui évaluent la profondeur technique d'un AI PM — ils voient un système multi-modèle, pas un simple wrapper LLM
- **Context:** L'utilisateur reçoit ses 5 résultats (V1). Il s'intéresse à un film. Il ouvre la page détail. Il voit "Similar Movies" (films aux caractéristiques proches) et "Viewers Also Liked" (films aimés par des spectateurs aux goûts similaires). Il découvre des films qu'il n'aurait jamais trouvés via le mood seul.

## Solution

| Pain | Feature |
|------|---------|
| L'expérience s'arrête aux 5 résultats, pas d'exploration | **Page détail film** avec deux sections de recommandations ML en dessous |
| Zéro notion de similarité entre films | **"Similar Movies"** — on analyse les caractéristiques de chaque film (synopsis, genres, acteurs) et on trouve les 5 films les plus proches. Comme un libraire qui te dit "si tu as aimé ce livre, tu aimeras celui-là parce qu'ils partagent le même style." |
| Zéro signal communautaire | **"Viewers Also Liked"** — on exploite les notes de 162 000 utilisateurs réels (dataset MovieLens) pour trouver 5 films que les spectateurs aux goûts similaires ont aussi bien notés. Comme Amazon "les clients qui ont acheté X ont aussi acheté Y." |
| LLM for everything = gap technique | **Architecture multi-modèle** — le LLM comprend le mood, le modèle de similarité trouve les films proches, le modèle communautaire exploite les comportements collectifs. Chacun sur son terrain. |

## Riskiest Assumption

**"MovieLens 25M (le dataset de référence avec 25 millions de notes de films) a une couverture suffisante des films populaires TMDB pour que le modèle communautaire puisse scorer les résultats — et les recommandations ML (films similaires + spectateurs ont aussi aimé) font découvrir des films que le mood-ranking LLM seul n'aurait pas surfacé."**

Si MovieLens ne couvre que des films pré-2018 et que TMDB Discover renvoie des films 2023-2026, le modèle communautaire est aveugle. Si les recommandations ML ne font que retourner les mêmes films que le LLM → zéro valeur ajoutée, le projet est un exercice technique sans impact produit. Le Walking Skeleton teste les deux.

## Scope Scoring

**Criteria:**
- **Pain** (1-3): Does this feature solve the core problem? 1 = nice-to-have, 3 = without it the product is useless.
- **Risk** (1-3): Does building this test our riskiest assumption? 1 = we already know the answer, 3 = this IS the critical test.
- **Effort** (1-3): How hard to build? 1 = a few hours, 2 = 1-2 days, 3 = 3+ days.

**Formula:** Score = Pain + Risk - Effort. **MVP threshold: ≥ 3.**

| Feature | Pain | Risk | Effort | Score | In/Out |
|---------|------|------|--------|-------|--------|
| Pipeline de mapping MovieLens → TMDB (fichier links.csv qui fait le pont entre les deux bases) | 3 | 3 | 1 | **5** | IN |
| Recommandations par similarité — analyse du synopsis, des genres et des acteurs pour trouver des films proches | 3 | 3 | 2 | **4** | IN |
| Recommandations communautaires — modèle entraîné sur 25M de notes utilisateurs pour prédire "les spectateurs ont aussi aimé" | 3 | 3 | 2 | **4** | IN |
| Endpoint API `/movie/{id}/similar` qui retourne les deux types de recommandations | 3 | 2 | 1 | **4** | IN |
| Évaluation comparative des approches sur un golden dataset de 10 films | 3 | 2 | 1 | **4** | IN |
| Page détail film (frontend Lovable) | 2 | 1 | 2 | **1** | OUT (post-BUILD) |
| Blend hybride — combiner les deux scores ML en un seul classement unifié | 2 | 2 | 1 | **3** | IN |
| Permettre à l'utilisateur de noter des films pour affiner son profil | 2 | 2 | 3 | **1** | OUT |
| Modèle deep learning pour les recommandations communautaires | 1 | 2 | 3 | **0** | OUT |
| Bouton en frontend pour switcher entre les approches | 1 | 1 | 2 | **0** | OUT |

### MVP (Score ≥ 3)
- **Mapping MovieLens → TMDB** — charger le fichier de correspondance entre les deux bases de films, mesurer la couverture (combien de films TMDB populaires sont aussi dans MovieLens ?)
- **Recommandations par similarité ("Similar Movies")** — analyser le texte du synopsis de chaque film (via une technique qui mesure l'importance des mots), combiner avec les genres et acteurs, puis calculer un score de proximité entre films → 5 films les plus proches
- **Recommandations communautaires ("Viewers Also Liked")** — entraîner un modèle de factorisation matricielle (on décompose le tableau "utilisateurs × films × notes" pour trouver des patterns cachés) sur MovieLens 25M → prédire les films qu'un spectateur similaire aimerait → 5 films
- **Blend hybride** — combiner les scores des deux approches (similarité + communautaire) normalisés sur la même échelle, pour une liste unifiée optionnelle
- **Endpoint API** — `GET /movie/{id}/similar` retourne les recommandations par similarité + communautaires + hybrides
- **Évaluation comparative** — les 3 approches évaluées sur le même jeu de 10 films de référence

### Out of Scope (Score < 3)
- Page détail frontend (sera construite via Lovable APRÈS le BUILD backend, comme en V1)
- Notation de films par l'utilisateur pour affiner son profil (nécessite de la persistance de données, V3)
- Modèle deep learning pour les recommandations communautaires (nécessite un GPU, complexité disproportionnée pour le gain)
- Bouton frontend pour switcher entre les approches de recommandation

## Success Metrics

| Level | Metric | Target | How to Test | Eval Gate |
|-------|--------|--------|-------------|-----------|
| **1. Couverture** | % des films TMDB populaires (top 500 par popularité) qui ont un identifiant dans MovieLens | ≥ 60% | Requêter TMDB Discover par popularité → vérifier le mapping dans links.csv | **BLOCKING** |
| **2. Pertinence similarité** | Les 5 "Similar Movies" sont-ils pertinents ? (évaluation humaine, échelle 1 à 3) | ≥ 2.5/3.0 en moyenne sur 10 films de référence | Prendre 10 films connus, évaluer les 5 recommandations similaires à l'aveugle | **BLOCKING** |
| **3. Pertinence communautaire** | Les 5 "Viewers Also Liked" sont-ils pertinents ? (évaluation humaine) | ≥ 2.0/3.0 (seuil plus bas car dépend de la couverture MovieLens) | 10 films de référence présents dans MovieLens, évaluer les 5 recommandations communautaires | **QUALITY** |
| **4. Valeur ajoutée** | % des recommandations ML qui sont DIFFÉRENTES des 5 résultats LLM mood | ≥ 80% des recs ML ≠ top 5 LLM | Pour 10 moods, comparer les recs ML vs les recs LLM du même film de départ | **QUALITY** |
| **5. Hybride** | Le classement hybride (similarité + communautaire combinés) est-il meilleur que chaque approche seule ? | Hybride ≥ meilleur des deux individuels sur ≥ 6/10 films de référence | Comparer les 3 classements sur 10 films de référence | **QUALITY** |
| **6. Temps de réponse** | Temps de réponse de l'endpoint `/movie/{id}/similar` | < 3 secondes | Mesurer sur 10 requêtes | **SIGNAL** |

## Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| V1 inchangé | **Le ranking LLM par mood reste intact** | Pertinence = 2.78/3.0. On ne touche pas ce qui marche. Le ML s'ajoute à côté, pas en remplacement. |
| Données d'entraînement | **MovieLens 25M** — un dataset académique de référence avec 25 millions de notes attribuées par 162 000 utilisateurs sur 62 000 films | Standard dans la recherche en systèmes de recommandation. Gratuit. Inclut un fichier de correspondance avec les identifiants TMDB. |
| Correspondance des identifiants | **links.csv** fourni par MovieLens — fait le pont entre les identifiants MovieLens, IMDB et TMDB | Fichier officiel. 62 000 films mappés. Sans ce pont, impossible de relier les notes MovieLens aux films TMDB. |
| Recommandations par similarité | **scikit-learn** — on mesure l'importance des mots dans chaque synopsis pour en faire un vecteur numérique, puis on compare les vecteurs entre films | Léger, pas de GPU nécessaire. La technique (appelée TF-IDF : Term Frequency-Inverse Document Frequency, qui pondère les mots rares plus fort que les mots courants) est la baseline standard pour mesurer la similarité entre textes. |
| Recommandations communautaires | **Librairie surprise** — factorisation matricielle (appelée SVD : Singular Value Decomposition, qui décompose le grand tableau "utilisateurs × films" en facteurs latents pour trouver des patterns cachés dans les goûts) | Librairie de référence en Python pour les systèmes de recommandation. Entraînement en moins de 5 minutes sur un laptop. |
| Blend hybride | **Score linéaire** — on combine les deux scores normalisés avec un poids configurable (50/50 par défaut, ajustable) | Simple, interprétable. On peut tester différentes répartitions dans l'évaluation. |
| Chargement des modèles | **Pré-entraînés en local, chargés en mémoire au démarrage du serveur** | Le modèle communautaire pèse moins de 100 Mo, la matrice de similarité moins de 50 Mo. Pas de GPU nécessaire. Compatible avec Render à $7/mois. |
| Nouveau endpoint | **GET /movie/{tmdb_id}/similar** → retourne 3 listes (similarité, communautaire, hybride) | Un seul appel API, 3 types de recommandations. Le frontend choisit comment les afficher. |
| Fallback | **Si un film TMDB n'est pas dans MovieLens → les recommandations communautaires sont vides, seule la similarité est retournée** | Dégradation gracieuse. La similarité marche toujours car elle utilise les métadonnées TMDB (synopsis, genres, acteurs) qui sont toujours disponibles. |
| Données pour les vecteurs films | **Métadonnées TMDB** (synopsis, genres, acteurs, mots-clés, note moyenne) | Déjà dans le pipeline V1 via la fonction d'enrichissement. Aucune nouvelle API nécessaire. |

## Architecture Flow

```
V1 (INCHANGÉ)
─────────────
mood → GPT (filters) → TMDB Discover (20) → GPT (rank top 5) → 5 movies
                                                                    │
                                                          user clicks on a movie
                                                                    │
V2 (NOUVEAU)                                                        ▼
────────────                                              GET /movie/{id}/similar
                                                                    │
                                    ┌───────────────────────────────┼───────────────────┐
                                    │                               │                   │
                                    ▼                               ▼                   ▼
                           ┌──────────────┐              ┌──────────────┐     ┌──────────────┐
                           │   Similarité │              │ Communautaire│     │   Hybride    │
                           │              │              │              │     │              │
                           │ Analyse du   │              │ Modèle       │     │ Combinaison  │
                           │ synopsis +   │              │ entraîné sur │     │ des deux     │
                           │ genres +     │              │ 25M notes    │     │ scores       │
                           │ acteurs      │              │ (MovieLens)  │     │ normalisés   │
                           └──────┬───────┘              └──────┬───────┘     └──────┬───────┘
                                  │                             │                    │
                                  ▼                             ▼                    ▼
                           5 "Similar Movies"         5 "Viewers Also Liked"   5 "Best Of Both"
                           (caractéristiques          (signal comportemental   (blend des deux
                            proches)                   de 162K spectateurs)     approches)
```

## Open Questions

- **Couverture temporelle MovieLens :** MovieLens 25M couvre des notes jusqu'à quand ? Si les données s'arrêtent en 2019, les films récents (2023-2026) renvoyés par TMDB Discover n'auront pas de score communautaire. Le Walking Skeleton doit mesurer ce gap. Fallback = similarité seule pour les films récents.
- **"Utilisateur synthétique" pour le modèle communautaire :** Sans vrai utilisateur qui note des films, comment simuler un profil ? Option A : utiliser les notes moyennes MovieLens par genre comme approximation ("un amateur de comédies"). Option B : prendre les films les mieux notés du genre correspondant au mood comme "profil implicite". À trancher au Walking Skeleton.
- **Normalisation des scores :** Le score de similarité va de 0 à 1 (proximité entre films). Le score communautaire va de 1 à 5 (note prédite). Pour combiner les deux dans le blend hybride, il faut les ramener sur la même échelle. Normalisation min-max sur chaque lot de candidats = le plus simple.
