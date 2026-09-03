#!/usr/bin/env python3
"""Pose dans la page les règles des classes de contenu qu'elle emploie sans les définir.

Suite de `fix-two-col.py`, qui traitait un seul cas à la main. `verifier-classes.py`
a montré que le défaut est plus large : 87 pages emploient une classe de contenu —
`remember`, `he-q`, `src-ref`, `key-point`, `translation`… — que ni leur `<style>`
inline ni aucune feuille qu'elles chargent ne définit. Le bloc s'affiche alors sans
fond, sans filet, sans direction RTL pour l'hébreu.

D'où viennent les règles posées ici : ces classes ne vivent PAS dans une feuille
commune, mais en ligne dans des milliers de pages (4 003 pages définissent `.he-q`,
1 288 `.remember`). La règle retenue pour chaque classe est donc la forme
MAJORITAIRE observée dans le dépôt, relevée mécaniquement — pas une règle inventée
pour l'occasion. Une page réparée ressemble ainsi à ses voisines.

On n'ajoute JAMAIS une feuille de style à la page : lui faire charger
`daat-enhance.css` importerait un système de design entier là où une seule règle
manque, et restylerait bien plus que le bloc à réparer.

Usage : python3 scripts/fix-classes.py [--dry-run] [--path sources/yoreh-deah]
Idempotent : une page qui définit déjà la classe n'est pas retouchée.
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Formes majoritaires relevées dans le dépôt (nombre de pages qui les portent).
REGLES = {
    'remember':       ".remember { background: #e8f4ea; border: 1.5px solid #2d7a3e; padding: 12px 18px; margin: 12px 0; border-radius: 4px; }",
    'he-q':           ".he-q { direction: rtl; unicode-bidi: embed; font-family: 'Frank Ruhl Libre', 'David', serif; font-weight: 600; color: #1A1F3A; }",
    'src-ref':        ".src-ref { text-align: left; font-size: 9.5pt; color: #5a4a1a; margin: -4px 0 14px 0; font-style: italic; }",
    'key-point':      ".key-point { background: #fff8e1; border-left: 5px solid #C5A55A; padding: 10px 16px; margin: 12px 0; page-break-inside: avoid; }",
    'comment-source': "blockquote.comment-source { font-style: normal; }",
    'src-paren':      ".src-paren { color: #5a4a1a; }",
    'translation':    ".translation { background: #f5f5f0; border-left: 3px solid #1A1F3A; padding: 12px 18px; margin: 15px 0; font-style: italic; }",
}

RE_LIEN_CSS = re.compile(r'<link[^>]+href="([^"]+\.css)"', re.I)
_cache = {}


def definies(css):
    return set(re.findall(r'\.([A-Za-z][\w-]*)', css))


def feuille(chemin):
    if chemin not in _cache:
        try:
            _cache[chemin] = definies(open(chemin, encoding='utf-8').read())
        except OSError:
            _cache[chemin] = set()
    return _cache[chemin]


def manquantes(path, html):
    corps = re.sub(r'<style\b.*?</style>', '', html, flags=re.S | re.I)
    employees = set()
    for m in re.finditer(r'class="([^"]*)"', corps):
        employees |= set(m.group(1).split())
    employees &= set(REGLES)
    if not employees:
        return []
    connues = set()
    for m in re.finditer(r'<style\b[^>]*>(.*?)</style>', html, flags=re.S | re.I):
        connues |= definies(m.group(1))
    for href in RE_LIEN_CSS.findall(html):
        rel = href.lstrip('/')
        cible = (os.path.join(ROOT, rel) if rel.startswith('assets/')
                 else os.path.normpath(os.path.join(os.path.dirname(path), href)))
        connues |= feuille(cible)
    return sorted(employees - connues)


def main(argv):
    dry = '--dry-run' in argv
    cible = 'sources'
    if '--path' in argv:
        cible = argv[argv.index('--path') + 1]
    base = cible if os.path.isabs(cible) else os.path.join(ROOT, cible)
    motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base

    touchees, total = 0, 0
    for p in sorted(glob.glob(motif, recursive=True)):
        html = open(p, encoding='utf-8').read()
        m = manquantes(p, html)
        if not m:
            continue
        if '</style>' not in html:
            print(f'  ⚠ {os.path.relpath(p, ROOT)} : aucun <style> où poser les règles')
            continue
        bloc = ('\n  /* Classes employées par cette page et définies nulle part ailleurs.\n'
                '     Formes majoritaires du dépôt — cf. scripts/fix-classes.py. */\n  '
                + '\n  '.join(REGLES[c] for c in m) + '\n')
        if not dry:
            open(p, 'w', encoding='utf-8').write(html.replace('</style>', bloc + '</style>', 1))
        touchees += 1
        total += len(m)
        print(f'  {os.path.relpath(p, ROOT)} : ' + ', '.join('.' + c for c in m))
    print(f"{'(à blanc) ' if dry else ''}{total} règle(s) posée(s) dans {touchees} page(s)")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
