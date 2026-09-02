#!/usr/bin/env python3
"""Ajoute au sitemap les 15 URL d'un ou plusieurs simanim Yoré Déa.

Usage : python3 scripts/sitemap-yd.py 119 120 121 [--date AAAA-MM-JJ]

Idempotent : une URL déjà présente n'est pas dupliquée. Les nouvelles entrées sont
ajoutées à la fin, avant </urlset> — le fichier existant n'est pas trié et le
retrier produirait un diff de 15 000 lignes pour rien : l'ordre est sans effet
sur l'interprétation d'un sitemap.

⚠️ Le découpage en blocs ne peut PAS être un `re.findall(r"  <url>.*?</url>")` :
ce motif non glouton, appliqué à un fichier où un bloc a perdu sa balise fermante,
avale le bloc suivant tout entier et RÉÉCRIT l'imbrication au lieu de la signaler.
Le défaut se propage alors d'un lot au suivant. C'est arrivé : le merge de
`61cab360` a mangé la fermeture du bloc /yd/127/halakha/he et emporté deux URL de
questions ; le passage suivant du script a porté l'anomalie de 3 blocs à 78 et rendu
le sitemap mal formé. Le découpage se fait donc ligne à ligne, en refusant tout
fichier dont les <url>/</url> ne s'apparient pas, et la sortie est revalidée.
"""
import sys, re, os, datetime, xml.dom.minidom


def decouper(body):
    """Découpe le corps en blocs <url>…</url>, en refusant tout appariement fautif."""
    blocks, courant = [], None
    for ligne in body.split("\n"):
        t = ligne.strip()
        if t == "<url>":
            if courant is not None:
                raise SystemExit("sitemap corrompu : <url> ouvert dans un <url> "
                                 "non fermé — réparer le fichier avant d'y ajouter")
            courant = ["  <url>"]
        elif t == "</url>":
            if courant is None:
                raise SystemExit("sitemap corrompu : </url> sans <url> ouvrant")
            courant.append("  </url>")
            blocks.append("\n".join(courant)); courant = None
        elif courant is not None:
            courant.append("    " + t)
        elif t:
            raise SystemExit("sitemap corrompu : ligne hors de tout <url> : " + t[:60])
    if courant is not None:
        raise SystemExit("sitemap corrompu : <url> final non fermé")
    return blocks

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

    brut = open(SITEMAP, encoding="utf-8").read()
    head, rest = brut.split("<urlset", 1)
    head = head + "<urlset" + rest.split(">", 1)[0] + ">\n"
    body = rest.split(">", 1)[1]
    tail = "</urlset>\n"
    body = body.replace("</urlset>", "").strip("\n")

    blocks = decouper(body)
    have = {re.search(r"<loc>(.*?)</loc>", b).group(1) for b in blocks}

    added = 0
    for n in nums:
        for u in urls(n):
            if u in have:
                continue
            blocks.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{date}</lastmod>\n"
                          f"    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>")
            have.add(u); added += 1

    corps = "\n".join(blocks)
    decouper(corps)                        # le corps doit repasser le même contrôle
    sortie = head + corps + "\n" + tail
    xml.dom.minidom.parseString(sortie)    # et le tout être un XML bien formé
    open(SITEMAP, "w", encoding="utf-8").write(sortie)
    print(f"sitemap : {added} URL ajoutée(s) · {len(blocks)} au total")

if __name__ == "__main__":
    main(sys.argv[1:])
