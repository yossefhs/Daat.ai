#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit ``daat_audit/data/terminologie.json`` à partir du site réel.

Pourquoi ce script existe
-------------------------
La première version du dictionnaire métier était **écrite à la main**, et
fausse : sept de ses dix entrées désignaient comme « forme canonique » une
graphie absente du site, et pour מוקצה la forme donnée comme fautive
(*Muktzeh*, 75 occurrences) était plus fréquente que la forme dite correcte
(*Mouktsé*, 41). Un contrôle bâti là-dessus aurait signalé en masse du texte
correct — exactement ce que le cahier des charges interdit (§4 : ne jamais
présenter une hypothèse comme une preuve).

Ce que le script décide, et ce qu'il ne décide pas
--------------------------------------------------
Il **regroupe** les graphies d'un même terme — que *Shabbat* et *Chabbat*
soient le même mot est un fait linguistique, pas une préférence — et il
**compte** leurs occurrences réelles. Il ne désigne aucune forme canonique :
choisir entre *Mouktsé* et *Muktzeh* est une décision éditoriale qui revient
au Rav, pas à l'outil. Le contrôle EDIT-001 se borne donc à signaler qu'une
page mélange deux graphies, en donnant les comptes du site.

    python3 scripts/build-terminologie.py [--sources ../sources] [--check]

``--check`` n'écrit rien et sort non nul si le fichier est désynchronisé.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# Graphies d'un même terme rencontrées sur le site. Regroupement linguistique
# uniquement : l'ordre n'exprime aucune préférence.
GROUPES: dict[str, list[str]] = {
    "shabbat": ["Shabbat", "Chabbat"],
    "mouktse": ["Mouktsé", "Muktzeh", "Muktza"],
    "melakha": ["Mélakha", "Melakha", "Melacha"],
    "melakhot": ["Mélakhot", "Melachot"],
    "lekhatehila": ["Lechatchila", "Lekhatchila"],
    "bediavad": ["Bediavad", "Bedieved"],
    "keli_richon": ["Kli rishon", "Keli rishon"],
    "keli_cheni": ["Kli sheni", "Keli sheni"],
}
# Ne PAS regrouper « Admour HaZaken » et « Alter Rebbe » : ce sont deux
# désignations légitimes du même maître, pas deux graphies d'un même mot.
# Les employer toutes deux dans une page n'est pas une incohérence.

_DEFAULT_SOURCES = pathlib.Path(__file__).resolve().parents[2] / "sources"
_OUT = pathlib.Path(__file__).resolve().parents[1] / "daat_audit" / "data" / "terminologie.json"

# Le texte visible seulement : une graphie enfouie dans une balise <meta> ou un
# attribut ne se lit pas et ne doit pas peser dans les comptes.
_TAG = re.compile(r"<[^>]+>")
_SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)


def visible_text(html: str) -> str:
    return _TAG.sub(" ", _SCRIPT.sub(" ", html))


def compter(sources: pathlib.Path) -> dict[str, dict[str, int]]:
    formes = {f for formes in GROUPES.values() for f in formes}
    motifs = {f: re.compile(rf"(?<![\w-]){re.escape(f)}(?![\w-])") for f in formes}
    counts = {f: 0 for f in formes}

    for path in sorted(sources.rglob("*.html")):
        text = visible_text(path.read_text(encoding="utf-8", errors="replace"))
        for forme, motif in motifs.items():
            counts[forme] += len(motif.findall(text))

    return {
        terme: {f: counts[f] for f in formes}
        for terme, formes in GROUPES.items()
    }


def construire(sources: pathlib.Path) -> dict:
    groupes = compter(sources)
    # Une graphie jamais attestée ne doit pas servir de référence : on l'écarte
    # plutôt que de la conserver « au cas où ».
    for terme, formes in groupes.items():
        groupes[terme] = {f: n for f, n in formes.items() if n > 0}
    return {
        "_commentaire": (
            "Généré par scripts/build-terminologie.py — ne pas éditer à la main. "
            "Groupes de graphies d'un même terme, avec leurs occurrences réelles "
            "dans sources/. Aucune forme n'est déclarée canonique : le choix "
            "éditorial revient au Rav (§4)."
        ),
        "groupes": {t: f for t, f in groupes.items() if len(f) > 1},
        "ecartes": {t: f for t, f in groupes.items() if len(f) <= 1},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=pathlib.Path, default=_DEFAULT_SOURCES)
    parser.add_argument("--check", action="store_true",
                        help="ne rien écrire ; sortir non nul si désynchronisé")
    args = parser.parse_args()

    if not args.sources.is_dir():
        print(f"sources introuvables : {args.sources}", file=sys.stderr)
        return 2

    data = construire(args.sources)
    rendu = json.dumps(data, ensure_ascii=False, indent=2) + "\n"

    if args.check:
        actuel = _OUT.read_text(encoding="utf-8") if _OUT.exists() else ""
        if actuel != rendu:
            print("terminologie.json désynchronisé — relancer sans --check",
                  file=sys.stderr)
            return 1
        print("terminologie.json à jour")
        return 0

    _OUT.write_text(rendu, encoding="utf-8")
    for terme, formes in data["groupes"].items():
        detail = ", ".join(f"{f} ({n})" for f, n in sorted(formes.items(),
                                                           key=lambda kv: -kv[1]))
        print(f"{terme:14} {detail}")
    if data["ecartes"]:
        print("\nGroupes écartés (une seule graphie attestée) :",
              ", ".join(data["ecartes"]))
    print(f"\n→ {_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
