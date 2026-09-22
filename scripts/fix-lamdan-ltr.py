#!/usr/bin/env python3
"""Un niveau 2 traduit doit se LIRE de gauche à droite — sauf son hébreu.

Les niveaux 2 de quarante-neuf simanim de Yoré Déa étaient servis entièrement en hébreu
sous leurs trois URL. En les traduisant, la feuille de style reste celle de la page
hébraïque : `direction: rtl` posé sur `body`, sur les titres de section, sur `th` et
`td`, sur `.cover`, sur les encadrés. La page française s'affiche alors alignée à droite,
listes et filets inversés — un défaut qu'AUCUNE porte ne voit, puisque le texte est bien
français et le `lang=` bien `fr`.

Le modèle est `sources/yoreh-deah/siman-234/niveau-2-lamdan.html`, produit correctement :
le RTL n'y subsiste que sur ce qui porte de l'hébreu — `.he`, `.he-q`, `h3.he-h3`, les
`::before` des encadrés (leurs étiquettes sont hébraïques), `td.he/th.he`, les
`blockquote` de citation, le bouton de copie, et la forme SCOPÉE `[dir="rtl"] th, td`.

Ce script retire le RTL des seuls sélecteurs de PROSE, et repasse leur alignement à
gauche. Il ne touche jamais un sélecteur hébreu, ni le fichier `-he`, qui est la variante
hébraïque et doit rester RTL de bout en bout.

Usage :
  python3 scripts/fix-lamdan-ltr.py 87 88 89        # des simanim
  python3 scripts/fix-lamdan-ltr.py --tous          # tous les niveaux 2 traduits
  python3 scripts/fix-lamdan-ltr.py 87 --dry-run
"""
import re, sys, os, io, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Un sélecteur porte de l'hébreu si son nom le dit. Tout le reste est de la prose.
# `ded-prefix` et `ded-name` sont la dédicace hébraïque du bandeau : le siman 234, qui
# est le modèle, les garde en RTL. Les oublier faisait toucher au modèle lui-même par ce
# script — c'est l'essai à blanc sur le 234 qui l'a montré, et c'est la raison de le
# faire systématiquement avant d'appliquer un correctif de masse.
HEBREU = re.compile(r'\.he\b|\.he-q\b|he-h3|he-title|he-sub|he-subject|::before'
                    r'|blockquote|daat-copy|\[dir="rtl"\]|source-ref|src-ref|sacred-text'
                    r'|ded-prefix|ded-name|ded-multi|yh-watermark')

RE_REGLE = re.compile(r'([^{}]+)\{([^}]*)\}')

def convertir(css):
    """Rend (css, nombre de règles dépouillées de leur RTL)."""
    out, pos, n = [], 0, 0
    for m in RE_REGLE.finditer(css):
        sel, corps = m.group(1), m.group(2)
        # le commentaire qui précède le sélecteur n'en fait pas partie
        sel_net = re.sub(r'/\*.*?\*/', '', sel, flags=re.S).strip()
        if HEBREU.search(sel_net):
            continue
        neuf = re.sub(r'\s*direction\s*:\s*rtl\s*;?', '', corps)
        neuf = re.sub(r'text-align\s*:\s*right', 'text-align: left', neuf)
        if neuf == corps:
            continue          # ne compter que ce qui change réellement
        out.append(css[pos:m.start(2)]); out.append(neuf)
        pos = m.end(2); n += 1
    out.append(css[pos:])
    return ''.join(out), n

def traiter(path, dry=False):
    s = io.open(path, encoding='utf-8').read()
    total = 0
    def rendre(m):
        nonlocal total
        neuf, n = convertir(m.group(0))
        total += n
        return neuf
    s2 = re.sub(r'(?s)<style[^>]*>.*?</style>', rendre, s)
    # une page traduite ne se déclare pas hébraïque à Google
    s2, n_lang = re.subn(r'"inLanguage"\s*:\s*"he-IL"',
                         '"inLanguage": "en-US"' if path.endswith('-en.html')
                         else '"inLanguage": "fr-FR"', s2)
    if s2 != s and not dry:
        io.open(path, 'w', encoding='utf-8').write(s2)
    return total, n_lang

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    if '--tous' in sys.argv:
        cibles = [p for p in sorted(glob.glob(
            os.path.join(ROOT, 'sources/yoreh-deah/siman-*/niveau-2-lamdan*.html')))
            if not p.endswith('-he.html')]
    else:
        cibles = []
        for a in args:
            for suf in ('', '-en'):
                p = os.path.join(ROOT,
                                 f'sources/yoreh-deah/siman-{a}/niveau-2-lamdan{suf}.html')
                if os.path.exists(p):
                    cibles.append(p)
    tr = tl = 0
    for p in cibles:
        r, l = traiter(p, dry)
        tr += r; tl += l
        if r or l:
            print(f"  {os.path.relpath(p, ROOT)} : {r} règle(s) repassée(s) en LTR"
                  + (f", inLanguage corrigé" if l else ""))
    print(f"\n{len(cibles)} fichier(s) examiné(s) · {tr} règle(s) de prose dépouillées du "
          f"RTL · {tl} inLanguage corrigé(s)")
    if dry:
        print("(essai à blanc — rien n'a été écrit)")
    return 0

if __name__ == '__main__':
    sys.exit(main())
