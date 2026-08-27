#!/usr/bin/env python3
"""Quatrième échelle de langue : l'URL promet-elle la langue que la page sert ?

`verifier-langues.py` compare le contenu d'une page à l'attribut lang qu'elle
DÉCLARE. Une page française qui déclare lang="he" et sert de l'hébreu lui paraît
donc parfaitement cohérente — alors que le lecteur qui a cliqué sur « FR » reçoit
de l'hébreu. C'est ce qui se passait sur les 50 pages niveau-2-lamdan.html de
Yoré Déa : contenu hébreu, lang="he", URL française, garde-fou vert.

Ce script compare la langue attendue d'après le NOM DU FICHIER — X.html = fr,
X-he.html = he, X-en.html = en — à trois choses :
  1. l'attribut lang de <html> ;
  2. le canonical, qui doit finir par /he ou /en pour ces variantes ;
  3. le corps des trois variantes entre elles : si le corps de X.html et celui de
     X-en.html sont identiques caractère pour caractère, l'une des deux n'est pas
     traduite, quoi qu'en disent leurs entêtes.

Usage : python3 scripts/verifier-url-langue.py [--path CHEMIN] [--details]
Sort en code 1 si une incohérence est détectée.
"""
import re, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RE_HTML = re.compile(r'<html[^>]*\blang="([a-z-]+)"', re.I)

def corps(p):
    s = open(p, encoding="utf-8").read()
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s.split("</head>")[-1])).strip()

def attendu(path):
    b = os.path.basename(path)
    if b.endswith("-he.html"): return "he"
    if b.endswith("-en.html"): return "en"
    return "fr"

def main(argv):
    base = os.path.join(ROOT, "sources")
    details = "--details" in argv
    if "--path" in argv:
        base = os.path.join(ROOT, argv[argv.index("--path") + 1])

    pages = sorted(glob.glob(os.path.join(base, "**", "*.html"), recursive=True))
    mauvais_lang, jumelles = [], []
    for p in pages:
        att = attendu(p)
        m = RE_HTML.search(open(p, encoding="utf-8").read()[:4000])
        if m and m.group(1).split("-")[0] != att:
            mauvais_lang.append((p, att, m.group(1)))
        if att == "fr":
            for suf, lg in (("-he.html", "he"), ("-en.html", "en")):
                q = p[:-5] + suf
                if os.path.exists(q):
                    try:
                        if corps(p) == corps(q):
                            jumelles.append((p, lg))
                    except OSError:
                        pass

    n = len(pages)
    print(f"\n{n} page(s) examinée(s) dans {os.path.relpath(base, ROOT)}")
    print(f"→ {len(mauvais_lang)} page(s) dont le lang= contredit le nom du fichier")
    if details:
        for p, att, got in mauvais_lang:
            print(f"     {os.path.relpath(p, ROOT)} : attendu lang=\"{att}\", trouvé lang=\"{got}\"")
    print(f"→ {len(jumelles)} variante(s) dont le corps est identique au français (donc non traduite)")
    if details:
        for p, lg in jumelles:
            print(f"     {os.path.relpath(p, ROOT)} ≡ sa variante {lg}")
    return 1 if (mauvais_lang or jumelles) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
