#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le site et l'e-mail annoncent-ils le même siman le même jour ?

Le Daat Yomi a deux sources de vérité indépendantes, et rien ne les reliait :

- **le site** porte le plan en dur dans un tableau ``var ENTRIES = [[…]]``
  inscrit dans chaque page d'accueil (fr/he/en) et dans les trois extraits de
  bandeau ; il n'y cherche pas par date, il **calcule** un numéro de jour à
  partir de ``data-start`` en comptant les jours d'étude — vendredi et samedi
  exclus — puis indexe le tableau à ce rang ;
- **l'e-mail quotidien** lit ``data/limoud-plan.json`` et y cherche la date.

Deux chemins, deux fichiers, aucun lien : il suffit qu'un lot soit ajouté d'un
côté et pas de l'autre, ou qu'un jour d'étude soit inséré, pour que la page du
jour et le courriel du matin annoncent deux simanim différents. Ce contrôle
ferme cet écart : il vérifie que, pour chacun des jours du plan,

1. le rang calculé par la fonction du site retombe bien sur l'entrée de cette
   date — c'est-à-dire que compter les jours d'étude et chercher la date
   donnent le même résultat ;
2. l'entrée du site et celle du plan JSON portent le même numéro de jour, le
   même siman et la même plage de séifim ;
3. les six tableaux inscrits dans les pages sont identiques entre eux.

Ce que le contrôle NE couvre pas, et qu'il faut avoir en tête :

- **les plans personnels.** Un abonné qui s'est fabriqué un plan a sa propre date
  de départ, et son courriel — « Mon plan · Jour N » — suit ce plan-là, non le
  rythme universel. Le site, lui, ne connaît ce plan que par le ``localStorage``
  du navigateur où il a été créé : partout ailleurs il retombe sur l'universel.
  Le même abonné peut donc lire un jour sur la page et un autre dans sa boîte
  sans qu'aucun calcul soit faux — c'est une divergence de source, pas de calcul,
  et elle est hors de portée d'un contrôle de fichiers.
- **l'heure d'envoi.** Le site bascule à minuit UTC, le courriel part à l'heure
  du cron ; entre les deux, la boîte de réception retarde sur la page.

    python3 scripts/verifier-limoud.py
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
RE_ENTRIES = re.compile(r"var ENTRIES = (\[\[.*?\]\]);", re.S)
RE_START = re.compile(r'data-start="(\d{4}-\d{2}-\d{2})"')
RE_TOTAL = re.compile(r'data-total="(\d+)"')
# Le plan ne compte que du dimanche au jeudi : vendredi et samedi sont sautés.
CHOMES = {4, 5}  # datetime.weekday() : lundi=0 … vendredi=4, samedi=5


def jour_detude(d: datetime.date) -> bool:
    return d.weekday() not in CHOMES


def rang_calcule(jour: datetime.date, depart: datetime.date) -> int:
    """La fonction du site, transposée : combien de jours d'étude jusqu'à ce jour."""
    if jour < depart:
        return 0
    n, cur = 0, depart
    while cur < jour:
        if jour_detude(cur):
            n += 1
        cur += datetime.timedelta(days=1)
    if jour_detude(jour):
        n += 1
    return n


def pages_avec_plan() -> list[pathlib.Path]:
    out = []
    for p in sorted(RACINE.glob("index*.html")):
        out.append(p)
    for p in sorted((RACINE / "data" / ".banner-snippets").glob("*.html")):
        out.append(p)
    return [p for p in out if RE_ENTRIES.search(p.read_text(encoding="utf-8"))]


def main() -> int:
    ecarts: list[str] = []

    pages = pages_avec_plan()
    if not pages:
        print("✗ aucune page ne porte de tableau ENTRIES — le bandeau a-t-il changé de forme ?")
        return 1

    # 1. Les tableaux des pages sont-ils identiques entre eux ?
    tables = {}
    for p in pages:
        t = p.read_text(encoding="utf-8")
        tables[p] = json.loads(RE_ENTRIES.search(t).group(1))
    reference = tables[pages[0]]
    for p, tab in tables.items():
        if [(e[0], e[1], e[2], e[5], e[6]) for e in tab] != \
           [(e[0], e[1], e[2], e[5], e[6]) for e in reference]:
            ecarts.append(f"{p.relative_to(RACINE)} : tableau différent de {pages[0].name}")

    # 2. Le rang calculé retombe-t-il sur la bonne date ?
    t0 = pages[0].read_text(encoding="utf-8")
    depart = datetime.date.fromisoformat(RE_START.search(t0).group(1))
    total = int(RE_TOTAL.search(t0).group(1))
    if total != len(reference):
        ecarts.append(f"data-total={total} mais le tableau compte {len(reference)} entrées")

    for e in reference:
        num, date = e[0], datetime.date.fromisoformat(e[1])
        calc = rang_calcule(date, depart)
        if calc != num:
            ecarts.append(f"{e[1]} : le site calcule le jour {calc}, le tableau dit {num}")

    # 3. Le plan de l'e-mail dit-il la même chose ?
    plan = json.loads((RACINE / "data" / "limoud-plan.json").read_text(encoding="utf-8"))
    par_date = {x["date"]: x for x in plan.get("entries", [])}
    if len(par_date) != len(reference):
        ecarts.append(f"le plan de l'e-mail compte {len(par_date)} jours, le site {len(reference)}")
    for e in reference:
        num, date, siman, s_deb, s_fin = e[0], e[1], e[2], e[5], e[6]
        m = par_date.get(date)
        if not m:
            ecarts.append(f"{date} : absent du plan de l'e-mail")
            continue
        if m.get("dayNumber") != num:
            ecarts.append(f"{date} : jour {num} sur le site, {m.get('dayNumber')} dans l'e-mail")
        if (m.get("siman") or {}).get("num") != siman:
            ecarts.append(f"{date} : siman {siman} sur le site, "
                          f"{(m.get('siman') or {}).get('num')} dans l'e-mail")
        seifim = m.get("seifim") or {}
        if seifim and (seifim.get("start"), seifim.get("end")) != (s_deb, s_fin):
            ecarts.append(f"{date} : séifim {s_deb}-{s_fin} sur le site, "
                          f"{seifim.get('start')}-{seifim.get('end')} dans l'e-mail")

    print(f"{len(reference)} jour(s) de plan · {len(pages)} page(s) porteuse(s) du tableau")
    if ecarts:
        for x in ecarts[:40]:
            print(f"  ✗ {x}")
        if len(ecarts) > 40:
            print(f"  … et {len(ecarts) - 40} autre(s)")
        print(f"→ {len(ecarts)} écart(s) entre le site et l'e-mail")
        return 1
    print("→ le site et l'e-mail annoncent le même siman chaque jour ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
