#!/usr/bin/env python3
"""Retire la barre redondante « ℹ️ … traduit » + sélecteur FR/HE/EN inline.

Cette barre (div sur fond #FFF8E5 avec une note de traduction et un second
sélecteur de langue) fait doublon avec le sélecteur flottant
(.lang-switcher-float) présent sur toutes les pages. On la supprime ; le
flottant reste. Cible les pages de siman. Idempotent.

Usage : python3 scripts/remove-translated-banner.py [--dry siman/fichier]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOB = "sources/shabbat/siman-*/*.html"

# Div dont le premier enfant est <span>ℹ️ … : c'est uniquement cette barre.
BANNER = re.compile(r"<div [^>]*>\s*<span>ℹ️.*?</div>\s*", re.DOTALL)


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--dry":
        p = ROOT / args[1]
        t = p.read_text(encoding="utf-8")
        m = BANNER.search(t)
        print("MATCH:" if m else "NO MATCH")
        if m:
            print(m.group(0)[:400])
        return 0

    files = sorted(ROOT.glob(GLOB))
    changed = 0
    for f in files:
        t = f.read_text(encoding="utf-8")
        nt = BANNER.sub("", t)
        if nt != t:
            f.write_text(nt, encoding="utf-8")
            changed += 1
    print(f"Fichiers de siman : {len(files)} | barre retirée : {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
