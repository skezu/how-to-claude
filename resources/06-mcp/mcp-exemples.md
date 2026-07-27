# Configs MCP prêtes à copier

Chaque bloc ci-dessous est un `.mcp.json` complet (portée **project**, à commiter à la racine du repo). Le JSON n'accepte pas les commentaires : les explications sont autour des blocs. Tous les secrets passent par des variables d'environnement (`${VAR}` ou `${VAR:-defaut}`) — **jamais en dur**.

## 1. GitHub (distant, OAuth)

Serveur HTTP officiel — l'authentification OAuth se fait via `/mcp` ou `claude mcp login github`, aucun token à gérer.

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

Variante stdio avec token personnel (si tu préfères un PAT) :

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"   # scopes minimaux, read-only si possible
```

## 2. Base de données (Postgres/MySQL)

Le DSN vient de l'environnement, avec un défaut local pour le dev :

```json
{
  "mcpServers": {
    "database": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub", "--dsn", "${DATABASE_URL:-postgresql://localhost/dev}"]
    }
  }
}
```

```bash
export DATABASE_URL="postgresql://user:pass@localhost/mydb"   # compte SQL read-only recommandé
```

## 3. Filesystem (accès à un dossier hors projet)

Le dernier argument limite l'accès à ce dossier — ne donne jamais `/` ou `~` en entier :

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projets"]
    }
  }
}
```

## 4. Slack

```json
{
  "mcpServers": {
    "slack": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_TOKEN": "${SLACK_TOKEN}"
      }
    }
  }
}
```

```bash
export SLACK_TOKEN="xoxb-xxxxxxxxxxxxx"
```

## 5. Atlassian (Jira + Confluence, distant, OAuth)

```json
{
  "mcpServers": {
    "atlassian": {
      "type": "sse",
      "url": "https://mcp.atlassian.com/v1/sse"
    }
  }
}
```

Puis `claude mcp login atlassian` (ou `/mcp`) pour le flux OAuth.

## 6. API interne avec header d'auth et défauts

Montre l'expansion `${VAR}` (erreur si absente) et `${VAR:-defaut}` (fallback) dans `url` et `headers` :

```json
{
  "mcpServers": {
    "api-interne": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}",
        "X-Env": "${DEPLOY_ENV:-staging}"
      }
    }
  }
}
```

## 7. Serveur maison relatif à la racine du projet

`${CLAUDE_PROJECT_DIR}` est injecté automatiquement dans les serveurs stdio et substitué dans `command`, `args` et `env`. `"alwaysLoad": true` garde les outils toujours chargés (à réserver aux serveurs utilisés à chaque tour) :

```json
{
  "mcpServers": {
    "repo-tools": {
      "type": "stdio",
      "command": "node",
      "args": ["${CLAUDE_PROJECT_DIR}/.claude/mcp/repo-tools.js"],
      "env": {
        "REPO_ROOT": "${CLAUDE_PROJECT_DIR}"
      },
      "alwaysLoad": true
    }
  }
}
```

## 8. Setup multi-serveurs complet (workflow de reporting)

GitHub pour les métriques PR, la base pour les ventes, Slack pour poster le rapport, filesystem pour l'archiver :

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "database": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub", "--dsn", "${DATABASE_URL}"]
    },
    "slack": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_TOKEN": "${SLACK_TOKEN}"
      }
    },
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${CLAUDE_PROJECT_DIR}/reports"]
    }
  }
}
```

## Rappels

- **Windows natif** : pour les serveurs `npx`, remplace `"command": "npx"` par `"command": "cmd", "args": ["/c", "npx", "-y", "@pkg", …]`.
- Chaque membre de l'équipe devra **approuver** ces serveurs à la première utilisation (`claude mcp reset-project-choices` pour recommencer).
- Vérifie la connexion avec `/mcp` : un serveur à **0 tools** = config à corriger.
