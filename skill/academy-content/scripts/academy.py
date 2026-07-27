#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
academy.py — outil en ligne de commande pour gérer le contenu de la plateforme
« Y Academy » (site statique piloté par site/data.js).

Sous-commandes :
  add-course     Ajoute un nouveau cours (sections vides par défaut)
  add-section    Ajoute une section (chapitre) à un cours existant
  add-lesson     Ajoute une leçon à une section, à partir de Markdown ou de HTML
  set-config     Modifie une ou plusieurs clés de config (branding)
  validate       Vérifie l'intégrité de data.js (JSON valide, ids uniques, etc.)
  list           Liste les cours, ou les sections/leçons d'un cours donné

Le fichier data.js a la forme :
    // commentaire...
    window.ACADEMY_DATA = { ... JSON ... };

Ce script préserve strictement le préfixe (commentaire + « window.ACADEMY_DATA = »)
et le suffixe (« ; » + retour à la ligne final) du fichier, et ne réécrit que le
bloc JSON, avec json.dumps(ensure_ascii=False, indent=1).

Dépendances : Python 3 (stdlib) + le paquet « markdown » (pip install markdown)
uniquement nécessaire pour add-lesson --markdown.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Localisation et (dé)sérialisation de data.js
# ---------------------------------------------------------------------------

# Capture (prefix)(body JSON)(suffix). Les deux premiers groupes sont non
# gourmands ; comme le regex est ancré sur toute la chaîne (^...$, re.DOTALL),
# le moteur n'accepte le suffixe que lorsqu'il correspond réellement à la toute
# fin du fichier — ce qui isole systématiquement le DERNIER « ; » du fichier,
# même si du HTML/JS embarqué dans les leçons contient lui-même des « }; ».
DATA_JS_RE = re.compile(
    r"^(?P<prefix>.*?window\.ACADEMY_DATA\s*=\s*)(?P<body>.*)(?P<suffix>;\s*)$",
    re.DOTALL,
)


class AcademyError(Exception):
    """Erreur métier destinée à être affichée proprement à l'utilisateur."""


def find_data_path(explicit):
    """Localise data.js : chemin explicite, sinon détection automatique."""
    if explicit:
        p = Path(explicit)
        if not p.exists():
            raise AcademyError(f"Fichier introuvable : {p}")
        return p

    cur = Path.cwd()
    for _ in range(8):
        candidate = cur / "site" / "data.js"
        if candidate.exists():
            return candidate
        if (cur / "data.js").exists() and cur.name == "site":
            return cur / "data.js"
        if cur.parent == cur:
            break
        cur = cur.parent

    candidate = Path.cwd() / "data.js"
    if candidate.exists():
        return candidate

    raise AcademyError(
        "Impossible de localiser data.js automatiquement. "
        "Précisez le chemin avec --data <chemin/vers/site/data.js>."
    )


def load_data(path: Path):
    """Retourne (prefixe, suffixe, dict JSON parsé)."""
    text = path.read_text(encoding="utf-8")
    m = DATA_JS_RE.match(text)
    if not m:
        raise AcademyError(
            f"{path} : structure inattendue — motif "
            "« window.ACADEMY_DATA = { ... }; » introuvable."
        )
    prefix, body, suffix = m.group("prefix"), m.group("body"), m.group("suffix")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise AcademyError(f"{path} : JSON invalide dans ACADEMY_DATA ({e})") from e
    return prefix, suffix, data


def save_data(path: Path, prefix: str, suffix: str, data: dict, backup: bool = True) -> None:
    """Réécrit data.js en conservant préfixe/suffixe d'origine."""
    if backup:
        bak = path.with_suffix(path.suffix + ".bak")
        shutil.copyfile(path, bak)
    body = json.dumps(data, ensure_ascii=False, indent=1)
    path.write_text(prefix + body + suffix, encoding="utf-8")


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Transforme un titre en identifiant-slug (minuscules, tirets, sans accents)."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text or "sans-titre"


def find_course(data: dict, course_id: str) -> dict:
    for c in data.get("courses", []):
        if c.get("id") == course_id:
            return c
    ids = ", ".join(c.get("id", "?") for c in data.get("courses", []))
    raise AcademyError(f"Cours « {course_id} » introuvable. Cours existants : {ids or '(aucun)'}")


def find_section(course: dict, section_ref: str) -> dict:
    """Résout une section par index numérique (0-based) ou par titre exact."""
    sections = course.setdefault("sections", [])
    if section_ref.isdigit():
        idx = int(section_ref)
        if 0 <= idx < len(sections):
            return sections[idx]
        raise AcademyError(
            f"Index de section {idx} hors limites (le cours a {len(sections)} section(s))."
        )
    matches = [s for s in sections if s.get("title") == section_ref]
    if not matches:
        titles = ", ".join(f'"{s.get("title")}"' for s in sections)
        raise AcademyError(
            f"Section « {section_ref} » introuvable. Sections existantes : {titles or '(aucune)'}"
        )
    if len(matches) > 1:
        print(
            f"! Attention : plusieurs sections partagent le titre « {section_ref} », "
            "la première est utilisée (précisez un index pour lever l'ambiguïté).",
            file=sys.stderr,
        )
    return matches[0]


def next_lesson_num(course: dict) -> str:
    """Calcule le prochain numéro de leçon (2 chiffres) à partir du max existant."""
    best = -1
    for section in course.get("sections", []):
        for lesson in section.get("lessons", []):
            raw = lesson.get("num")
            if raw is not None and str(raw).isdigit():
                best = max(best, int(raw))
    nxt = best + 1
    return f"{nxt:02d}"


def convert_markdown(md_text: str, strip_h1: bool = True) -> str:
    """Convertit du Markdown en HTML avec les extensions tables + fenced_code."""
    try:
        import markdown
    except ImportError as e:
        raise AcademyError(
            "Le paquet Python « markdown » est requis pour --markdown "
            "(installez-le avec : pip install markdown)"
        ) from e

    if strip_h1:
        md_text = re.sub(r"^\s*#\s+.*\n?", "", md_text, count=1)

    md = markdown.Markdown(extensions=["tables", "fenced_code"])
    return md.convert(md_text)


def read_content_arg(markdown_path, html_path, keep_h1: bool) -> str:
    if bool(markdown_path) == bool(html_path):
        raise AcademyError("Précisez exactement une source : --markdown OU --html.")
    if markdown_path:
        p = Path(markdown_path)
        if not p.exists():
            raise AcademyError(f"Fichier Markdown introuvable : {p}")
        return convert_markdown(p.read_text(encoding="utf-8"), strip_h1=not keep_h1)
    p = Path(html_path)
    if not p.exists():
        raise AcademyError(f"Fichier HTML introuvable : {p}")
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Sous-commandes
# ---------------------------------------------------------------------------

def cmd_add_course(args, data: dict) -> str:
    for c in data.get("courses", []):
        if c.get("id") == args.id:
            raise AcademyError(f"Un cours avec l'id « {args.id} » existe déjà.")

    course = {
        "id": args.id,
        "title": args.title,
        "shortDescription": args.short_description or "",
        "icon": args.icon or "book",
        "registered": bool(args.registered),
        "sections": [],
    }
    courses = data.setdefault("courses", [])
    if args.index is not None:
        courses.insert(max(0, min(args.index, len(courses))), course)
    else:
        courses.append(course)
    return f"Cours ajouté : « {course['title']} » (id={course['id']})"


def cmd_add_section(args, data: dict) -> str:
    course = find_course(data, args.course)
    section = {"title": args.title, "lessons": []}
    sections = course.setdefault("sections", [])
    if args.index is not None:
        sections.insert(max(0, min(args.index, len(sections))), section)
    else:
        sections.append(section)
    return (
        f"Section ajoutée au cours « {course['title']} » : « {args.title} » "
        f"(position {sections.index(section)})"
    )


def cmd_add_lesson(args, data: dict) -> str:
    course = find_course(data, args.course)
    section = find_section(course, args.section)

    html = read_content_arg(args.markdown, args.html, args.keep_h1)

    lesson_id = args.id or slugify(args.title)
    existing_ids = {
        l.get("id") for s in course.get("sections", []) for l in s.get("lessons", [])
    }
    if lesson_id in existing_ids:
        raise AcademyError(
            f"Une leçon avec l'id « {lesson_id} » existe déjà dans ce cours. "
            "Précisez --id pour en choisir un autre."
        )

    lesson = {
        "id": lesson_id,
        "title": args.title,
        "num": args.num if args.num is not None else next_lesson_num(course),
        "duration": args.duration,
        "html": html,
    }
    lessons = section.setdefault("lessons", [])
    if args.index is not None:
        lessons.insert(max(0, min(args.index, len(lessons))), lesson)
    else:
        lessons.append(lesson)
    return (
        f"Leçon ajoutée : « {lesson['title']} » (id={lesson_id}, num={lesson['num']}) "
        f"dans « {course['title']} » / « {section['title']} »"
    )


def cmd_set_config(args, data: dict) -> str:
    config = data.setdefault("config", {})
    if not args.set:
        raise AcademyError("Précisez au moins une paire --set clé=valeur.")
    changed = []
    for pair in args.set:
        if "=" not in pair:
            raise AcademyError(f"Format invalide « {pair} » (attendu : clé=valeur)")
        key, value = pair.split("=", 1)
        key = key.strip()
        old = config.get(key)
        config[key] = value
        changed.append(f"{key}: {old!r} -> {value!r}")
    return "Configuration mise à jour :\n  " + "\n  ".join(changed)


def _validate(data: dict):
    errors = []
    warnings = []

    if "config" not in data or not isinstance(data["config"], dict):
        errors.append("Clé « config » manquante ou invalide.")
    if "courses" not in data or not isinstance(data["courses"], list):
        errors.append("Clé « courses » manquante ou invalide (attendu une liste).")
        return errors, warnings

    course_ids = set()
    all_lesson_ids = {}

    for ci, course in enumerate(data["courses"]):
        label = f"courses[{ci}]"
        for field in ("id", "title", "sections"):
            if field not in course:
                errors.append(f"{label} : champ requis manquant « {field} ».")
        cid = course.get("id", f"?{ci}")
        label = f"cours « {cid} »"
        if cid in course_ids:
            errors.append(f"Id de cours dupliqué : « {cid} ».")
        else:
            course_ids.add(cid)

        sections = course.get("sections")
        if not isinstance(sections, list):
            errors.append(f"{label} : « sections » doit être une liste.")
            continue

        lesson_ids_in_course = set()
        for si, section in enumerate(sections):
            slabel = f"{label} / section[{si}]"
            if "title" not in section:
                errors.append(f"{slabel} : champ « title » manquant.")
            if "lessons" not in section:
                errors.append(f"{slabel} : section orpheline — champ « lessons » manquant.")
                continue
            lessons = section.get("lessons") or []
            if not isinstance(lessons, list):
                errors.append(f"{slabel} : « lessons » doit être une liste.")
                continue
            if not lessons:
                warnings.append(f"{slabel} (« {section.get('title')} ») : section vide (0 leçon).")
            for li, lesson in enumerate(lessons):
                llabel = f"{slabel} / lesson[{li}]"
                required = {"id", "title", "num", "html"}
                missing = required - set(lesson.keys())
                if missing:
                    errors.append(f"{llabel} : champ(s) manquant(s) {sorted(missing)}.")
                    continue
                lid = lesson["id"]
                if lid in lesson_ids_in_course:
                    errors.append(f"{label} : id de leçon dupliqué au sein du cours : « {lid} ».")
                else:
                    lesson_ids_in_course.add(lid)
                if lid in all_lesson_ids and all_lesson_ids[lid] != cid:
                    warnings.append(
                        f"Id de leçon « {lid} » utilisé à la fois dans « {all_lesson_ids[lid]} » "
                        f"et « {cid} » (pas bloquant, mais déconseillé)."
                    )
                all_lesson_ids.setdefault(lid, cid)
                if "duration" not in lesson:
                    warnings.append(f"{llabel} (« {lid} ») : champ « duration » absent (utiliser null si inconnu).")
                num = lesson.get("num")
                if not (isinstance(num, str) and num.isdigit()):
                    warnings.append(f"{llabel} (« {lid} ») : « num » attendu sous forme de chaîne numérique, reçu {num!r}.")

    return errors, warnings


def cmd_validate(args, data: dict) -> str:
    errors, warnings = _validate(data)
    lines = []
    if warnings:
        lines.append(f"Avertissements ({len(warnings)}) :")
        lines += [f"  - {w}" for w in warnings]
    if errors:
        lines.append(f"Erreurs ({len(errors)}) :")
        lines += [f"  - {e}" for e in errors]
        lines.append("RÉSULTAT : INVALIDE")
        print("\n".join(lines))
        raise SystemExit(1)
    lines.append("RÉSULTAT : OK — data.js est valide.")
    return "\n".join(lines)


def cmd_list(args, data: dict) -> str:
    lines = []
    if args.course:
        course = find_course(data, args.course)
        lines.append(f"Cours « {course['title']} » (id={course['id']}, registered={course.get('registered')})")
        for si, section in enumerate(course.get("sections", [])):
            lines.append(f"  [{si}] Section : {section.get('title')} ({len(section.get('lessons', []))} leçon(s))")
            for li, lesson in enumerate(section.get("lessons", [])):
                lines.append(
                    f"       [{li}] {lesson.get('num')} — {lesson.get('title')} "
                    f"(id={lesson.get('id')}, duration={lesson.get('duration')})"
                )
    else:
        courses = data.get("courses", [])
        if not courses:
            return "Aucun cours."
        for course in courses:
            nb_sections = len(course.get("sections", []))
            nb_lessons = sum(len(s.get("lessons", [])) for s in course.get("sections", []))
            lines.append(
                f"- {course.get('id')} : « {course.get('title')} » "
                f"({nb_sections} section(s), {nb_lessons} leçon(s), registered={course.get('registered')})"
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

READ_ONLY_COMMANDS = {"validate", "list"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="academy.py",
        description="Gère le contenu de la plateforme Y Academy (site/data.js).",
    )
    p.add_argument("--data", help="Chemin vers site/data.js (détection automatique si omis)")
    p.add_argument("--no-backup", action="store_true", help="Ne pas créer de data.js.bak avant écriture")

    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("add-course", help="Ajoute un nouveau cours")
    sp.add_argument("--id", required=True, help="Identifiant (slug) unique du cours")
    sp.add_argument("--title", required=True, help="Titre affiché du cours")
    sp.add_argument("--short-description", default="", help="Description courte (page d'accueil)")
    sp.add_argument("--icon", default="book", help="Icône du cours (défaut: book)")
    sp.add_argument("--registered", action="store_true", help="Marquer le cours comme « Inscrit »")
    sp.add_argument("--index", type=int, default=None, help="Position d'insertion (défaut: fin de liste)")
    sp.set_defaults(func=cmd_add_course)

    sp = sub.add_parser("add-section", help="Ajoute une section à un cours existant")
    sp.add_argument("--course", required=True, help="Id du cours")
    sp.add_argument("--title", required=True, help="Titre de la section")
    sp.add_argument("--index", type=int, default=None, help="Position d'insertion (défaut: fin de liste)")
    sp.set_defaults(func=cmd_add_section)

    sp = sub.add_parser("add-lesson", help="Ajoute une leçon à une section")
    sp.add_argument("--course", required=True, help="Id du cours")
    sp.add_argument("--section", required=True, help="Titre exact de la section, ou son index (0-based)")
    sp.add_argument("--markdown", help="Fichier Markdown source (converti en HTML)")
    sp.add_argument("--html", help="Fichier HTML source (utilisé tel quel)")
    sp.add_argument("--keep-h1", action="store_true", help="Ne pas retirer le titre H1 du Markdown avant conversion")
    sp.add_argument("--title", required=True, help="Titre de la leçon")
    sp.add_argument("--duration", default=None, help='Durée affichée (ex: "30 min"), omis = aucune durée')
    sp.add_argument("--id", default=None, help="Id (slug) de la leçon (défaut: dérivé du titre)")
    sp.add_argument("--num", default=None, help='Numéro affiché, ex "05" (défaut: auto-incrémenté)')
    sp.add_argument("--index", type=int, default=None, help="Position dans la section (défaut: fin de liste)")
    sp.set_defaults(func=cmd_add_lesson)

    sp = sub.add_parser("set-config", help="Modifie une ou plusieurs clés de config")
    sp.add_argument(
        "--set", action="append", metavar="CLE=VALEUR",
        help="Paire clé=valeur à définir dans config (répétable)",
    )
    sp.set_defaults(func=cmd_set_config)

    sp = sub.add_parser("validate", help="Valide l'intégrité de data.js")
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("list", help="Liste les cours, ou le détail d'un cours")
    sp.add_argument("--course", default=None, help="Id du cours à détailler (défaut: liste tous les cours)")
    sp.set_defaults(func=cmd_list)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        path = find_data_path(args.data)
        prefix, suffix, data = load_data(path)
        message = args.func(args, data)
        if args.command not in READ_ONLY_COMMANDS:
            errors, _warnings = _validate(data)
            if errors:
                print("! Écriture annulée : la modification produirait un data.js invalide :", file=sys.stderr)
                for e in errors:
                    print(f"  - {e}", file=sys.stderr)
                return 1
            save_data(path, prefix, suffix, data, backup=not args.no_backup)
            print(f"OK — {path} mis à jour" + ("" if args.no_backup else f" (sauvegarde : {path}.bak)"))
        print(message)
        return 0
    except AcademyError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1
    except SystemExit as e:
        return int(e.code) if e.code is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
