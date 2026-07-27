#!/usr/bin/env python3
"""Génère les leçons du cours claude-code-11-etapes dans site/data.js à partir
des README des 11 modules.

Ce script ne touche QU'à l'entrée `courses[]` dont l'id est
`claude-code-11-etapes` : il préserve tel quel le reste de data.js (config,
autres cours comme `claude-code-101`), en s'appuyant sur le même mécanisme de
préfixe/suffixe que le skill « academy-content » (scripts/academy.py).
"""
import json
import re
import shutil
from pathlib import Path

import markdown

# Le script vit dans <racine-projet>/site/build_data.py
SITE_DIR = Path(__file__).resolve().parent
ROOT = SITE_DIR.parent
OUT = SITE_DIR / "data.js"
RESOURCES_DIR = SITE_DIR / "resources"

DATA_JS_RE = re.compile(
    r"^(?P<prefix>.*?window\.ACADEMY_DATA\s*=\s*)(?P<body>.*)(?P<suffix>;\s*)$",
    re.DOTALL,
)

MODULES = [
    ("00-decouvrir-claude", "Découvrir Claude : Chat, Cowork ou Code ?"),
    ("01-demarrer-claude-code", "Démarrer avec Claude Code"),
    ("02-memoire-claude-md", "Mémoire & CLAUDE.md"),
    ("03-commandes-slash", "Commandes slash"),
    ("04-skills", "Skills"),
    ("05-sous-agents", "Sous-agents"),
    ("06-mcp", "MCP (Model Context Protocol)"),
    ("07-hooks", "Hooks"),
    ("08-plugins", "Plugins"),
    ("09-tips-avances", "Tips avancés"),
    ("10-entreprise", "Claude en entreprise"),
]

SECTIONS = [
    ("Débutant — Les fondations", [0, 1, 2, 3]),
    ("Intermédiaire — Étendre Claude", [4, 5, 6, 7, 8]),
    ("Avancé — Maîtriser et déployer", [9, 10]),
]

slug_by_dir = {d: d for d, _ in MODULES}


def extract_meta(text):
    """Durée si présente dans l'en-tête du module."""
    m = re.search(r"Durée\**\s*:\s*~?\s*([\d,]+\s*(?:h|min)[^·\n*]*)", text)
    return m.group(1).strip() if m else None


def rewrite_links(html, module_dir):
    """Réécrit les liens relatifs d'une leçon :
    - ../NN-xxx/README.md -> lien interne vers une autre leçon du cours ;
    - fichier annexe du module (ex. agents/relecteur-code.md) -> lien
      cliquable vers site/resources/<module_dir>/<chemin>, s'il a bien été
      copié à cet endroit (sinon neutralisé en <code> avec un avertissement,
      pour ne jamais publier un lien mort silencieusement).
    """
    def repl_lesson(m):
        target = m.group(2)
        return f'href="lesson.html?course=claude-code-11-etapes&lesson={target}"'

    html = re.sub(r'href="\.\./((\d\d-[a-z-]+))/README\.md[^"]*"', repl_lesson, html)

    def repl_resource(m):
        href, text = m.group(1), m.group(2)
        dest = RESOURCES_DIR / module_dir / href
        if dest.exists():
            return f'<a href="resources/{module_dir}/{href}">{text}</a>'
        print(f"! lien annexe introuvable, neutralisé : {module_dir} -> {href}")
        return f'<code>{text}</code>'

    html = re.sub(
        r'<a href="(?!https?://|#|lesson\.html)([^"]*)">(.*?)</a>',
        repl_resource,
        html,
        flags=re.DOTALL,
    )
    return html


def convert(md_text, module_dir):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    html = md.convert(md_text)
    # Illustrations : ../illustrations/NN_xxx.svg -> illustrations/NN_xxx.svg
    # (site/illustrations/ est à la racine servie, pas besoin de remonter)
    html = re.sub(r'(src="|src=\')\.\./illustrations/', r'\1illustrations/', html)
    return rewrite_links(html, module_dir)


lessons_flat = {}
sections_js = []
lesson_ids = []

for sec_title, idxs in SECTIONS:
    sec = {"title": sec_title, "lessons": []}
    for i in idxs:
        d, title = MODULES[i]
        text = (ROOT / d / "README.md").read_text(encoding="utf-8")
        # retire le H1 (réaffiché par le layout leçon)
        body = re.sub(r"^#\s+.*\n", "", text, count=1)
        duration = extract_meta(text)
        html = convert(body, d)
        lesson = {
            "id": d,
            "title": title,
            "num": d.split("-")[0],
            "duration": duration,
            "html": html,
        }
        sec["lessons"].append(lesson)
        lesson_ids.append(d)
    sections_js.append(sec)

course = {
    "id": "claude-code-11-etapes",
    "title": "Bien utiliser Claude Code",
    "shortDescription": "Le parcours complet en 11 étapes pour maîtriser Claude Code : "
    "du premier prompt jusqu'à l'orchestration de sous-agents et au déploiement en entreprise.",
    "icon": "book",
    "registered": True,
    "sections": sections_js,
}

# --- Fusion dans data.js existant --------------------------------------
# On ne régénère QUE le cours claude-code-11-etapes ; tout le reste de
# data.js (config, autres cours comme claude-code-101) est préservé tel
# quel, à l'identique du mécanisme prefix/suffix de scripts/academy.py.
if not OUT.exists():
    raise SystemExit(f"{OUT} introuvable — ce script ne fait que mettre à jour "
                      "un data.js existant, il ne le crée pas de zéro.")

existing_text = OUT.read_text(encoding="utf-8")
m = DATA_JS_RE.match(existing_text)
if not m:
    raise SystemExit(f"{OUT} : structure inattendue — motif "
                      "« window.ACADEMY_DATA = { ... }; » introuvable.")
prefix, suffix = m.group("prefix"), m.group("suffix")
data = json.loads(m.group("body"))

courses = data.setdefault("courses", [])
replaced = False
for idx, c in enumerate(courses):
    if c.get("id") == "claude-code-11-etapes":
        courses[idx] = course
        replaced = True
        break
if not replaced:
    courses.append(course)

backup = OUT.with_suffix(OUT.suffix + ".bak")
shutil.copyfile(OUT, backup)

body = json.dumps(data, ensure_ascii=False, indent=1)
OUT.write_text(prefix + body + suffix, encoding="utf-8")
print(f"OK {OUT} ({OUT.stat().st_size/1024:.0f} KB), {len(lesson_ids)} leçons "
      f"régénérées pour claude-code-11-etapes (sauvegarde : {backup})")
print(f"Cours présents dans data.js : {[c.get('id') for c in courses]}")
