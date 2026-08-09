#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Traductions tronquées ou incomplètes — le gate qui manquait.

Les deux gates existants ne voient pas ce défaut. ``audit-simanim.py`` regarde
la structure ; ``verifier-citations.py`` confronte chaque citation hébraïque à
sa source — et conclut « conforme » quand l'hébreu est parfait. Or il peut
l'être et la **traduction s'arrêter en chemin** : le lecteur francophone voit
alors le cas posé et pas sa résolution.

C'est arrivé au siman 271 séif ד, où trois propositions — celles qui portent
justement la conclusion pratique sur la répétition de HaMotsi — n'avaient
aucun équivalent français. Aucun contrôle automatique ne pouvait le dire.

Ce script apparie chaque bloc de texte source à la traduction qui le suit et
signale deux choses :

1. **Séif non traduit du tout** — l'hébreu est reproduit, et la traduction
   renvoie ailleurs (« Voir l'analyse pratique : ce seif traite de… ») au lieu
   de rendre le texte. Cela se constate exactement, sans seuil.
2. **Traduction anormalement courte** par rapport à l'hébreu. Le seuil n'est
   pas deviné : il est calculé sur la distribution réelle du site (décile
   inférieur), de sorte qu'on signale ce qui sort de l'usage constaté et non
   ce qui s'écarte d'une idée a priori. Les lettres hébraïques de la
   traduction comptent : le site garde en hébreu les termes techniques, et les
   ignorer pénalisait exactement les pages les plus fidèles à cet usage.
3. **Parenthèses de source non reprises** — « (ב״י) », « (אורח חיים בשם תוס') ».
   Le Mehaber y attribue ses sources ; les laisser tomber prive le lecteur de
   l'appareil critique.

    python3 scripts/verifier-traductions.py [--siman 271] [--quiet]
"""
from __future__ import annotations

import argparse
import pathlib
import re
import statistics
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent / "sources"

RE_BLOC = re.compile(
    r'<(?P<tag>blockquote|div|p)[^>]*class="[^"]*(?P<cls>text-source|sacred-text|translation)[^"]*"[^>]*>'
    r"(?P<contenu>.*?)</(?P=tag)>",
    re.S,
)
RE_TAG = re.compile(r"<[^>]*>")
HEBREU = re.compile(r"[֐-׿]")
LATIN = re.compile(r"[A-Za-zÀ-ÿ]")
# Parenthèse contenant de l'hébreu : c'est ainsi que le Mehaber attribue ses
# sources — « (ב״י) », « (אורח חיים בשם תוס') ».
RE_PAREN_HE = re.compile(r"\([^()]*[֐-׿][^()]*\)")


def texte(html: str) -> str:
    return re.sub(r"\s+", " ", RE_TAG.sub(" ", html)).strip()


def paires(chemin: pathlib.Path) -> list[tuple[str, str]]:
    """[(texte source, traduction)] — chaque source appariée à la traduction
    qui la suit immédiatement."""
    blocs = [(m.group("cls"), texte(m.group("contenu")))
             for m in RE_BLOC.finditer(chemin.read_text(encoding="utf-8"))]
    out = []
    for i, (cls, contenu) in enumerate(blocs):
        if cls == "translation":
            continue
        suivant = blocs[i + 1] if i + 1 < len(blocs) else None
        if suivant and suivant[0] == "translation":
            out.append((contenu, suivant[1]))
    return out


# Une « traduction » qui renvoie ailleurs au lieu de rendre le texte. Ce n'est
# pas une traduction courte : c'est une absence de traduction, et elle se
# constate exactement — sans seuil ni statistique.
NON_TRADUIT = re.compile(
    r"Voir l'analyse pratique|See the practical analysis|ראה הניתוח המעשי"
    r"|ce seif (?:traite|fait partie)", re.I)


def mesurer(source: str, trad: str) -> tuple[int, int, float]:
    """Longueur de la traduction rapportée à celle de la source.

    Les lettres hébraïques de la *traduction* comptent autant que les latines :
    l'usage du site est de garder en hébreu les termes techniques — « on dit
    ברוך שאמר avant les פסוקי דזמרה » traduit tout, et ne pas compter ces
    lettres faisait chuter le ratio d'une traduction complète. Le biais visait
    précisément les pages les plus fidèles à cet usage."""
    he = len(HEBREU.findall(source))
    rendu = len(LATIN.findall(trad)) + len(HEBREU.findall(trad))
    return he, rendu, (rendu / he if he else 0.0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--siman", type=int)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    fichiers = sorted(RACINE.rglob("niveau-*.html"))
    fichiers = [f for f in fichiers
                if not f.stem.endswith(("-he", "-en"))]           # le FR porte la traduction
    if args.siman:
        fichiers = [f for f in fichiers if f"siman-{args.siman}/" in str(f)]

    mesures: list[tuple[pathlib.Path, int, str, int, int, float, int, int]] = []
    for f in fichiers:
        for i, (src, trad) in enumerate(paires(f), 1):
            he, fr, ratio = mesurer(src, trad)
            if he < 40:
                continue          # trop court pour conclure
            p_src = len(RE_PAREN_HE.findall(src))
            p_trad = trad.count("(")
            mesures.append((f, i, src, he, fr, ratio, p_src, p_trad,
                            bool(NON_TRADUIT.search(trad))))

    if not mesures:
        print("Aucune paire source/traduction trouvée.", file=sys.stderr)
        return 1

    ratios = sorted(m[5] for m in mesures)
    seuil = statistics.quantiles(ratios, n=10)[0] if len(ratios) >= 10 else min(ratios)

    absentes = [m for m in mesures if m[8]]
    courtes = [m for m in mesures if m[5] < seuil and not m[8]]
    parenth = [m for m in mesures if m[6] > 0 and m[7] < m[6] and not m[8]]

    print(f"{len(mesures)} paire(s) source/traduction examinée(s) "
          f"dans {len(fichiers)} page(s)")
    print(f"Ratio médian (lettres rendues / lettres de la source) : "
          f"{statistics.median(ratios):.2f}")
    print(f"Seuil (décile inférieur, calculé sur le site) : {seuil:.2f}")
    if absentes:
        pages = sorted({m[0].relative_to(RACINE) for m in absentes})
        print(f"\n⛔ {len(absentes)} séif(s) reproduit(s) en hébreu et NON TRADUIT(s) "
              f"— la traduction renvoie ailleurs au lieu de rendre le texte")
        print(f"   dans {len(pages)} page(s) : "
              + ", ".join(str(p).split('/')[1] for p in pages[:12])
              + (" …" if len(pages) > 12 else ""))
    print()

    if not args.quiet:
        for titre, lot, detail in (
            ("TRADUCTIONS ANORMALEMENT COURTES", courtes,
             lambda m: f"ratio {m[5]:.2f} — {m[3]} lettres hébraïques, {m[4]} latines"),
            ("PARENTHÈSES DE SOURCE NON REPRISES", parenth,
             lambda m: f"{m[6]} parenthèse(s) hébraïque(s), {m[7]} dans la traduction"),
        ):
            print(f"── {titre} ({len(lot)}) " + "─" * max(0, 40 - len(titre)))
            for m in lot[:40]:
                rel = m[0].relative_to(RACINE)
                print(f"  {rel} · bloc {m[1]} — {detail(m)}")
                print(f"      {m[2][:110]}")
            if len(lot) > 40:
                print(f"  … et {len(lot) - 40} autre(s)")
            print()

    total = len({(m[0], m[1]) for m in courtes + parenth})
    print(f"{total} bloc(s) à revoir · {len(absentes)} séif(s) non traduit(s).")
    return 1 if total or absentes else 0


if __name__ == "__main__":
    raise SystemExit(main())
