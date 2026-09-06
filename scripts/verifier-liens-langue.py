#!/usr/bin/env python3
"""Septième garde-fou : un lien interne mène-t-il à la page de LA MÊME LANGUE ?

`verifier-liens.py` demande si un lien mène à un fichier réel. C'est nécessaire et
ce n'est pas suffisant : depuis `niveau-1-base-he.html`, un lien vers
`niveau-2-lamdan.html` mène à un fichier qui existe parfaitement — la page
FRANÇAISE. Le lecteur hébréophone qui clique « niveau 2 » change de langue sans
l'avoir demandé, et le contrôle des liens sort vert.

Aucun des six autres ne peut le voir. `verifier-liens.py` ne juge que l'existence
du fichier ; `verifier-langues.py` et `verifier-url-langue.py` jugent le contenu
de la page, jamais la destination de ses liens.

Le même défaut existe sous forme absolue (`/yd/156/` depuis une page hébraïque au
lieu de `/yd/156/he`) : il a été trouvé sur trois index du lot 153-159, et corrigé
là. Celui-ci est sa forme relative, et il est bien plus répandu.


Le défaut existe sous DEUX formes, et le script contrôle les deux :
  · relative — `href="niveau-2-lamdan.html"` depuis `X-he.html` ;
  · absolue  — `href="/yd/160/"` depuis `X-he.html`, au lieu de `/yd/160/he`.
La seconde a été trouvée trois fois sur des index déjà publiés, et une quatrième
sur le siman 161 pendant sa production. Elle est pire que la première : elle vise
une URL publique, donc elle survit à toute réorganisation des fichiers.

Ce que le script contrôle : dans toute page `X-he.html` ou `X-en.html`, un lien
relatif vers `index.html` ou `niveau-N-….html` doit porter le suffixe de langue de
la page, dès lors que le fichier cible existe. Un lien vers une variante
inexistante n'est pas réécrit — ce serait échanger un défaut contre un lien mort.

Usage :
    python3 scripts/verifier-liens-langue.py                       # tout sources/
    python3 scripts/verifier-liens-langue.py --path sources/yoreh-deah
    python3 scripts/verifier-liens-langue.py --lignes              # + le détail

Code de sortie non nul dès qu'un lien change la langue du lecteur.
"""
import os
import re
import sys
import glob
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Un lien relatif, dans le même répertoire, vers une page d'étude ou l'index.
# Le motif exclut les liens DÉJÀ suffixés : sans la garde `(?<!-he)(?<!-en)`,
# « niveau-1-base-he.html » correspond, et le script cherche en vain un
# « niveau-1-base-he-he.html » — il comptait alors 5756 liens parfaitement
# corrects comme « variante absente », c'est-à-dire qu'il disait faux dans son
# propre rapport.
RE_LIEN = re.compile(r'href="((?:index|niveau-\d-[a-z0-9-]+?))(?<!-he)(?<!-en)\.html((?:#[\w.-]+)?)"')
SUFFIXES = {'-he': 'he', '-en': 'en'}
# La forme absolue : /yd/160/ (français) au lieu de /yd/160/he.
RE_ABS = re.compile(r'href="/yd/(\d+)/"')


def defauts(path):
    """Liens de la page qui mènent à une autre langue que la sienne."""
    base = os.path.basename(path)
    suf = next((s for s in SUFFIXES if base.endswith(s + '.html')), None)
    if suf is None:
        return []                       # page française : le lien nu est correct
    html = open(path, encoding='utf-8').read()
    out = []
    for m in RE_LIEN.finditer(html):
        cible = m.group(1) + suf + '.html'
        if not os.path.exists(os.path.join(os.path.dirname(path), cible)):
            continue                    # pas de variante : ne rien promettre
        ligne = html.count('\n', 0, m.start()) + 1
        out.append((ligne, m.group(1) + '.html', cible))

    lang = SUFFIXES[suf]
    for m in RE_ABS.finditer(html):
        ligne = html.count('\n', 0, m.start()) + 1
        out.append((ligne, '/yd/%s/' % m.group(1), '/yd/%s/%s' % (m.group(1), lang)))
    return out


def main(argv):
    detail = '--lignes' in argv
    cible = 'sources'
    if '--path' in argv:
        cible = argv[argv.index('--path') + 1]
    base = cible if os.path.isabs(cible) else os.path.join(ROOT, cible)
    motif = os.path.join(base, '**', '*.html') if os.path.isdir(base) else base

    pages, fautives, total = 0, 0, 0
    par_siman = collections.Counter()
    for p in sorted(glob.glob(motif, recursive=True)):
        pages += 1
        d = defauts(p)
        if not d:
            continue
        fautives += 1
        total += len(d)
        rel = os.path.relpath(p, ROOT)
        par_siman[os.path.dirname(rel)] += len(d)
        if detail:
            for ligne, avant, apres in d:
                print(f'  {rel}:{ligne} : {avant} → {apres}')

    if par_siman:
        print()
        for d, n in par_siman.most_common(12):
            print(f'  {d:<44} {n:>4} lien(s)')
        if len(par_siman) > 12:
            print(f'  … et {len(par_siman) - 12} autre(s) répertoire(s)')

    print(f'\n{pages} page(s) examinée(s) dans {cible}')
    print(f'→ {fautives} page(s) portant {total} lien(s) qui changent la langue du lecteur')
    return 1 if fautives else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
