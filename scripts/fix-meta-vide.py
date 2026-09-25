#!/usr/bin/env python3
"""Combler les trous d'une meta description de niveau 2 : « של סימן  ביורה דעה — . »

Le générateur des niveaux 2 laisse, dans certaines pages, l'emplacement du
NUMÉRO de siman et celui du SUJET vides — sans rien casser à l'affichage, parce
que la meta description ne se lit pas dans la page. Ce que le lecteur ne voit
pas, Google le lit, et l'aperçu de partage aussi :

    <meta name="description" content="Level 2 (Lamdan) of Siman  in Yoreh
    De'ah — . In-depth pilpul: …">

Vingt-huit fichiers étaient dans ce cas — dix-huit variantes hébraïques et dix
anglaises des simanim 183-200 —, tous repérés par un arbitre sur UN siman.

Les deux valeurs manquantes vivent dans le `<title>` du même fichier, qui est
correct partout : « סימן קצ״א · רמה 2 (למדן) — דם הנמצא במי רגליה | יורה דעה ».
On les y prend, on ne les invente pas. Idempotent : une fois le trou comblé, le
motif « של סימן  » à double espace n'existe plus.
"""
import re, sys, glob, io

TITRE = re.compile(r'<title>(.*?)</title>', re.S)
# « סימן קצ״א · רמה 2 (למדן) — <sujet> | יורה דעה »
#  « Siman 191 · Level 2 (Lamdan) — <sujet> | Yoreh De'ah »
RE_HE = re.compile(r'^\s*סימן\s+(?P<num>\S+)\s*·[^—]*—\s*(?P<sujet>.*?)\s*\|')
RE_EN = re.compile(r"^\s*Siman\s+(?P<num>\S+)\s*·[^—]*—\s*(?P<sujet>.*?)\s*\|")
TROU_HE = re.compile(r'(של סימן) {2}(ביורה דעה) — \.')
TROU_EN = re.compile(r"(of Siman) {2}(in Yoreh De'ah) — \.")

def traiter(path, dry=False):
    s = io.open(path, encoding='utf-8').read()
    m = TITRE.search(s)
    if not m:
        return 0
    for rx, trou in ((RE_HE, TROU_HE), (RE_EN, TROU_EN)):
        t = rx.match(m.group(1))
        if not t or not trou.search(s):
            continue
        num, sujet = t.group('num'), t.group('sujet')
        if not num or not sujet:
            print(f'  {path} : titre lui-même incomplet, laissé tel quel')
            return 0
        neuf, n = trou.subn(lambda x: f'{x.group(1)} {num} {x.group(2)} — {sujet}.', s)
        if n and not dry:
            io.open(path, 'w', encoding='utf-8').write(neuf)
        if n:
            print(f'  {path} : n° « {num} » et sujet rétablis')
        return n
    return 0

def main():
    dry = '--dry-run' in sys.argv
    cibles = [a for a in sys.argv[1:] if not a.startswith('--')]
    fichiers = cibles or sorted(glob.glob('sources/**/*.html', recursive=True))
    total = sum(traiter(f, dry) for f in fichiers)
    print(f'\n{len(fichiers)} fichier(s) examiné(s) · {total} meta description(s) comblée(s)'
          + ('  [essai à blanc]' if dry else ''))

if __name__ == '__main__':
    main()
