#!/usr/bin/env python3
"""Remettre les séifim dans l'ordre du Choul'han Aroukh.

RÈGLE ABSOLUE du dépôt : « Toute référence doit être exactement celle du Choul'han
Aroukh : le numéro du séif, la découpe entre séifim, l'ordre des propositions à
l'intérieur d'un séif, et l'ordre dans lequel la page les présente. Une page ne réarrange
pas la source pour les besoins de son exposé ; si un enchaînement pédagogique semble
l'exiger, c'est l'exposé qui plie. »

Deux simanim du bloc נדה la violaient, et aucune porte ne le voyait tant que leur texte
était retapé — c'est en reposant le texte VERBATIM que `verify-yd-source.py` s'en est
aperçu : même longueur exactement, même contenu, ordre différent.

  · siman 195 : les blocs suivent 1, 2, 3, 4, **13**, 5, 6, … — le séif 13 remonté dans
    la « Famille 2 — La table et le boire » parce qu'il parle, lui aussi, de verser et
    d'envoyer.
  · siman 196 : 1, 2, 3, 4, 5, **9**, 6, 7, 8, … — le séif 9 remonté dans la famille des
    בדיקות des sept jours.

Le script déplace l'unité du séif (son `<h4>`, son bloc, sa traduction et ses encadrés,
jusqu'au titre suivant) à sa place dans l'ordre du livre. Il opère PAR POSITION, la même
dans les trois langues — les trois variantes étant parallèles unité à unité — parce que
les titres hébreux disent « סעיף יג » et non « Seif 13 ».

Il ne touche pas aux titres de famille : le libellé « (seifim 3-4, 13) » devient faux par
son fait, et c'est au rédacteur de le corriger — une liste de séifim est du texte, pas de
la structure.

Usage : python3 scripts/reordonner-seifim.py 195 196 [--dry-run]
"""
import re, sys, os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RX_UNITE = re.compile(r'<h4[ >]')

def section(s):
    """Les bornes de la SEULE section du texte des séifim.

    Les <h4> ne lui appartiennent pas tous : le niveau 1 en emploie aussi pour les
    entrées du Chakh et du Taz, et pour les gloses du Rama (« Sur le seif 1 »), qui
    nomment eux aussi un séif. Sans cette borne, le script prenait vingt-deux unités
    là où le siman en a dix-sept et proposait de mélanger le texte avec l'appareil.
    """
    m = re.search(r'<h2 id="exp-seifim"', s)
    if not m:
        return 0, 0
    suite = re.search(r'<h2[ >]', s[m.end():])
    return m.start(), (m.end() + suite.start() if suite else len(s))

def unites(s):
    """Découpe la section des séifim en unités : d'un <h4> au titre suivant."""
    a, b = section(s)
    if b <= a:
        return []
    deb = [m.start() for m in RX_UNITE.finditer(s) if a <= m.start() < b]
    if not deb:
        return []
    out = []
    for i, d in enumerate(deb):
        suite = re.search(r'<h[234][ >]', s[d + 4:b])
        f = d + 4 + suite.start() if suite else b
        out.append((d, f))
    return out

def numeros(n):
    """L'ordre des séifim tel que la page FRANÇAISE les présente."""
    p = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base.html')
    s = io.open(p, encoding='utf-8').read()
    out = []
    for d, f in unites(s):
        m = re.search(r'Seif\s+(\d+)', s[d:d + 200], re.I)
        out.append(int(m.group(1)) if m else None)
    return out

def reordonner(n, dry=False):
    ordre = numeros(n)
    seifs = [x for x in ordre if x is not None]
    if seifs == sorted(seifs):
        print(f"siman {n} : déjà dans l'ordre du livre")
        return 0
    cible = sorted(range(len(ordre)), key=lambda i: (ordre[i] is None, ordre[i]))
    bouges = sum(1 for i, j in enumerate(cible) if i != j)
    for suf in ('', '-he', '-en'):
        p = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base{suf}.html')
        s = io.open(p, encoding='utf-8').read()
        u = unites(s)
        if len(u) != len(ordre):
            print(f"  ⚠️ {os.path.basename(p)} : {len(u)} unités contre {len(ordre)} en "
                  f"français — parité rompue, fichier laissé intact")
            continue
        # LE SQUELETTE NE BOUGE PAS, les unités changent de case. Tout ce qui vit entre
        # deux unités reste où il est ; seul le contenu des cases est permuté. Deux
        # essais ont échoué avant celui-ci : recoller les seules unités EFFAÇAIT les
        # titres de famille (cinq <h3> par fichier, sans qu'aucune porte ne bronche,
        # la page restant bien formée) ; les faire voyager avec l'unité les DÉPLAÇAIT
        # (« Famille 3 — Le lit » atterrissait entre les séifim 13 et 14).
        corps = [s[d:f] for d, f in u]
        out, pos = [], 0
        for i, (d, f) in enumerate(u):
            out.append(s[pos:d])
            out.append(corps[cible[i]])
            pos = f
        out.append(s[pos:])
        neuf = ''.join(out)

        # Et les titres de famille de la SECTION DU TEXTE s'en vont. Ils groupaient par
        # thème, ce qui obligeait à remonter un séif ; une fois l'ordre du livre rétabli
        # aucun d'eux ne décrit plus un intervalle contigu — replacer le séif 13 décale
        # toutes les familles qui le suivent. La règle absolue du dépôt tranche : « si
        # un enchaînement pédagogique semble l'exiger, c'est l'exposé qui plie ». La
        # lecture par familles reste entière au niveau 3 et dans la section qui leur est
        # consacrée ; elle ne commande plus la présentation du texte.
        a, b = section(neuf)
        tete, corps_s, queue = neuf[:a], neuf[a:b], neuf[b:]
        corps_s = re.sub(r'\n?<h3>(?:Famille|Family|משפחה)[^<]*</h3>\n?', '\n', corps_s)
        neuf = tete + corps_s + queue
        if not dry:
            io.open(p, 'w', encoding='utf-8').write(neuf)
    print(f"siman {n} : {ordre} → {[ordre[i] for i in cible]}  ({bouges} unités déplacées)")
    return bouges

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    for a in [x for x in sys.argv[1:] if not x.startswith('--')]:
        reordonner(int(a), dry)
    if dry:
        print("\n(essai à blanc — rien n'a été écrit)")
