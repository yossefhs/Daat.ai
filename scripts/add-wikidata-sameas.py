#!/usr/bin/env python3
"""add-wikidata-sameas.py — ajoute le sameAs Wikidata à l'entité auteur #rav-samama.

Insère "sameAs": ["https://www.wikidata.org/wiki/Q140170943"] dans la définition
du Person #rav-samama (pages « À propos » + pages siman). Idempotent.

    python3 scripts/add-wikidata-sameas.py [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKIDATA = "https://www.wikidata.org/wiki/Q140170943"

# Définition du Person (ligne @id avec virgule finale), capture l'indentation.
DEF_RE = re.compile(r'( *)"@id": "https://daattorah\.com/#rav-samama",\n')

TARGETS = [ROOT / "about.html", ROOT / "about-he.html", ROOT / "about-en.html"]
TARGETS += list((ROOT / "sources" / "shabbat").rglob("*.html"))


def main() -> None:
    dry = "--dry-run" in sys.argv
    added = skipped = 0
    for path in TARGETS:
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        if "Q140170943" in html or "#rav-samama" not in html:
            skipped += 1
            continue
        new, n = DEF_RE.subn(
            lambda m: m.group(0) + f'{m.group(1)}"sameAs": ["{WIKIDATA}"],\n', html
        )
        if n == 0:
            skipped += 1
            continue
        added += 1
        if not dry:
            path.write_text(new, encoding="utf-8")
    print(f"sameAs Wikidata ajouté : {added}")
    print(f"Ignoré                : {skipped}")
    if dry:
        print("(dry-run)")


if __name__ == "__main__":
    main()
