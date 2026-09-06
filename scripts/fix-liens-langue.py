#!/usr/bin/env python3
"""Rend à chaque lien interne la langue de la page qui le porte.

Correctif de ce que `verifier-liens-langue.py` mesure : depuis `X-he.html`, un
lien vers `niveau-2-lamdan.html` envoie le lecteur hébréophone sur la page
française. Le fichier existe, donc le contrôle des liens sort vert ; seul le
lecteur s'en aperçoit, et il est déjà parti.

Le correctif ajoute le suffixe de langue de la page au lien, **et seulement si le
fichier cible existe**. Un lien vers une variante absente n'est pas réécrit : on
n'échange pas un défaut de langue contre un lien mort. L'ancre (`#sec-3`) est
conservée telle quelle.

Usage : python3 scripts/fix-liens-langue.py [--dry-run] [--path sources/yoreh-deah]
Idempotent : un lien déjà suffixé ne correspond plus au motif.
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Le motif exclut les liens DÉJÀ suffixés : sans la garde `(?<!-he)(?<!-en)`,
# « niveau-1-base-he.html » correspond, et le script cherche en vain un
# « niveau-1-base-he-he.html » — il comptait alors 5756 liens parfaitement
# corrects comme « variante absente », c'est-à-dire qu'il disait faux dans son
# propre rapport.
RE_LIEN = re.compile(r'href="((?:index|niveau-\d-[a-z0-9-]+?))(?<!-he)(?<!-en)\.html((?:#[\w.-]+)?)"')
SUFFIXES = ('-he', '-en')
# Forme absolue du même défaut : /yd/160/ depuis une page hébraïque.
RE_ABS = re.compile(r'href="/yd/(\d+)/"')


def main(argv):
    dry = '--dry-run' in argv
    cible = 'sources'
    if '--path' in argv:
        cible = argv[argv.index('--path') + 1]
    base = cible if os.path.isabs(cible) else os.path.join(ROOT, cible)
    motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base

    fichiers, total, sautes = 0, 0, 0
    for p in sorted(glob.glob(motif, recursive=True)):
        nom = os.path.basename(p)
        suf = next((s for s in SUFFIXES if nom.endswith(s + '.html')), None)
        if suf is None:
            continue
        rep = os.path.dirname(p)
        html = open(p, encoding='utf-8').read()
        n = 0

        def remplace(m):
            nonlocal n, sautes
            stem, ancre = m.group(1), m.group(2)
            if not os.path.exists(os.path.join(rep, stem + suf + '.html')):
                sautes += 1
                return m.group(0)
            n += 1
            return f'href="{stem}{suf}.html{ancre}"'

        neuf = RE_LIEN.sub(remplace, html)
        lang = suf.lstrip('-')
        neuf, k = RE_ABS.subn(lambda m: 'href="/yd/%s/%s"' % (m.group(1), lang), neuf)
        n += k
        if n:
            fichiers += 1
            total += n
            if not dry:
                open(p, 'w', encoding='utf-8').write(neuf)
            print(f'  {os.path.relpath(p, ROOT)} : {n} lien(s)')
    print(f"{'(à blanc) ' if dry else ''}{total} lien(s) rendus à leur langue "
          f"dans {fichiers} fichier(s)"
          + (f" · {sautes} laissé(s) intact(s), variante absente" if sautes else ""))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
