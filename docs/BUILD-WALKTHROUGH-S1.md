# BUILD Walkthrough — Scope 1 : Le pipeline complet

> On passe de "5 films bruts" a "5 films tries sur le volet avec explications et plateformes de streaming".

---

## Ce qu'on avait, et ce qui manquait

Le Walking Skeleton a prouve que l'IA sait traduire une humeur en criteres de recherche. Mais l'experience etait encore brute. Trois gros manques :

**1. Pas de "ou regarder".** Le systeme te dit "regarde Parasite" mais ne te dit pas si c'est sur Netflix, Disney+ ou nulle part. Tu dois aller chercher toi-meme. C'est exactement le probleme qu'on essaie de resoudre.

**2. My Little Pony.** Le Walking Skeleton a renvoye un dessin anime My Little Pony comme "film d'action epique". Les filtres mecaniques ne suffisent pas — il faut qu'une IA re-examine les resultats et elimine les absurdites.

**3. Pas d'explication.** Le systeme te dit "regarde The Dark Knight" mais ne te dit pas **pourquoi** il correspond a ton humeur. C'est comme un vendeur qui te tend un livre sans dire un mot. Tu veux savoir : "pourquoi celui-la ?"

Le Scope 1 resout ces trois problemes.

---

## La nouvelle architecture — 4 etapes au lieu de 3

Le Walking Skeleton avait 3 etapes : Traducteur → Catalogue → Enrichissement. Le Scope 1 en ajoute une quatrieme : le **Curateur**.

Imagine que tu vas dans une librairie et que tu dis "je veux un truc drole pour ce soir, disponible en poche".

1. **Le traducteur** comprend que tu veux : humour, format poche.
2. **Le catalogue** sort 20 livres qui correspondent aux criteres.
3. **L'enrichissement** complete les fiches (resume, couverture, disponibilite en librairie).
4. **Le curateur** — c'est la nouveaute — examine les 20 livres, en choisit les 5 meilleurs pour toi, et te dit **pourquoi** chacun va te plaire : "celui-la c'est un humour absurde a la Monty Python", "celui-la c'est plus feel-good, parfait si t'es fatigue".

Voici le nouveau flux :

```
Toi : "un truc drole sur Netflix"
         │
         ▼
    ┌─────────────┐
    │  Traducteur  │  ← comprend ton humeur + ta plateforme
    └──────┬──────┘
           │  criteres : genre=Comedie, plateforme=Netflix
           ▼
    ┌─────────────┐
    │  Catalogue   │  ← cherche 20 films (au lieu de 5)
    └──────┬──────┘
           │  20 films bruts
           ▼
    ┌─────────────┐
    │ Enrichissement│ ← complete chaque fiche + plateformes
    └──────┬──────┘
           │  20 films complets avec Netflix/Disney+/etc.
           ▼
    ┌─────────────┐
    │   Curateur   │  ← IA choisit les 5 meilleurs + explique
    └──────┬──────┘     pourquoi chacun matche ton humeur
           │
           │  5 films tries avec "pourquoi ce film"
           ▼
    Reponse finale
```

Pourquoi 20 films au lieu de 5 ? Parce que le curateur a besoin de choix. Si tu lui donnes 5 films, il ne peut pas vraiment "choisir" — il prend tout. Avec 20, il peut eliminer les My Little Pony, privilegier les films qui collent vraiment au mood, et ne garder que la creme.

---

## Changement 1 : "Ou regarder ce film ?"

### Le probleme

Tu dis "un film drole sur Netflix". Le Walking Skeleton ne comprenait pas "sur Netflix" — il ignorait cette partie. Et meme s'il trouvait des films, il ne savait pas sur quelles plateformes ils etaient disponibles.

### La solution en 2 parties

**Partie A — Le traducteur apprend les plateformes.** On ajoute une case dans le formulaire de l'IA : "plateforme de streaming". Comme pour les genres, chaque plateforme a un numero :

| Plateforme | Numero TMDB |
|-----------|-------------|
| Netflix | 8 |
| Amazon Prime | 9 |
| Disney+ | 337 |
| Hulu | 15 |
| Max (HBO) | 1899 |
| Apple TV+ | 350 |
| Paramount+ | 531 |

Quand tu dis "sur Netflix", l'IA remplit la case `plateforme = 8`. Le catalogue TMDB sait alors ne renvoyer que les films disponibles sur Netflix aux Etats-Unis.

**Partie B — L'enrichissement inclut les plateformes.** Pour chaque film, on fait maintenant un appel supplementaire a TMDB pour savoir sur quelles plateformes il est disponible. TMDB utilise les donnees de **JustWatch** (le site qui regroupe tous les catalogues de streaming).

Le resultat : chaque film revient avec la liste de ses plateformes, y compris le logo de chaque service. Netflix, Disney+, Amazon Prime — tout est la.

### Ce que ca donne concretement

Toi : **"Comedy on Netflix"**

Le traducteur genere : `genre = Comedie (35), plateforme = Netflix (8)`

Le catalogue cherche les comedies disponibles sur Netflix et renvoie :
- "Glass Onion: A Knives Out Mystery" — Netflix
- "Don't Look Up" — Netflix
- "The Wolf of Wall Street" — Netflix
- "Forrest Gump" — Netflix + Amazon Prime + Paramount+
- "KPop Demon Hunters" — Netflix

Chaque film arrive avec le logo Netflix et eventuellement d'autres plateformes ou il est aussi disponible.

---

## Changement 2 : Le curateur elimine les absurdites

### Le probleme de My Little Pony

Le Walking Skeleton a montre une faiblesse : les filtres TMDB sont **mecaniques**. Si TMDB classe My Little Pony dans "Action" et que ce dessin anime a une bonne note, il passe les filtres. Le catalogue ne "comprend" pas qu'un dessin anime de 44 minutes n'est pas un "epic action movie".

C'est comme un moteur de recherche Google qui te renvoie des resultats techniquement corrects mais absurdes. Tu tapes "jaguar rapide" et tu obtiens des articles sur la voiture ET sur l'animal. Techniquement correct, pratiquement inutile.

### La solution : une deuxieme IA qui re-examine

On cree un nouveau module, le **curateur** (`recommender.py`). Son job :

1. Recevoir les 20 films enrichis + ton humeur d'origine
2. Lire le synopsis, le genre et le ton de chaque film
3. Eliminer ceux qui ne collent clairement pas (My Little Pony pour "epic action")
4. Choisir les 5 meilleurs et les classer du plus pertinent au moins pertinent
5. Ecrire une explication personnalisee pour chacun

Le curateur utilise la meme technique que le traducteur (function calling) pour garantir un format structure. Il recoit un formulaire avec 5 emplacements a remplir : pour chacun, l'identifiant du film et l'explication.

### Comment le curateur "choisit"

On lui donne des instructions precises :

- **Priorise la coherence avec le mood.** "Light and funny for a tired couple" → favorise les films doux et droles, pas les comedies noires ou satiriques.
- **Si l'utilisateur mentionne une plateforme**, favorise les films disponibles dessus.
- **Evite les absurdites.** Un dessin anime pour enfants n'est pas un "intense thriller night", meme si TMDB le classe dans Thriller.
- **Ecris comme si tu recommandais a un ami.** Pas de jargon technique. Pas de "basé sur les filtres TMDB". Juste : "ce film est parfait pour toi parce que..."
- **Ecris dans la meme langue que l'utilisateur.** Si le mood est en francais, les explications sont en francais.

### Un exemple concret

Toi : **"Light and funny for a tired couple"**

Les 20 candidats incluent un melange de comedies : des dessins animes, des comedies romantiques, des satires, des comedies noires.

Le curateur choisit :
1. **Zootopia** — "Un film d'animation plein d'humour et de tendresse, parfait pour une soiree legere. L'histoire est entrainante et les personnages attachants — ideal pour se detendre apres une longue journee."
2. **Shrek** — "Un humour signature et des personnages charmants pour un divertissement leger — exactement ce qu'il faut pour un couple fatigue qui veut se changer les idees."
3. **The SpongeBob Movie** — "Une aventure fantaisiste dans un monde sous-marin colore. L'humour est debile et bon enfant — zero prise de tete."
4. **Eternity** — "Un film qui melange romance et humour dans une reflexion legere sur les choix de vie. Touchant sans etre lourd."
5. **The Naked Gun** — "Une comedie absurde avec des gags a la chaine. Garanti de faire rire."

Tu remarques la difference avec le Walking Skeleton : les films sont tries par pertinence, les dessins animes ultra-enfantins ne dominent plus, et chaque recommandation t'explique **pourquoi elle te correspond**.

---

## Changement 3 : Le formulaire s'enrichit

Recapitulons les changements dans le formulaire de l'IA :

| Ce qui existait deja (WS) | Ce qu'on a ajoute (Scope 1) |
|---------------------------|---------------------------|
| Genre(s) | Plateforme de streaming |
| Note minimum | |
| Duree min/max | |
| Tri (popularite, note, recence) | |
| Periode (films recents, annees 90...) | |

Un seul champ ajoute. Le gros du travail du Scope 1 n'est pas dans le traducteur — c'est dans le curateur (nouveau) et l'enrichissement (ameliore).

---

## Ce qui a merde (et ce qu'on en a appris)

### Le curateur hallucine des identifiants

Premier test du curateur : on lui donne 20 films et on lui demande d'en choisir 5. Il renvoie 5 choix... mais 2 d'entre eux ont des identifiants qui ne correspondent a aucun film de la liste. L'IA a **invente** des identifiants.

C'est un probleme connu avec les IA generatives : elles "hallucinent" — elles inventent des donnees qui n'existent pas. Dans notre cas, l'IA a probablement melange l'identifiant d'un film de la liste avec celui d'un film qu'elle connait de sa memoire.

Resultat : au lieu de 5 films, on n'en recevait que 3 (les 2 autres etaient ignores car introuvables).

**La correction :** Deux mesures.
1. On ajoute la liste exacte des identifiants valides dans le message envoye a l'IA : "Tu dois UNIQUEMENT utiliser ces identifiants : [1084242, 991494, 14874, ...]". Ca reduit le risque d'hallucination.
2. On ajoute un filet de securite : si l'IA renvoie moins de 5 films valides, on complete automatiquement avec les meilleurs candidats restants. Le systeme ne retournera jamais moins de 5 films.

Apres correction, le test "Comedy on Netflix" renvoie bien 5/5 films, tous sur Netflix.

### La latence explose

Le Walking Skeleton repondait en 2-3 secondes. Le Scope 1 repond en **17-23 secondes**. Pourquoi ?

Le calcul :
- 1 appel GPT pour le traducteur (~1-2s)
- 1 appel TMDB Discover (~0.3s)
- 20 appels TMDB Detail, un par film (~3s)
- 20 appels TMDB Watch Providers, un par film (~3s)
- 1 appel GPT pour le curateur (~2-3s)
- **Total : ~45 appels sequentiels (les uns apres les autres)**

C'est comme faire 45 coups de telephone, un par un, au lieu de les passer en meme temps. La bonne nouvelle : c'est un probleme d'optimisation, pas de conception. On peut paralleliser ces appels (les lancer en meme temps) dans un scope futur. Pour l'instant, 20 secondes est acceptable pour un side project — l'utilisateur attend une fois, pas a chaque seconde.

---

## Les resultats des tests

6 tests definis avant de coder, chacun verifiant un aspect different du pipeline complet.

| # | Ce qu'on teste | Humeur / test | Resultat | Verdict |
|---|---------------|--------------|---------|---------|
| 1 | Filtre Netflix | "Comedy on Netflix" | 5/5 films sur Netflix (Glass Onion, Don't Look Up, Forrest Gump...) | **PASS** |
| 2 | Filtre Disney+ | "Action on Disney+" | 5/5 films sur Disney+ (Avengers, Avatar, Iron Man...) | **PASS** |
| 3 | Explications | "Light and funny for a tired couple" | 5/5 explications referencent "light", "tired", "couple" | **PASS** |
| 4 | Qualite du tri | "Best thriller of the last 5 years" | #1 mieux note que #5 (Parasite, Joker dans le top 5) | **PASS** |
| 5 | Affiches de films | N'importe quel mood | 5/5 films ont une affiche valide | **PASS** |
| 6 | Fiche complete | "A great drama" | 5/5 films ont : titre, note, duree, synopsis, plateformes, explication | **PASS** |

**Gate : 6/6 PASS**

---

## Avant/apres : la difference entre le Skeleton et le Scope 1

Pour illustrer la progression, voici la meme requete traitee par le Skeleton puis par le Scope 1 :

**Requete :** "Comedy on Netflix"

### Version Walking Skeleton (avant)

```
Filtres : genre = Comedie
(pas de filtre Netflix — la plateforme est ignoree)

Films :
1. Zootopia 2 — Comedie, 7.6/10, 108 min
2. The Wrecking Crew — Comedie, 6.9/10, 124 min
3. SpongeBob Movie — Comedie, 6.7/10, 89 min
4. Try Seventeen — Comedie, 6.2/10, 96 min
5. Send Help — Comedie, 7.1/10, 113 min

Pas de plateforme. Pas d'explication. Pas de tri intelligent.
```

### Version Scope 1 (apres)

```
Filtres : genre = Comedie, plateforme = Netflix (8)

Films :
1. KPop Demon Hunters — Netflix
   "Un melange d'humour et de fantasy, leger et fun."
2. Don't Look Up — Netflix
   "Une satire mordante avec un casting exceptionnel."
3. Glass Onion: A Knives Out Mystery — Netflix
   "Un whodunit comique qui melange humour et suspense."
4. Crazy, Stupid, Love. — Netflix
   "Une comedie romantique qui explore l'amour avec charme."
5. Forrest Gump — Netflix
   "Un classique avec beaucoup d'humour et d'emotion."

Chaque film sur Netflix. Chaque film explique. Les absurdites eliminees.
```

La difference est nette : le Scope 1 est un **produit utilisable**. Le Walking Skeleton etait une preuve de concept.

---

## Ce qu'il reste a faire

Le pipeline complet fonctionne. Mais le produit n'est pas encore utilisable par quelqu'un qui n'est pas developpeur : il faut taper des commandes dans un terminal, lire du JSON brut. Personne ne va faire ca un vendredi soir.

Le Scope 2 transformera ca en un **vrai produit** :
- Un site web ou tu tapes ton humeur et tu vois 5 jolies cartes de films avec affiches
- Des badges de streaming (le logo Netflix, Disney+, etc.) sur chaque carte
- Un design moderne qui donne envie de l'utiliser
- Deploye sur internet — accessible a tout le monde, pas juste en local

C'est la transformation de "ca marche dans le terminal" a "ma femme peut l'utiliser sans instructions".
