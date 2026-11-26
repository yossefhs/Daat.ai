#!/usr/bin/env python3
"""Pose le lien « suivant » de N vers N+1 dans les 15 pages de N (réécrit le 26 novembre 2026, l'original ayant été perdu).

usage : liens-suivant.py RACINE N [N ...]   (pose N -> N+1 pour chaque N ; ou N:M pour N -> M)
Niveaux : <span class="nav-spacer"></span> → <a href="/oh/M/niv[/lang]" class="nav-next">Siman M →</a>
          (HE : « ← סימן XXX · M »), au format des liens déjà publiés (siman 392).
Index   : <a href="/oh/M/[lang]" class="next">Siman M — titre →</a> après le lien « prev » du <nav class="siman-neighbors">
          (HE : « ← סימן XXX — titre »), le titre venant du <title> de l'index de M.
Chaque remplacement est compté : exactement 1 par fichier, sinon arrêt sans rien écrire.
"""
import re, sys, pathlib

racine = pathlib.Path(sys.argv[1])
NIVEAUX = {'niveau-1-base': 'base', 'niveau-2-lamdan': 'lamdan', 'niveau-3-synthese': 'synthese', 'niveau-4-daat-harav': 'daat-harav'}
HE_NUM = {389: 'שפ״ט', 390: 'ש״צ', 391: 'שצ״א', 392: 'שצ״ב', 393: 'שצ״ג', 394: 'שצ״ד', 395: 'שצ״ה', 396: 'שצ״ו',
          397: 'שצ״ז', 398: 'שצ״ח', 399: 'שצ״ט', 400: 'ת׳', 401: 'ת״א'}


def titre(m, suf):
    t = (racine / f'sources/shabbat/siman-{m}/index{suf}.html').read_text()
    return re.search(r'<title>(.*?) \| ', t).group(1).split(' — ', 1)[1]


ecrits = {}
for arg in sys.argv[2:]:
    n, m = (int(x) for x in arg.split(':')) if ':' in arg else (int(arg), int(arg) + 1)
    for suf, lang in (('', ''), ('-he', 'he'), ('-en', 'en')):
        for stem, niv in NIVEAUX.items():
            f = racine / f'sources/shabbat/siman-{n}/{stem}{suf}.html'
            s = f.read_text()
            href = f'/oh/{m}/{niv}' + (f'/{lang}' if lang else '')
            lien = (f'<a href="{href}" class="nav-next">← סימן {HE_NUM[m]} · {m}</a>' if lang == 'he'
                    else f'<a href="{href}" class="nav-next">Siman {m} →</a>')
            s2, k = re.subn(r'<span class="nav-spacer"></span>(\s*</nav>)', lambda x: lien + x.group(1), s)
            assert k == 1, (f, k)
            ecrits[f] = s2
        f = racine / f'sources/shabbat/siman-{n}/index{suf}.html'
        s = f.read_text()
        href = f'/oh/{m}/' + lang
        lien = (f'<a href="{href}" class="next">← סימן {HE_NUM[m]} — {titre(m, suf)}</a>' if lang == 'he'
                else f'<a href="{href}" class="next">Siman {m} — {titre(m, suf)} →</a>')
        pat = r'(<nav class="siman-neighbors"[^>]*>\s*<a [^>]*class="prev">[^<]*</a>)(?:\s*<span></span>)?(\s*</nav>)'
        s2, k = re.subn(pat, lambda x: x.group(1) + '\n      ' + lien + x.group(2), s)
        assert k == 1, (f, k)
        ecrits[f] = s2
for f, s in ecrits.items():
    f.write_text(s)
print(len(ecrits), 'fichiers écrits')
