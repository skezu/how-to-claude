---
name: rapport-hebdo
description: Génère le rapport d'activité hebdomadaire de l'équipe à partir de l'historique git. Utiliser quand l'utilisateur demande un rapport hebdo, un point d'avancement, un résumé de la semaine ou un compte rendu d'activité.
argument-hint: "[nb-jours]"
disable-model-invocation: true
allowed-tools: Bash(git log *), Bash(git shortlog *), Read
---

# Rapport hebdomadaire

Skill « tâche » avec effets contrôlés : seul l'utilisateur peut l'invoquer
(`disable-model-invocation: true`), via `/rapport-hebdo` ou `/rapport-hebdo 14`.

## Contexte

Nombre de jours à couvrir : `$ARGUMENTS` (défaut : 7 si vide).

- Commits de la période : !`git log --since="7 days ago" --oneline --no-merges`
- Contributeurs : !`git shortlog -sn --since="7 days ago"`

## Ta tâche

1. **Lis le modèle** dans [templates/modele-rapport.md](templates/modele-rapport.md)
   et respecte exactement sa structure (progressive disclosure : ce fichier
   n'est chargé que maintenant, pas au démarrage).
2. Regroupe les commits par thème fonctionnel, pas par ordre chronologique.
   Ignore les commits `chore` sauf s'ils sont structurants.
3. Rédige en français, phrases courtes, orienté résultat (« l'export CSV
   fonctionne » plutôt que « travail sur l'export »).
4. Signale explicitement les points de blocage détectés (revert, fix en
   série sur le même fichier, commits `wip`).
5. Sauvegarde le rapport dans `rapports/rapport-YYYY-MM-DD.md` (date du jour)
   et affiche-le à l'utilisateur.

## Garde-fous

- Ne jamais inventer d'activité absente de l'historique git.
- Ne pas inclure de noms de fichiers internes sensibles (`.env`, secrets).
- Si l'historique est vide sur la période, le dire et s'arrêter.
