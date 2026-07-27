---
name: academy-content
description: >
  Ajoute et gère le contenu de la plateforme de cours statique « Y Academy »
  (site/data.js). À utiliser quand l'utilisateur demande d'ajouter un cours,
  d'ajouter une leçon, d'ajouter une section, de créer du contenu pédagogique,
  de modifier le curriculum, de changer le branding (siteName, config) ou de
  publier un module sur la plateforme Y Academy / academy / data.js. Déclencheurs
  typiques : « ajoute un cours », « ajoute une leçon », « crée une nouvelle
  section », « publie ce README sur la plateforme », « mets à jour le nom du
  site », « vérifie data.js », « valide le contenu de l'academy ».
---

# academy-content

Ce skill gère le contenu de la plateforme de cours statique dont toutes les
données (cours, sections, leçons, branding) vivent dans un unique fichier
`site/data.js`, sous la forme :

```js
// commentaire d'en-tête
window.ACADEMY_DATA = { "config": {...}, "courses": [...] };
```

**Ne jamais éditer `data.js` à la main avec Edit/Write.** Toute modification
doit passer par le script `scripts/academy.py`, qui parse le JSON entre
`window.ACADEMY_DATA = ` et le `;` final, applique la modification en mémoire,
valide le résultat, puis réécrit le fichier avec
`json.dumps(ensure_ascii=False, indent=1)` en préservant strictement le
préfixe (commentaire + `window.ACADEMY_DATA = `) et le suffixe (`;` final) —
ce qui garantit un diff minimal et un fichier JS toujours valide.

## Schéma des données

- `config` : dictionnaire de labels/branding (`siteName`, `startLabel`,
  `academyLabel`, etc.) — toutes les valeurs sont des chaînes.
- `courses[]` : `{ id (slug unique), title, shortDescription, icon, registered (bool), sections[] }`
- `sections[]` (dans un cours) : `{ title, lessons[] }` — **pas d'id propre**,
  on les référence par titre exact ou par index (0-based).
- `lessons[]` (dans une section) : `{ id (slug unique dans le cours), title,
  num (chaîne "00".."99"), duration (chaîne ou null), html (contenu HTML de
  la leçon) }`

Les pages du site retrouvent une leçon par `(course.id, lesson.id)` en
aplatissant toutes les sections du cours — l'id de leçon doit donc être
unique **au sein d'un même cours** (l'unicité inter-cours est recommandée
mais pas strictement obligatoire).

## Prérequis

```bash
pip install markdown   # une seule fois, nécessaire pour add-lesson --markdown
```

Le script n'utilise que la stdlib Python 3 + le paquet `markdown` (extensions
`tables` et `fenced_code`).

## Localisation de data.js

Le script détecte automatiquement `site/data.js` en remontant l'arborescence
depuis le répertoire courant. Si la détection échoue, ou si plusieurs
plateformes existent dans l'environnement, précise le chemin explicitement
avec `--data <chemin/vers/site/data.js>`.

Avant toute modification, si le chemin n'est pas évident, utilise
`python3 scripts/academy.py --data <chemin> list` pour confirmer que c'est
le bon fichier (le nom des cours affichés doit correspondre à ce que
l'utilisateur attend).

## Marche à suivre générale

1. **Toujours commencer par inspecter l'état actuel** :
   ```bash
   python3 scripts/academy.py --data <chemin/site/data.js> list
   python3 scripts/academy.py --data <chemin/site/data.js> list --course <id-du-cours>
   ```
   Cela évite les doublons d'id et permet de choisir la bonne section/le bon
   index.
2. **Exécuter la ou les sous-commandes nécessaires** (voir ci-dessous). Chaque
   commande d'écriture (`add-course`, `add-section`, `add-lesson`,
   `set-config`) :
   - valide automatiquement le résultat avant d'écrire (refuse et n'écrit
     rien si la modification produirait un `data.js` invalide) ;
   - crée une sauvegarde `data.js.bak` avant d'écrire (sauf `--no-backup`) ;
   - affiche un message de confirmation avec les ids/titres créés.
3. **Toujours terminer par une validation explicite** :
   ```bash
   python3 scripts/academy.py --data <chemin/site/data.js> validate
   ```
   Corriger tout ce qui apparaît en « Erreurs » avant de considérer la tâche
   terminée. Les « Avertissements » (section vide, `duration` absente, id de
   leçon dupliqué entre deux cours différents) ne bloquent pas mais valent la
   peine d'être signalés à l'utilisateur.
4. Résumer à l'utilisateur ce qui a été ajouté/modifié, avec l'id du cours,
   de la section et de la leçon concernés, et l'URL relative pour la voir
   (`course.html?course=<id>` ou `lesson.html?course=<id>&lesson=<id>`).

## Sous-commandes

### Ajouter un cours

```bash
python3 scripts/academy.py --data <chemin> add-course \
  --id "mon-nouveau-cours" \
  --title "Titre du cours" \
  --short-description "Description courte affichée sur la page d'accueil." \
  --icon book \
  --registered
```
- `--id` doit être un slug unique (vérifié par le script, erreur sinon).
- `--registered` marque le cours comme « Inscrit » (badge sur la page
  d'accueil) ; omis par défaut (`false`).
- `--index N` insère le cours à la position N dans la liste (par défaut :
  ajouté à la fin).
- Le cours est créé avec `sections: []` (vide) — utiliser `add-section`
  ensuite.

### Ajouter une section à un cours existant

```bash
python3 scripts/academy.py --data <chemin> add-section \
  --course "mon-nouveau-cours" \
  --title "Débutant — Les fondations"
```
- `--index N` pour insérer à une position précise (par défaut : ajoutée à la
  fin des sections du cours).
- La section est créée avec `lessons: []`.

### Ajouter une leçon à une section

À partir d'un fichier Markdown fourni par l'utilisateur (converti en HTML
avec les extensions `tables` + `fenced_code`) :

```bash
python3 scripts/academy.py --data <chemin> add-lesson \
  --course "mon-nouveau-cours" \
  --section "Débutant — Les fondations" \
  --markdown "/chemin/vers/lecon.md" \
  --title "Titre de la leçon" \
  --duration "20 min"
```

À partir de contenu HTML déjà rédigé (utilisé tel quel, sans conversion) :

```bash
python3 scripts/academy.py --data <chemin> add-lesson \
  --course "mon-nouveau-cours" \
  --section 0 \
  --html "/chemin/vers/lecon.html" \
  --title "Titre de la leçon"
```

Notes :
- `--section` accepte soit le **titre exact** de la section, soit son
  **index** (0-based, ex : `0` pour la première section du cours).
- `--id` est optionnel : par défaut il est dérivé du titre (slugifié, accents
  retirés). Fournir un `--id` explicite si le titre est ambigu ou si tu veux
  reprendre une convention de nommage type `05-sous-agents`.
- `--num` est optionnel : par défaut, auto-incrémenté à partir du plus grand
  numéro déjà présent dans le cours (format `"00"`, `"01"`, ...).
- `--duration` est optionnel : omis, la leçon n'affiche pas de durée
  (`duration: null`).
- Par défaut, le script **retire le premier titre H1** du Markdown avant
  conversion (le layout de la leçon affiche déjà le titre séparément via
  `lesson.title` — garder le H1 produirait un titre en double). Utiliser
  `--keep-h1` pour désactiver ce comportement si nécessaire.
- Si le Markdown source contient des liens relatifs vers d'autres modules
  (ex. `../05-sous-agents/README.md`), ils ne sont **pas** réécrits
  automatiquement vers des liens `lesson.html?...` — à ajuster manuellement
  dans le Markdown/HTML si besoin avant conversion, selon le cours cible.
- Si aucune section ne correspond au titre donné, le script liste les titres
  de sections existants dans le message d'erreur — relire ce message avant de
  réessayer plutôt que de deviner.

### Modifier le branding / la configuration

```bash
python3 scripts/academy.py --data <chemin> set-config \
  --set siteName="Nouveau Nom" \
  --set startLabel="Démarrer"
```
- `--set clé=valeur` est répétable pour changer plusieurs clés en un seul
  appel.
- Toutes les valeurs de `config` sont des chaînes (labels de bouton, titres
  de page, etc.) — pas de valeurs booléennes/numériques dans ce dictionnaire.

### Valider l'intégrité de data.js

```bash
python3 scripts/academy.py --data <chemin> validate
```
Vérifie : que le fichier est un JSON valide encapsulé correctement dans
`window.ACADEMY_DATA = ...;`, que les ids de cours sont uniques, que chaque
section a bien un champ `lessons` (pas de « section orpheline »), que les ids
de leçon sont uniques au sein de chaque cours, que les champs requis
(`id`, `title`, `num`, `html`) sont présents sur chaque leçon. Retourne un
code de sortie non nul si des erreurs sont trouvées — à corriger avant de
considérer la tâche terminée.

### Lister le contenu existant

```bash
python3 scripts/academy.py --data <chemin> list
python3 scripts/academy.py --data <chemin> list --course "mon-nouveau-cours"
```
À utiliser en premier pour repérer les ids/titres de cours et sections
existants avant d'ajouter du contenu, et en dernier pour vérifier le résultat.

## Bonnes pratiques

- Ne jamais modifier `data.js` en édition de texte brute : toujours passer
  par ce script, qui garantit un JSON valide et un diff propre.
- Toujours lancer `validate` après une série de modifications, avant de
  répondre à l'utilisateur que la tâche est terminée.
- En cas d'erreur du script (id dupliqué, section introuvable, cours
  introuvable, fichier Markdown/HTML manquant), lire le message d'erreur
  affiché — il indique explicitement les ids/titres disponibles pour corriger
  la commande, plutôt que de re-parser `data.js` à la main.
- Le script crée une sauvegarde `data.js.bak` avant chaque écriture ; en cas
  de doute après une modification, comparer avec cette sauvegarde plutôt que
  de tout reconstruire.
- Toutes les interactions (messages du script, confirmations à
  l'utilisateur) doivent être en français, avec accents.
