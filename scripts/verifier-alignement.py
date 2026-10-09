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
3505 blocs confrontés dans les 1700 pages des trois compartiments, **10 écarts
dans 8 pages** — et **Hilkhot Chabbat en entier, ses 124 simanim, à zéro**. Les
1341 pages gagnées en lisant aussi les étiquettes inline n'ont produit aucun
signalement nouveau hormis celui qu'on cherchait, le siman 243, depuis corrigé ;
et le motif ``SUGYA`` a retiré les cinq sugyot du siman 242 que le contrôle
cherchait dans un siman qui ne compte qu'un séif.

Ce qui reste tient en deux familles : le siman 101 de Yoreh De'ah, dont deux
blocs annoncent des séifim dont l'hébreu ne se retrouve nulle part dans le siman
— consigné dans ``audit/alignement-a-verifier.md`` pour le Rav —, et huit blocs
sans titre de séif qui récapitulent ou citent un Rishon. Avant ces trois ajustements il en rapportait 143 dans 56
pages, dont l'échantillonnage a montré qu'ils étaient presque tous du bruit
d'orthographe ou de commentaire ; le contrôle n'y a pourtant rien perdu — c'est
lui, ainsi ajusté, qui a fait ressortir les deux blocs du siman 79 numérotés
3 et 4 alors qu'ils sont les séifim 4 et 9, et les deux blocs du siman 101 de
Yoreh De'ah dont l'hébreu ne se retrouve nulle part dans le siman.

Ce qui subsiste est un plancher de bruit connu : des blocs sans titre de séif
qui citent une baraïta ou récapitulent, que les filtres de contenu n'attrapent
pas. Il vaut comme garde-fou de non-régression.

Mesure du 7 octobre 2026, après trois réparations (plage chaînée lue en
entier dans les deux écritures ; numéral de base exigé VRAI, « סעיף אחד/יחיד »
lu 1 quand le siman n'a qu'un séif ; lacune légitime seulement sur la liste
mesurée) : 7 695 fichiers, 23 701 blocs, 22 887 étiquettes (+68), 24 anomalies
— contre 26. Les deux disparues sont un seul bloc, OH 8 séifim 7-10, que FR et
EN signalaient « introuvable » et HE taisait : il EST bien ces quatre séifim,
dans l'ordre. Mais il TRONQUE le séif 10 (« או כשילבש טלית אחר… של ראשון »
manque dans les trois langues) — défaut de recopie que cette porte ne juge pas
et que l'ancien signal ne voyait que par accident, sous un faux motif.

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
# Une etiquette de seif ne surplombe pas toujours le bloc : elle peut etre DANS
# le paragraphe — « <p><strong>סעיף א.</strong> לא ישכיר אדם מרחץ… » ou, sur les
# pages d'index, « <p><strong>א.</strong> … ». Ces paragraphes n'ont pas de
# classe et n'etaient donc pas des blocs du tout : le controle ne les voyait
# meme pas.
#
# C'est par la qu'est passe le siman 243, ou le champ, le four, le moulin et la
# glose du Rama — tous dans le seif א — etaient publies sous « סעיף ב », avec
# une clause deplacee qui donnait comme raison de PERMETTRE le champ ce que le
# Choulhan Aroukh donne comme raison d'INTERDIRE le bain. Aucun des quatre
# garde-fous ne pouvait le voir : les citations etaient reelles, la langue
# juste, la structure conforme. C'etait le decoupage qui etait faux.
RE_BLOC_INLINE = re.compile(
    r"<p[^>]*>\s*(?:<(?!strong)[^>]*>\s*)*<strong>\s*"
    r"(?P<etq>(?:סעיף|[Ss][ée]if)?\s*[א-ת][׳״]?[א-ת]?[׳״]?[א-ת]?\s*[.:׳']?)\s*</strong>"
    r"(?P<contenu>.*?)</p>",
    re.S,
)
RE_BLOC_LIGNE = re.compile(
    r"^\s*<strong>\s*(?P<etq>(?:סעיף|[Ss][ée]if)?\s*[א-ת][׳״]?[א-ת]?[׳״]?[א-ת]?\s*[.:׳']?)\s*</strong>"
    r"(?P<contenu>[^\n]*?)(?:<br\s*/?>|</div>|$)",
    re.M,
)
# ---------------------------------------------------------------------------
# Le niveau 4 n'etait pas regarde du tout, et ce n'etait pas faute de fichiers
# dans la liste : son texte source n'est dans AUCUNE des classes que RE_BLOC
# connait. Il vit dans « <p class="sa-he"> », a l'interieur d'un
# « <details class="seif-details"> » dont le « <span class="seif-num"> » dit le
# seif. Mesure faite avant d'y toucher : sur les 1095 pages niveau-4-daat-harav
# des trois langues, RE_BLOC captait ZERO bloc. Ajouter ces fichiers a la liste
# sans ce motif-ci aurait lu 1095 pages de plus et compare RIEN — la porte verte
# qui ne compare rien, qui est pire qu'une porte absente.
#
# Et ce texte-la n'est PAS le Choul'han Aroukh : c'est le CHOUL'HAN AROUKH
# HARAV, un autre livre, a la numerotation propre. Le confronter au Mehaber
# aurait produit un bruit massif et faux. On le confronte a son livre.
RE_DETAILS = re.compile(
    r'<details[^>]*class="[^"]*seif-details[^"]*"[^>]*>(?P<c>.*?)</details>', re.S)
RE_SEIF_NUM = re.compile(
    r'<span[^>]*class="[^"]*seif-num[^"]*"[^>]*>(?P<e>.*?)</span>', re.S)
RE_SUMMARY = re.compile(r"<summary[^>]*>(?P<s>.*?)</summary>", re.S)
RE_SA_HE = re.compile(r'<p[^>]*class="[^"]*sa-he[^"]*"[^>]*>(?P<t>.*?)</p>', re.S)
# L'etiquette se lit « סעיף א », « סעיף יא » (sans gershayim), et parfois
# « סעיף א' » avec une apostrophe ASCII — 5 blocs mesures, un defaut de contenu
# que cette porte lit sans le corriger. On n'en garde que le prefixe « סעיף N » :
# 80 des 9942 blocs ecrivent « סעיף ג — Seif 3 (heavy brine) », et le tiret d'un
# tel intitule est exactement le piege de plage qui a deja produit une fausse
# trouvaille dans ce depot.
RE_ETQ_HARAV = re.compile(r"סעיף\s+([א-ת][׳״']?[א-ת]?[׳״']?[א-ת]?)")
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
                       r"קידושין|כתובות|בבא [קמב]|סנהדרין|נדרים|מועד קטן|"
                       r"פאה|דמאי|שביעית|תרומות|מעשרות|חלה|ערלה|ביכורים|"
                       r"ידים|עדיות|אבות)\s")
# La formule d'attribution amoraïque n'ouvre pas toujours le bloc : la page cite
# « בַּמֶּה מְעַנְּגוֹ? אָמַר רַב יְהוּדָה בְּרֵיהּ דְּרַב שְׁמוּאֵל בַּר שִׁילַת מִשְּׁמֵיהּ דְּרַב… »
# — la guemara commence par sa question, et le nom vient après. Le motif ancré en
# tête ne la voyait pas, et cinq sugyot du siman 242 ressortaient « introuvables »
# dans un siman qui ne compte qu'un séif.
#
# Ces chaînes-là ne se rencontrent pas dans le Choul'han Aroukh : il tranche, il
# ne rapporte pas qui a dit quoi à qui. On peut donc les chercher n'importe où
# dans le bloc sans affaiblir le contrôle.
SUGYA = re.compile(r"אמר רב |אמר רבי |א״ר |תנו רבנן|ת״ר |תנא דבי|בריה דרב|משמיה ד|"
                   r"אמר להם הקדוש ברוך הוא|אמר להן הקדוש ברוך הוא|דתניא|דתנן|"
                   r"אמר שמואל|אמר עולא|אמר אביי|אמר רבא")
LIVRES = {"shabbat": "Shulchan Arukh, Orach Chayim",
          "orah-haim": "Shulchan Arukh, Orach Chayim",
          "yoreh-deah": "Shulchan Arukh, Yoreh De'ah"}
# Le niveau 4 d'Orah Haim et de Hilkhot Chabbat expose la chitah de l'Admour
# HaZaken : son texte source est le Choul'han Aroukh HaRav. Yoreh De'ah n'a pas
# de niveau 4 de ce genre — son niveau 4 est « halakha lema'asse » — et n'entre
# donc pas dans cette table.
LIVRES_HARAV = {"shabbat": "Shulchan Arukh HaRav, Orach Chayim",
                "orah-haim": "Shulchan Arukh HaRav, Orach Chayim"}
RE_TITRE = re.compile(r"<h[234][^>]*>(.*?)</h[234]>", re.S)
# Un bloc placé sous un titre de commentateur n'est pas un séif du Choul'han
# Aroukh, quoi que dise son contenu — critère plus sûr que de chercher le nom
# du commentateur dans le texte hébreu, qui ne s'y trouve pas toujours.
# ⚠ ELLE NE CONNAISSAIT QUE LA FORME LATINE « s.k. », pas la forme hebraique
# « ס״ק » — qui est pourtant celle du depot : 5 246 titres de bloc l'emploient.
# C'est la meme cecite que celle qu'on repare ici, a un autre endroit. En nombre
# de blocs reellement atteints elle coute peu — 2 blocs, mesures, dont AUCUN ne
# portait d'etiquette de seif — mais l'un des deux produisait un signalement
# faux : le « פתחי תשובה ס״ק א » du siman 116 de Yoreh De'ah, une entree
# d'appareil que la porte cherchait parmi les seifim du Choul'han Aroukh.
RE_COMMENTATEUR = re.compile(
    r"Taz|Shach|Chakh|Chach|S'?hakh|Mishna Berura|Michna Beroura|Beour Halakha"
    r"|Magen Avraham|Baer Heitev|Pri Megadim|Kaf ha|Yalkut|s\.k\."
    r"|Pit'?hei Teshuva|Nekudot HaKessef"
    r"|ט״ז|ש״ך|מ״ב|ס״ק|פתחי תשובה|פת״ש|נקודות הכסף", re.I)
# Un numeral hebraique : une a trois lettres, avec geresh ou gershayim possibles.
NUM_HE = r"[א-ת][׳״']?[א-ת]?[׳״']?[א-ת]?"
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


def seifim(livre: str, n: int) -> list[str] | str:
    """Les séifim du Choul'han Aroukh, ou ``LACUNE`` / ``ECHEC``.

    Rendait ``None`` pour les deux : un siman que Sefaria ne numérise pas — le
    seul du dépôt est Yoreh De'ah 169 — et un incident de réseau étaient le même
    silence, et le siman sortait de la mesure sans que rien ne le dise. Quand la
    v3 n'aboutit pas, on redemande à ``api/texts``, qui rend la lacune
    explicitement (``ref`` juste, ``error`` nul, ``he`` vide) ; ce qui n'est pas
    une lacune est alors un échec, et se dit comme tel.
    """
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{livre.replace(' ', '_').replace(',', '')}-{n}.json"
    if f.exists():
        out = json.loads(f.read_text(encoding="utf-8"))
        if out:
            return out
    u = (f"https://www.sefaria.org/api/v3/texts/"
         f"{urllib.parse.quote(f'{livre} {n}')}?return_format=text_only&version=hebrew")
    try:
        v = json.load(urllib.request.urlopen(u, timeout=40))["versions"][0]["text"]
    except Exception:
        return _lacune_ou_echec(livre, n)
    out = [lettres_mots(x) for x in (v if isinstance(v, list) else [v])]
    if not any(s.strip() for s in out):
        return _lacune_ou_echec(livre, n)
    f.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def _lacune_ou_echec(livre: str, n: int) -> str:
    """Le livre n'a-t-il pas ce siman, ou la mesure a-t-elle échoué ?

    Le signe qui ne trompe pas est que le ``ref`` servi finit par le numéro
    demandé : sur un ref mal formé Sefaria rend 200 et le livre entier.
    """
    u = (f"https://www.sefaria.org/api/texts/"
         f"{urllib.parse.quote(livre.replace(' ', '_'))}.{n}?context=0&pad=0")
    try:
        d = json.load(urllib.request.urlopen(u, timeout=40))
    except Exception as e:
        RAISONS[(livre, n)] = f"api/texts : {type(e).__name__}"
        return ECHEC
    if d.get("error") or not str(d.get("ref", "")).rstrip().endswith(f" {n}"):
        RAISONS[(livre, n)] = f"ref servi {d.get('ref')!r}, error {d.get('error')!r}"
        return ECHEC
    he = d.get("he")
    he = he if isinstance(he, list) else ([he] if he else [])
    if not any(str(x).strip() for x in he):
        return _lacune(livre, n)
    RAISONS[(livre, n)] = "v3 sans texte, v1 avec texte"
    return ECHEC


# Trois issues qu'il ne faut surtout pas confondre, et que l'ancien
# ``seifim`` confondait en rendant ``None`` pour les deux dernieres :
LACUNE = "lacune"        # le livre n'a pas ce siman : rien a confronter, c'est normal
ECHEC = "echec"          # la mesure n'a pas abouti : la porte ne doit RIEN conclure
RAISONS: dict[tuple[str, int], str] = {}
# ⚠ UN REF JUSTE AVEC UN he VIDE N'EST PAS A LUI SEUL UNE LACUNE. Sefaria rend ce
# meme triplet pour un siman que l'ouvrage n'a pas ET pour une reponse
# degradee : les blocs du niveau 4 disparaissaient alors, la porte imprimait
# « lacune, normal : 1 » et SORTAIT EN 0. Une lacune n'est donc legitime que
# pour un siman de cette liste, MESUREE le 7 octobre 2026 en interrogeant
# api/texts siman par siman sur tous les simanim du depot qui ont un niveau 4 :
# 63 simanim du Choul'han Aroukh HaRav, et Yoreh De'ah 169. Ailleurs, un he vide
# est une mesure non faite (code 3).
#
# Deux ecarts avec la liste qui circulait (« 170-179 », puis « 170-173, 175-176,
# 208-241 ») : 169 MANQUE au Choul'han Aroukh HaRav (he vide, ref juste) et
# 212-215 y FIGURENT (11, 7, 2 et 5 seifim). Une liste recopiee sans mesure
# aurait fait de 212-215 une lacune « normale » le jour ou Sefaria repondrait mal.
_HARAV = "Shulchan Arukh HaRav, Orach Chayim"
LACUNES_MESUREES = (
    {(_HARAV, n) for n in [*range(132, 155), 157, *range(169, 174), 175, 176,
                           *range(208, 212), *range(216, 242), 304, 322]}
    | {("Shulchan Arukh, Yoreh De'ah", 169)})


def _lacune(livre: str, n: int) -> str:
    """Un he vide sous un ref juste : LACUNE si elle est mesuree, ECHEC sinon."""
    if (livre, n) in LACUNES_MESUREES:
        return LACUNE
    RAISONS[(livre, n)] = "ref juste, he VIDE, hors de la liste des lacunes mesurees"
    return ECHEC
_MEMO_HARAV: dict[int, list[str] | str] = {}


def seifim_harav(livre: str, n: int) -> list[str] | str:
    """Les seifim du Choul'han Aroukh HaRav, ou ``LACUNE`` / ``ECHEC``.

    L'Admour HaZaken n'a pas redige tout Orah Haim — voir LACUNES_MESUREES
    (132-154, 157, 169-173, 175-176, 208-211, 216-241, 304, 322 parmi les
    simanim du depot ; 174 et 177-179 EXISTENT), et la page est alors une
    page-pont sans aucun bloc de seif. Sefaria rend pour ces simanim un ``ref``
    juste, ``error`` nul et un ``he`` VIDE : c'est une lacune de l'ouvrage, pas
    un echec de mesure, et les deux doivent se dire differemment — une porte qui
    rend zero sur un echec reseau est indiscernable d'une porte sans anomalie.

    On passe par ``api/texts`` et non ``api/v3/texts`` parce que la v3 rend un
    404 sur ces simanim-la, ce qui rend la lacune indiscernable d'un ref faux ;
    la v1 rend la lacune explicitement. Et l'on verifie que le ``ref`` servi
    finit par le numero demande : sur un ref mal forme Sefaria rend 200 et le
    livre entier.

    Le resultat n'est mis en cache que s'il n'est PAS vide : un cache qui
    persiste un vide transforme une lacune — ou un incident reseau — en verite
    definitive.
    """
    if n in _MEMO_HARAV:
        return _MEMO_HARAV[n]
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{livre.replace(' ', '_').replace(',', '')}-{n}-v1.json"
    if f.exists():
        out = json.loads(f.read_text(encoding="utf-8"))
        if out:
            _MEMO_HARAV[n] = out
            return out
    u = (f"https://www.sefaria.org/api/texts/"
         f"{urllib.parse.quote(livre.replace(' ', '_'))}.{n}?context=0&pad=0")
    try:
        d = json.load(urllib.request.urlopen(u, timeout=40))
    except Exception as e:
        RAISONS[(livre, n)] = f"api/texts : {type(e).__name__}"
        _MEMO_HARAV[n] = ECHEC
        return ECHEC
    if d.get("error") or not str(d.get("ref", "")).rstrip().endswith(f" {n}"):
        RAISONS[(livre, n)] = f"ref servi {d.get('ref')!r}, error {d.get('error')!r}"
        _MEMO_HARAV[n] = ECHEC          # ref servi != siman demande : on ne conclut pas
        return ECHEC
    he = d.get("he")
    he = he if isinstance(he, list) else ([he] if he else [])
    if not any(str(x).strip() for x in he):
        _MEMO_HARAV[n] = _lacune(livre, n)      # jamais mis en cache
        return _MEMO_HARAV[n]
    out = [lettres_mots(x if isinstance(x, str) else " ".join(map(str, x)))
           for x in he]
    f.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    _MEMO_HARAV[n] = out
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


def blocs(chemin: pathlib.Path) -> list[tuple[str, str, list[int] | None, bool]]:
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
        out.append((texte, titre, numeros(titre), False))

    # Paragraphes dont l'etiquette de seif est inline. On ne leur pose que la
    # question FORTE — « est-ce bien ce seif-la ? » — et jamais la faible
    # — « est-ce quelque part dans le siman ? » : ces paragraphes portent
    # souvent une paraphrase du seif et non son texte, et l'introuvable y serait
    # du bruit. Le decalage, lui, reste decisif : une paraphrase du seif א ne
    # ressemble pas au seif ב.
    vus_inline = set()
    for m in list(RE_BLOC_INLINE.finditer(html)) + list(RE_BLOC_LIGNE.finditer(html)):
        etq = re.sub(r"\s+", " ", RE_TAG.sub(" ", m.group("etq"))).strip(" .:")
        nomme = bool(re.match(r"[Ss][ée]if|סעיף", etq))
        # Sans le mot « סעיף », une etiquette nue doit etre COURTE pour etre un
        # numero : « א. », « י״א ». Trois lettres et plus, c'est un mot ou une
        # sigle — אבל, הב״ח, הב״י — que la guematria lisait 33, 15, 17.
        if not nomme and len(re.findall(r"[א-ת]", etq)) > 2:
            continue
        nums = numeros(etq if nomme else f"סעיף {etq}")
        if not nums:
            continue
        texte = re.sub(r"\s+", " ", RE_TAG.sub(" ", m.group("contenu"))).strip()
        cle = (tuple(nums), texte[:60])
        if cle in vus_inline:
            continue                      # les deux motifs peuvent viser le meme paragraphe
        vus_inline.add(cle)
        out.append((texte, f"[inline] {etq}", nums, True))
    return out


def blocs_harav(chemin: pathlib.Path) -> list[tuple[str, str, list[int] | None, bool]]:
    """Les blocs de seif du niveau 4 : texte du Choul'han Aroukh HaRav + etiquette.

    L'etiquette se lit d'abord dans ``span.seif-num``, et a defaut dans le texte
    du ``<summary>`` : 80 des 9942 blocs mesures n'ont pas ce span et portent leur
    etiquette directement dans le summary. Ces blocs-la sont rendus dans l'ordre
    du document, qui est celui de la source — ce sont des ``<details>`` en serie
    et non les cellules d'un tableau comparatif : la question de l'ordre leur est
    donc posable, contrairement aux colonnes d'un tableau, dont l'ordre est celui
    de l'expose et non celui du livre.
    """
    html = chemin.read_text(encoding="utf-8")
    out = []
    for m in RE_DETAILS.finditer(html):
        inner = m.group("c")
        mn = RE_SEIF_NUM.search(inner)
        if mn:
            brut = RE_TAG.sub(" ", mn.group("e"))
        else:
            ms = RE_SUMMARY.search(inner)
            brut = RE_TAG.sub(" ", ms.group("s")) if ms else ""
        brut = re.sub(r"\s+", " ", brut).strip()
        # Meme lecture que numeros() : vrai numeral, frontiere de mot, et
        # « סעיף אחד / יחיד » rendu UNIQUE. L'ancienne guematrie brute lisait
        # « סעיף אחד » 13 ici aussi.
        if not RE_ETQ_HARAV.search(brut):
            continue                      # pas d'etiquette de seif : hors du perimetre
        nums = _lire_lettres(brut)
        if not nums:
            continue
        textes = [RE_TAG.sub(" ", t) for t in RE_SA_HE.findall(inner)]
        texte = re.sub(r"\s+", " ", " ".join(textes)).strip()
        if not texte:
            continue
        out.append((texte, f"[seif-details] {brut[:40]}", nums, False))
    return out


def numeros(titre: str) -> list[int] | None:
    """Les séifim que le titre revendique. ``None`` : le bloc n'est pas un séif.

    Un titre peut couvrir une plage, et même plusieurs — « séifim 6-8, 16-21,
    23-24 » sur les pages qui regroupent par thème. N'en lire que la première
    fabriquerait un décalage là où la page est explicite.
    """
    if RE_COMMENTATEUR.search(titre):
        return None
    # ⚠ LES TROIS LANGUES N'ECRIVENT PAS L'ETIQUETTE PAREIL, et la forme des pages
    # HEBRAIQUES n'etait lue par aucune des deux branches : elles ecrivent
    # « סעיף 1 — … », le mot hebreu avec un CHIFFRE ARABE. La branche latine exige
    # le mot « Seif », la branche hebraique exige une lettre hebraique : cette
    # forme-la tombait entre les deux, le bloc perdait son etiquette, et la page
    # etait renvoyee a la question faible et a celle de l'ordre — d'ou 36 fichiers
    # « niveau-1-base-he.html » de Yoreh De'ah couverts de « retours en arriere »
    # que leurs jumeaux francais et anglais n'avaient pas. 469 occurrences dans
    # sources/, dans 36 niveau-1-base-he et 2 niveau-3-synthese-he.
    #
    # LE TIRET DE PLAGE N'A PAS D'ESPACES : « סעיפים 1-3 » est une plage, le tiret
    # de « סעיף 1 — חתיכה » est un separateur de titre. On coupe donc au tiret
    # espace avant de lire, sans quoi « סעיף 2 — 3 conditions » annoncerait les
    # seifim 2 ET 3.
    # ⚠ UNE ETIQUETTE COMPOSEE PORTE DEUX ADRESSES, et n'en lire qu'une fabrique
    # un decalage la ou la page est explicite. Mesure faite a la main contre
    # Sefaria sur trois des six signalements nouveaux ouverts : les titres
    # « les proportions des seifim 6 et 7 » (Yoreh De'ah 126) et « (seifim 9 et
    # 12) » (134) etaient lus « seif 6 » et « seif 9 » seuls, parce que le
    # separateur est le MOT « et » et non une virgule ; le bloc portait le second
    # seif, verbatim, et la porte criait au decalage. On accepte donc « et »,
    # « and », « ו » et « & » entre deux numeros.
    SEP = r"(?:\s*(?:,|et|and|&|ו)\s*)"
    for mot in (r"(?:סעיפים|סעיף)", r"[Ss][ée]if(?:im)?"):
        m = re.search(mot + r"\s+([\d\s,–—-]+(?:" + SEP + r"[\d–—-]+)*)", titre)
        if not m:
            continue
        # LE TIRET DE PLAGE N'A PAS D'ESPACES : « סעיפים 1-3 » est une plage, le
        # tiret de « סעיף 1 — חתיכה » est un separateur de titre. On coupe donc
        # au tiret espace avant de lire, sans quoi « סעיף 2 — 3 conditions »
        # annoncerait les seifim 2 ET 3.
        brut = re.split(r"\s+[-–—]\s+", m.group(1).strip())[0]
        out: list[int] = []
        for part in re.split(r"[,\s]+|\bet\b|\band\b|&", brut.strip()):
            # « 7-8-9-10 » : une plage CHAINEE a plus de deux bornes. L'ancien
            # motif n'en voulait que deux, et la chaine entiere etait perdue.
            r = re.fullmatch(r"\d+(?:[–—-]\d+)+", part or "")
            if r:
                b = [int(x) for x in re.split(r"[–—-]", part)]
                if all(y > x for x, y in zip(b, b[1:])):
                    out += list(range(b[0], b[-1] + 1))
            elif part.isdigit():
                out.append(int(part))
        if out:
            return out
    # « Seif א », « סעיף י״א » : le gershayim précède la dernière lettre, il
    # faut donc l'inclure dans la capture, sans quoi tout séif ≥ 11 est lu 10.
    #
    # ⚠ ET UNE PLAGE S'ECRIT AUSSI EN LETTRES. « (סעיף ט-טו) », au niveau 4 du
    # siman 190 de Yoreh De'ah, annonce les séifim 9 A 15 ; n'en lire que la
    # première borne faisait crier au décalage sur un bloc qui porte le séif 11,
    # c'est-à-dire DANS la plage annoncée. Le tiret sans espaces, là encore, est
    # ce qui distingue la plage du séparateur de titre.
    #
    # ⚠ LA GUEMATRIE DU NUMERAL DE BASE. Le garde-fou de _suite_he ne couvrait que
    # la SUITE ; le premier jeton, lui, etait lu en guematrie quel qu'il fut, sur
    # ses trois premieres lettres et sans frontiere de mot : « סעיף אחד » valait
    # 13, « סעיף יחיד » [28, 4], « הסעיף היחיד » 23, « הסעיף המדבר … (סעיף י״ג) »
    # 49 (« המד » !), un « מי » inline 50. Mesure sur les 7 695 pages : 101 blocs
    # qui DECLARAIENT leur seif perdaient ainsi leur etiquette au rabotage hors
    # bornes, et retombaient en silence dans la question faible. On exige donc
    # un VRAI numeral (voir _numeral) suivi d'une frontiere de mot, on essaie
    # chaque occurrence de « סעיף » et non la premiere seule, et « אחד / יחיד »
    # devient UNIQUE, que examiner() lit 1 si le siman n'a qu'un seif.
    #
    # ⚠ LA PLAGE CHAINEE. « (סעיפים ז-ח-ט-י) » etait lue [7, 8] : le motif ne
    # prenait que deux bornes, et la suite « -ט-י » n'etait pas un jeton de
    # _suite_he. Au siman 8 d'Orah Haim, le meme bloc (recouvrement 43 %)
    # basculait d'un seuil a l'autre selon la langue : signale en FR et EN,
    # silencieux en HE. On lit la chaine en entier.
    return _lire_lettres(titre)


def _lire_lettres(titre: str) -> list[int]:
    """Les seifim ecrits en LETTRES apres « Seif » ou « סעיף » (voir numeros)."""
    for mot in (r"[Ss][ée]if(?:im)?", r"(?:סעיפים|סעיף)"):
        for m in re.finditer(mot + r"\s+", titre):
            reste = titre[m.end():]
            if mot.startswith("(") and re.match(r"ה?(?:אחד|יחיד)(?![א-ת])", reste):
                return [UNIQUE]
            c = RE_CHAINE_HE.match(reste)
            if not c:
                continue
            bornes = [_numeral(x) for x in re.split(r"[-־–—]", c.group(0))]
            if not all(bornes):
                continue
            if any(b <= a for a, b in zip(bornes, bornes[1:])):
                bornes = bornes[:1]       # chaine non croissante : un seul numero sur
            out = list(range(bornes[0], bornes[-1] + 1))
            return out + _suite_he(reste[c.end():])
    return []


# Un vrai numeral hebraique : 1 ou 2 lettres, ou un geresh/gershayim ; une lettre
# par ordre de grandeur, de la plus grande a la plus petite (כ״ג, jamais גכ ni
# מי) ; 15 et 16 s'ecrivent ט״ו / ט״ז, jamais י״ה / י״ו. « אחד » (1, 8, 4) et
# « מי » (40, 10) n'en sont pas.
RE_CHAINE_HE = re.compile(rf"{NUM_HE}(?:[-־–—]{NUM_HE})*(?![א-ת])")
UNIQUE = 0          # « סעיף אחד / יחיד » : le seif 1 SI le siman n'en a qu'un


def _numeral(j: str) -> int | None:
    lettres_ = re.sub(r"[׳״\"']", "", j)
    if not lettres_ or not all(c in VALEURS for c in lettres_):
        return None
    if len(lettres_) > 2 and not re.search(r"[׳״\"']", j):
        return None
    vals = [VALEURS[c] for c in lettres_]
    if lettres_ in ("טו", "טז"):
        return sum(vals)
    if lettres_ in ("יה", "יו"):
        return None
    # Une lettre par ORDRE DE GRANDEUR, dans l'ordre decroissant : « מי » (40 et
    # 10, deux dizaines) n'est pas 50, qui s'ecrit נ.
    ordres = [len(str(v)) for v in vals]
    if any(b >= a for a, b in zip(ordres, ordres[1:])):
        return None
    return sum(vals)


# ⚠ ET LA MEME CLAUSE DANS LA PAGE HEBRAIQUE. J'ai d'abord ferme la classe des
# etiquettes composees dans les pages francaises et anglaises — « seifim 6 et 7 »
# — et laisse ouvertes leurs jumelles hebraiques, « סעיפים ו׳ וז׳ » (Yoreh De'ah
# 126) et « (סעיפים ט׳ ו־י״ב) » (134), ou la conjonction est COLLEE au numero ou
# suivie d'un MAQAF. C'est mot pour mot la faute que ce depot documente : une
# clause ne couvre le lecteur que dans la page qu'il a sous les yeux.
#
# Le garde-fou qui compte ici est le GUEMATRIQUE : tout mot hebreu court est un
# nombre si on le lit en guematrie. Le PREMIER numero reste lu comme avant — il
# suit immediatement le mot « סעיף », ce qui le qualifie — mais un jeton de SUITE
# n'est accepte que s'il porte un geresh ou un gershayim, ou s'il est d'une seule
# lettre ; et l'on s'arrete au premier jeton qui n'en est pas un, sans quoi la
# suite du titre serait lue comme des numeros de seif.
def _suite_he(txt: str) -> list[int]:
    out: list[int] = []
    for jeton in re.split(r"[\s,]+", (txt or "").strip()):
        j = jeton.strip("()[].:·—–")
        if not j:
            continue        # un separateur en tete ne termine pas la liste
        j = re.sub(r"^ו[־–—-]?(?=[א-ת])", "", j)      # « וז׳ », « ו־י״ב »
        if re.fullmatch(rf"{NUM_HE}(?:[-־–—]{NUM_HE})+", j):
            b = [_num_he(x) for x in re.split(r"[-־–—]", j)]
            if all(b) and all(y > x for x, y in zip(b, b[1:])):
                out += list(range(b[0], b[-1] + 1))
                continue
            break
        g = _num_he(j)
        if g is None:
            break
        out.append(g)
    return out


def _num_he(j: str) -> int | None:
    """La guematrie d'un jeton, mais seulement s'il se DONNE pour un numeral."""
    if not j or not re.fullmatch(NUM_HE, j):
        return None
    if re.search(r"[׳״']", j) or len(re.findall(r"[א-ת]", j)) == 1:
        return _numeral(j)
    return None


def examiner(chemin: pathlib.Path, livre: str, n: int,
             inline_seul: bool = False, role: str = "entier"):
    """Rend ``(blocs confrontés, étiquettes lues, écarts d'étiquette,
    écarts d'ordre, statut)``.

    ``statut`` vaut ``None`` quand la source a répondu, ``LACUNE`` quand le livre
    n'a pas ce siman, ``ECHEC`` quand la mesure n'a pas abouti. Les trois se
    disaient auparavant de la même manière — un zéro muet — et un zéro muet sur
    un échec réseau est indiscernable d'une page sans anomalie.
    """
    if role == "harav":
        src = seifim_harav(livre, n)
        if src == LACUNE:
            # Une lacune legitime se dit en page-pont, sans AUCUN bloc de seif :
            # un bloc qui y revendique un seif cite un texte que l'ouvrage n'a pas.
            lot = blocs_harav(chemin)
            return 0, 0, [f"bloc {i} : annoncé séif {'-'.join(map(str, a))} du "
                          f"Choul'han Aroukh HaRav, qui n'a pas de siman {n} — "
                          f"« {t[:60]} »" for i, (_, t, a, _) in enumerate(lot, 1)
                          ], [], src
        if isinstance(src, str):
            return 0, 0, [], [], src
        lot = blocs_harav(chemin)
    else:
        src = seifim(livre, n)
        if isinstance(src, str):
            return 0, 0, [], [], src
        lot = blocs(chemin)
    sq = [squelette(s) for s in src]
    ecarts, ordre, vus, etq, dernier = [], [], 0, 0, 0
    for i, (b, titre, annonces, inline) in enumerate(lot, 1):
        if annonces is None:
            continue          # bloc placé sous un titre de commentateur
        if inline_seul and not inline:
            continue          # sur ces pages, seule l'étiquette inline fait foi
        # ⚠ MESURÉ AVANT DE CONCLURE, et c'est la réserve de ce contrôle. Le
        # niveau 4 de Yoreh De'ah est une page de psak RANGÉE PAR THÈME : ses
        # blocs source vivent sous des titres thématiques, l'ordre y est celui de
        # l'exposé et non celui du livre, et un même bloc peut condenser ou citer
        # l'appareil. Lui poser la question faible (« est-ce quelque part dans le
        # siman ? ») et celle de l'ordre rendait 83 signalements pour 148 simanim,
        # dont 57 « retours en arrière » qui ne sont pas des défauts mais la forme
        # même de la page. On s'y borne donc à la seule question qui s'y pose :
        # LE BLOC ANNONCÉ SÉIF N EST-IL LE SÉIF N ?
        if role == "etiquette" and not annonces:
            continue
        # Ces filtres de CONTENU existent pour distinguer un séif d'un commentaire
        # là où le balisage ne le dit pas. Au niveau 4, il le dit : un
        # « p.sa-he » à l'intérieur d'un « details.seif-details » EST le texte du
        # séif, par construction. Les y appliquer ne faisait donc que perdre des
        # blocs, et sur un faux motif — la guematria. Mesuré sur les 9939 blocs
        # des trois langues : 51 écartés, et les 51 à tort, tous sur « ט״ז » (16)
        # ou « מ״ב » (42) lus comme le Taz et la Michna Beroura alors qu'ils sont
        # un compte de séifim (« ובו ט״ז סעיפים »), une mesure (« ט״ז אמה »), un
        # daf (« דף ט״ז ע״א »), un verset (« קדושים י״ט, ט״ז ») ou un numéro de
        # siman (« בסימן רמ״ב »). Aucun n'était un commentateur.
        nu = re.sub(r"^[\s\"'«»]+", "", lettres_mots(b))
        if role != "harav" and (COMMENTAIRE.search(b) or TALMUD.match(nu)
                                or MASSEKHET.search(b)
                                or SUGYA.search(lettres_mots(b))):
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
        # « סעיף אחד / יחיד » n'est le seif 1 que d'un siman qui n'en a qu'un ;
        # ailleurs c'est « un seif », et le bloc n'a pas d'etiquette.
        if UNIQUE in annonces:
            annonces = ([1] if len(src) == 1
                        else [k for k in annonces if k != UNIQUE])
        hors = [k for k in annonces if not 1 <= k <= len(src)]
        annonces = [k for k in annonces if 1 <= k <= len(src)]
        if inline and not annonces:
            continue          # etiquette inline hors du siman : ce n'est pas un seif
        # Un bloc qui DECLARE un seif que le siman n'a pas — et rien d'autre —
        # retombait en silence dans la question faible. C'est la deuxieme
        # question du contrat de cette porte (« le bloc annonce existe-t-il
        # seulement dans ce siman ? ») ; elle n'etait posee nulle part.
        if hors and not annonces:
            etq += 1
            ecarts.append(
                f"bloc {i} : annoncé séif {'-'.join(map(str, hors))}, mais le siman "
                f"{n} n'a que {len(src)} séif(s) — « {titre[:60]} »")
            continue
        if annonces:
            etq += 1
            # Vérification forte : le bloc est-il le séif qu'il annonce ?
            attendu = max(scores[k - 1][0] for k in annonces)
            if (place not in annonces and meilleur >= DECALAGE_MIN
                    and meilleur - attendu >= DECALAGE_ECART):
                ecarts.append(
                    f"bloc {i} : annoncé séif {'-'.join(map(str, annonces))}, "
                    f"mais correspond au séif {place} ({meilleur:.0%} contre "
                    f"{attendu:.0%}) — « {titre[:60]} »")
            elif meilleur < INTROUVABLE_ANNONCE and not inline:
                ecarts.append(
                    f"bloc {i} : annoncé séif {'-'.join(map(str, annonces))}, "
                    f"introuvable dans le siman {n} (meilleur recouvrement "
                    f"{meilleur:.0%}, au séif {place}) — « {titre[:60]} »")
            # Les blocs « seif-details » du niveau 4 sont des <details> EN SERIE
            # qui portent le texte source : leur ordre est celui du livre, et la
            # question de l'ordre leur est donc posable. Celui des cellules d'un
            # tableau comparatif ne l'est pas — c'est l'ordre de l'expose — et
            # c'est pourquoi aucune cellule de tableau n'entre ici.
            if role == "harav":
                if min(annonces) < dernier:
                    ordre.append(
                        f"bloc {i} : séif {min(annonces)}, après le séif "
                        f"{dernier} — retour en arrière — « {titre[:60]} »")
                dernier = max(annonces)
            continue          # l'ordre est déjà dit par le titre : rien à déduire
        if meilleur < SEUIL:
            ecarts.append(f"bloc {i} : introuvable dans le siman {n} "
                          f"(meilleur recouvrement {meilleur:.0%} au séif {place})")
        else:
            if place < dernier:
                ordre.append(f"bloc {i} : séif {place}, après le séif "
                             f"{dernier} — retour en arrière")
            dernier = place
    return vus, etq, ecarts, ordre, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--siman", type=int)
    ap.add_argument("--section")
    args = ap.parse_args()

    # Le niveau 1 porte le texte du seif : on l'examine entierement.
    # Les autres pages le citent par fragments, sous une etiquette inline —
    # « סעיף א. », « א. » —, et le reste y est du commentaire : on ne leur pose
    # donc QUE la question forte, sur ces etiquettes. Sans cela le siman 243,
    # dont le mauvais decoupage vivait dans l'index et le niveau 2, n'etait
    # meme pas regarde.
    # ⚠ CETTE LISTE EXCLUAIT PRECISEMENT LA OU LE DEFAUT VIT. Elle ne portait que
    # « niveau-1-base.html », « index.html », « niveau-2-lamdan.html » et
    # « niveau-3-synthese.html » : ni le niveau 4, ni AUCUNE variante -he / -en.
    # Mesure faite avant d'y toucher : 2052 pages lues sur les 7695 pages de
    # siman du depot, soit 5643 ignorees — les 1539 pages de niveau 4 et les
    # 4104 variantes hebreu et anglaise des quatre autres radicaux. Or la porte
    # est nee du siman 243, et sept des dix cellules fausses etablies depuis sont
    # des decalages de seif ou des attributions croisees du NIVEAU 4, dans les
    # trois langues.
    #
    # ⚠ DEUX RADICAUX DE NIVEAU 4, et un glob sur un seul rate un compartiment
    # entier en silence : « niveau-4-daat-harav » pour Orah Haim et Hilkhot
    # Chabbat, « niveau-4-halakha » pour Yoreh De'ah.
    #
    # Le niveau 1 porte le texte du seif : on l'examine entierement.
    # Les autres pages le citent par fragments, sous une etiquette inline —
    # « סעיף א. », « א. » —, et le reste y est du commentaire : on ne leur pose
    # donc QUE la question forte, sur ces etiquettes. Sans cela le siman 243,
    # dont le mauvais decoupage vivait dans l'index et le niveau 2, n'etait
    # meme pas regarde.
    LANGUES = ("", "-he", "-en")
    ENTIER = tuple(f"niveau-1-base{s}.html" for s in LANGUES)
    # Le niveau 4 de Yoreh De'ah porte ses blocs source sous des titres
    # THEMATIQUES, dont la plupart ne nomment aucun seif : la question faible
    # (« est-ce quelque part dans le siman ? ») y produit du bruit, la question
    # forte s'y pose quand le titre nomme un seif. Il va donc avec les pages
    # ou seule l'etiquette fait foi — mais ses etiquettes sont portees par les
    # titres de bloc et non par des paragraphes inline, d'ou ENTIER_ETQ.
    INLINE = tuple(f"{t}{s}.html" for t in
                   ("index", "niveau-2-lamdan", "niveau-3-synthese")
                   for s in LANGUES)
    ENTIER_ETQ = tuple(f"niveau-4-halakha{s}.html" for s in LANGUES)
    # Niveau 4 d'Orah Haim et de Chabbat : son texte source n'est dans aucune des
    # classes de RE_BLOC et n'est PAS le Choul'han Aroukh — c'est le Choul'han
    # Aroukh HaRav. Voir blocs_harav / seifim_harav.
    HARAV = tuple(f"niveau-4-daat-harav{s}.html" for s in LANGUES)

    fichiers = []
    for role, noms in (("entier", ENTIER), ("inline", INLINE),
                       ("etiquette", ENTIER_ETQ), ("harav", HARAV)):
        for nom in noms:
            fichiers += [(f, role) for f in sorted(RACINE.rglob(nom))]
    if args.section:
        fichiers = [(f, r) for f, r in fichiers if f.parent.parent.name == args.section]
    if args.siman:
        fichiers = [(f, r) for f, r in fichiers if f.parent.name == f"siman-{args.siman}"]
    fichiers.sort(key=lambda x: (str(x[0]), x[1]))

    total_blocs = total_etq = pages = 0
    ecarts_etq = ecarts_ordre = 0
    lus = 0
    lacunes: set[tuple[str, int]] = set()
    echecs: set[tuple[str, int]] = set()
    for f, role in fichiers:
        section = f.parent.parent.name
        livre = (LIVRES_HARAV if role == "harav" else LIVRES).get(section)
        m = re.fullmatch(r"siman-(\d+)", f.parent.name)
        if not livre or not m:
            continue
        n = int(m.group(1))
        lus += 1
        vus, etq, ece, eco, statut = examiner(
            f, livre, n, inline_seul=(role == "inline"), role=role)
        if statut == LACUNE:
            lacunes.add((livre, n))
        elif statut == ECHEC:
            echecs.add((livre, n))
        total_blocs += vus
        total_etq += etq
        if ece or eco:
            pages += 1
            ecarts_etq += len(ece)
            ecarts_ordre += len(eco)
            print(f"⚠ {f.relative_to(RACINE)}")
            for e in ece + eco:
                print(f"     {e}")

    # ⚠ UNE PORTE QUI NE COMPARE RIEN ET SORT VERTE EST PIRE QU'UNE PORTE ABSENTE.
    # Ces quatre comptes sont imprimes expres, et le dernier distingue la lacune
    # d'ouvrage — l'Admour HaZaken n'a pas redige ce siman — de l'echec de mesure.
    print(f"\nFichiers lus ................. {lus}")
    print(f"Blocs confrontés à la source . {total_blocs}")
    print(f"Étiquettes de séif lues ...... {total_etq}")
    print(f"Anomalies d'étiquette ........ {ecarts_etq}")
    print(f"Anomalies d'ordre ............ {ecarts_ordre}")
    print(f"→ {ecarts_etq + ecarts_ordre} écart(s) d'alignement dans {pages} page(s)")
    if lacunes:
        print(f"Simanim sans texte dans l'ouvrage (lacune, normal) : {len(lacunes)}")
    if echecs:
        print(f"⚠ Simanim NON ATTEINTS (la mesure n'a pas abouti) : {len(echecs)}")
        for livre, n in sorted(echecs)[:20]:
            print(f"     {livre} {n} — {RAISONS.get((livre, n), '?')}")
    if not total_blocs:
        print("⚠ RIEN N'A ÉTÉ CONFRONTÉ — la porte ne conclut pas.")
        return 3
    if echecs:
        return 3
    return 1 if (ecarts_etq or ecarts_ordre) else 0


if __name__ == "__main__":
    raise SystemExit(main())
