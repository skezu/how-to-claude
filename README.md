# Y Academy — plateforme de cours locale

Réplique fidèle de l'UX/UI de la plateforme Anthropic Courses (Skilljar), alimentée par le guide « Bien utiliser Claude Code » en 11 étapes. Aucun serveur requis : ouvre simplement `index.html` dans un navigateur.

## Pages

| Fichier | Rôle | Équivalent cible |
|---------|------|------------------|
| `index.html` | Liste des cours (cartes) | anthropic.skilljar.com |
| `course.html?course=ID` | Fiche cours : hero, progression, curriculum dépliable | /claude-101 |
| `lesson.html?course=ID&lesson=ID` | Leçon : sidebar 420 px + contenu + navigation Précédent/Suivant | /claude-101/xxxx |

La progression (leçons terminées, marque-page) est stockée dans le `localStorage` du navigateur. Cliquer « Suivant » marque la leçon comme terminée, comme sur le site cible.

## Personnalisation

Tout vit dans `data.js` (`window.ACADEMY_DATA`) :

- **Branding** : `config.siteName`, labels des boutons, fils d'Ariane… — modifie et recharge.
- **Cours / sections / leçons** : le tableau `courses[]`. Chaque leçon contient son HTML.
- **Design** : variables CSS en tête de `styles.css` (couleurs, polices). Les tokens actuels sont ceux mesurés sur le site cible : canvas `#faf9f5`, encre `#141413`, sidebar `#f0eee6`, bleu `#0164cc`, bouton sombre `#2c2b25`.

## Ajouter du contenu : le skill `academy-content`

Le dossier `skill/academy-content/` contient un skill Claude (aussi packagé en `.skill` installable) qui pilote `scripts/academy.py` :

```bash
python3 skill/academy-content/scripts/academy.py list
python3 skill/academy-content/scripts/academy.py add-course --id mon-cours --title "Mon cours"
python3 skill/academy-content/scripts/academy.py add-section --course mon-cours --title "Partie 1"
python3 skill/academy-content/scripts/academy.py add-lesson --course mon-cours --section "Partie 1" \
  --title "Ma leçon" --markdown lecon.md --duration "45 min"
python3 skill/academy-content/scripts/academy.py validate
```

Le script sauvegarde un `.bak` avant chaque écriture et valide la cohérence (ids uniques, JSON parsable) avant d'enregistrer.

## Régénérer data.js depuis les modules

Si les README des modules 00-10 évoluent, régénère l'intégralité des leçons :

```bash
python3 ../scripts/build_epub.py   # (EPUB, inchangé)
# et pour le site :
python3 build_data.py              # si copié ici, sinon relancer la conversion
```

> Note : `data.js` est généré à partir des `README.md` des modules — ne pas y éditer le HTML des leçons à la main si le module source doit rester la référence.
