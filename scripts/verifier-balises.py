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
  · un attribut de langue absent de <html ;
  · un ATTRIBUT EN DOUBLE sur une même balise, et une VALEUR COUPÉE par un guillemet ;
  · un bloc JSON-LD que json.loads ne lit pas ;
  · une ENTITÉ DOUBLÉE (« &amp;quot; »), qui s'affiche en toutes lettres.

Les quatre dernières familles sont nées d'une page qui sortait « 0 défaut » ici :

    <meta name="description" content="… : "בּוֹרֵא נְפָשׁוֹת רַבּוֹת" עַל …">

(Orah Haïm 207, niveau 4 hébreu, octobre 2026). Le guillemet intérieur ferme la
valeur : Google et les aperçus de partage lisaient « … : », et le reste devenait
des dizaines d'attributs parasites — « בּוֹרֵא », « רַבּוֹת" »… Ce script ne lisait
que les chevrons, et un guillemet n'en est pas un. On lit donc chaque balise avec
html.parser, qui découpe les attributs comme le navigateur, et l'on signale :
  · un nom d'attribut répété — le navigateur garde le PREMIER et jette les autres
    (html.parser rend le dernier) : un style= doublé n'applique que le premier ;
  · un nom d'attribut qui n'en est pas un (lettre hébraïque, guillemet, ponctuation,
    accent) : c'est le reste d'une valeur coupée, et l'on imprime ce que le
    navigateur garde de la valeur.
Mesure du 13 octobre 2026, sur les 8 663 pages du site : 15 pages, 26 balises —
20 <meta> coupées sur 13 pages, dans les trois langues (8 hébraïques, 8 anglaises,
4 françaises), et 6 <div> d'un niveau 4 de Yoré Déa (132, FR et EN) portant deux
style= : le premier seul était appliqué, l'encadré du psak perdait fond et bordure.
Cinq de ces <meta> avaient été « raccourcies » par scripts/fix-meta-descriptions.py
(commit cd617d936) : sa regex lisait la valeur jusqu'au premier guillemet, la
récrivait, et recollait la suite telle quelle. Au 244 elle avait même remplacé la
description par une autre, tirée du <title>, parce qu'elle lisait « Étude du Siman
רמ » — 16 caractères, « trop court ». Le même guillemet cassait 2 blocs JSON-LD sur
7 872, où il fallait un \\" — dont celui du 207, dont seule la <meta> avait été
réparée. Et 19 entités échappées deux fois, sur 6 pages de Yoré Déa, faisaient lire
« נ&quot;ט » à Google et « Beer &amp; Beverages » au lecteur du catalogue anglais.
Toutes réparées le même jour.

Ce n'est PAS un validateur HTML complet : c'est le petit ensemble de défauts qui
peuvent passer une relecture humaine, traverser un build et arriver en production.

Usage :
    python3 scripts/verifier-balises.py                       # tout le site
    python3 scripts/verifier-balises.py --path sources/yoreh-deah/siman-132
    python3 scripts/verifier-balises.py --lignes              # + le détail ligne à ligne

Le site, c'est chaque .html du dépôt hors node_modules et hors répertoires cachés
(.git, .claude, data/.banner-snippets, qui sont des fragments) — sources/, limoud/,
blog/, questions/, la racine. Jusqu'au 13 octobre 2026 la porte ne lisait que sources/,
et la seule page de limoud/ fautive lui échappait.

Code de sortie non nul dès qu'un défaut est trouvé.
"""
import os
import re
import sys
import glob
import json
from collections import Counter
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Un « < » entre l'ouverture d'une balise et sa fermeture. On exclut les
# comparaisons à l'intérieur d'un script, traitées à part.
RE_CHEVRON_INTERNE = re.compile(r'<[a-zA-Z][^<>]*<')
UNIQUES = {'<html': 1, '<head': 1, '<body': 1}

# Un nom d'attribut tel que le site les écrit (html.parser les rend en minuscules) :
# id, class, data-*, aria-*, http-equiv, xml:lang. Tout le reste — une lettre
# hébraïque, un guillemet, une virgule, un accent — est le morceau d'une valeur coupée.
RE_NOM_ATTRIBUT = re.compile(r'^[a-z_:][-a-z0-9_:.]*$')
RE_JSONLD = re.compile(r'<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>',
                       re.S | re.I)

# « &amp;quot; » : une entité échappée une seconde fois s'affiche en toutes lettres.
RE_ENTITE_DOUBLEE = re.compile(r'&amp;(?:[a-z]+|#\d+|#x[0-9a-f]+);', re.I)

DOUBLE = 'ATTRIBUT EN DOUBLE'
COUPEE = 'VALEUR COUPÉE'
JSONLD = 'JSON-LD ILLISIBLE'
ENTITE = 'ENTITÉ DOUBLÉE'


class LecteurAttributs(HTMLParser):
    """Lit chaque balise ouvrante comme le navigateur découpe ses attributs."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []

    def handle_starttag(self, tag, attrs):
        ligne = self.getpos()[0]
        noms = [k for k, _ in attrs]
        # Les parasites d'une valeur coupée commencent au premier nom invraisemblable,
        # ou plus tôt : « what "acting like one of the two" requires » donne acting,
        # like, one, of, the — des noms plausibles, sans valeur — avant « two" ». On
        # remonte donc sur les attributs nus jusqu'à celui dont la valeur a été coupée.
        debut = len(noms)
        invraisemblables = [i for i, k in enumerate(noms) if not RE_NOM_ATTRIBUT.match(k)]
        if invraisemblables:
            debut = invraisemblables[0]
            while debut > 0 and attrs[debut - 1][1] is None:
                debut -= 1
            coupe = attrs[debut - 1] if debut else None
            garde = f'{coupe[0]}="…{(coupe[1] or "")[-60:]}"' if coupe else '(aucune valeur)'
            self.out.append((ligne, COUPEE,
                             f'<{tag}> le navigateur lit {garde} ; '
                             f'{len(noms) - debut} attribut(s) parasite(s) : '
                             + ' '.join(noms[debut:debut + 6]) + (' …' if len(noms) - debut > 6 else '')))
        # Un mot répété dans la valeur coupée n'est qu'un symptôme de la coupure :
        # les doubles se cherchent parmi les attributs qui la précèdent.
        avant = noms[:debut]
        doubles = sorted({k for k in avant if avant.count(k) > 1})
        if doubles:
            # Le navigateur garde la PREMIÈRE occurrence ; on montre ce qu'il jette.
            jetes = '; '.join(k if v is None else f'{k}="{v}"' for i, (k, v) in enumerate(attrs[:debut])
                              if k in doubles and k in avant[:i])
            self.out.append((ligne, DOUBLE,
                             f'<{tag}> {", ".join(doubles)} — le navigateur garde le premier '
                             f'et jette : {jetes[:120]}'))

    handle_startendtag = handle_starttag


def defauts(html):
    """Liste des défauts de charpente d'un document : (ligne, famille, message)."""
    out = []

    # On raisonne sur le document DÉBARRASSÉ de ses commentaires et de ses
    # scripts : « a < b » y est du code légitime, et le commentaire « injecté en
    # haut du <body> » qui coiffe le bandeau de dédicace n'est pas un second
    # <body>. Sans cette précaution le script accusait 805 pages saines.
    net = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    net = re.sub(r'<script\b.*?</script>', '', net, flags=re.S | re.I)

    for m in RE_CHEVRON_INTERNE.finditer(net):
        ligne = net.count('\n', 0, m.start()) + 1
        out.append((ligne, 'BALISE IMBRIQUÉE', 'balise imbriquée dans une balise : ' + m.group(0)[:60]))

    for balise, attendu in UNIQUES.items():
        n = len(re.findall(balise + r'[\s>]', net, re.I))
        if n != attendu:
            out.append((0, 'BALISE UNIQUE', f'{balise}> présent {n} fois au lieu de {attendu}'))

    sans_com = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    for balise in ('style', 'script'):
        ouv = len(re.findall(r'<%s\b' % balise, sans_com, re.I))
        fer = len(re.findall(r'</%s\s*>' % balise, sans_com, re.I))
        if ouv != fer:
            out.append((0, 'BLOC NON REFERMÉ', f'<{balise}> ouvert {ouv} fois, fermé {fer} fois'))

    if not html.rstrip().endswith('</html>'):
        out.append((0, 'FIN DE FICHIER', 'le fichier ne finit pas par </html>'))

    m = re.search(r'<html\b([^>]*)>', net, re.I)
    if m and not re.search(r'\blang\s*=', m.group(1)):
        out.append((0, 'LANG ABSENT', '<html> sans attribut lang'))

    lecteur = LecteurAttributs()
    lecteur.feed(html)
    lecteur.close()
    out.extend(lecteur.out)

    # commentaires blanchis, sauts de ligne gardés : les numéros de ligne restent ceux du fichier
    blanchi = re.sub(r'<!--.*?-->', lambda c: '\n' * c.group(0).count('\n'), html, flags=re.S)
    for m in RE_JSONLD.finditer(blanchi):
        try:
            json.loads(m.group(1))
        except ValueError as e:
            ligne = blanchi.count('\n', 0, m.start(1)) + getattr(e, 'lineno', 1)
            out.append((ligne, JSONLD, f'{getattr(e, "msg", e)} — '
                        + m.group(1)[max(0, getattr(e, 'pos', 0) - 40):getattr(e, 'pos', 0) + 20]
                        .replace('\n', ' ').strip()))

    hors_scripts = re.sub(r'<script\b.*?</script\s*>', lambda c: '\n' * c.group(0).count('\n'),
                          blanchi, flags=re.S | re.I)
    for m in RE_ENTITE_DOUBLEE.finditer(hors_scripts):
        ligne = hors_scripts.count('\n', 0, m.start()) + 1
        out.append((ligne, ENTITE, f'{m.group(0)} s\'affiche en toutes lettres — '
                    + hors_scripts[max(0, m.start() - 40):m.end() + 10].replace('\n', ' ').strip()))

    return out


def pages_du_site():
    """Chaque .html du dépôt, hors node_modules et hors répertoires cachés."""
    for d, sous, fichiers in os.walk(ROOT):
        sous[:] = sorted(s for s in sous if s != 'node_modules' and not s.startswith('.'))
        for f in sorted(fichiers):
            if f.endswith('.html'):
                yield os.path.join(d, f)


def main(argv):
    detail = '--lignes' in argv
    cible = 'le site'
    if '--path' in argv:
        cible = argv[argv.index('--path') + 1]
        base = cible if os.path.isabs(cible) else os.path.join(ROOT, cible)
        motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base
        chemins = sorted(glob.glob(motif, recursive=True))
    else:
        chemins = list(pages_du_site())

    pages, fautives, total = 0, 0, 0
    familles = Counter()
    for p in chemins:
        pages += 1
        d = defauts(open(p, encoding='utf-8').read())
        if not d:
            continue
        fautives += 1
        total += len(d)
        familles.update(f for _, f, _ in d)
        rel = os.path.relpath(p, ROOT)
        print(f'  {rel}')
        if detail:
            for ligne, famille, msg in d:
                print(f'      {("ligne %d" % ligne) if ligne else "       "} : {famille} — {msg}')
        else:
            for _, famille, msg in d[:3]:
                print(f'      {famille} — {msg[:140]}')

    print(f'\n{pages} page(s) examinée(s) dans {cible}')
    print(f'→ {fautives} page(s) à la charpente fautive ({total} défaut(s))')
    for famille, n in familles.most_common():
        print(f'   {n:5d}  {famille}')
    return 1 if fautives else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
