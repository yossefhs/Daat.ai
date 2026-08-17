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

Il reste que la plupart des blocs **disent eux-mêmes** de quel séif ils
relèvent, par le titre qui les surplombe — « Seif 4 — … », « Texte original
(séifim 5-7) ». Ce titre est une donnée de la page, non une supposition : on
peut donc poser la question forte — *est-ce bien ce séif-là ?* — au lieu de la
seule question faible — *est-ce quelque part dans le siman ?* Trois questions,
selon ce que le bloc annonce :

- **le bloc annoncé « séif N » est-il le séif N ?** S'il ressemble bien
  davantage à un autre séif, la page l'a mal numéroté ;
- **le bloc annoncé existe-t-il seulement dans ce siman ?** Sinon le texte
  affiché n'est pas celui qu'il prétend être ;
- **pour les blocs sans titre de séif, les blocs se suivent-ils dans l'ordre
  de la source ?** Un retour en arrière signale un bloc déplacé ou dupliqué.

Deux normalisations, sans lesquelles le contrôle se noie
--------------------------------------------------------
Un bloc placé sous un titre de commentateur — « Taz s.k. 1 » — n'est pas un
séif et sort du périmètre : le chercher dans le Choul'han Aroukh ne produit que
du bruit, et le critère du titre est plus sûr que de guetter le nom du
commentateur dans l'hébreu, qui ne s'y trouve pas toujours.

Surtout, les pages vocalisées écrivent en ktiv haser — אֲפִלּוּ — là où
l'imprimé non vocalisé de Sefaria écrit plein — אפילו. La comparaison
littérale déclarait « introuvable » des séifim recopiés mot pour mot : c'était
l'essentiel des signalements de Yoreh De'ah, dont les pages sont vocalisées.
Retirer les yod et vav met les deux graphies sur le même pied.

Ce qu'il rapporte aujourd'hui
------------------------------
2359 blocs confrontés dans les 359 pages des trois compartiments, **16 écarts
dans 10 pages**. Avant ces trois ajustements il en rapportait 143 dans 56
pages, dont l'échantillonnage a montré qu'ils étaient presque tous du bruit
d'orthographe ou de commentaire ; le contrôle n'y a pourtant rien perdu — c'est
lui, ainsi ajusté, qui a fait ressortir les deux blocs du siman 79 numérotés
3 et 4 alors qu'ils sont les séifim 4 et 9, et les deux blocs du siman 101 de
Yoreh De'ah dont l'hébreu ne se retrouve nulle part dans le siman.

Ce qui subsiste est un plancher de bruit connu : des blocs sans titre de séif
qui citent une baraïta ou récapitulent, que les filtres de contenu n'attrapent
pas. Il vaut comme garde-fou de non-régression.

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
RE_TITRE = re.compile(r"<h[234][^>]*>(.*?)</h[234]>", re.S)
# Un bloc placé sous un titre de commentateur n'est pas un séif du Choul'han
# Aroukh, quoi que dise son contenu — critère plus sûr que de chercher le nom
# du commentateur dans le texte hébreu, qui ne s'y trouve pas toujours.
RE_COMMENTATEUR = re.compile(
    r"Taz|Shach|Chakh|Chach|S'?hakh|Mishna Berura|Michna Beroura|Beour Halakha"
    r"|Magen Avraham|Baer Heitev|Pri Megadim|Kaf ha|Yalkut|s\.k\."
    r"|ט״ז|ש״ך|מ״ב", re.I)
VALEURS = {"א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8,
           "ט": 9, "י": 10, "כ": 20, "ל": 30, "מ": 40, "נ": 50, "ס": 60,
           "ע": 70, "פ": 80, "צ": 90}
# Un bloc déclaré « séif 3 » qui ressemble bien davantage au séif 4 est un
# décalage. Le critère est *relatif* — l'écart entre le meilleur séif et le
# séif annoncé — et non absolu : une page qui développe les abréviations de
# l'imprimé (בד״א → במה דברים אמורים) tombe légitimement à 50 % de recouvrement
# avec son propre séif, et un seuil absolu la condamnerait à tort.
DECALAGE_MIN = 0.80
DECALAGE_ECART = 0.30
# Un bloc annoncé peut aussi ne correspondre à *rien* dans le siman ; le
# critère relatif ci-dessus ne le voit pas, puisqu'aucun autre séif ne le
# revendique non plus. Le seuil est placé à distance des deux bords : sur les
# 2139 blocs annoncés du site, le plus bas des blocs légitimes est à 43 %
# (une page qui condense trois séifim en un bloc), et les deux seuls blocs
# au-dessous de 40 % sont à 15 % et 23 %.
INTROUVABLE_ANNONCE = 0.35


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


def squelette(s: str) -> str:
    """Le texte privé de ses matres lectionis.

    Une page vocalisée écrit en ktiv haser — אֲפִלּוּ — là où l'édition imprimée
    non vocalisée écrit plein — אפילו. La comparaison littérale déclarait alors
    « introuvable » un séif recopié mot pour mot : c'est ce qui produisait
    l'essentiel des signalements de Yoreh De'ah, dont les pages sont vocalisées.
    Retirer les yod et vav met les deux graphies sur le même pied ; ce qui
    subsiste d'un écart après cette normalisation n'est plus orthographique.
    """
    return re.sub(r"[יו]", "", s)


def blocs(chemin: pathlib.Path) -> list[tuple[str, list[int]]]:
    """Les blocs de la page, chacun avec les séifim que son titre revendique.

    Rattacher un bloc au titre qui le surplombe est ce qui distingue un séif
    d'un commentaire : un bloc placé sous « Taz s.k. 1 » n'a pas à figurer dans
    le Choul'han Aroukh, et le chercher n'y produit que du bruit. Le titre dit
    aussi *quel* séif le bloc prétend être — ce qui permet la vérification forte
    (est-ce bien celui-là ?) et non la seule vérification faible (est-ce
    quelque part dans le siman ?).
    """
    html = chemin.read_text(encoding="utf-8")
    out = []
    for m in RE_BLOC.finditer(html):
        titres = RE_TITRE.findall(html[:m.start()])
        titre = re.sub(r"\s+", " ", RE_TAG.sub(" ", titres[-1])).strip() if titres else ""
        texte = re.sub(r"\s+", " ", RE_TAG.sub(" ", m.group("contenu"))).strip()
        out.append((texte, titre, numeros(titre)))
    return out


def numeros(titre: str) -> list[int] | None:
    """Les séifim que le titre revendique. ``None`` : le bloc n'est pas un séif.

    Un titre peut couvrir une plage, et même plusieurs — « séifim 6-8, 16-21,
    23-24 » sur les pages qui regroupent par thème. N'en lire que la première
    fabriquerait un décalage là où la page est explicite.
    """
    if RE_COMMENTATEUR.search(titre):
        return None
    m = re.search(r"[Ss][ée]if(?:im)?\s+([\d\s,–—-]+)", titre)
    if m:
        out: list[int] = []
        for part in re.split(r"[,\s]+", m.group(1).strip()):
            r = re.fullmatch(r"(\d+)[–—-](\d+)", part)
            if r:
                out += list(range(int(r.group(1)), int(r.group(2)) + 1))
            elif part.isdigit():
                out.append(int(part))
        if out:
            return out
    # « Seif א », « סעיף י״א » : le gershayim précède la dernière lettre, il
    # faut donc l'inclure dans la capture, sans quoi tout séif ≥ 11 est lu 10.
    m = (re.search(r"[Ss][ée]if\s+([א-ת][׳״]?[א-ת]?[׳״]?[א-ת]?)", titre)
         or re.search(r"סעיף\s+([א-ת][׳״]?[א-ת]?[׳״]?[א-ת]?)", titre))
    if m:
        g = gematria(m.group(1))
        if g:
            return [g]
    return []


def gematria(s: str) -> int | None:
    s = re.sub(r"[׳״\"']", "", s)
    return sum(VALEURS[c] for c in s) if s and all(c in VALEURS for c in s) else None


def examiner(chemin: pathlib.Path, livre: str, n: int) -> tuple[int, list[str]]:
    src = seifim(livre, n)
    if not src:
        return 0, []
    sq = [squelette(s) for s in src]
    ecarts, vus, dernier = [], 0, 0
    for i, (b, titre, annonces) in enumerate(blocs(chemin), 1):
        if annonces is None:
            continue          # bloc placé sous un titre de commentateur
        nu = re.sub(r"^[\s\"'«»]+", "", lettres_mots(b))
        if COMMENTAIRE.search(b) or TALMUD.match(nu) or MASSEKHET.search(b):
            continue          # commentaire ou sugya, non séif : hors du périmètre
        temoins = [squelette(m)
                   for m in re.findall(r"[א-ת]{3,}", lettres_mots(b))][:MOTS_TEMOINS]
        temoins = [w for w in temoins if len(w) >= 2]
        if len(temoins) < 6:
            continue          # trop court pour être identifié sans ambiguïté
        vus += 1
        scores = [(sum(1 for w in temoins if w in s) / len(temoins), j + 1)
                  for j, s in enumerate(sq)]
        meilleur, place = max(scores)
        annonces = [k for k in annonces if 1 <= k <= len(src)]
        if annonces:
            # Vérification forte : le bloc est-il le séif qu'il annonce ?
            attendu = max(scores[k - 1][0] for k in annonces)
            if (place not in annonces and meilleur >= DECALAGE_MIN
                    and meilleur - attendu >= DECALAGE_ECART):
                ecarts.append(
                    f"bloc {i} : annoncé séif {'-'.join(map(str, annonces))}, "
                    f"mais correspond au séif {place} ({meilleur:.0%} contre "
                    f"{attendu:.0%}) — « {titre[:60]} »")
            elif meilleur < INTROUVABLE_ANNONCE:
                ecarts.append(
                    f"bloc {i} : annoncé séif {'-'.join(map(str, annonces))}, "
                    f"introuvable dans le siman {n} (meilleur recouvrement "
                    f"{meilleur:.0%}, au séif {place}) — « {titre[:60]} »")
            continue          # l'ordre est déjà dit par le titre : rien à déduire
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
