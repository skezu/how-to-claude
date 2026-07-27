# Bloc à copier dans ton CLAUDE.md

Copie le bloc ci-dessous tel quel dans le CLAUDE.md de ton projet (après avoir installé les agents [`quick-fixer`](agents/quick-fixer.md), [`implementer`](agents/implementer.md) et [`architect`](agents/architect.md) dans `.claude/agents/`).

```markdown
## Délégation par complexité

Avant toute tâche, évalue sa complexité et délègue au bon agent :

- Édition mécanique (renommage, remplacement, typo, formatage, déplacement
  de fichier) → agent `quick-fixer`
- Implémentation bien définie (fonction, endpoint, test, refacto localisé,
  bug à cause connue) → agent `implementer`
- Conception, bug complexe à cause inconnue, décision structurante →
  agent `architect`, puis implémentation par `implementer`

Règles :
- En cas de doute entre deux niveaux, choisis le niveau supérieur.
- Ne délègue pas si la tâche dépend fortement du contexte de la conversation
  en cours (le sous-agent ne voit pas l'historique).
- Après délégation, vérifie le résultat avant de me répondre.

## Efficacité tokens

- Ne relis pas les fichiers que tu viens d'écrire ou de modifier.
- Ne résume pas ce que tu viens de faire, sauf ambiguïté.
- Ne recopie pas de gros blocs de code dans tes réponses, sauf demande.
```
