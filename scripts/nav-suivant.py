#!/usr/bin/env python3
"""Rétablit le lien « siman suivant » une fois le siman visé produit, et pose le
libellé canonique du lot.

`fix-nav-suivant.py` neutralise, avant publication, les liens qui pointent vers un
siman pas encore écrit : leur href retombe sur le catalogue. Ce script fait le chemin
inverse quand le siman existe enfin — et corrige au passage le libellé, que l'agent du
lot précédent avait dû inventer faute de titre canonique disponible.

Le fichier de titres tient sur une ligne :
    123|קכ״ג|<titre hébreu>|<titre anglais>|<titre français>

Usage : python3 scripts/nav-suivant.py 123 --titres /tmp/p/nav-123.txt [--dry-run]
Idempotent : un lien déjà rétabli ne correspond plus au motif.
"""
import re, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIEN = re.compile(r'<a href="/yd/(?:he|en)?"([^>]*)>(.*?)</a>', re.S)


def main(argv):
    dry = "--dry-run" in argv
    num = int(argv[0])
    champs = open(argv[argv.index("--titres") + 1], encoding="utf-8").read().strip().split("|")
    heNum, tHe, tEn, tFr = [c.strip() for c in champs[1:5]]
    libelle = {
        "":    f"Siman {num} — {tFr} →",
        "-en": f"Siman {num} — {tEn} →",
        "-he": f"← סימן {heNum} · {num} — {tHe}",
    }

    total = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "sources/yoreh-deah/siman-*/*.html"))):
        suf = "-he" if p.endswith("-he.html") else "-en" if p.endswith("-en.html") else ""
        lang = {"": "", "-he": "he", "-en": "en"}[suf]
        cible = f"/yd/{num}/{lang}" if lang else f"/yd/{num}/"
        html = open(p, encoding="utf-8").read()
        n = 0

        def remplace(m):
            nonlocal n
            attrs, texte = m.group(1), m.group(2)
            # on ne touche qu'aux liens dont le libellé désigne bien ce siman
            if str(num) not in re.sub(r"<[^>]+>", "", texte):
                return m.group(0)
            n += 1
            # la carte de navigation reçoit le libellé canonique ;
            # un renvoi en ligne (« … voir le siman 123 ») garde le sien
            neuf = libelle[suf] if 'class="next"' in attrs else texte
            return f'<a href="{cible}"{attrs}>{neuf}</a>'

        neuf = LIEN.sub(remplace, html)
        if n:
            total += n
            if not dry:
                open(p, "w", encoding="utf-8").write(neuf)
            print(f"  {os.path.relpath(p, ROOT)} : {n} lien(s) rétabli(s)")
    print(f"{'(à blanc) ' if dry else ''}{total} lien(s) vers le siman {num}")


if __name__ == "__main__":
    main(sys.argv[1:])
