#!/usr/bin/env python3
"""Retirer la balise <bdi> écrite À L'INTÉRIEUR d'un <title>.

    <title>Siman <bdi>רמ״ה</bdi> · Niveau 2 Lamdan — … | DAAT</title>

Le contenu d'un `<title>` est du TEXTE : la spécification HTML n'y reconnaît
aucun élément. Ce que le navigateur affiche dans l'onglet, ce que Google imprime
dans son résultat et ce que montre un aperçu de partage, c'est donc la chaîne
telle quelle, balises comprises — vérifié avec l'analyseur HTML de la
bibliothèque standard, qui rend le titre entier comme une seule donnée texte.

784 pages du compartiment Hilkhot Chabbat étaient dans ce cas, et elles seules :
le générateur qui les a produites enveloppait le numéral hébreu dans un `<bdi>`
pour l'isoler du texte latin — ce qui est la bonne idée AILLEURS que dans un
titre. Dans le corps, où l'élément fonctionne, 613 pages l'emploient et le
script n'y touche pas.

Un arbitre l'a signalé sur un siman en demandant qu'on en mesure d'abord
l'étendue, ce qui est la règle du dépôt : 784, dans un seul compartiment, et pas
une occurrence dans og:title, twitter:title, headline ou les descriptions.

Idempotent : une fois la balise retirée, le motif ne s'applique plus.
"""
import re, sys, glob, io

RE_TITRE = re.compile(r'(<title>)(.*?)(</title>)', re.S)
RE_BDI = re.compile(r'</?bdi\b[^>]*>')

def traiter(path, dry=False):
    s = io.open(path, encoding='utf-8').read()
    n = 0
    def rendre(m):
        nonlocal n
        interieur, k = RE_BDI.subn('', m.group(2))
        n += k
        return m.group(1) + interieur + m.group(3)
    neuf = RE_TITRE.sub(rendre, s)
    if n and not dry:
        io.open(path, 'w', encoding='utf-8').write(neuf)
    return n

def main():
    dry = '--dry-run' in sys.argv
    cibles = [a for a in sys.argv[1:] if not a.startswith('--')]
    fichiers = cibles or sorted(glob.glob('sources/**/*.html', recursive=True))
    total, touches = 0, 0
    for f in fichiers:
        n = traiter(f, dry)
        if n:
            total += n; touches += 1
    print(f'{len(fichiers)} fichier(s) examiné(s) · {touches} titre(s) nettoyé(s) · '
          f'{total} balise(s) retirée(s)' + ('  [essai à blanc]' if dry else ''))
    return 0

if __name__ == '__main__':
    sys.exit(main())
