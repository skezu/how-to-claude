# Règles de style « Anthropic Academy » — pour la rédaction des leçons

Règles dérivées de l'analyse stylistique des 14 leçons du cours Claude 101 (Anthropic, Skilljar). Objectif : écrire des leçons **originales en français** qui adoptent le même ton, la même structure et les mêmes procédés pédagogiques — sans jamais recopier le texte source.

## 1. Gabarit de leçon (ordre strict)

1. **Durée estimée** — première ligne : `**Durée estimée :** X minutes`.
2. **Objectifs d'apprentissage** — titre `## Objectifs d'apprentissage`, phrase d'intro « À la fin de cette leçon, tu sauras : », puis 3-5 puces commençant par un **verbe à l'infinitif** (expliquer, identifier, créer, configurer…).
3. **Points clés** (`## Points clés`) — 3-5 puces format « **Concept en gras** : développement d'une phrase ». Placé AVANT le détail : on donne la conclusion d'abord. Optionnel pour les leçons catalogues ou de clôture.
4. **Corps** — sections `##` thématiques, sous-sections `###`. La première section ouvre par une **définition directe + analogie concrète** (« Pense à X comme… »).
5. **Réflexion** (`## Réflexion`) — 2-3 questions ouvertes tournées vers la pratique du lecteur, jamais un quiz noté.
6. **La suite** (`## La suite`) — 1-2 phrases de transition nommant explicitement la leçon suivante par son titre exact.

Variantes assumées : les leçons « catalogue » (listes de cas d'usage/outils) abandonnent Points clés et Réflexion ; la leçon de clôture remplace tout par un récapitulatif du parcours + ressources + encouragement final.

## 2. Ton et voix

- **Adresse directe** en tutoiement, ton consultatif jamais injonctif : « tu peux », « pense à », « essaie » — l'impératif brut est réservé aux procédures numérotées et aux slogans de clôture.
- **Rassurant et normalisant** : un premier échec est présenté comme une étape normale du processus, jamais comme un problème.
- **Aucun alarmisme** : tout risque mentionné est immédiatement suivi d'une action corrective concrète.
- Phrases courtes déclaratives en ouverture, plus longues et énumératives dans les explications. Phrases-verdict courtes en fin de paragraphe pour marteler (« C'est tout. », « Commence simple. »).
- Le corps explicatif peut rester descriptif à la 3e personne sur Claude (« Claude lit… », « Claude est conçu pour… »), le « tu » domine dans les objectifs et scénarios.

## 3. Procédés de présentation

- **Le prompt comme unité d'exemple universelle** : chaque concept abstrait est ancré par un exemple de prompt complet « entre guillemets », éventuellement décortiqué puce par puce juste après (« Dans ce prompt : … »).
- **Bon / meilleur** : pour enseigner la qualité d'un prompt, montrer une version correcte puis une version supérieure (« "X" fonctionne, mais "X + contexte + format" est meilleur »), plutôt qu'énoncer une règle abstraite.
- **Scénarios narratifs à la 2e personne** au présent pour ancrer une fonctionnalité (« Tu es devant un dashboard inconnu… »), regroupés dans des blocs « À essayer quand : ».
- **Procédures = listes numérotées** (Étape 1, Étape 2…), avec actions d'interface concrètes. Tout le reste en puces non ordonnées.
- **Tableaux comparatifs UNIQUEMENT pour comparer** 2-3 entités concurrentes (ex. Chat/Cowork/Code, Projects/Skills, défi/cause/remède). Jamais de tableau décoratif.
- **« Pro tip »** : astuce pratique isolée, 1-2 par leçon max, paragraphe commençant par `**Pro tip :**`.
- **Exemples groupés par métier** quand pertinent (gestion de projet, communication, finance…), 3 prompts par groupe.
- **Renvois externes plutôt qu'exhaustivité** : le contenu est volontairement condensé (600-1 000 mots) ; pour approfondir, on renvoie explicitement vers le module complet du cours « Bien utiliser Claude Code » ou la documentation.

## 4. Mise en avant des idées

- Le **gras** est réservé au premier segment d'une puce (le concept) ou au nom d'une fonctionnalité à sa première mention — **jamais** de gras au milieu d'une phrase courante.
- **Répéter le message central sous 3 formes** : annoncé dans Points clés, développé dans le corps, reformulé en conclusion/tableau. Une formule-résumé mémorable par leçon (ex. « les projets stockent le savoir, les skills exécutent le processus »).
- **Continuité inter-leçons** : citer la leçon précédente/suivante par son titre exact ; reprendre mot pour mot les cadres introduits ailleurs (le triptyque de prompt, etc.).
- **Message sécurité récurrent** formulé en garde-fou rassurant : Claude n'accède qu'à ce que tu vois déjà, les permissions sont révocables à tout moment, n'installe que depuis des sources de confiance.
- **Désambiguïsation** : quand deux fonctionnalités se ressemblent, bloc « Utilise X quand… / préfère Y quand… ».

## 5. Longueurs cibles

| Type de leçon | Mots | Durée annoncée |
|---------------|------|----------------|
| Conceptuelle dense | 700-1 000 | 15-20 min |
| Procédurale/tutoriel | 800-1 000 | 20 min |
| Catalogue (cas d'usage, outils) | 350-600 | 10 min |
| Clôture | 400-500 | 5 min |

Densité décroissante vers la fin du parcours : denses au début, catalogues ensuite, clôture brève.

## 6. Interdits

- Recopier des phrases des leçons Anthropic (le style s'imite, le texte non).
- Gras au milieu d'une phrase, emojis en dehors des pastilles de niveau existantes, ton alarmiste, exclamations en rafale.
- Tableaux hors comparaison, listes à puces de plus de 6 items sans regroupement.
- Développer in extenso ce qu'un renvoi vers le module complet couvre déjà.
