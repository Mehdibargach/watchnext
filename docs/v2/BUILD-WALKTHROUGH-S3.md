# BUILD Walkthrough — Scope 3 : Le frontend — deux rails de recommandations sur la page detail

> WatchNext V2 — ML Recommendations
> Date : 2026-03-01

---

## 1. Ce que fait ce Scope

Les Scopes 1 et 2 ont construit toute la mecanique invisible : les modeles de recommandation, le module hybride, l'evaluation objective, les seuils de confiance. Tout ca tourne sur le backend — le serveur qui fait les calculs. Mais l'utilisateur, lui, ne voit rien. Il ouvre WatchNext, il cherche un film par humeur, il obtient ses 5 resultats... et c'est tout. Le systeme de recommandation de la V2 existe, mais personne ne peut y acceder.

Le Scope 3 branche la vitrine sur l'atelier. Concretement : quand tu cliques sur un film, tu arrives sur une page qui te montre les details du film (affiche, note, synopsis), et **en dessous**, deux rangees horizontales de films recommandes qu'on appelle des "rails" :

- **"Similar Movies"** — des films qui partagent les memes caracteristiques (synopsis, genres, acteurs). C'est comme parcourir le meme rayon dans un videoclub : tu as pris un thriller scandinave, le rayon te montre d'autres thrillers scandinaves.
- **"Viewers Also Liked"** — des films aimes par des spectateurs qui ont les memes gouts que toi. C'est comme demander au vendeur du videoclub : "les gens qui louent ce film, ils prennent quoi d'autre ?" Il ne regarde pas le genre ou les acteurs — il regarde les habitudes des clients.

Chaque affiche dans un rail est cliquable. Tu cliques sur un film recommande, tu atterris sur SA page detail, avec SES propres rails de recommandations. Et ainsi de suite. C'est le meme mecanisme que Wikipedia : tu cherches "Dark Knight", tu vois un lien vers "Christopher Nolan", tu cliques, tu decouvres "Memento", tu cliques encore. Une navigation infinie par curiosite.

---

## 2. Ce qui change par rapport au Scope 2

| Scope 2 | Scope 3 |
|---------|---------|
| Les recommandations existent dans le backend, accessibles uniquement par un appel technique (endpoint API — un point d'acces que les programmes interrogent, pas les humains) | Les recommandations sont visibles par l'utilisateur dans l'interface |
| Pas de page detail | Page detail complete avec rails de recommandations |
| Le PM teste en lancant des commandes dans le terminal | L'utilisateur teste en cliquant |
| Seuils de confiance definis mais pas appliques visuellement | Un rail qui n'atteint pas le seuil n'apparait tout simplement pas a l'ecran |

---

## 3. Ce qu'on a construit, etape par etape

### La page detail — le cadre

Chaque film a maintenant sa propre page. En haut : l'affiche en grand, le titre, l'annee, la note, les genres, le synopsis. C'est la vitrine classique. En dessous : les deux rails de recommandations.

Le design suit l'identite existante de WatchNext : fond sombre (#0B0F1A), accent indigo (#6366F1), typographie identique a la page d'accueil. Pas de rupture visuelle. L'utilisateur ne se dit pas "tiens, j'ai change d'application" — il reste dans le meme univers.

### Les rails — les deux etageres du videoclub

Chaque rail est une rangee horizontale d'affiches de films. Sur desktop, 5 affiches cote a cote. Sur mobile, une grille de 2 colonnes avec un bottom sheet (un panneau qui glisse depuis le bas de l'ecran quand tu cliques sur un film).

Le frontend appelle le point d'acces du backend : `GET /movie/{id}/similar`. L'API (Application Programming Interface — le contrat entre le frontend et le backend, comme un menu de restaurant : tu commandes par numero, la cuisine te sert le plat) repond avec deux listes de films. Chaque film arrive avec toutes ses informations : titre, affiche, note, annee, genres. Le frontend n'a rien a calculer — il affiche.

### La logique conditionnelle — cacher plutot que montrer du bruit

La decision prise dans le Scope 2 prend vie ici. Si le backend renvoie une liste vide pour un rail (parce que le film est trop recent, ou que le modele n'est pas assez confiant), ce rail n'apparait pas. Pas de message "aucun resultat". Pas de rangee vide. Le rail est simplement absent.

C'est le meme principe que Netflix : si l'algorithme n'a pas de recommandations fiables pour une categorie, la ligne disparait. L'utilisateur ne sait meme pas qu'elle aurait pu exister. Mieux vaut un silence que du bruit.

### Les skeleton loaders — l'attente qui ne fait pas fuir

Pendant que le backend calcule les recommandations (environ 0.5 seconde), l'utilisateur ne voit pas un ecran blanc. Il voit des cartes grises rectangulaires qui pulsent doucement — comme des emplacements reserves pour les affiches qui arrivent. On appelle ca des "skeleton loaders" (des squelettes de chargement). C'est une convention visuelle qu'on retrouve sur YouTube, LinkedIn, ou Netflix : au lieu de dire "chargement en cours...", on montre la forme de ce qui va apparaitre.

L'effet psychologique est mesurable : un squelette visuel donne l'impression que l'application charge plus vite qu'un spinner circulaire qui tourne dans le vide. L'utilisateur voit la structure de la page se remplir progressivement, pas un ecran qui attend une reponse.

### La navigation infinie — le rabbit hole

Chaque affiche dans un rail est un lien vers la page detail de ce film. Tu cliques sur "Batman Begins" dans les recommandations de "The Dark Knight", tu arrives sur la page de "Batman Begins" — avec SES propres rails. La, tu vois "The Prestige". Tu cliques. Nouveaux rails. L'exploration ne s'arrete que quand l'utilisateur decide d'arreter.

C'est le mecanisme qui transforme un outil de recherche ("je cherche un film") en outil de decouverte ("je me laisse guider"). La V1 repond a une question. La V2 ouvre des portes.

---

## 4. Comment ca a ete construit — un seul prompt Lovable

Le frontend de WatchNext est construit avec Lovable — un outil visuel qui genere du code React (le framework qui structure l'interface) a partir de descriptions en langage naturel. Concretement, tu ecris un prompt detaille, et Lovable genere les fichiers de code correspondants.

Pour le Scope 3, un seul prompt a suffi. Pas d'iteration. Pas de va-et-vient. Pourquoi ? Parce que le prompt contenait tout ce que Lovable avait besoin de savoir :

- La structure exacte de la reponse de l'API (quels champs, quels types, quels cas ou une liste peut etre vide)
- Les regles conditionnelles (si la liste est vide, ne pas afficher le rail)
- Les specs visuelles (couleurs, tailles, espacement, comportement mobile)
- Le comportement de navigation (clic sur une affiche = nouvelle page detail)

C'est l'apprentissage cle de ce Scope, et il merite qu'on s'y arrete.

---

## 5. Ce qu'on a appris

### 1. Quand l'API est bien concue, le frontend devient mecanique

Tout le travail dur a ete fait dans les Scopes 1 et 2 : structurer la reponse de l'API, decider quand une liste est vide, inclure toutes les metadonnees necessaires (affiche, note, annee — pas juste l'identifiant du film). Le frontend n'a eu aucune decision a prendre. Il recoit des donnees completes et les affiche.

C'est comme un serveur de restaurant qui recoit une assiette parfaitement dressee en cuisine. Il n'a pas a rearanger les ingredients, a verifier la cuisson, ou a ajouter une sauce. Il la pose sur la table. Si la cuisine a bien fait son travail, le service est trivial.

A l'inverse, une API mal concue force le frontend a faire des acrobaties : appeler plusieurs points d'acces, recombiner des donnees, gerer des cas d'erreur que le backend aurait du traiter. C'est le backend qui doit absorber la complexite pour que le frontend reste simple.

### 2. La qualite du prompt Lovable determine le nombre d'iterations

Sur DocuQuery AI (le side project precedent), le frontend Lovable avait demande 3 iterations de prompting. Sur WatchNext V1, c'etait pareil — plusieurs allers-retours pour corriger des details visuels et des comportements. Sur WatchNext V2 Scope 3 : une seule iteration.

La difference ? Le degre de precision du prompt. Quand tu donnes a Lovable la forme exacte de la reponse API, les regles conditionnelles ("si cette liste est vide, ne montre pas ce rail"), et les specs visuelles ("5 affiches en ligne sur desktop, grille 2 colonnes sur mobile"), il n'a pas besoin de deviner. Et quand un outil de generation de code ne devine pas, il ne se trompe pas.

C'est un pattern plus large que Lovable : plus tu es precis dans tes specs, moins tu iteres. Ca semble evident dit comme ca. Mais dans la pratique, la plupart des gens ecrivent des prompts vagues ("fais-moi une page de detail avec des recommandations") et passent 5 iterations a corriger ce que 10 minutes de specs auraient evite.

---

## 6. Resultats — 7 micro-tests, 7 PASS

| # | Ce qu'on teste | Resultat | Verdict |
|---|---------------|----------|---------|
| S3-1 | La page detail affiche les infos du film (titre, affiche, note, genres, synopsis) | Tous les champs presents et lisibles | **PASS** |
| S3-2 | Le rail "Similar Movies" affiche des affiches cliquables | 5 affiches, clic ouvre la page detail du film | **PASS** |
| S3-3 | Le rail "Viewers Also Liked" affiche des affiches cliquables | 5 affiches, clic ouvre la page detail du film | **PASS** |
| S3-4 | Navigation infinie : clic sur une reco charge SES rails | Chaque page de film a ses propres recommandations | **PASS** |
| S3-5 | Rail masque si la liste est vide | Film recent (hors MovieLens) : "Viewers Also Liked" absent, pas d'erreur | **PASS** |
| S3-6 | Skeleton loaders pendant le chargement | Cartes grises qui pulsent, remplacees par les affiches | **PASS** |
| S3-7 | Design coherent avec l'app existante (dark theme, responsive) | Desktop 5 colonnes, mobile 2 colonnes, memes couleurs, meme typo | **PASS** |

**Gate : 7/7 PASS. PM GO.**

---

## Fichiers crees / modifies

| Fichier | Action | Pourquoi |
|---------|--------|----------|
| Frontend Lovable (page detail + rails) | Cree | Tout le Scope 3 — page detail, rails, skeleton loaders, navigation |
| `docs/v2/BUILD-LOG.md` | Mis a jour | Entree Scope 3 complete |
| `docs/v2/BUILD-WALKTHROUGH-S3.md` | Cree | Ce document |

---

## Et ensuite ?

Le BUILD V2 est complet. Walking Skeleton (7/7), Scope 1 (6/6), Scope 2 (8/8), Scope 3 (7/7) — 28 micro-tests, tous PASS. Le systeme de recommandation ML est construit, evalue, et visible par l'utilisateur. Les deux rails fonctionnent. Les seuils de confiance protegent contre le bruit. La navigation infinie transforme la recherche en decouverte.

Prochaine etape : deployer le backend V2 sur Render et connecter le frontend Lovable au backend de production. Puis EVALUATE formellement sur le golden dataset.

---

*Scope 3 V2 — 2026-03-01*
*7/7 PASS — PM GO*
