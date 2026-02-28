# BUILD LOG — WatchNext V2 (ML Recommendations)

## Walking Skeleton — 2026-02-28

**Objectif :** Tester la Riskiest Assumption — couverture MovieLens, faisabilité similarité + communautaire, complémentarité des deux approches.

**Ce qui a été fait :**
- Téléchargé MovieLens 25M (25 millions de notes, 62K films, fichier de correspondance vers TMDB)
- Construit le mapping MovieLens → TMDB (62 316 films mappés)
- Modèle de similarité : analyse des synopsis TMDB via TF-IDF (2000 films, 5000 features textuelles)
- Modèle communautaire : factorisation matricielle (SVD, 100 facteurs) sur 5M de notes échantillonnées
- Script de test complet avec 7 micro-tests

**Résultats :** 7/7 PASS
- Couverture : 98% des films TMDB connus sont dans MovieLens
- Similarité Dark Knight : 5/5 pertinents (Batman Begins, Dark Knight Rises, Batman 89, Batman Forever, Face/Off)
- Similarité Toy Story : 4/5 pertinents (Toy Story 2 & 3 parfaits, 2 comédies OK, 1 thriller non pertinent)
- Communautaire Dark Knight : 5/5 plausibles (Batman Begins, Dark Knight Rises, Sweeney Todd, 12 Angry Men, Starter for 10)
- Communautaire Toy Story : 3/5 plausibles (seuil minimum)
- Différenciation : 6 films différents sur 10 entre les deux approches

**Décisions prises :**
- scikit-surprise ne compile pas sur Python 3.14 → remplacé par scipy.sparse.linalg.svds (facteurs latents directs)
- Filtre minimum 50 notes par film dans le modèle communautaire (sans ce filtre, les films obscurs avec peu de notes produisent des vecteurs bruités → recommandations absurdes)
- Couverture testée sur les films les plus connus (par nombre de votes TMDB), pas les plus récents (MovieLens s'arrête en 2019)
- Authentification TMDB : Bearer token dans le header (comme V1), pas api_key en paramètre

**Problèmes rencontrés :**
- Mismatch venv Python 3.11 vs pip 3.14 → recréé le venv proprement
- TMDB 401 Unauthorized → le token est un JWT Bearer, pas une api_key classique

**PM Validation Gate :**
- PM a validé : Dark Knight (similarité + communautaire) = bons résultats
- PM a relevé : Toy Story similarité faible (Malice = thriller, pas pertinent), communautaire faible (3/5 minimum)
- PM demande : méthode d'évaluation objective (pas juste du subjectif) → à intégrer dans Scope 2
- **Verdict PM : GO** — le concept fonctionne, améliorations dans les Scopes

**Temps :** ~2h (setup + script + debug + 2 runs)
