#!/bin/bash
# Hook PostToolUse : formate automatiquement le fichier que Claude vient d'ecrire.
#
# Evenement : PostToolUse
# Matcher   : Write|Edit
#
# Installation :
#   mkdir -p .claude/hooks
#   cp 07-hooks/formate-apres-edition.sh .claude/hooks/
#   chmod +x .claude/hooks/formate-apres-edition.sh
#   # puis reference-le dans .claude/settings.json (voir hooks-exemples.json)
#
# Le hook lit le JSON sur stdin, extrait file_path, et lance le formateur
# adapte a l'extension. S'il n'y a pas de formateur installe, il ne fait rien.
# Compatible macOS, Linux, Windows (Git Bash).

# 1. Lire tout le JSON envoye par Claude Code sur stdin
INPUT=$(cat)

# 2. Extraire file_path (sed portable, sans dependance a jq)
FILE_PATH=$(echo "$INPUT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)

# 3. Rien a faire si pas de fichier
if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# 4. Formater selon l'extension — chaque formateur est optionnel
case "$FILE_PATH" in
  *.js|*.jsx|*.ts|*.tsx|*.json|*.css|*.md)
    command -v prettier >/dev/null 2>&1 && prettier --write "$FILE_PATH" 2>/dev/null
    ;;
  *.py)
    if command -v ruff >/dev/null 2>&1; then
      ruff format "$FILE_PATH" 2>/dev/null
    elif command -v black >/dev/null 2>&1; then
      black "$FILE_PATH" 2>/dev/null
    fi
    ;;
  *.go)
    command -v gofmt >/dev/null 2>&1 && gofmt -w "$FILE_PATH" 2>/dev/null
    ;;
  *.rs)
    command -v rustfmt >/dev/null 2>&1 && rustfmt "$FILE_PATH" 2>/dev/null
    ;;
esac

# exit 0 : on n'empeche jamais l'operation, on reagit apres coup
exit 0
