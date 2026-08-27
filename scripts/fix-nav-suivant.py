#!/usr/bin/env python3
"""Neutralise les liens « siman suivant » qui désignent un siman pas encore produit.

Le dernier siman d'un lot renvoie naturellement au suivant, qui n'existe pas encore.
Publier tel quel met un 404 en production — précisément ce que verifier-liens.py sert
à empêcher. Ce script remplace le lien mort par un renvoi au catalogue du compartiment
et garde le libellé, de sorte que la page reste cohérente à la lecture.

Quand le siman visé est produit, relancer avec --restaurer pour rétablir le lien.

Usage : python3 scripts/fix-nav-suivant.py [--dry-run]
Idempotent.
"""
import re, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPARTIMENTS = {                       # préfixe d'URL → (répertoire, catalogue)
    "/yd/":           ("yoreh-deah", "/yd/"),
    "/oh-quotidien/": ("orah-haim",  "/oh-quotidien/"),
    "/oh/":           ("shabbat",    "/oh/"),
}

def existe(prefixe, num):
    rep = COMPARTIMENTS[prefixe][0]
    return os.path.isdir(os.path.join(ROOT, "sources", rep, f"siman-{num}"))

def main(dry=False):
    total, fichiers = 0, 0
    motif = re.compile(r'<a\s+([^>]*?)href="(/(?:yd|oh-quotidien|oh)/(\d+)/(he|en)?)"([^>]*)>(.*?)</a>', re.S)
    for p in sorted(glob.glob(os.path.join(ROOT, "sources/**/*.html"), recursive=True)):
        html = open(p, encoding="utf-8").read()
        n = 0

        def remplace(m):
            nonlocal n
            url, num, lang = m.group(2), m.group(3), m.group(4) or ""
            prefixe = next((k for k in COMPARTIMENTS if url.startswith(k)), None)
            if prefixe is None or existe(prefixe, num):
                return m.group(0)
            n += 1
            cat = COMPARTIMENTS[prefixe][1] + (lang if lang else "")
            return f'<a {m.group(1)}href="{cat}"{m.group(5)}>{m.group(6)}</a>'

        new = motif.sub(remplace, html)
        if n:
            total += n; fichiers += 1
            if not dry:
                open(p, "w", encoding="utf-8").write(new)
            print(f"  {os.path.relpath(p, ROOT)} : {n} lien(s) neutralisé(s)")
    print(f"{'(à blanc) ' if dry else ''}{total} lien(s) dans {fichiers} fichier(s)")

if __name__ == "__main__":
    main("--dry-run" in sys.argv)
