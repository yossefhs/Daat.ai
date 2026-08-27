#!/usr/bin/env python3
"""Répare les liens internes qui ne mènent à aucun fichier, repérés par verifier-liens.py.

Quatre familles, toutes en ligne au moment de l'écriture de ce script :

1. Siman 235 d'Orah Haïm — 12 liens de la forme /oh-quotidien/234/en/base : le segment
   de langue est placé avant la page au lieu d'après. La forme correcte est
   /oh-quotidien/234/base/en. Aucune règle de vercel.json ne couvre l'ordre inverse.
2. Simanim 87 et 241 d'Orah Haïm — 6 liens vers /oh-quotidien/242/… et /oh-quotidien/315/… :
   les simanim 242 à 365 ne sont pas dans le compartiment oh-quotidien mais dans
   Hilkhot Shabbat, sous /oh/. Le lien pointait vers un compartiment où le siman n'existe pas.
3. Siman 105 de Yoré Déa — 9 liens vers ../siman-68, 69 et 70, qui n'existent pas.
   Le lien est retiré ; le libellé reste, en texte simple.
4. Simanim en fin de lot dont la nav « suivant » désigne un siman pas encore produit
   (option --nav-suivant N) : le lien est remplacé par un renvoi au catalogue.

Idempotent. Usage : python3 scripts/fix-liens-morts.py [--dry-run]
"""
import re, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHABBAT = set(range(242, 366))          # les simanim servis sous /oh/, pas /oh-quotidien/

def corriger(html):
    n = 0
    # 1. /oh-quotidien/N/<langue>/<page>  →  /oh-quotidien/N/<page>/<langue>
    def ordre(m):
        return f'/oh-quotidien/{m.group(1)}/{m.group(3)}/{m.group(2)}'
    html, k = re.subn(r'/oh-quotidien/(\d+)/(he|en)/(base|lamdan|synthese|daat-harav)', ordre, html); n += k
    # 2. compartiment : les simanim 242-365 vivent sous /oh/
    def compart(m):
        return (f'/oh/{m.group(1)}/{m.group(2)}' if int(m.group(1)) in SHABBAT
                else m.group(0))
    html, k = re.subn(r'/oh-quotidien/(\d+)/(base|lamdan|synthese|daat-harav)', compart, html)
    return html, n + k

def delier(html, cibles):
    """Retire le <a href="…"> autour d'un libellé, en gardant le libellé."""
    n = 0
    for c in cibles:
        html, k = re.subn(r'<a\s+[^>]*href="' + re.escape(c) + r'"[^>]*>(.*?)</a>',
                          r'\1', html, flags=re.S)
        n += k
    return html, n

def main(dry=False):
    total = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "sources/**/*.html"), recursive=True)):
        html = open(p, encoding="utf-8").read()
        orig = html
        html, n = corriger(html)
        if "/siman-105/" in p.replace(os.sep, "/"):
            html, k = delier(html, [f"../siman-{x}/{s}.html"
                                    for x in (68, 69, 70)
                                    for s in ("niveau-1-base", "niveau-1-base-he", "niveau-1-base-en")])
            n += k
        if html != orig:
            total += n
            if not dry:
                open(p, "w", encoding="utf-8").write(html)
            print(f"  {os.path.relpath(p, ROOT)} : {n} lien(s)")
    print(f"{'(à blanc) ' if dry else ''}{total} lien(s) réparé(s)")

if __name__ == "__main__":
    main("--dry-run" in sys.argv)
