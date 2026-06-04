#!/usr/bin/env python3
"""Injecte le script de partage par section dans chaque page de siman.

Ajoute, au début du <body> (juste après le script du bandeau de dédicace s'il
est présent, sinon après <body>), la ligne :
    <script src="/assets/js/share-text.js" defer></script>

Le script ajoute un bouton 📤 sur chaque section (h2.section-title) ; il ne fait
rien sur les pages sans section. Idempotent et ré-exécutable.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIMAN_GLOB = "sources/shabbat/siman-*/**/*.html"
SCRIPT_TAG = '  <script src="/assets/js/share-text.js" defer></script>\n'
MARKER = "share-text.js"
BANNER_RE = re.compile(r'(<script src="/assets/js/dedicace-banner\.js" defer></script>\n)')
BODY_RE = re.compile(r"(<body\b[^>]*>)", re.IGNORECASE)


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    m = BANNER_RE.search(text)
    if m:
        insert_at = m.end()
        new_text = text[:insert_at] + SCRIPT_TAG + text[insert_at:]
    else:
        b = BODY_RE.search(text)
        if not b:
            return False
        insert_at = b.end()
        new_text = text[:insert_at] + "\n" + SCRIPT_TAG + text[insert_at:]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    files = sorted(ROOT.glob(SIMAN_GLOB))
    changed = sum(1 for f in files if process(f))
    print(f"Pages de siman traitées : {len(files)}")
    print(f"  Script de partage ajouté : {changed}")
    print(f"  Déjà équipées / ignorées : {len(files) - changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
