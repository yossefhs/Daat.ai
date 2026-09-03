#!/usr/bin/env python3
"""Aligne les libellés de navigation sur le titre canonique du siman visé.

Deux simanim produits en parallèle se nomment l'un l'autre de mémoire, et chacun
invente un libellé pour son voisin avant que celui-ci n'existe. Le lecteur voit
alors, sur la page 150, « Siman 149 — Les lois de la foire des idolâtres », et sur
la page 149 elle-même « La foire des non-Juifs ». Deux noms pour un seul siman, et
le catalogue en donne un troisième si l'on n'y prend pas garde.

Le titre canonique est celui que le siman se donne à lui-même : le <h1> de son
propre `index`, dans chaque langue — c'est aussi celui que le catalogue reprend.
Ce script relit tous les liens de navigation `class="prev"` / `class="next"` vers
`/yd/N/`, `/yd/N/he`, `/yd/N/en` et réécrit leur libellé depuis cette source.

Les flèches et la forme des libellés sont conservées telles que le dépôt les écrit :
    FR/EN   « ← Siman N — titre »  ·  « Siman N — titre → »
    HE      « → סימן ק״נ · N — titre »  ·  « סימן ק״נ · N — titre ← »

Usage : python3 scripts/nav-titres.py [--dry-run] [--path sources/yoreh-deah]
Idempotent : un libellé déjà conforme n'est pas réécrit.
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RE_LIEN = re.compile(r'<a href="/yd/(\d+)/(he|en)?"\s+class="(prev|next)">(.*?)</a>')
_titres = {}


def titre(num, lang):
    """Titre canonique du siman, tel que son propre index le porte."""
    cle = (num, lang)
    if cle not in _titres:
        suf = {'': '', 'he': '-he', 'en': '-en'}[lang]
        p = os.path.join(ROOT, f'sources/yoreh-deah/siman-{num}/index{suf}.html')
        try:
            s = open(p, encoding='utf-8').read()
            h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1)
            _titres[cle] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h1)).strip()
        except (OSError, AttributeError):
            _titres[cle] = None
    return _titres[cle]


def libelle(num, lang, sens):
    """Libellé attendu, flèches comprises."""
    t = titre(num, lang)
    if not t:
        return None
    if lang == 'he':
        # le <h1> hébreu porte déjà « סימן ק״נ — titre » ; on y insère le chiffre
        m = re.match(r'^(סימן\s+\S+)\s*—\s*(.*)$', t)
        if not m:
            return None
        return (f'→ {m.group(1)} · {num} — {m.group(2)}' if sens == 'prev'
                else f'{m.group(1)} · {num} — {m.group(2)} ←')
    return f'← {t}' if sens == 'prev' else f'{t} →'


def main(argv):
    dry = '--dry-run' in argv
    cible = 'sources/yoreh-deah'
    if '--path' in argv:
        cible = argv[argv.index('--path') + 1]
    base = cible if os.path.isabs(cible) else os.path.join(ROOT, cible)
    motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base

    total, fichiers = 0, 0
    for p in sorted(glob.glob(motif, recursive=True)):
        html = open(p, encoding='utf-8').read()
        n = 0

        def remplace(m):
            nonlocal n
            num, lang, sens, texte = int(m.group(1)), m.group(2) or '', m.group(3), m.group(4)
            attendu = libelle(num, lang, sens)
            if attendu is None or texte == attendu:
                return m.group(0)
            n += 1
            print(f'  {os.path.relpath(p, ROOT)}\n      – {texte}\n      + {attendu}')
            return f'<a href="/yd/{num}/{lang}" class="{sens}">{attendu}</a>'

        neuf = RE_LIEN.sub(remplace, html)
        if n:
            total += n
            fichiers += 1
            if not dry:
                open(p, 'w', encoding='utf-8').write(neuf)
    print(f"{'(à blanc) ' if dry else ''}{total} libellé(s) réaligné(s) dans {fichiers} fichier(s)")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
