#!/usr/bin/env python3
"""« ס״ק 12 » → « ס״ק י״ב » — le numéro de séif katan en numéral hébreu.

Le dépôt écrit partout le séif katan en lettres : le modèle du siman 234 porte
quarante numéraux hébreux et zéro chiffre arabe, et les sept simanim voisins du
lot 111-118 n'en portent aucun. Le siman 113 en portait 134 — soixante-sept en
français, soixante-sept en anglais — au milieu de références par ailleurs
hébraïques : « (ש״ך יו״ד קי״ג ס״ק 1) », quand la prose de la même page écrit
« ס״ק א׳ » cinquante-six fois.

Aucune porte ne le voit : ce n'est ni une citation fausse, ni une langue
fautive, ni une classe absente. C'est une référence illisible pour qui lit
l'hébreu, et incohérente avec elle-même.

À la différence de `heb-nums.py`, qui accole le chiffre arabe au numéral
(« סימן קע״ו · 176 », la forme des tuiles du catalogue), on ne garde ici QUE le
numéral : c'est la forme qu'emploient les 414 autres simanim.

Protections — les mêmes que `heb-nums.py`, pour les mêmes raisons :
tout ce qui est entre « … » ou “ … ” est du verbatim et ne se réécrit pas ;
les blocs de texte source (blockquote.text-source, .sa-he) non plus. Le script
est idempotent : une fois converti, le motif « ס״ק <chiffres> » a disparu.
"""
import re, sys, glob, io

ONES = ['', 'א','ב','ג','ד','ה','ו','ז','ח','ט']
TENS = ['', 'י','כ','ל','מ','נ','ס','ע','פ','צ']
HUNS = ['', 'ק','ר','ש','ת']

def heb(n):
    # le siman 228 de Yoré Déa est assez long pour que le Chakh y dépasse le
    # centième séif katan : ס״ק ק״ג, ס״ק קי״א. Le français les écrivait déjà
    # ainsi, l'anglais en chiffres — une divergence entre les deux langues.
    r = n % 100
    t = 'טו' if r == 15 else 'טז' if r == 16 else TENS[r // 10] + ONES[r % 10]
    s = HUNS[n // 100] + t
    return s + '׳' if len(s) == 1 else s[:-1] + '״' + s[-1]

def spans(s, pat):
    return [(m.start(), m.end()) for m in re.finditer(pat, s, re.S)]

RE_SK = re.compile(r'ס״ק(\s+)(\d{1,3})\b')
# Second défaut, de la même famille : le numéral hébreu écrit SANS gershayim —
# « ס״ק יב » au lieu de « ס״ק י״ב ». 1 476 occurrences dans 164 fichiers, tous
# compartiments confondus. Ce n'est pas une coquille d'affichage : le gershayim est
# ce qui distingue un NOMBRE d'un mot, et c'est déjà sur cette distinction que
# reposait la refonte de verifier-denombrements.py.
RE_SK_HEB = re.compile(r'ס״ק(\s+)([\u05D0-\u05EA]{2,3})(?![\u05D0-\u05EA\u05F3\u05F4])')

def nu(s_):
    """La forme sans gershayim du numéral, pour l'aller-retour de contrôle."""
    return s_.replace('\u05F4', '').replace('\u05F3', '')

def valeur(mot):
    """Le nombre que ce mot vaut s'il EST un numéral canonique, sinon None.

    Le contrôle se fait par aller-retour : on essaie tous les nombres de 1 à 499 et
    l'on ne retient que celui dont la forme canonique, gershayim retirés, est
    exactement le mot lu. « שם » (là-bas) ne vaut donc rien, et « כו » — qui est
    aussi l'abréviation de « וכו׳ » — ne passe que s'il est écrit tel quel, ce qui
    est la forme de 26. Le doute restant est traité par les protections de
    guillemets, comme pour les chiffres arabes.
    """
    for n in range(1, 500):
        if nu(heb(n)) == mot:
            return n
    return None

def convert(path, apply=False):
    s = io.open(path, encoding='utf-8').read()
    protect = (spans(s, r'<blockquote class="text-source">.*?</blockquote>')
               + spans(s, r'<[^>]*class="[^"]*sa-he[^"]*"[^>]*>.*?</[a-z]+>')
               + spans(s, r'«.*?»') + spans(s, r'“.*?”'))
    out, n = [], 0
    for m in RE_SK.finditer(s):
        num = int(m.group(2))
        if not 1 <= num <= 499:
            continue
        if any(a <= m.start() < b for a, b in protect):
            continue
        out.append((m.start(), m.end(), f'ס״ק{m.group(1)}{heb(num)}'))
        n += 1
    for m in RE_SK_HEB.finditer(s):
        num = valeur(m.group(2))
        if num is None:
            continue
        if any(a <= m.start() < b for a, b in protect):
            continue
        out.append((m.start(), m.end(), f'ס״ק{m.group(1)}{heb(num)}'))
        n += 1
    out.sort(key=lambda x: x[0])
    if apply and out:
        for deb, fin, txt in reversed(out):
            s = s[:deb] + txt + s[fin:]
        io.open(path, 'w', encoding='utf-8').write(s)
    return n

def main():
    apply = '--dry-run' not in sys.argv
    cibles = [a for a in sys.argv[1:] if not a.startswith('--')]
    fichiers = cibles or sorted(glob.glob('sources/**/*.html', recursive=True))
    total, touches = 0, 0
    for f in fichiers:
        n = convert(f, apply)
        if n:
            total += n; touches += 1
            print(f'  {f} : {n} référence(s)')
    print(f'\n{len(fichiers)} fichier(s) examiné(s) · {touches} modifié(s) · '
          f'{total} « ס״ק N » rendu(s) en numéral hébreu'
          + ('' if apply else '  [essai à blanc]'))
    return 0

if __name__ == '__main__':
    sys.exit(main())
