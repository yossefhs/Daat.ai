#!/usr/bin/env python3
"""Répare les liens de niveau des pages index-he / index-en de Yoré Déa.

Les cartes « Niveau 01/02/03/04 » des index hébreu et anglais pointaient vers la
page FRANÇAISE du niveau : la carte « Niveau 02 » de index-he.html menait à
niveau-2-lamdan.html au lieu de niveau-2-lamdan-he.html. Le défaut touchait les
50 simanim, systématiquement sur le niveau 2, et les quatre niveaux sur un siman.

Le lecteur hébréophone ou anglophone qui cliquait sur « Niveau 2 » tombait donc
sur la page française — sans erreur visible, ce qu'aucun des trois garde-fous ne
pouvait voir : verifier-langues.py juge la langue du contenu d'une page, pas la
langue de la page vers laquelle elle pointe.

Idempotent. Usage : python3 scripts/fix-yd-index-lang-links.py [--dry-run]
"""
import re, glob, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NIVEAUX = ("niveau-1-base", "niveau-2-lamdan", "niveau-3-synthese", "niveau-4-halakha")

def main(dry=False):
    total, touches = 0, 0
    for suf in ("he", "en"):
        for p in sorted(glob.glob(os.path.join(ROOT, f"sources/yoreh-deah/siman-*/index-{suf}.html"))):
            html = open(p, encoding="utf-8").read()
            orig = html
            for n in NIVEAUX:
                html = html.replace(f'href="{n}.html"', f'href="{n}-{suf}.html"')
            if html != orig:
                n = sum(1 for x in NIVEAUX if f'href="{x}.html"' in orig)
                total += n; touches += 1
                if not dry:
                    open(p, "w", encoding="utf-8").write(html)
                print(f"  {os.path.relpath(p, ROOT)} : {n} lien(s)")
    print(f"{'(à blanc) ' if dry else ''}{total} lien(s) réparé(s) dans {touches} fichier(s)")
    return 0

if __name__ == "__main__":
    sys.exit(main("--dry-run" in sys.argv))
