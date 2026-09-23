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

# Les propriétés dont le côté doit basculer quand la page passe en LTR.
COTES = ('padding', 'margin', 'border')

def permuter_cotes(corps):
    """Bascule la géométrie latérale d'une règle hébraïque vers le sens LTR."""
    def swap(m):
        prop, cote = m.group(1), m.group(2)
        if prop not in COTES:
            return m.group(0)
        return f"{prop}-{'left' if cote == 'right' else 'right'}"
    return re.sub(r'\b(' + '|'.join(COTES) + r')-(right|left)\b', swap, corps)

RE_LISTE = re.compile(r'(?:^|[\s,>])(?:ol|ul)\b')
RE_GEOM_HE = re.compile(r'padding-right(\s*:\s*)([1-9]\d*px)(\s*;\s*)padding-left(\s*:\s*)0')

def redresser_listes(sel, corps):
    """`ol.stylish { padding-right: 22px; padding-left: 0 }` → l'inverse.

    La borne `if 'rtl' in corps` de `convertir` protège l'idempotence, mais elle
    laisse passer tout un genre de règle : celles qui posent la géométrie
    hébraïque SANS déclarer `direction: rtl`. Le retrait des listes y est à
    droite, et en LTR le sommaire et les listes numérotées n'ont plus de retrait
    du tout. Un arbitre l'a relevé sur le siman 118 ; mesuré ensuite sur tout le
    dépôt, c'étaient 129 règles dans 68 pages non hébraïques — les 24 simanim
    traduits du chantier et le bloc נדה, c'est-à-dire précisément ce que ce
    script avait touché. Un correctif local n'en aurait réparé que deux.

    Deux bornes, et elles comptent : le sélecteur doit viser une LISTE (jamais
    une bordure d'encadré — la permutation non bornée aurait renvoyé le modèle
    du siman 234 de border-left à border-right), et il ne doit pas être déjà
    porté par un `[dir="rtl"]`, qui vise du contenu hébreu et a raison de garder
    sa géométrie. Idempotent : après coup `padding-right` vaut 0, le motif ne
    s'applique plus.
    """
    if 'dir="rtl"' in sel or not RE_LISTE.search(sel):
        return corps
    return RE_GEOM_HE.sub(
        lambda m: f'padding-left{m.group(1)}{m.group(2)}{m.group(3)}padding-right{m.group(4)}0',
        corps)

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
        # Retirer le RTL ne suffit pas : le gabarit hébreu met le retrait des listes
        # à DROITE — `ol.stylish { padding-right: 22px; padding-left: 0 }`. En LTR, le
        # sommaire et les listes numérotées perdent alors tout retrait à gauche et les
        # puces débordent. Un arbitre l'a vu là où le script ne regardait pas : il
        # corrigeait la direction du texte et laissait la géométrie hébraïque.
        # …mais SEULEMENT si la règle portait le RTL. Sans cette borne, le script
        # n'est pas idempotent et retourne la géométrie d'une page DÉJÀ en LTR : l'essai
        # à blanc sur le siman 234, qui est le modèle, annonçait dix règles modifiées —
        # il aurait renvoyé ses encadrés de border-left à border-right. Une règle
        # convertie ne porte plus de direction:rtl, donc un second passage ne fait rien.
        if 'rtl' in corps:
            neuf = permuter_cotes(neuf)
        else:
            neuf = redresser_listes(sel_net, neuf)
        if neuf == corps:
            continue          # ne compter que ce qui change réellement
        out.append(css[pos:m.start(2)]); out.append(neuf)
        pos = m.end(2); n += 1
    out.append(css[pos:])
    return ''.join(out), n

def traiter(path, dry=False):
    s = io.open(path, encoding='utf-8').read()
    # ⚠️ NE JAMAIS CONVERTIR UNE PAGE QUI EST ENCORE HÉBRAÏQUE. Ce script suppose
    # qu'un traducteur est passé avant lui : il retire le RTL d'une prose devenue
    # française ou anglaise. Lancé sur un `niveau-2-lamdan.html` qui sert encore
    # la page hébraïque sous une URL française — ce qu'étaient encore les dix-huit
    # simanim 183-200 — il aligne à gauche un corps hébreu et déclare fr-FR un
    # JSON-LD qui décrit de l'hébreu : il AGGRAVE la page au lieu de la réparer.
    # J'ai fait exactement cela, sur trente-six fichiers, avant de m'en apercevoir
    # par `verifier-url-langue.py`. Le `lang=` du fichier est le témoin le plus
    # sûr : tant qu'il dit `he`, le corps n'a pas été traduit.
    #
    # Le `lang=` ne suffit PAS à le dire : les variantes `-en.html` de ces mêmes
    # simanim déclaraient déjà `lang="en"` tout en servant le corps hébreu. Ce
    # qui tranche, c'est le corps lui-même — et la séparation est nette, sans
    # zone grise : une page traduite porte environ 70 % de lettres latines
    # (0,696 au siman 118, 0,713 au modèle 234), une page encore hébraïque 1 %
    # (0,014 au siman 190). Le seuil est posé très bas, à 25 %, pour ne jamais
    # refuser une page réellement traduite.
    corps = re.search(r'(?s)<body.*?</body>', s)
    if corps:
        txt = re.sub(r'(?s)<(script|style)\b.*?</\1>', '', corps.group(0))
        txt = re.sub(r'<[^>]+>', ' ', txt)
        heb = len(re.findall(r'[\u05D0-\u05EA]', txt))
        lat = len(re.findall(r'[A-Za-z\u00C0-\u00FF]', txt))
        if lat / (heb + lat + 1) < 0.25:
            print(f'  {path} : IGNORÉ — le corps est encore hébraïque '
                  f'({lat} lettres latines pour {heb} hébraïques) ; '
                  f'traduire la page avant de la redresser')
            return 0, 0
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
