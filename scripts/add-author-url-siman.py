#!/usr/bin/env python3
"""add-author-url-siman.py — relie l'auteur des pages siman à la page auteur.

Les pages siman définissent déjà le Person #rav-samama (référencé comme `author`
de l'Article), mais sans `url`. On ajoute `url` → page auteur, ce qui connecte
l'entité E-E-A-T sur tout le corpus (1863 pages). Idempotent.

    python3 scripts/add-author-url-siman.py [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "shabbat"
AUTHOR_URL = "https://daattorah.com/auteur/rav-yossef-haim-samama.html"

# La DÉFINITION du Person a une virgule finale ; les simples références n'en ont pas.
DEF_RE = re.compile(r'( *)("@id": "https://daattorah\.com/#rav-samama",\n)')


def main() -> None:
    dry = "--dry-run" in sys.argv
    added = skipped = 0
    for path in SRC.rglob("*.html"):
        html = path.read_text(encoding="utf-8")
        if "/auteur/rav-yossef" in html or "#rav-samama" not in html:
            skipped += 1
            continue
        new, n = DEF_RE.subn(
            lambda m: m.group(0) + m.group(1) + f'"url": "{AUTHOR_URL}",\n', html, count=1
        )
        if n == 0:
            skipped += 1
            continue
        added += 1
        if not dry:
            path.write_text(new, encoding="utf-8")
    print(f"Person.url ajouté : {added}")
    print(f"Ignoré           : {skipped}")
    if dry:
        print("(dry-run)")


if __name__ == "__main__":
    main()
