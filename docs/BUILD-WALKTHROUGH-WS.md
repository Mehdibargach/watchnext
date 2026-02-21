# BUILD Walkthrough — Walking Skeleton

> WatchNext: tu dis ce que tu ressens, l'app te recommande 5 films.

---

## Le probleme qu'on resout

C'est vendredi soir. Tu ouvres Netflix. Tu scrolles. 10 minutes passent. Tu ouvres Disney+. Tu scrolles encore. Tu finis par mettre un truc que t'as deja vu. On est tous passes par la.

Le probleme, c'est que les plateformes te recommandent en fonction de ce que t'as **deja regarde**. Pas en fonction de ce que tu **ressens maintenant**. T'es creve apres une longue journee ? Netflix ne le sait pas. T'as envie d'un truc qui te fasse oublier le monde pendant 2 heures ? L'algorithme s'en fiche — il te propose le meme carrousel qu'hier.

WatchNext resout ca. Tu lui dis ton humeur en langage naturel — "je suis fatigue, je veux un truc drole et leger" — et il te sort 5 films qui collent.

---

## C'est quoi un Walking Skeleton ?

Avant de construire l'app complete, on commence par le **Walking Skeleton**. C'est un terme qui vient d'Alistair Cockburn (un pionnier du developpement logiciel). L'idee est simple :

**Construire la version la plus fine possible qui traverse tout le systeme de bout en bout.**

Imagine que tu veux ouvrir un restaurant. Avant de signer le bail, d'embaucher 10 serveurs et d'imprimer les menus, tu fais un test : tu prepares UN plat, tu le sers a UN client, tu vois s'il aime. Si le plat est bon, tu continues. Si le client grimace, tu sais avant d'avoir depense 100 000 euros.

Pour WatchNext, le Walking Skeleton c'est ca :

> Un mood entre en texte → 5 films sortent en reponse.

Pas d'interface graphique. Pas de "ou regarder ce film". Pas de jolies cartes avec des affiches. Juste le coeur du systeme : est-ce qu'une IA peut transformer une humeur floue en recommandations de films pertinentes ?

C'est notre **hypothese la plus risquee** (ce qu'on appelle la Riskiest Assumption dans la methode). Si ca ne marche pas, rien d'autre ne compte. Si ca marche, on construit le reste par-dessus.

---

## Comment ca marche — vue d'ensemble

Le systeme fonctionne en 3 etapes. Pour comprendre, imagine un traducteur specialise dans les films.

**Etape 1 — Le traducteur.** Tu dis "je suis fatigue, un truc drole et court". Le traducteur (une IA, GPT-4o-mini) comprend que tu veux : genre = Comedie, duree = moins de 2 heures, et il traduit ca en **criteres de recherche** que la base de films comprend.

**Etape 2 — Le catalogue.** Ces criteres sont envoyes a **TMDB** (The Movie Database) — une enorme base de donnees publique avec plus de 900 000 films. C'est comme si tu donnais une fiche de criteres a un libraire : "je veux une comedie, pas trop longue, bien notee". Le libraire revient avec 5 livres qui correspondent.

**Etape 3 — L'enrichissement.** Les films reviennent avec des infos de base (titre, note). Mais il manque des details importants comme la duree exacte ou l'affiche du film. Donc on fait un aller-retour supplementaire pour completer chaque fiche.

Voici le flux complet :

```
Toi : "je suis fatigue, un truc drole et court"
         │
         ▼
    ┌─────────────┐
    │  Traducteur  │  ← GPT-4o-mini (IA d'OpenAI)
    │  (mood_parser)│     comprend ton humeur
    └──────┬──────┘     et la traduit en criteres
           │
           │  criteres : genre=Comedie, duree<120min
           ▼
    ┌─────────────┐
    │  Catalogue   │  ← TMDB (base de 900K+ films)
    │  (tmdb_client)│    cherche les films qui matchent
    └──────┬──────┘
           │
           │  5 films avec titre, note, affiche, duree
           ▼
    Reponse : Zootopia 2, SpongeBob, Shrek...
```

**3 fichiers, 3 responsabilites :**
- `mood_parser.py` — le traducteur : comprend ton humeur, la convertit en criteres
- `tmdb_client.py` — le catalogue : interroge la base de films avec ces criteres
- `api.py` — le chef d'orchestre : recoit ta demande, appelle le traducteur puis le catalogue, te renvoie le resultat

---

## Le traducteur : comment l'IA comprend ton humeur

C'est la piece centrale. Comment faire pour qu'une IA comprenne "je suis fatigue, un truc drole" et le transforme en quelque chose d'utilisable ?

### Le probleme de la traduction libre

Si tu demandes a une IA "donne-moi des criteres de recherche pour une comedie courte", elle pourrait repondre n'importe comment :
- `"genre: comedie, duree: courte"` (texte libre, inutilisable par un programme)
- `{"genre": "Comedy", "max_runtime": 120}` (JSON, mais les noms des champs sont inventes)
- `Cherche des films droles de moins de 2h` (phrase, completement inutilisable)

C'est comme si tu demandais a un traducteur de remplir un formulaire administratif, mais sans lui donner le formulaire. Il va improviser, et chaque fois le resultat sera different.

### La solution : le formulaire pre-rempli

On utilise une technique d'OpenAI appelee **function calling**. L'idee : au lieu de demander a l'IA de generer du texte libre, on lui donne un **formulaire avec des cases precises a remplir**.

Imagine un formulaire de recherche Netflix avec des cases a cocher :
- Genre : [ ] Action [ ] Comedie [ ] Horreur [ ] Romance ...
- Note minimum : [____] / 10
- Duree max : [____] minutes
- Trier par : ( ) Popularite ( ) Meilleure note ( ) Plus recent

L'IA recoit ce formulaire et ne peut que remplir les cases. Elle ne peut pas inventer de nouvelles cases ni repondre en texte libre. Ca garantit que le resultat est toujours dans le format que le catalogue attend.

Concretement, voici les cases du formulaire :

| Case | Ce qu'elle contient | Exemple |
|------|-------------------|---------|
| Genre(s) | Numero(s) de genre TMDB | `35` = Comedie, `27` = Horreur |
| Note minimum | Note TMDB sur 10 | `6.0` (par defaut, pour eviter les mauvais films) |
| Duree min/max | En minutes | `90` min, `120` max |
| Trier par | Critere de tri | Popularite, meilleure note, plus recent |
| Periode | Dates de sortie | `2020-01-01` a `2026-12-31` pour "films recents" |

### Pourquoi des numeros pour les genres ?

TMDB n'utilise pas les mots "Comedie" ou "Horreur". Il utilise des numeros : Comedie = 35, Horreur = 27, Science-Fiction = 878. C'est comme les codes postaux — tu ne peux pas ecrire "Paris", tu dois ecrire "75000".

On donne la table de correspondance directement a l'IA dans ses instructions :

```
Action: 28, Comedie: 35, Horreur: 27, Romance: 10749,
Science-Fiction: 878, Thriller: 53, Drame: 18...
```

Comme ca, quand tu dis "un truc drole", l'IA sait que c'est le code `35`.

### Un exemple concret

Toi : **"Something mind-bending like Inception"**

L'IA comprend :
- "mind-bending" → Science-Fiction ou Thriller
- "like Inception" → Inception est un film de Sci-Fi (878) et de Thriller (53)
- Pas de mention de duree → on ne touche pas cette case
- Pas de mention de "recents" → on ne touche pas les dates

Resultat du formulaire : `genre = 878|53` (Sci-Fi OU Thriller), `note minimum = 6.0`, `tri = popularite`

Le `|` entre les numeros veut dire "OU" — on veut des films de Sci-Fi **ou** de Thriller, pas forcement les deux a la fois.

---

## Le catalogue : comment TMDB trouve les films

TMDB (The Movie Database) est une base de donnees gratuite et ouverte, maintenue par des benevoles. Elle contient plus de 900 000 films avec leurs details : titre, genres, note, duree, affiche, synopsis. C'est la meme base que des apps comme JustWatch ou Letterboxd utilisent en coulisses.

On utilise un point d'acces specifique de TMDB appele **Discover**. C'est comme un moteur de recherche avance : tu lui donnes des criteres (genre, note minimum, duree), il te renvoie les films qui correspondent.

### Le probleme des fiches incompletes

Discover renvoie les films avec des infos de base : titre, note, genres. Mais il ne renvoie pas la **duree** ni **l'affiche en haute qualite**. C'est genant, parce que si tu as dit "un truc court", on doit pouvoir verifier que les films font moins de 2 heures.

La solution : pour chaque film, on fait un appel supplementaire pour recuperer sa fiche complete (duree, affiche, synopsis complet). C'est comme si le libraire te donnait d'abord une liste de 5 titres, puis allait chercher chaque livre en rayon pour te montrer la couverture et le resume.

Au total, pour une requete avec 5 films, on fait 6 appels a TMDB :
- 1 appel Discover (la liste de films)
- 5 appels Detail (un par film, pour completer la fiche)

C'est rapide : TMDB autorise 40 appels par seconde, donc ces 6 appels prennent moins d'une demi-seconde.

---

## Le chef d'orchestre : comment tout s'assemble

`api.py` est le chef d'orchestre. C'est le point d'entree — celui qui recoit ta demande et coordonne le travail.

Le flux est lineaire :

1. Tu envoies ton humeur : `"Something funny and light, under 2 hours"`
2. Le chef d'orchestre appelle le traducteur → recoit les criteres
3. Le chef d'orchestre appelle le catalogue avec ces criteres → recoit 5 films
4. Le chef d'orchestre enrichit chaque film avec sa fiche complete
5. Le chef d'orchestre te renvoie le tout avec le temps de reponse

On utilise **FastAPI**, un framework Python qui permet de creer des points d'acces web. C'est l'equivalent d'un serveur de restaurant : il recoit les commandes (les requetes) et les achemine vers la cuisine (les modules).

---

## Les decisions qu'on a prises (et pourquoi)

### Pourquoi GPT-4o-mini et pas un modele plus puissant ?

GPT-4o-mini est le "petit modele rapide" d'OpenAI. Il coute environ $0.15 par million de mots en entree — environ 20 fois moins cher que les gros modeles. Pour notre cas — comprendre une humeur et remplir un formulaire de 7 cases — il est largement suffisant. Pas besoin d'un canon pour tuer une mouche.

### Pourquoi TMDB et pas IMDB ?

IMDB n'a pas d'API publique gratuite. TMDB est gratuit, bien documente, et offre un catalogue de 900K+ films avec des infos de streaming (sur quelle plateforme chaque film est disponible). En plus, TMDB est utilise par des apps grand public comme JustWatch — c'est donc fiable et a jour.

### Pourquoi pas de frontend pour le Skeleton ?

Le but du Walking Skeleton n'est pas de faire joli. C'est de tester l'hypothese la plus risquee le plus vite possible. L'hypothese ici : "une IA peut transformer une humeur floue en recommandations pertinentes." On n'a pas besoin d'une interface graphique pour tester ca — un simple appel en ligne de commande suffit.

Si l'hypothese ne tient pas, on aurait perdu zero temps sur le design. Si elle tient, on construit l'interface par-dessus.

---

## Ce qui a merde (et ce qu'on en a appris)

### My Little Pony dans les films d'action

Quand on a teste "Epic action movie, well-rated", le systeme a renvoye "My Little Pony: Equestria Girls - Spring Breakdown" comme film d'action bien note. Pourquoi ? Parce que TMDB le classe dans la categorie "Action" et qu'il a une note de 8.46/10.

Le systeme a fait exactement ce qu'on lui a demande : trouver des films d'action bien notes. Le probleme, c'est qu'il ne **comprend** pas ce qu'est un "epic action movie" — il se contente d'appliquer des filtres mecaniques.

**Ce qu'on en a appris :** Les filtres seuls ne suffisent pas. Il faut une deuxieme etape ou l'IA **re-examine** les resultats et elimine les incoherences. C'est exactement ce qu'on construira dans le Scope 1 : un module de re-classement intelligent.

### L'IA trouve un meilleur chemin que prevu

Pour "Epic action movie, well-rated", on attendait que l'IA mette une note minimum de 7/10. Elle a fait autrement : elle a mis la note minimum a 6, mais a trie par "meilleure note d'abord". Resultat ? Les 5 premiers films avaient tous une note superieure a 8.4 — mieux que ce qu'on esperait.

**Ce qu'on en a appris :** L'IA ne suit pas toujours le chemin qu'on prevoit, mais le resultat peut etre meilleur. C'est un comportement typique des systemes a base d'IA : on definit le "quoi" (trouve les meilleurs films d'action), l'IA choisit le "comment" (trier par note plutot que filtrer par seuil).

---

## Les resultats des tests

On a defini 5 tests avant d'ecrire le code. Chaque test prend une humeur differente et verifie que les filtres generes et les films retournes sont coherents.

| # | Humeur testee | Ce qu'on attendait | Ce que l'IA a genere | Films OK ? | Temps | Verdict |
|---|--------------|-------------------|---------------------|-----------|-------|---------|
| 1 | "Funny and light, under 2 hours" | Comedie + duree < 120 min | Comedie (35) + max 120 min | 5/5 comedies, toutes < 120 min | 3.0s | **PASS** |
| 2 | "Scary movie for Halloween" | Horreur | Horreur (27) | 5/5 films d'horreur | 2.4s | **PASS** |
| 3 | "Epic action, well-rated" | Action + note > 7.0 | Action (28) + tri par note | 5/5 action, toutes > 8.4 | 3.0s | **PASS** |
| 4 | "Romantic date night" | Romance | Romance (10749) | 5/5 films romantiques | 2.2s | **PASS** |
| 5 | "Mind-bending like Inception" | Sci-Fi ou Thriller | Sci-Fi\|Thriller (878\|53) | 5/5 sci-fi/thriller | 2.1s | **PASS** |

**Gate : 5/5 PASS**

---

## Skeleton Check — est-ce que l'hypothese tient ?

**Oui.** L'IA traduit fidelement les humeurs en criteres de recherche. Les constats :

1. **La correspondance genre fonctionne.** "Funny" → Comedie, "scary" → Horreur, "like Inception" → Sci-Fi + Thriller. Zero erreur sur les codes de genre.

2. **Les contraintes sont respectees.** "Under 2 hours" → duree max 120 min. "Recent" → films depuis 2020. L'IA comprend les contraintes implicites.

3. **Les references de films marchent.** "Like Inception" → l'IA deduit les genres du film sans qu'on ait rien programme de special. Elle connait les films.

4. **C'est rapide.** 2 a 3 secondes par requete. Largement acceptable pour une experience utilisateur (notre cible etait 5 secondes max).

**Conclusion : on continue.** L'hypothese la plus risquee est validee. On passe au Scope 1 pour ajouter les plateformes de streaming, un classement intelligent des films, et des explications personnalisees.
