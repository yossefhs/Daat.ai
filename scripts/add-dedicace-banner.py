#!/usr/bin/env python3
"""Injecte le bandeau de dédicaces en haut du <body> de chaque page de siman.

Ajoute, juste après la balise <body...> ouvrante, la ligne :
    <script src="/assets/js/dedicace-banner.js" defer></script>

Le script JS déduit le numéro de siman depuis l'URL, interroge
/api/dedicace/{N} et insère le bandeau (masqué s'il n'y a aucune dédicace).

Idempotent : ignore les fichiers déjà équipés. Réexécutable après génération
de nouveaux simanim.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIMAN_GLOB = "sources/shabbat/siman-*/**/*.html"
SCRIPT_TAG = '  <script src="/assets/js/dedicace-banner.js" defer></script>\n'
MARKER = "dedicace-banner.js"
BODY_RE = re.compile(r"(<body\b[^>]*>)", re.IGNORECASE)


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    m = BODY_RE.search(text)
    if not m:
        return False
    insert_at = m.end()
    # Insère sur une nouvelle ligne juste après <body...>
    new_text = text[:insert_at] + "\n" + SCRIPT_TAG + text[insert_at:]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    files = sorted(ROOT.glob(SIMAN_GLOB))
    changed = 0
    skipped = 0
    for f in files:
        if process(f):
            changed += 1
        else:
            skipped += 1
    print(f"Pages de siman traitées : {len(files)}")
    print(f"  Bandeau ajouté         : {changed}")
    print(f"  Déjà équipées / sans <body> : {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
