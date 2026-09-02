#!/usr/bin/env python3
"""Cinquième garde-fou : la page est-elle un document HTML bien formé ?

Les quatre autres regardent le CONTENU. `audit-simanim.py` compte les fichiers et
traque le générique, `verifier-citations.py` confronte chaque verbatim à Sefaria,
`verifier-langues.py` et `verifier-url-langue.py` demandent si la page est écrite
dans la langue qu'elle annonce. Aucun ne lit la charpente du document — et c'est
ainsi que les trois pages d'index du siman 132 ont été publiées portant

    <body<body class="daat-reset daat-body">

soit une balise ouvrante à l'intérieur d'une autre. Le navigateur s'en accommode
en silence, les quatre garde-fous sortaient verts, et le défaut est resté en ligne.
Ce que ce script cherche, c'est précisément ce que personne ne regardait :

  · un « < » à l'intérieur d'une balise (le cas du 132) ;
  · une balise unique présente zéro ou plusieurs fois (<html, <head>, <body) ;
  · un <style> ou un <script> jamais refermé ;
  · un fichier qui ne finit pas par </html> ;
  · un attribut de langue absent de <html.

Ce n'est PAS un validateur HTML complet : c'est le petit ensemble de défauts qui
peuvent passer une relecture humaine, traverser un build et arriver en production.

Usage :
    python3 scripts/verifier-balises.py                       # tout sources/
    python3 scripts/verifier-balises.py --path sources/yoreh-deah/siman-132
    python3 scripts/verifier-balises.py --lignes              # + le détail ligne à ligne

Code de sortie non nul dès qu'un défaut est trouvé.
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Un « < » entre l'ouverture d'une balise et sa fermeture. On exclut les
# comparaisons à l'intérieur d'un script, traitées à part.
RE_CHEVRON_INTERNE = re.compile(r'<[a-zA-Z][^<>]*<')
UNIQUES = {'<html': 1, '<head': 1, '<body': 1}


def defauts(html):
    """Liste des défauts de charpente d'un document."""
    out = []

    # On raisonne sur le document DÉBARRASSÉ de ses commentaires et de ses
    # scripts : « a < b » y est du code légitime, et le commentaire « injecté en
    # haut du <body> » qui coiffe le bandeau de dédicace n'est pas un second
    # <body>. Sans cette précaution le script accusait 805 pages saines.
    net = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    net = re.sub(r'<script\b.*?</script>', '', net, flags=re.S | re.I)

    for m in RE_CHEVRON_INTERNE.finditer(net):
        ligne = net.count('\n', 0, m.start()) + 1
        out.append((ligne, 'balise imbriquée dans une balise : ' + m.group(0)[:60]))

    for balise, attendu in UNIQUES.items():
        n = len(re.findall(balise + r'[\s>]', net, re.I))
        if n != attendu:
            out.append((0, f'{balise}> présent {n} fois au lieu de {attendu}'))

    sans_com = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    for balise in ('style', 'script'):
        ouv = len(re.findall(r'<%s\b' % balise, sans_com, re.I))
        fer = len(re.findall(r'</%s\s*>' % balise, sans_com, re.I))
        if ouv != fer:
            out.append((0, f'<{balise}> ouvert {ouv} fois, fermé {fer} fois'))

    if not html.rstrip().endswith('</html>'):
        out.append((0, 'le fichier ne finit pas par </html>'))

    m = re.search(r'<html\b([^>]*)>', net, re.I)
    if m and not re.search(r'\blang\s*=', m.group(1)):
        out.append((0, '<html> sans attribut lang'))

    return out


def main(argv):
    detail = '--lignes' in argv
    cible = 'sources'
    if '--path' in argv:
        cible = argv[argv.index('--path') + 1]

    base = cible if os.path.isabs(cible) else os.path.join(ROOT, cible)
    motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base

    pages, fautives, total = 0, 0, 0
    for p in sorted(glob.glob(motif, recursive=True)):
        pages += 1
        d = defauts(open(p, encoding='utf-8').read())
        if not d:
            continue
        fautives += 1
        total += len(d)
        rel = os.path.relpath(p, ROOT)
        print(f'  {rel}')
        if detail:
            for ligne, msg in d:
                print(f'      {("ligne %d" % ligne) if ligne else "       "} : {msg}')
        else:
            for _, msg in d[:3]:
                print(f'      {msg}')

    print(f'\n{pages} page(s) examinée(s) dans {cible}')
    print(f'→ {fautives} page(s) à la charpente fautive ({total} défaut(s))')
    return 1 if fautives else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
