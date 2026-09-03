#!/usr/bin/env python3
"""Replie chaque citation de commentateur sur une seule ligne, référence comprise.

`verifier-citations.py` extrait les citations LIGNE À LIGNE. Un bloc réparti sur
plusieurs lignes, dont la référence vit dans un <p class="src-ref"> posé après la
fermeture du blockquote, lui est donc invisible : la citation sort en « sans
référence » et n'est jamais confrontée à sa source. Mesuré sur le siman 127 : 30 de
ses 174 citations, soit près d'une sur six, échappaient au contrôle — non pas
fausses, mais non surveillées.

Ce script remet chaque bloc `comment-source` sur une ligne, encadre son hébreu de
« … » s'il ne l'est pas déjà, et fait entrer la référence dans le blockquote sous
forme de <span class="src-ref">. Le rendu ne change pas : deux règles CSS sont
ajoutées à la feuille inline pour que le span reste un bloc en style normal.

Le texte lui-même n'est jamais touché — ni un mot, ni une ponctuation.

Usage : python3 scripts/plier-citations.py sources/yoreh-deah/siman-127 [...] [--dry-run]
Idempotent : un bloc déjà plié ne correspond plus au motif.
"""
import re, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HE = re.compile(r'[א-ת]')
BLOC = re.compile(
    r'<blockquote class="comment-source"([^>]*)>\s*(.*?)\s*</blockquote>'
    r'(?:\s*<p class="src-ref">\s*(.*?)\s*</p>)?',
    re.S)
CSS = ('blockquote.comment-source .src-ref{display:block;font-style:normal;'
       'margin-top:.4rem;font-size:.9em;opacity:.85}')


def plier(html):
    n = 0

    def repl(m):
        nonlocal n
        attrs, corps, ref = m.group(1), m.group(2), m.group(3)
        if '\n' not in m.group(0) and (ref is None):
            return m.group(0)                      # déjà sur une ligne, rien à faire
        corps = re.sub(r'\s*\n\s*', ' ', corps).strip()
        if not HE.search(re.sub(r'<[^>]+>', '', corps)):
            return m.group(0)                      # pas d'hébreu : on ne touche pas
        if '«' not in corps and '»' not in corps:
            corps = '« ' + corps + ' »'
        if ref:
            ref = re.sub(r'\s*\n\s*', ' ', ref).strip()
            corps += f' <span class="src-ref">{ref}</span>'
        n += 1
        return f'<blockquote class="comment-source"{attrs}>{corps}</blockquote>'

    out = BLOC.sub(repl, html)
    if n and '.comment-source .src-ref' not in out:
        out = out.replace('</style>', '    ' + CSS + '\n  </style>', 1)
    return out, n


def main(argv):
    dry = '--dry-run' in argv
    total, fichiers = 0, 0
    for cible in [a for a in argv if not a.startswith('--')]:
        base = os.path.join(ROOT, cible)
        motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base
        for p in sorted(glob.glob(motif, recursive=True)):
            html = open(p, encoding='utf-8').read()
            neuf, n = plier(html)
            if n:
                total += n; fichiers += 1
                if not dry:
                    open(p, 'w', encoding='utf-8').write(neuf)
                print(f"  {os.path.relpath(p, ROOT)} : {n} bloc(s)")
    print(f"{'(à blanc) ' if dry else ''}{total} citation(s) repliée(s) dans {fichiers} fichier(s)")


if __name__ == '__main__':
    main(sys.argv[1:])
