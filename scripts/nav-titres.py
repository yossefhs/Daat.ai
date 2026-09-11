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

⚠️ LE <h1> EST CANONIQUE POUR L'IDENTITÉ DU SIMAN, PAS POUR SON LIBELLÉ DE NAVIGATION.
Recopié tel quel, il traîne deux choses qui n'ont rien à faire dans une barre de
navigation : un SOUS-TITRE après deux-points (le siman 183 s'intitule « La femme qui
voit du sang compte sept jours propres : מקור, הרגשה et le fondement de la Nidah »,
le 118 « … (חותמות) : un ou deux sceaux, les signes et la נאמנות »), et, en hébreu,
la VOCALISATION complète (le 143). Le sous-titre explique, il ne nomme pas ; et le
nikoud d'un libellé de navigation n'est que du bruit.
Le libellé retenu est donc le titre COUPÉ à son premier deux-points, et dévocalisé
en hébreu. C'est ce qui a fait renoncer à réaligner 69 libellés des simanim 119-145 :
la moitié des réécritures dégradait la navigation au lieu de la corriger.

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


# Le nikoud et les te'amim SEULEMENT. Le bloc U+0591-U+05C7 contient aussi de la
# PONCTUATION qui appartient au mot : le maqaf ־ (U+05BE), le paseq (U+05C0), le
# sof passouq (U+05C3). Les prendre pour du nikoud faisait de « דף־גשר » un
# « דףגשר » — un mot qui n'existe pas, dans le libellé du siman 169.
NIKOUD = re.compile(r'[\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]')


def _elaguer(t, lang):
    """Le titre, ramené à ce qui NOMME le siman : sans sous-titre, sans nikoud.

    Le deux-points sépare le nom de son explication — on garde le nom. En français
    il s'écrit « … : … » (espace insécable comprise), en anglais « …: … » ; dans
    les deux cas on ne coupe que si les deux moitiés sont substantielles, pour ne
    pas amputer un titre qui emploierait le signe autrement.
    """
    if lang == 'he':
        return NIKOUD.sub('', t).strip()
    m = re.search(r'[\s\u00a0]*:[\s\u00a0]+', t)
    if m and m.start() >= 12 and len(t) - m.end() >= 4:
        return t[:m.start()].strip()
    return t


def libelle(num, lang, sens):
    """Libellé attendu, flèches comprises."""
    t = titre(num, lang)
    if not t:
        return None
    t = _elaguer(t, lang)
    if lang == 'he':
        # Le <h1> hébreu s'écrit sous deux formes : « סימן ק״נ — titre » et
        # « סימן ק״נ · 150 — titre ». Ne reconnaître que la première faisait
        # renoncer le script EN SILENCE, et trois index hébreux gardaient un
        # libellé français sous une URL hébraïque.
        m = re.match(r'^(סימן\s+\S+)(?:\s*·\s*\d+)?\s*—\s*(.*)$', t)
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
