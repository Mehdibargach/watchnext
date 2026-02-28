# BUILD Walkthrough — V2 Scope 1 : Le pipeline complet

> Le script de test du Walking Skeleton devient un vrai systeme : modules separes, entrainement ameliore, endpoint API pret a l'emploi.

---

## Ce que fait cette tranche

Le Walking Skeleton a prouve que l'idee tient : on peut prendre un film, analyser son synopsis et les notes des spectateurs, et trouver des films similaires. Mais c'etait un script unique — un gros fichier ou tout est melange. Comme un chef qui prepare un repas de test dans sa cuisine personnelle : ca marche, mais c'est impossible a reproduire dans un vrai restaurant.

Le Scope 1 transforme cette preuve de concept en systeme utilisable. On separe chaque responsabilite dans son propre fichier (modules), on ameliore l'entrainement des modeles, et on cree un point d'acces (endpoint API) pour que n'importe quel programme puisse demander : "donne-moi des films similaires a celui-ci."

---

## Ce qui a change par rapport au Walking Skeleton

| Aspect | Walking Skeleton | Scope 1 |
|--------|-----------------|---------|
| Structure | 1 script monolithique | 4 modules separes dans `core/ml/` |
| Films analyses | 2 000 | 3 000 |
| Notes de spectateurs | 5 millions | 10 millions |
| Genres dans l'analyse | Poids normal (noyes dans le synopsis) | Poids triple (repetes 3 fois) |
| Acteurs | Pas pris en compte | Inclus dans le profil de chaque film |
| Acces | Lancer un script manuellement | Endpoint API integre au backend existant |
| Films hors MovieLens | Pas gere | Reponse valide, liste "Also Liked" vide |
| Enrichissement | Pas de details TMDB | Titre, genres, note, annee, affiche, synopsis |

La difference la plus importante n'est pas visible dans ce tableau : c'est la **separation des responsabilites**. Chaque module fait une seule chose et la fait bien. On peut ameliorer un module sans toucher aux autres.

---

## Ce qu'on a construit, etape par etape

### Etape 1 — Ranger la cuisine

Le Walking Skeleton, c'etait un chef qui cuisine, fait la vaisselle et sert les clients — tout seul, dans une seule piece. Ca marche pour un test. Pas pour un restaurant.

Le Scope 1 separe les responsabilites. Quatre fichiers, quatre roles distincts, regroupes dans un dossier `core/ml/` :

| Fichier | Son role | Analogie |
|---------|---------|----------|
| `data_loader.py` | Charger les donnees MovieLens et le pont vers TMDB | Le magasinier qui recoit les ingredients |
| `content_based.py` | Analyser les synopsis pour trouver des films similaires | Le sommelier qui compare les vins par leurs caracteristiques |
| `collaborative.py` | Utiliser les notes des spectateurs pour trouver "les spectateurs ont aussi aime" | Le serveur qui dit "les clients qui ont pris ce plat ont aussi adore celui-la" |
| `similar.py` | Orchestrer les deux approches et retourner les resultats | Le chef qui assemble l'assiette finale |

Pourquoi c'est important ? Parce que si le sommelier se trompe, on peut le corriger sans toucher au magasinier. Chaque piece est independante. C'est le principe de base de la modularite — et ca rend le systeme maintenable.

### Etape 2 — Ameliorer l'entrainement

Le Walking Skeleton analysait 2 000 films avec 5 millions de notes. Le Scope 1 passe a 3 000 films et 10 millions de notes. Plus de donnees = des patterns plus fiables. Mais le vrai gain n'est pas dans le volume — il est dans deux astuces sur le contenu.

**Astuce 1 — Tripler le poids des genres.** Dans le Walking Skeleton, l'analyse de similarite se basait uniquement sur le synopsis du film. Le probleme : deux films peuvent utiliser des mots similaires dans leur synopsis sans rien avoir en commun.

Imagine deux livres. L'un est un thriller psychologique ou le personnage principal parle de sa "famille dysfonctionnelle". L'autre est une comedie familiale joyeuse. Les deux utilisent le mot "famille". Pour un algorithme qui compare les mots, ces deux livres se ressemblent. Pour un humain, ils n'ont rien a voir.

La solution : on repete le genre trois fois dans le profil textuel de chaque film. Si un film est un thriller, son profil contient `GENRE_thriller GENRE_thriller GENRE_thriller` en plus du synopsis. Comme ca, le genre pese beaucoup plus lourd que n'importe quel mot isole du synopsis. Un thriller matche d'abord avec d'autres thrillers, meme si leurs synopsis utilisent des mots differents.

**Astuce 2 — Ajouter les acteurs.** Meme logique. Deux films avec Leonardo DiCaprio ont probablement un public similaire, meme si leurs histoires n'ont rien en commun. On ajoute les noms des acteurs principaux dans le profil : `ACTOR_leonardo_dicaprio`. Ca empeche deux films de matcher juste parce que leurs synopsis decrivent un "homme tourmente" de la meme facon.

Le resultat : une matrice de 2 994 films avec 8 000 caracteristiques chacun (les mots du synopsis + les genres triples + les acteurs). Quand on cherche "films similaires a The Dark Knight", le systeme regarde d'abord les genres et les acteurs, puis affine avec le contenu du synopsis.

### Etape 3 — Creer le point d'acces

Le Walking Skeleton se lancait en tapant une commande dans le terminal. Le Scope 1 integre tout dans le backend FastAPI existant (celui de la V1 mood-based). Un nouveau point d'acces : `GET /movie/{tmdb_id}/similar`.

Tu lui donnes l'identifiant d'un film (par exemple 155, c'est The Dark Knight). Il te repond avec deux listes :

- **"Similar Movies"** — 5 films qui ressemblent par leur contenu (synopsis, genres, acteurs). L'analyse par le sommelier.
- **"Viewers Also Liked"** — 5 films aimes par les memes spectateurs. La recommandation par le serveur.

Chaque film revient avec ses details complets : titre, genres, note, annee de sortie, affiche, et synopsis. Pas besoin de faire d'appels supplementaires — tout est la.

### Etape 4 — Gerer les cas limites

Que se passe-t-il si tu demandes les films similaires a Oppenheimer (sorti en 2023) ? MovieLens s'arrete en 2019 — il ne connait pas ce film. Le Walking Skeleton n'avait pas prevu ce cas.

Le Scope 1 gere ca proprement. "Similar Movies" fonctionne toujours (il se base sur le synopsis TMDB, pas sur MovieLens). "Viewers Also Liked" retourne une liste vide — pas une erreur, pas un crash. Juste : "on n'a pas assez de donnees de spectateurs pour ce film-la."

C'est le principe du **fallback propre** : degrader gracieusement plutot que planter. Si le restaurant n'a plus de dessert, le serveur dit "on n'a plus de tiramisu ce soir" — il ne ferme pas le restaurant.

---

## Les problemes qu'on a rencontres

### Le fichier fantome de 678 Mo

MovieLens contient un fichier de 678 Mo : `ratings.csv` (10 millions de lignes de notes de spectateurs). Le projet est stocke sur iCloud. Et iCloud a une particularite : pour economiser de l'espace disque, il remplace les gros fichiers par un "placeholder" — une coquille vide qui fait semblant d'etre le fichier. Quand tu l'ouvres, iCloud telecharge le vrai fichier en arriere-plan.

Sauf que notre script essayait de lire 678 Mo d'un coup. iCloud n'a pas suivi. Erreur : `OSError: [Errno 89] Operation canceled`. Le fichier etait la... mais pas vraiment la. Un fantome.

**La solution :** Telecharger MovieLens directement depuis le site source (grouplens.org) vers le dossier `/tmp` — un dossier temporaire qui n'est pas synchronise par iCloud. Et dans le code, on a ajoute un mecanisme automatique : si le fichier sur iCloud ne repond pas, le systeme va chercher la copie dans `/tmp`.

Lecon apprise : quand on travaille avec des fichiers volumineux sur un Mac avec iCloud, toujours verifier que le fichier est **physiquement present** sur le disque, pas juste un placeholder.

### Le script de test qui retourne zero resultat

Premier lancement du module orchestrateur (`similar.py`) en dehors du serveur API : zero resultat. Pas d'erreur, juste... rien.

La cause : la cle d'acces TMDB (le "mot de passe" pour interroger la base de films) etait chargee automatiquement par le serveur API au demarrage. Mais le script de test, lance directement, ne passait pas par le serveur — donc pas de cle, donc TMDB refusait les requetes silencieusement.

**La solution :** Ajouter le chargement de la cle au debut du script de test. Un oubli banal, mais un bon rappel : ce qui marche dans un contexte (le serveur) ne marche pas forcement dans un autre (le script de test).

---

## Les resultats : 6 micro-tests, 6 PASS

Six tests definis avant de coder. Chacun verifie un aspect different du pipeline.

| # | Ce qu'on teste | Comment | Resultat | Verdict |
|---|---------------|---------|----------|---------|
| S1-1 | Le point d'acces repond | Appeler `/movie/155/similar` (The Dark Knight) | 5 "Similar" + 5 "Also Liked" retournes | **PASS** |
| S1-2 | Ca marche sur differents genres | 5 films testes : action, animation, horreur, romance, drame | Chaque genre retourne des similaires coherents (3/5 minimum par seed) | **PASS** |
| S1-3 | Film recent hors MovieLens | Oppenheimer (2023, absent de MovieLens) | "Similar" fonctionne, "Also Liked" vide — pas de crash | **PASS** |
| S1-4 | Film qui n'existe pas | ID bidon (999999999) | Pas de crash, le serveur reste en vie | **PASS** |
| S1-5 | Fiches completes | 10 films verifies | Titre, genres, note, annee, affiche, synopsis — 0 champ manquant | **PASS** |
| S1-6 | Rapidite | Moyenne sur 5 requetes | 1.6 seconde en moyenne, 1.9 seconde maximum (seuil : 3 secondes) | **PASS** |

**Gate : 6/6 PASS**

---

## Le retour du PM et ce qu'on en a tire

Le PM a teste le systeme sur 5 films de genres differents. Pas juste "est-ce que ca repond" — un examen film par film de la pertinence.

**The Shining (horreur) :** Solide. "Similar" retourne des films d'horreur coherents. "Also Liked" fait remonter des films de cinephiles fans de Kubrick — une surprise bienvenue, pas une incoherence.

**The Notebook (romance) :** Tres bon. "Similar" reste dans la romance. "Also Liked" propose Love Actually et The Fault in Our Stars — exactement le genre de films qu'un fan de The Notebook regarderait ensuite.

**Dark Knight (action) :** Moyen. "Similar" retourne 5 films Batman — techniquement correct, mais un peu "tunnel vision". "Also Liked" : 2 pertinents sur 5.

**Toy Story (animation) :** OK mais surprenant. "Similar" inclut The 40-Year-Old Virgin — un choix inattendu pour une suite de Toy Story. "Also Liked" inclut The Fountainhead — un choix qui fait lever un sourcil.

**Fight Club (drame) :** Faible. Tokyo Drift dans les "Similar" — difficile a justifier. "Also Liked" peu coherent.

**La vraie question du PM :** Apres avoir vu ces resultats inegaux, le PM a pose LA question : "Comment on evalue ca objectivement ? La, c'est moi qui regarde film par film et qui dis si c'est pertinent ou pas. Ca ne passe pas a l'echelle."

Cette question a declenche une discussion sur trois methodes d'evaluation :
1. **Overlap de genres** — est-ce que les films recommandes partagent le genre du film de depart ?
2. **Hit Rate** — est-ce que nos recommandations apparaissent aussi dans les recommandations TMDB (une reference externe) ?
3. **Evaluation humaine structuree** — noter chaque recommandation sur une echelle, pas juste "pertinent / pas pertinent"

Le PM a decide : la methode du Hit Rate (comparer nos resultats a ceux de TMDB) sera integree dans le Scope 2. C'est cette question — "comment on mesure objectivement la qualite ?" — qui structure toute la suite.

**Verdict PM : GO.** La qualite inegale n'est pas un bloquant pour le Scope 1 — c'est le terrain du Scope 2 (blend hybride + evaluation formelle). Le pipeline fonctionne. Les modules sont separes. Le point d'acces repond. On avance.

---

## Ce qu'on a appris

**1. La structure compte autant que l'algorithme.** Passer d'un script a quatre modules n'a pas change les resultats. Mais ca a rendu le systeme testable, maintenable, et ameliorable. Sans cette reorganisation, le Scope 2 (blend hybride + evaluation) aurait ete un cauchemar a implementer.

**2. Le poids des genres change tout.** Tripler le tag de genre dans le profil textuel — un truc simple, presque trivial — a considerablement reduit les recommandations hors-sujet. Le Walking Skeleton recommandait Malice (un thriller) pour Toy Story. Le Scope 1, avec les genres ponderes, reste dans le bon registre. La lecon : avant de chercher un algorithme plus puissant, verifie que tes donnees d'entree sont bien calibrees.

**3. Les cas limites revelent la robustesse.** Un film qui n'existe pas, un film trop recent pour etre dans MovieLens, un fichier fantome sur iCloud. Chaque cas limite est une occasion de rendre le systeme plus solide. Le fallback propre — repondre "je n'ai pas cette info" plutot que planter — c'est ce qui separe un prototype d'un produit.

**4. Le PM comme evaluateur subjectif, ca ne suffit pas.** La question du PM ("comment on evalue objectivement ?") est le vrai livrable de ce scope. Pas le code, pas les modules — la prise de conscience qu'il faut une methode de mesure. C'est exactement le probleme que le livre decrit : en IA, ce n'est pas construire qui est dur. C'est evaluer.
