#!/usr/bin/env python3
"""Cinquième garde-fou : chaque lien interne mène-t-il à un fichier réel ?

Les URL publiques du site sont courtes (/yd/120/base, /oh-quotidien/207/lamdan) et
ne correspondent à aucun fichier sur le disque : c'est vercel.json qui les réécrit.
Un lien peut donc être parfaitement formé, passer tous les autres contrôles, et
renvoyer un 404 en production — c'est ce qui est arrivé à 663 pages d'index dont les
liens de niveau ont vécu cassés en ligne jusqu'à ce qu'on les teste à la main.

Ce script rejoue les `rewrites` et les `redirects` de vercel.json comme le ferait
Vercel, et vérifie que la destination existe sur le disque.

Usage : python3 scripts/verifier-liens.py [--path CHEMIN] [--details]
Sort en code 1 si un lien interne ne mène à rien.
"""
import json, re, os, sys, glob
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOTE = "daattorah.com"

def compile_src(src):
    """Traduit un motif Vercel (/yd/:n(\\d+)/base) en expression régulière."""
    out, i = "", 0
    while i < len(src):
        if src[i] == ":":
            m = re.match(r":(\w+)(\(([^)]*)\))?", src[i:])
            out += f"(?P<{m.group(1)}>{m.group(3) or '[^/]+'})"
            i += m.end()
        else:
            out += re.escape(src[i]); i += 1
    return re.compile("^" + out + "$")

def charger_regles():
    v = json.load(open(os.path.join(ROOT, "vercel.json"), encoding="utf-8"))
    rew = [(compile_src(r["source"]), r["destination"]) for r in v.get("rewrites", [])]
    red = [(compile_src(r["source"]), r["destination"]) for r in v.get("redirects", [])]
    return rew, red

def resoudre(url, rew, red, profondeur=0):
    """Renvoie le chemin disque visé, ou None si aucune règle ni fichier."""
    if profondeur > 5:
        return None
    for rx, dest in red:
        m = rx.match(url)
        if m:
            d = dest
            for k, val in (m.groupdict() or {}).items():
                d = d.replace(":" + k, val).replace(":" + k + "*", val)
            return resoudre(d.split("#")[0].split("?")[0], rew, red, profondeur + 1)
    for rx, dest in rew:
        m = rx.match(url)
        if m:
            d = dest
            for k, val in (m.groupdict() or {}).items():
                d = d.replace(":" + k, val).replace(":" + k + "*", val)
            return d.lstrip("/")
    p = url.lstrip("/")
    for cand in (p, p + "index.html" if p.endswith("/") else p + ".html"):
        if cand and os.path.exists(os.path.join(ROOT, cand)):
            return cand
    return None

def main(argv):
    details = "--details" in argv
    base = os.path.join(ROOT, argv[argv.index("--path") + 1]) if "--path" in argv else os.path.join(ROOT, "sources")
    rew, red = charger_regles()

    casses, vus = [], 0
    for p in sorted(glob.glob(os.path.join(base, "**", "*.html"), recursive=True)):
        html = open(p, encoding="utf-8").read()
        rep = os.path.dirname(p)
        for href in set(re.findall(r'href="([^"#][^"]*)"', html)):
            u = urlparse(href)
            if u.scheme and u.netloc and u.netloc.replace("www.", "") != HOTE:
                continue                      # lien externe
            chemin = u.path
            if not chemin or chemin.startswith("mailto:") or chemin.startswith("tel:"):
                continue
            vus += 1
            if chemin.startswith("/"):
                cible = resoudre(chemin, rew, red)
                ok = cible is not None and os.path.exists(os.path.join(ROOT, cible))
            else:                              # lien relatif : simple existence
                ok = os.path.exists(os.path.normpath(os.path.join(rep, chemin)))
            if not ok:
                casses.append((os.path.relpath(p, ROOT), href))

    print(f"\n{vus} lien(s) interne(s) examiné(s) dans {os.path.relpath(base, ROOT)}")
    print(f"→ {len(casses)} lien(s) ne menant à aucun fichier")
    if details:
        for f, h in sorted(casses):
            print(f"     {f} → {h}")
    return 1 if casses else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
