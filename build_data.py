#!/usr/bin/env python3
"""Génère site/data.js à partir des README des 11 modules."""
import json
import re
from pathlib import Path

import markdown

ROOT = Path("/sessions/elegant-trusting-darwin/mnt/How To Claude")
OUT = ROOT / "site" / "data.js"

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


def rewrite_links(html):
    """Liens relatifs ../NN-xxx/README.md -> liens internes de leçon."""
    def repl(m):
        target = m.group(2)
        return f'href="lesson.html?course=claude-code-11-etapes&lesson={target}"'

    html = re.sub(r'href="\.\./((\d\d-[a-z-]+))/README\.md[^"]*"', repl, html)
    # Liens vers fichiers annexes du module -> désactivés proprement
    html = re.sub(r'<a href="(?!https?://|#|lesson\.html)[^"]*">([^<]*)</a>',
                  r'<code>\1</code>', html)
    return html


def convert(md_text):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    html = md.convert(md_text)
    return rewrite_links(html)


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
        html = convert(body)
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

data = {
    "config": {
        "siteName": "Y Academy",
        "academyLabel": "Y Academy",
        "academyUrl": "index.html",
        "coursesLabel": "Cours",
        "homeTitle": "Y Academy — Cours",
        "heroTitle": "Nos cours",
        "breadcrumbRoot": "Y Academy",
        "breadcrumbCourses": "Cours",
        "startLabel": "Commencer",
        "resumeLabel": "Reprendre",
        "registeredLabel": "Inscrit",
        "registerLabel": "S'inscrire | GRATUIT",
        "curriculumLabel": "Curriculum",
        "overviewLabel": "Aperçu du cours",
        "courseOverviewLabel": "Course Overview",
        "progressLabel": "{done} leçon(s) sur {total} terminée(s) ({pct}%)",
        "nextLabel": "Suivant",
        "prevLabel": "Précédent",
        "completeLabel": "Marquer comme terminé",
        "completedLabel": "Terminé ✓",
    },
    "courses": [course],
}

js = "// Données de la plateforme — généré par build_data.py, éditable à la main ou via le skill « academy-content »\n"
js += "window.ACADEMY_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
OUT.write_text(js, encoding="utf-8")
print(f"OK {OUT} ({OUT.stat().st_size/1024:.0f} KB), {len(lesson_ids)} leçons")
