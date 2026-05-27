#!/usr/bin/env python3
"""Corrige le titre du Rav sur toutes les pages :
   - "הרב יוסף חיים סממה" -> "רב יוסף חיים סממה" (sans le ה)
   - Supprime "תלמיד חכם · מעביר שיעורים בהלכה ובחסידות" (et ses variantes)
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1. Remplacements simples (avant regex)
SIMPLE_REPLACEMENTS = [
    ("הרב יוסף חיים סממה", "רב יוסף חיים סממה"),
]

# 2. Phrases a supprimer entierement
# La phrase peut etre seule, dans un <p>, suivie ou precedee de ponctuation.
# On supprime l'occurrence du texte ; les balises HTML qui l'entourent peuvent rester (vides) ou contenir d'autres choses.
PHRASES_TO_REMOVE = [
    "תלמיד חכם · מעביר שיעורים בהלכה ובחסידות",
    "תלמיד חכם — מעביר שיעורים בהלכה ובחסידות",
    "תלמיד חכם · מעביר שיעורים בהלכה",
]

# 3. Nettoyage des elements HTML restes vides apres la suppression
# Exemple : <p>תלמיד חכם · …</p> devient <p></p> ; on supprime <p></p>, <span></span>, <em></em>, etc.
EMPTY_TAG_PATTERNS = [
    re.compile(r'<p[^>]*>\s*</p>'),
    re.compile(r'<span[^>]*>\s*</span>'),
    re.compile(r'<em[^>]*>\s*</em>'),
    re.compile(r'<div class="rav-title"[^>]*>\s*</div>'),
    re.compile(r'<div class="rav-tagline"[^>]*>\s*</div>'),
    re.compile(r'<div class="rav-subtitle"[^>]*>\s*</div>'),
]


def process_file(path: Path) -> bool:
    """Renvoie True si le fichier a ete modifie."""
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    new = original

    # 1. Remplacements simples
    for old, replacement in SIMPLE_REPLACEMENTS:
        new = new.replace(old, replacement)

    # 2. Suppression des phrases
    for phrase in PHRASES_TO_REMOVE:
        new = new.replace(phrase, "")

    # 3. Nettoyer les balises restees vides
    for pattern in EMPTY_TAG_PATTERNS:
        new = pattern.sub("", new)

    if new != original:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    targets = []
    # Toutes les pages HTML du repo (hors node_modules et .git)
    for p in ROOT.rglob("*.html"):
        if any(part in {"node_modules", ".git"} for part in p.parts):
            continue
        targets.append(p)

    modified = 0
    for p in targets:
        if process_file(p):
            modified += 1

    print(f"Termine : {modified}/{len(targets)} fichiers modifies")


if __name__ == "__main__":
    main()
