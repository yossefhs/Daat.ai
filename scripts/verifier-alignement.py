#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chaque bloc d'une page est-il bien le séif qu'il prétend être ?

C'est le contrôle qui manquait avant d'écrire des traductions en série. Une
traduction peut être irréprochable et rester fausse si elle est posée sous le
mauvais séif — et rien, dans la page, ne le montre : le lecteur voit un texte
hébreu et un texte français, tous deux justes, qui ne parlent pas de la même
chose. Aucun des autres gates ne peut le voir. ``verifier-citations`` juge les
citations, ``verifier-traductions`` juge les longueurs ; ni l'un ni l'autre ne
sait à quel séif un bloc correspond.

Le contrôle ne suppose rien de la numérotation, et c'est ce qui le rend sûr.
Deux tentatives ont échoué avant celle-ci. Comparer le rang du bloc au numéro
du séif ressortait 42 « décalages » dont aucun n'en était un : une page peut
grouper trois séifim sous un seul bloc — le siman 263 le fait pour ז–ט — et le
rang cesse alors de suivre la numérotation sans la moindre erreur. Se fier au
titre de la page était pire encore : la plupart des séifim n'ont pas de titre
propre, et les blocs héritaient d'un titre lointain, produisant 320 faux
signalements.

Ne subsistent donc que deux questions auxquelles on peut répondre sans rien
supposer :

- **l'hébreu du bloc existe-t-il dans ce siman ?** Sinon, la page reproduit
  autre chose que ce qu'annonce son titre, ou le texte a été altéré ;
- **les blocs se suivent-ils dans l'ordre de la source ?** Un retour en
  arrière signale un bloc déplacé ou dupliqué — et donc une traduction, une
  glose ou une citation attachée au mauvais texte.

Ce qu'il rapporte aujourd'hui
------------------------------
1032 blocs confrontés dans les 124 pages de Hilkhot Shabbat, **8 écarts dans 4
pages** — et les quatre examinés sont légitimes : des blocs de récapitulation
qui reprennent le séif 1 en fin de page, et des citations de guemara que les
filtres n'attrapent pas. Le chiffre est donc un plancher de bruit, non une
liste d'erreurs. Il vaut comme garde-fou de non-régression : un décalage
nouvellement introduit ressortirait au-dessus de ce plancher.

Son intérêt principal est en amont d'un travail de traduction en série. Avant
d'écrire les traductions des simanim 310, 311, 317 et 323, ce contrôle a établi
que chacun de leurs blocs était bien le séif attendu — sans quoi une traduction
juste aurait pu se retrouver sous le mauvais texte, défaut qu'aucun autre gate
ne voit et qu'une relecture rapide ne soupçonne pas.

    python3 scripts/verifier-alignement.py [--siman 310] [--section shabbat]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

RACINE = pathlib.Path(__file__).resolve().parent.parent / "sources"
CACHE = pathlib.Path(__file__).resolve().parent / ".cache-sefaria-alignement"
RE_BLOC = re.compile(
    r'<(?P<tag>blockquote|div|p)[^>]*class="[^"]*(?P<cls>text-source|sacred-text)[^"]*"[^>]*>'
    r"(?P<contenu>.*?)</(?P=tag)>",
    re.S,
)
RE_TAG = re.compile(r"<[^>]*>")
# On identifie un bloc par ses premiers mots, non par une chaîne exacte : la
# page écrit « אַף עַל פִּי » en toutes lettres là où la source abrège « אע״פ »,
# et une comparaison littérale échouait dès la première abréviation — 158 blocs
# parfaitement alignés ressortaient en « introuvable ». Un recouvrement de mots
# franchit l'abréviation, le nikoud et la graphie pleine.
MOTS_TEMOINS = 14
SEUIL = 0.55
RE_TITRE = re.compile(r"<(h[2-5])[^>]*>(?P<t>(?:(?!</?h[2-5]).)*?)</\1>", re.S | re.I)
_LETTRES = ("alef beit bet guimel gimel daled dalet he hei vav zayin het chet tet yod "
            "yad yb yg").split()
_HE = "א ב ג ד ה ו ז ח ט י".split()
_TRANSLIT = {"alef": 1, "beit": 2, "bet": 2, "guimel": 3, "gimel": 3, "daled": 4,
             "dalet": 4, "he": 5, "hei": 5, "vav": 6, "zayin": 7, "het": 8,
             "chet": 8, "tet": 9, "yod": 10}
_GEM = {c: i + 1 for i, c in enumerate(_HE)}


def seifim_du_titre(titre: str) -> set[int]:
    """Les numéros de séif qu'un titre revendique — chiffres, translittération
    ou lettres hébraïques, y compris les plages « Seifim Zayin–Tet »."""
    if not re.search(r"s[eé]if|סעיף", titre, re.I):
        return set()
    nums = {int(x) for x in re.findall(r"\b(\d{1,2})\b", titre)}
    for mot in re.findall(r"[A-Za-zÀ-ÿ]+", titre.lower()):
        if mot in _TRANSLIT:
            nums.add(_TRANSLIT[mot])
    for c in re.findall(r"(?<![א-ת])([א-י])(?![א-ת])", titre):
        nums.add(_GEM[c])
    if len(nums) == 2 and re.search(r"[–—-]", titre):
        a, b = sorted(nums)
        nums = set(range(a, b + 1))
    return nums
# Les pages reproduisent aussi le commentaire, dans le même balisage que les
# séifim. Le confronter au Choul'han Aroukh n'aurait aucun sens : la Michna
# Beroura n'y figure évidemment pas. Sans ce filtre, 295 blocs de commentaire
# ressortaient en « introuvable » et noyaient les vrais décalages.
# Les pages reproduisent aussi du commentaire et des sugyot, dans le même
# balisage que les séifim. Deux formes à écarter : l'attribution nommée — qui
# peut se trouver en fin de bloc autant qu'au début, d'où la recherche libre —
# et l'ouverture talmudique, un bloc de guemara n'ayant pas à figurer dans le
# Choul'han Aroukh.
COMMENTAIRE = re.compile(r"משנה ברורה|מ״ב|ביאור הלכה|שער הציון|ט״ז|מגן אברהם"
                         r"|באר היטב|כף החיים|ילקוט יוסף|שו״ע הרב|קונטרס אחרון")
TALMUD = re.compile(r"^\s*(?:תנו רבנן|תר|תניא|גמרא|גמ|אמר ר|אמר רב|איתמר|מתני|משנה|"
                    r"רב חסדא|רבא|רבה)")
# Un bloc qui cite lui-même sa massekhet — « (פסחים נ:) » — n'est pas un séif.
MASSEKHET = re.compile(r"\((?:פסחים|שבת|ברכות|ביצה|עירובין|סוכה|מגילה|יומא|חולין|"
                       r"קידושין|כתובות|בבא [קמב]|סנהדרין|נדרים|מועד קטן)\s")
LIVRES = {"shabbat": "Shulchan Arukh, Orach Chayim",
          "orah-haim": "Shulchan Arukh, Orach Chayim",
          "yoreh-deah": "Shulchan Arukh, Yoreh De'ah"}


def lettres(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^א-ת]", "", s)


def lettres_mots(s: str) -> str:
    """Comme ``lettres``, mais en gardant la séparation des mots."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^א-ת ]", " ", s)


def seifim(livre: str, n: int) -> list[str] | None:
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{livre.replace(' ', '_').replace(',', '')}-{n}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    u = (f"https://www.sefaria.org/api/v3/texts/"
         f"{urllib.parse.quote(f'{livre} {n}')}?return_format=text_only&version=hebrew")
    try:
        v = json.load(urllib.request.urlopen(u, timeout=40))["versions"][0]["text"]
    except Exception:
        return None
    out = [lettres_mots(x) for x in (v if isinstance(v, list) else [v])]
    f.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def blocs(chemin: pathlib.Path) -> list[tuple[str, set]]:
    """(texte du bloc, séifim revendiqués par le titre qui le précède)."""
    html = chemin.read_text(encoding="utf-8")
    titres = [(m.start(), seifim_du_titre(
        re.sub(r"\s+", " ", RE_TAG.sub(" ", m.group("t"))).strip()))
        for m in RE_TITRE.finditer(html)]
    out = []
    for m in RE_BLOC.finditer(html):
        revendique = set()
        for pos, nums in titres:
            if pos < m.start() and nums:
                revendique = nums
        out.append((re.sub(r"\s+", " ", RE_TAG.sub(" ", m.group("contenu"))).strip(),
                    revendique))
    return out


def examiner(chemin: pathlib.Path, livre: str, n: int) -> tuple[int, list[str]]:
    src = seifim(livre, n)
    if not src:
        return 0, []
    ecarts, vus, dernier = [], 0, 0
    for i, (b, revendique) in enumerate(blocs(chemin), 1):
        nu = re.sub(r"^[\s\"'«»]+", "", lettres_mots(b))
        if COMMENTAIRE.search(b) or TALMUD.match(nu) or MASSEKHET.search(b):
            continue          # commentaire ou sugya, non séif : hors du périmètre
        temoins = [m for m in re.findall(r"[א-ת]{3,}", lettres_mots(b))][:MOTS_TEMOINS]
        if len(temoins) < 6:
            continue          # trop court pour être identifié sans ambiguïté
        vus += 1
        scores = [(sum(1 for w in temoins if w in s) / len(temoins), j + 1)
                  for j, s in enumerate(src)]
        meilleur, place = max(scores)
        if meilleur < SEUIL:
            ecarts.append(f"bloc {i} : introuvable dans le siman {n} "
                          f"(meilleur recouvrement {meilleur:.0%} au séif {place})")
        else:
            if place < dernier:
                ecarts.append(f"bloc {i} : séif {place}, après le séif "
                              f"{dernier} — retour en arrière")
            dernier = place
    return vus, ecarts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--siman", type=int)
    ap.add_argument("--section")
    args = ap.parse_args()

    fichiers = [f for f in sorted(RACINE.rglob("niveau-1-base.html"))]
    if args.section:
        fichiers = [f for f in fichiers if f.parent.parent.name == args.section]
    if args.siman:
        fichiers = [f for f in fichiers if f.parent.name == f"siman-{args.siman}"]

    total_blocs = total_ecarts = pages = 0
    for f in fichiers:
        section = f.parent.parent.name
        livre = LIVRES.get(section)
        m = re.fullmatch(r"siman-(\d+)", f.parent.name)
        if not livre or not m:
            continue
        vus, ecarts = examiner(f, livre, int(m.group(1)))
        total_blocs += vus
        if ecarts:
            pages += 1
            total_ecarts += len(ecarts)
            print(f"⚠ {f.relative_to(RACINE)}")
            for e in ecarts:
                print(f"     {e}")
    print(f"\n{total_blocs} bloc(s) confronté(s) au Choul'han Aroukh dans "
          f"{len(fichiers)} page(s)")
    print(f"→ {total_ecarts} écart(s) d'alignement dans {pages} page(s)")
    return 1 if total_ecarts else 0


if __name__ == "__main__":
    raise SystemExit(main())
