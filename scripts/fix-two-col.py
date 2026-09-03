#!/usr/bin/env python3
"""Rend leur mise en page aux blocs `daat-two-col` orphelins de leur feuille.

`assets/css/daat-enhance.css` définit la colonne double — hébreu à droite en RTL,
traduction à gauche, comme une page de Choulhan Aroukh imprimé. 907 pages du site
emploient ces classes ; 27 le font sans jamais charger cette feuille et sans
redéfinir les règles dans leur `<style>` inline. Chez elles, le bloc n'est pas
mal aligné : il n'est pas mis en page du tout. Les deux colonnes s'empilent nues,
sans fond, sans filet d'or, sans direction RTL — et l'hébreu s'affiche donc dans
la police et le sens du corps de texte français.

Aucun garde-fou ne pouvait le voir : le HTML est valide, les citations sont
justes, la langue est la bonne. C'est un agent qui l'a remarqué en comparant son
gabarit à celui du siman voisin.

Le correctif est volontairement minimal. Ces pages portent tout leur style en
ligne et ne chargent que les deux feuilles de widgets ; leur ajouter
`daat-enhance.css` importerait un système de design entier dans une page qui n'en
utilise qu'une règle, et restylerait bien plus que le bloc à réparer. On recopie
donc les seules règles `daat-two-col`, à l'identique de la feuille, à la fin du
`<style>` inline.

Usage : python3 scripts/fix-two-col.py [--dry-run]
Idempotent : une page qui définit déjà `.daat-two-col` n'est pas retouchée.
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Recopiées telles quelles de assets/css/daat-enhance.css (bloc « colonne double »).
REGLES = """
  /* Colonne double — recopié de assets/css/daat-enhance.css, que cette page ne
     charge pas. Sans ces règles le bloc n'est pas mis en page du tout. */
  .daat-two-col { display: grid; grid-template-columns: 1fr; gap: 24px; margin: 28px 0;
    background: #FBF7EF; border: 1px solid #E4DDD0; border-radius: 4px; overflow: hidden; }
  @media (min-width: 980px) { .daat-two-col { grid-template-columns: 1fr 1fr; } }
  .daat-two-col-he, .daat-two-col-fr { padding: 28px 32px; }
  .daat-two-col-he { background: linear-gradient(-90deg, #FBF7EF 0%, #FBF7EF 92%, #EDE3CE 100%);
    font-family: 'Frank Ruhl Libre', 'David', 'Times New Roman', serif; direction: rtl;
    text-align: right; font-size: 1.18rem; line-height: 1.95; color: #1A1F3A;
    border-right: 3px solid #B8972A; }
  .daat-two-col-fr { font-family: 'Source Serif 4', 'Cormorant Garamond', Georgia, serif;
    font-size: 1.05rem; line-height: 1.75; color: #3D4266;
    border-left: 3px solid rgba(184, 151, 42, 0.4); }
  @media (max-width: 979px) {
    .daat-two-col-he { border-right: 3px solid #B8972A; border-left: none; }
    .daat-two-col-fr { border-top: 1px solid #E4DDD0; border-left: none; }
  }
"""


def orpheline(html):
    """La page emploie-t-elle la colonne double sans que rien ne la définisse ?"""
    if 'daat-two-col' not in html:
        return False
    if 'daat-enhance' in html:
        return False
    return not re.search(r'\.daat-two-col\s*\{', html)


def main(argv):
    dry = '--dry-run' in argv
    touchees = 0
    for p in sorted(glob.glob(os.path.join(ROOT, 'sources', '**', '*.html'), recursive=True)):
        html = open(p, encoding='utf-8').read()
        if not orpheline(html):
            continue
        if '</style>' not in html:
            print(f'  ⚠ {os.path.relpath(p, ROOT)} : aucun <style> inline où poser les règles')
            continue
        neuf = html.replace('</style>', REGLES + '</style>', 1)
        touchees += 1
        if not dry:
            open(p, 'w', encoding='utf-8').write(neuf)
        print(f'  {os.path.relpath(p, ROOT)}')
    print(f"{'(à blanc) ' if dry else ''}{touchees} page(s) rendue(s) à leur mise en page")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
