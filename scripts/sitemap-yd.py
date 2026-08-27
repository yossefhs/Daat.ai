#!/usr/bin/env python3
"""Ajoute au sitemap les 15 URL d'un ou plusieurs simanim Yoré Déa.

Usage : python3 scripts/sitemap-yd.py 119 120 121 [--date AAAA-MM-JJ]

Idempotent : une URL déjà présente n'est pas dupliquée. Les nouvelles entrées sont
ajoutées à la fin, avant </urlset> — le fichier existant n'est pas trié et le
retrier produirait un diff de 15 000 lignes pour rien : l'ordre est sans effet
sur l'interprétation d'un sitemap.
"""
import sys, re, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(ROOT, "sitemap.xml")
PAGES = ["", "base", "lamdan", "synthese", "halakha"]
LANGS = ["", "/en", "/he"]

def urls(n):
    out = []
    for p in PAGES:
        base = f"https://daattorah.com/yd/{n}/" + p
        for l in LANGS:
            if p == "":
                out.append(base if l == "" else base + l.lstrip("/"))
            else:
                out.append(base + l)
    return out

def main(argv):
    date = datetime.date.today().isoformat()
    nums = []
    i = 0
    while i < len(argv):
        if argv[i] == "--date":
            date = argv[i + 1]; i += 2; continue
        nums.append(int(argv[i])); i += 1

    xml = open(SITEMAP, encoding="utf-8").read()
    head, rest = xml.split("<urlset", 1)
    head = head + "<urlset" + rest.split(">", 1)[0] + ">\n"
    body = rest.split(">", 1)[1]
    tail = "</urlset>\n"
    body = body.replace("</urlset>", "").strip("\n")

    blocks = re.findall(r"  <url>.*?</url>", body, re.S)
    have = {re.search(r"<loc>(.*?)</loc>", b).group(1) for b in blocks}

    added = 0
    for n in nums:
        for u in urls(n):
            if u in have:
                continue
            blocks.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{date}</lastmod>\n"
                          f"    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>")
            have.add(u); added += 1

    open(SITEMAP, "w", encoding="utf-8").write(head + "\n".join(blocks) + "\n" + tail)
    print(f"sitemap : {added} URL ajoutée(s) · {len(blocks)} au total")

if __name__ == "__main__":
    main(sys.argv[1:])
