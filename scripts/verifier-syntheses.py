#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Synthèses qui contredisent le corps de leur propre page.

Le défaut que ce script cherche a échappé aux trois autres gates, et c'est ce
qui le rend dangereux. Au siman 271, les « règles à retenir » disaient
« Mehaber avant — kiddush ; Rama après », alors que SA OH 271:12 porte
l'inverse : le Mehaber fait laver les mains APRÈS (« אחר שקידש על הכוס נוטל
ידיו »), le Rama AVANT (« ויש אומרים דלכתחילה יש ליטול ידיו קודם הקידוש »).

Le corps de la page était juste. Seule la ligne de synthèse était fausse —
c'est-à-dire précisément celle que le lecteur emporte. Aucune citation n'était
fautive, aucune traduction n'était courte : rien de mécanique ne pouvait le
dire, et il a fallu qu'un lecteur tique.

Ce que ce script sait faire, et ce qu'il ne sait pas
----------------------------------------------------
Il ne comprend pas le sens. Il exploite une régularité du corpus : le Mehaber
et le Rama y sont souvent opposés sur un couple ORDONNÉ — avant/après. Quand
une synthèse attribue un terme du couple à chacun, on peut confronter cette
attribution au corps de la page, où le texte du Mehaber précède la hagaha
(« הגה : ») et où les marqueurs hébreux correspondants sont repérables.

Deux précautions, apprises de deux versions qui donnaient un résultat inversé :

**Le découpage se fait par séif, pas par page.** Un siman compte une hagaha par
séif ou presque ; prendre la première de la page revient à confronter la
synthèse au texte d'un séif sans rapport. Le raisonnement n'a de sens que dans
les limites d'un même séif.

**Aucun appariement par sujet.** Deviner de quel séif parle une ligne française
demanderait une analyse lexicale qui échouait sur la formulation même du défaut
recherché. À la place : une ligne n'est signalée que si **un séif de sa page la
contredit exactement** et qu'**aucun autre ne la soutient**. Le silence est le
comportement par défaut ; c'est ce qui permet de faire confiance au bruit.

Il ne signale donc qu'une famille de contresens — l'inversion des deux
autorités sur un couple ordonné. C'est étroit, mais c'est exactement le défaut
constaté, et il vaut mieux un contrôle étroit et sûr qu'un contrôle large qui
devinerait.

Sa portée, mesurée et non supposée
-----------------------------------
Sur les 988 pages françaises : 2683 séifim, 281 lignes citant les deux
autorités — dont **7** attribuent un terme d'un couple à chacune, et **1** se
trouve dans une page dont un séif oppose les mêmes termes sur le même acte.

C'est donc un **garde-fou de non-régression**, pas un gate de site. Le facteur
limitant est structurel : 417 séifim seulement sur 2683 reproduisent une hagaha
« הגה : », faute de quoi il n'y a pas de position du Rama à confronter. Le
script imprime cette portée avec son résultat, pour qu'un « 0 contradiction »
ne se lise jamais comme « les synthèses sont vérifiées ». Elles ne le sont pas :
tout le reste relève de la relecture.

    python3 scripts/verifier-syntheses.py [--siman 271] [--fichier CHEMIN]
"""
from __future__ import annotations

import argparse
import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parent.parent / "sources"
RE_TAG = re.compile(r"<[^>]*>")

# Couple ORDONNÉ : (termes français du terme A, marqueurs hébreux de A),
#                  (termes français du terme B, marqueurs hébreux de B).
COUPLES = [
    (("avant", "before"), ("קודם", "לפני", "טרם"),
     ("après", "apres", "after"), ("אחר ש", "לאחר", "אחרי", "אח״כ", "אחכ")),
    (("permis", "permet", "autoris", "permitted"), ("מותר", "שרי", "ומותר"),
     ("interdit", "défend", "forbidden", "prohibit"), ("אסור", "ואסור", "אין להתיר")),
]

MEHABER = re.compile(r"m[eé]haber|mechaber|המחבר|מחבר", re.I)
RAMA = re.compile(r"\brama\b|\brema\b|רמ[\"'״׳]א|הרמ״א", re.I)
RE_HAGAHA = re.compile(r"הגה\s*[:：]")
# Une section de séif : le titre porte « Seif », « Séif » ou « סעיף ».
RE_TITRE_SEIF = re.compile(
    r"<(h[2-5])[^>]*>(?P<t>(?:(?!</?h[2-5]).)*?)</\1>", re.S | re.I)
EST_SEIF = re.compile(r"\bs[eé]if\b|סעיף", re.I)
LATIN = re.compile(r"[A-Za-zÀ-ÿ]")


def texte(html: str) -> str:
    return re.sub(r"\s+", " ", RE_TAG.sub(" ", html)).strip()


def sections_de_seif(html: str) -> list[str]:
    """Le corps de chaque séif, borné par son titre et le titre suivant."""
    titres = list(RE_TITRE_SEIF.finditer(html))
    out = []
    for i, m in enumerate(titres):
        if not EST_SEIF.search(texte(m.group("t"))):
            continue
        fin = titres[i + 1].start() if i + 1 < len(titres) else len(html)
        out.append(texte(html[m.end():fin]))
    return out


def premier_marqueur(zone: str, marqueurs_a: tuple,
                     marqueurs_b: tuple) -> tuple[str, int] | None:
    """Le terme du couple qui apparaît le premier dans cette zone, et sa place."""
    pa = min((zone.find(m) for m in marqueurs_a if m in zone), default=-1)
    pb = min((zone.find(m) for m in marqueurs_b if m in zone), default=-1)
    if pa < 0 and pb < 0:
        return None
    if pb < 0 or (0 <= pa < pb):
        return "A", pa
    return "B", pb


# Préfixes d'une lettre (ו ה ב ל כ מ ש) — les retirer rapproche « שקידש » de
# « קידש » sans prétendre à une analyse morphologique.
RE_PREFIXE = re.compile(r"^[והבלכמש]")
VIDES = {"את", "אין", "יש", "כל", "אשר", "אבל", "אלא", "אם", "לא", "רק",
         "כמו", "אחר", "קודם", "לאחר", "אחרי", "לפני", "טרם", "עד", "כן",
         "זה", "הוא", "היא", "אני", "אנו", "וכן", "וכל", "גם", "או"}


def mots_autour(zone: str, position: int, fenetre: int = 40) -> set[str]:
    """Les mots substantiels qui entourent un marqueur, préfixes retirés."""
    extrait = zone[max(0, position - fenetre): position + fenetre]
    out = set()
    for mot in re.findall(r"[א-ת]{3,}", extrait):
        mot = RE_PREFIXE.sub("", mot) if len(mot) > 3 else mot
        if len(mot) >= 3 and mot not in VIDES:
            out.add(mot)
    return out


def positions_du_seif(section: str, marq_a: tuple, marq_b: tuple) -> tuple | None:
    """(terme du Mehaber, terme du Rama) d'après l'hébreu de ce séif.

    Le texte du Mehaber précède « הגה : », celui du Rama le suit. On s'arrête
    à la traduction française : au-delà, l'hébreu appartient à un commentaire
    ou à un autre appareil, plus au séif lui-même.

    Deux termes opposés ne suffisent pas à faire une opposition : au séif 271:5
    le Mehaber écrit « קודם שיקדשו » à propos de boire et le Rama « לאחר שבירך »
    à propos de HaMotsi — mots contraires, sujets différents, aucune divergence.
    On exige donc que les deux marqueurs portent sur **le même acte**, attesté
    par un mot substantiel commun à leurs deux voisinages (ici « ידיו »).
    """
    h = RE_HAGAHA.search(section)
    if not h:
        return None
    avant = section[:h.start()]
    apres = section[h.end():]
    # Borne basse de la hagaha : la première phrase française qui suit.
    fr = re.search(r"[A-Za-zÀ-ÿ]{4,}(?:[ ,][A-Za-zÀ-ÿ]{2,}){3,}", apres)
    if fr:
        apres = apres[:fr.start()]
    m = premier_marqueur(avant, marq_a, marq_b)
    r = premier_marqueur(apres, marq_a, marq_b)
    if m is None or r is None or m[0] == r[0]:
        return None          # pas une opposition sur ce couple
    if not (mots_autour(avant, m[1]) & mots_autour(apres, r[1])):
        return None          # termes contraires, mais sur deux sujets distincts
    return m[0], r[0]


def lignes_de_synthese(html: str) -> list[str]:
    """Éléments de liste où la synthèse attribue une position à chaque autorité."""
    out = []
    for m in re.finditer(r"<li[\s>][^>]*>(.*?)</li>", html, re.S):
        t = texte(m.group(1))
        if MEHABER.search(t) and RAMA.search(t):
            out.append(t)
    return out


def attribution(ligne: str, autorite: re.Pattern, a: tuple, b: tuple) -> str | None:
    """Quel terme du couple la ligne attribue-t-elle à cette autorité ?

    Le terme retenu est le premier qui suit le nom de l'autorité, avant que
    l'autre autorité ne soit nommée.
    """
    m = autorite.search(ligne)
    if not m:
        return None
    suite = ligne[m.end():].lower()
    autre = RAMA if autorite is MEHABER else MEHABER
    fin = autre.search(suite)
    if fin:
        suite = suite[: fin.start()]
    trouve = premier_marqueur(suite, a, b)
    return trouve[0] if trouve else None


def examiner(chemin: pathlib.Path,
             couverture: dict | None = None) -> list[tuple[str, tuple, tuple, str]]:
    html = chemin.read_text(encoding="utf-8")
    sections = sections_de_seif(html)
    lignes = lignes_de_synthese(html)
    if couverture is not None:
        couverture["sections"] += len(sections)
        couverture["lignes"] += len(lignes)
    if not sections or not lignes:
        return []
    trouves = []
    for a_fr, a_he, b_fr, b_he in COUPLES:
        corps = [p for p in (positions_du_seif(s, a_he, b_he) for s in sections)
                 if p is not None]
        if couverture is not None:
            couverture["seifim_opposes"] += len(corps)
        for ligne in lignes:
            paire = (attribution(ligne, MEHABER, a_fr, b_fr),
                     attribution(ligne, RAMA, a_fr, b_fr))
            if None in paire or paire[0] == paire[1]:
                continue
            if couverture is not None:
                couverture["attributions"] += 1
            if not corps:
                continue
            if couverture is not None:
                couverture["confrontees"] += 1
            if paire in corps:
                continue          # un séif de la page soutient l'attribution
            contre = [c for c in corps if c == (paire[1], paire[0])]
            if not contre:
                continue          # rien ne la contredit non plus : on se tait
            mot = {"A": a_fr[0], "B": b_fr[0]}
            trouves.append((ligne, paire, contre[0], f"{mot['A']}/{mot['B']}"))
    return trouves


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--siman", type=int)
    ap.add_argument("--fichier", type=pathlib.Path)
    args = ap.parse_args()

    if args.fichier:
        fichiers = [args.fichier]
    else:
        fichiers = [f for f in sorted(RACINE.rglob("niveau-*.html"))
                    if not f.stem.endswith(("-he", "-en"))]
        if args.siman:
            fichiers = [f for f in fichiers if f"siman-{args.siman}/" in str(f)]

    couverture = dict.fromkeys(
        ("sections", "lignes", "seifim_opposes", "attributions", "confrontees"), 0)
    pages = 0
    signales = 0
    for f in fichiers:
        res = examiner(f, couverture)
        if res:
            pages += 1
        for ligne, paire, corps, couple in res:
            signales += 1
            mots = dict(zip("AB", couple.split("/")))
            rel = f.relative_to(RACINE) if not args.fichier else f
            print(f"⚠ {rel}")
            print(f"   synthèse : Mehaber « {mots[paire[0]]} » · Rama « {mots[paire[1]]} »")
            print(f"   séif      : Mehaber « {mots[corps[0]]} » · Rama « {mots[corps[1]]} »")
            print(f"   → {ligne[:160]}\n")

    # La portée est annoncée avec le résultat, et non laissée à supposer.
    # « 0 contradiction » ne veut pas dire « les synthèses sont vérifiées » :
    # ce contrôle ne parle que des lignes qui attribuent un terme d'un couple
    # ordonné à chacune des deux autorités, dans une page dont un séif oppose
    # les mêmes termes sur le même acte. Tout le reste échappe à la mécanique
    # et relève de la relecture.
    print(f"{len(fichiers)} page(s) · {couverture['sections']} séifim · "
          f"{couverture['lignes']} lignes citant Mehaber et Rama")
    print(f"Portée réelle du contrôle : {couverture['attributions']} attribution(s) "
          f"exploitable(s), dont {couverture['confrontees']} confrontée(s) à un séif "
          f"opposé de leur page ({couverture['seifim_opposes']} séifim opposés trouvés)")
    print(f"→ {signales} contradiction(s) dans {pages} page(s)")
    return 1 if signales else 0


if __name__ == "__main__":
    raise SystemExit(main())
