#!/usr/bin/env python3
"""Hook PreToolUse : bloque les commandes shell dangereuses et protege les fichiers sensibles.

Evenement : PreToolUse
Matcher   : Bash (commandes) + Read|Edit|Write (fichiers sensibles)

Installation :
    mkdir -p .claude/hooks
    cp 07-hooks/bloque-commandes-dangereuses.py .claude/hooks/
    # puis reference-le dans .claude/settings.json (voir hooks-exemples.json)

Protocole :
    - Entree  : JSON sur stdin (tool_name, tool_input, session_id, cwd...)
    - exit 0  : autoriser (stdout peut contenir du JSON avance)
    - exit 2  : bloquer (stderr est renvoye a Claude comme raison du blocage)

Test en isolation :
    echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' \
      | python3 bloque-commandes-dangereuses.py ; echo "exit=$?"
"""
import json
import re
import sys

# Commandes bloquees sans discussion : quasi toujours destructrices.
COMMANDES_BLOQUEES = [
    (r"\brm\s+-rf\s+/(\s|$)", "rm -rf / (suppression de la racine)"),
    (r"\brm\s+-rf\s+\*", "rm -rf * (suppression massive)"),
    (r"\bsudo\s+rm\b", "sudo rm (suppression en root)"),
    (r"\bdd\s+if=/dev/(zero|random)", "dd sur un device (ecrasement disque)"),
    (r":\(\)\{\s*:\|:&\s*\};:", "fork bomb"),
    (r"\bmkfs\.", "mkfs (formatage de systeme de fichiers)"),
    (r"\bgit\s+push\s+.*--force\b", "git push --force"),
    (r"\bDROP\s+(TABLE|DATABASE)\b", "DROP TABLE/DATABASE"),
    (r"curl\s+[^|]*\|\s*(ba)?sh", "curl | sh (execution de script distant)"),
]

# Fichiers sensibles : lecture/ecriture refusee via la sortie JSON avancee.
FICHIERS_SENSIBLES = [
    r"\.env(\.|$)",
    r"\.ssh/",
    r"id_rsa",
    r"\.aws/credentials",
    r"secrets?\.(json|ya?ml)$",
]


def main() -> None:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # --- Cas 1 : commandes Bash dangereuses -> exit 2 (blocage simple) ---
    if tool_name == "Bash":
        commande = tool_input.get("command", "")
        for motif, raison in COMMANDES_BLOQUEES:
            if re.search(motif, commande, re.IGNORECASE):
                # stderr = raison du blocage, renvoyee a Claude
                print(f"Commande bloquee : {raison}", file=sys.stderr)
                print(f"Commande : {commande}", file=sys.stderr)
                sys.exit(2)
        sys.exit(0)

    # --- Cas 2 : acces a un fichier sensible -> deny via JSON avance ---
    if tool_name in ("Read", "Edit", "Write"):
        chemin = tool_input.get("file_path", "")
        for motif in FICHIERS_SENSIBLES:
            if re.search(motif, chemin):
                sortie = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f"Fichier sensible protege par un hook : {chemin}"
                        ),
                    }
                }
                print(json.dumps(sortie))
                sys.exit(0)  # exit 0 : c'est le JSON qui porte la decision

    sys.exit(0)


if __name__ == "__main__":
    main()
