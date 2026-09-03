#!/usr/bin/env python3
"""Sixième garde-fou : la classe employée par la page est-elle définie quelque part ?

C'est le défaut que `fix-two-col.py` a corrigé une fois, à la main, sur 27 pages —
et qui est revenu aussitôt sous une autre forme, sur 27 autres pages. Il mérite un
contrôle, pas un correctif de plus.

Une page peut employer `class="daat-two-col"` ou `class="he-q"` sans que rien ne
définisse ces classes : ni son `<style>` inline, ni aucune des feuilles qu'elle
charge. Le navigateur n'émet aucune erreur, le HTML reste valide, les citations
restent justes, la langue reste la bonne — et le bloc n'est pas mal mis en page,
il n'est pas mis en page DU TOUT. Deux colonnes nues, l'hébreu dans le sens du
français ; ou des citations qui perdent leur taille et leur interligne.

Aucun des cinq autres garde-fous ne peut le voir : ils lisent le contenu, la
langue, les liens, la charpente — jamais le rapport entre une classe et sa
définition.

On ne contrôle pas TOUTES les classes du site (les classes posées par le
JavaScript des widgets n'ont pas à être définies dans la page). On contrôle la
liste des classes de CONTENU ci-dessous, celles qui portent la mise en page des
pages d'étude et dont l'absence se voit à l'œil.

Usage :
    python3 scripts/verifier-classes.py                         # tout sources/
    python3 scripts/verifier-classes.py --path sources/yoreh-deah
    python3 scripts/verifier-classes.py --lignes                # + le détail par page

Code de sortie non nul dès qu'une classe de contenu est employée sans définition.
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Les classes qui portent la mise en page du contenu d'étude. Une page qui en
# emploie une sans que rien ne la définisse affiche le bloc sans aucun style.
CLASSES = [
    'daat-two-col', 'daat-two-col-he', 'daat-two-col-fr',
    'he-q', 'src-ref', 'comment-source', 'text-source', 'sacred-text',
    'index-box', 'remember', 'key-point', 'definition',
    'rishon-card', 'hakira-box', 'pilpul-box', 'machloket-box',
    'nafka-mina-box', 'yesod-box', 'teruts-box', 'kashya-box',
    'rav-box', 'seif-details', 'translation', 'src-paren',
    # Le codage couleur du verdict dans les tableaux de psak. Six pages des
    # simanim 149 et 152 l'employaient sans le définir : « Interdit » et
    # « Permis » s'y affichaient en noir, et rien ne le signalait.
    'chaud', 'froid',
]

RE_LIEN_CSS = re.compile(r'<link[^>]+href="([^"]+\.css)"', re.I)


def definies_dans(css):
    """Noms de classes définies par une feuille de style (ou un <style> inline)."""
    return set(re.findall(r'\.([A-Za-z][\w-]*)', css))


_cache = {}


def feuille(chemin):
    if chemin not in _cache:
        try:
            _cache[chemin] = definies_dans(open(chemin, encoding='utf-8').read())
        except OSError:
            _cache[chemin] = set()
    return _cache[chemin]


def defauts(path, html):
    """Classes de contenu employées par la page sans définition atteignable."""
    corps = re.sub(r'<style\b.*?</style>', '', html, flags=re.S | re.I)
    employees = set()
    for m in re.finditer(r'class="([^"]*)"', corps):
        employees |= set(m.group(1).split())
    employees &= set(CLASSES)
    if not employees:
        return []

    # Ce que la page définit elle-même, plus ce qu'apportent ses feuilles.
    connues = set()
    for m in re.finditer(r'<style\b[^>]*>(.*?)</style>', html, flags=re.S | re.I):
        connues |= definies_dans(m.group(1))
    for href in RE_LIEN_CSS.findall(html):
        rel = href.lstrip('/')
        if rel.startswith('assets/'):
            cible = os.path.join(ROOT, rel)
        else:
            cible = os.path.normpath(os.path.join(os.path.dirname(path), href))
        connues |= feuille(cible)

    return sorted(employees - connues)


def main(argv):
    detail = '--lignes' in argv
    cible = 'sources'
    if '--path' in argv:
        cible = argv[argv.index('--path') + 1]

    base = cible if os.path.isabs(cible) else os.path.join(ROOT, cible)
    motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base

    pages, fautives, manquantes = 0, 0, {}
    for p in sorted(glob.glob(motif, recursive=True)):
        pages += 1
        d = defauts(p, open(p, encoding='utf-8').read())
        if not d:
            continue
        fautives += 1
        for c in d:
            manquantes.setdefault(c, []).append(os.path.relpath(p, ROOT))
        if detail:
            print(f'  {os.path.relpath(p, ROOT)} : ' + ', '.join(d))

    if manquantes:
        print()
        for c, pp in sorted(manquantes.items(), key=lambda kv: -len(kv[1])):
            print(f'  .{c:<20} employée sans définition dans {len(pp)} page(s)'
                  f'  — p. ex. {pp[0]}')

    print(f'\n{pages} page(s) examinée(s) dans {cible}')
    print(f'→ {fautives} page(s) employant une classe de contenu que rien ne définit')
    return 1 if fautives else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
