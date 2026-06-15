#!/usr/bin/env python3
"""fix-wikidata-sameas.py — corrige le câblage de l'entité Wikidata Q140170943.

Q140170943 est l'entité de l'ORGANISATION (daattorah.com / DAAT), pas du Rav.
Un câblage précédent l'avait mise par erreur en sameAs du Person #rav-samama.
Ce script : (1) retire le sameAs du Person, (2) l'ajoute à l'Organization.
Idempotent.

    python3 scripts/fix-wikidata-sameas.py [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
Q = "https://www.wikidata.org/wiki/Q140170943"

# Retire la ligne sameAs insérée juste après la définition du Person #rav-samama.
REMOVE_PERSON = re.compile(
    r'("@id": "https://daattorah\.com/#rav-samama",\n)'
    r' *"sameAs": \["https://www\.wikidata\.org/wiki/Q140170943"\],\n'
)
# Ajoute le sameAs après la définition de l'Organization #organization.
ORG_DEF = re.compile(r'( *)("@id": "https://daattorah\.com/#organization",\n)')

TARGETS = [ROOT / "about.html", ROOT / "about-he.html", ROOT / "about-en.html"]
TARGETS += list((ROOT / "sources" / "shabbat").rglob("*.html"))


def main() -> None:
    dry = "--dry-run" in sys.argv
    person_cleaned = org_wired = 0
    for path in TARGETS:
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        orig = html

        html, n_rm = REMOVE_PERSON.subn(r"\1", html)
        if n_rm:
            person_cleaned += 1

        # Ajoute à l'Organization seulement si l'entité n'est pas déjà présente.
        if "Q140170943" not in html and ORG_DEF.search(html):
            html = ORG_DEF.sub(lambda m: m.group(0) + m.group(1) + f'"sameAs": ["{Q}"],\n', html)
            org_wired += 1

        if html != orig and not dry:
            path.write_text(html, encoding="utf-8")

    print(f"Person nettoyé (sameAs retiré) : {person_cleaned}")
    print(f"Organization câblée (sameAs)   : {org_wired}")
    if dry:
        print("(dry-run)")


if __name__ == "__main__":
    main()
