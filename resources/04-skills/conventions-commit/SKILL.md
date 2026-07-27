---
name: conventions-commit
description: Applique les conventions de commit du projet (Conventional Commits en français). Utiliser dès qu'il faut rédiger, corriger ou relire un message de commit, préparer un commit, ou quand l'utilisateur mentionne commit, message de commit ou historique git.
---

# Conventions de commit

Skill « connaissance » : Claude l'applique automatiquement dès qu'un commit est en jeu.

## Format

```text
type(scope): sujet à l'impératif, sans majuscule initiale, sans point final

Corps optionnel : le POURQUOI du changement, pas le comment.
```

## Types autorisés

| Type | Usage |
|---|---|
| `feat` | Nouvelle fonctionnalité visible par l'utilisateur |
| `fix` | Correction de bug |
| `docs` | Documentation uniquement |
| `refactor` | Changement de code sans changement de comportement |
| `test` | Ajout ou correction de tests |
| `chore` | Outillage, dépendances, CI |
| `perf` | Amélioration de performance |

## Règles

1. **Sujet ≤ 72 caractères**, à l'impératif : « ajoute », « corrige », « supprime ».
2. **`scope` = le dossier ou module touché** (ex. `feat(auth):`, `fix(api):`). Adapte la liste des scopes à ton projet.
3. **Un commit = un changement logique.** Si tu dois écrire « et » dans le sujet, découpe en deux commits.
4. Le corps explique le **pourquoi** ; le diff montre déjà le comment.
5. Breaking change : ajoute `!` après le scope (`feat(api)!:`) et un paragraphe `BREAKING CHANGE:` dans le corps.
6. Jamais de `Co-Authored-By` généré automatiquement, jamais d'emoji dans le sujet.

## Exemples

```text
feat(auth): ajoute la connexion via SSO Google

Les clients entreprise exigent le SSO. On passe par OAuth 2.0
plutôt que SAML pour réutiliser le middleware existant.
```

```text
fix(api): corrige le timeout sur les exports volumineux
```

```text
refactor(paiements)!: remplace le client Stripe v8 par v12

BREAKING CHANGE: la variable d'environnement STRIPE_KEY devient
STRIPE_SECRET_KEY.
```

## Anti-exemples à refuser

- `update code` — pas de type, sujet vide de sens.
- `fix: fixed the bug.` — passé, point final, aucun contexte.
- `feat(ui): ajoute le bouton et corrige le CSS et met à jour les deps` — trois changements, trois commits.
