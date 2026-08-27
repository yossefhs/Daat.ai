#!/usr/bin/env python3
"""Réserve « … » au verbatim hébreu, et rend « … » latin à “ … ”.

Convention du site (règle 17 du cahier des charges de production) : les chevrons
signalent une citation hébraïque mot pour mot, et rien d'autre. C'est ce qui rend le
vérificateur de citations utilisable : il n'a à juger que ce qui est réellement une
citation. Un « je ne te crois pas » français entre chevrons le fait chercher, dans
Sefaria, un texte qui n'y sera jamais.

Ce script ne touche qu'aux paires de chevrons ne contenant PAS UNE SEULE lettre
hébraïque — donc jamais à une citation, même partielle, même mêlée de français.

Usage : python3 scripts/fix-guillemets.py sources/yoreh-deah/siman-123 [...] [--dry-run]
Idempotent.
"""
import re, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HE = re.compile(r'[א-ת]')
PAIRE = re.compile(r'«([^«»]{1,600})»', re.S)


def main(argv):
    dry = '--dry-run' in argv
    cibles = [a for a in argv if not a.startswith('--')]
    total, fichiers = 0, 0
    for cible in cibles:
        base = os.path.join(ROOT, cible)
        motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base
        for p in sorted(glob.glob(motif, recursive=True)):
            html = open(p, encoding='utf-8').read()
            n = 0

            def remplace(m):
                nonlocal n
                if HE.search(m.group(1)):
                    return m.group(0)      # contient de l'hébreu : c'est une citation
                n += 1
                return '“' + m.group(1) + '”'

            neuf = PAIRE.sub(remplace, html)
            if n:
                total += n; fichiers += 1
                if not dry:
                    open(p, 'w', encoding='utf-8').write(neuf)
                print(f"  {os.path.relpath(p, ROOT)} : {n}")
    print(f"{'(à blanc) ' if dry else ''}{total} paire(s) latine(s) convertie(s) dans {fichiers} fichier(s)")


if __name__ == '__main__':
    main(sys.argv[1:])
