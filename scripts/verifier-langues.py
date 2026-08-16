#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chaque page est-elle écrite dans la langue qu'elle annonce ?

Le site tient trois versions de chaque page — ``X.html`` en français,
``X-he.html`` en hébreu, ``X-en.html`` en anglais — et rien, jusqu'ici, ne
vérifiait que le corps d'une page correspondait à son suffixe. Une page pouvait
donc porter ``lang="en"``, servir l'URL ``/oh/304/base/en``, et afficher un
corps entièrement français : c'est ce qui se passait sur sept pages, dont quatre
complètes (simanim 304 et 322, niveaux 1 et 3). Aucun autre contrôle ne pouvait
le voir — ``audit-simanim`` juge la structure, ``verifier-citations`` les
citations hébraïques, ``verifier-traductions`` la longueur des traductions par
rapport à leur source ; tous trois passent au vert sur une page entière restée
dans la mauvaise langue.

Méthode
-------
On retire l'entête, les scripts et les styles, on supprime le balisage, puis on
compte des mots-témoins **sans ambiguïté** : les listes excluent tout ce qui
peut apparaître dans une translittération (``l'akum``, ``d'oraisa``, ``bal
techaktzou``) ou dans les deux langues à la fois. Le verdict ne porte pas sur un
seuil absolu — une page anglaise cite légitimement du français, et l'inverse —
mais sur la **domination** d'une langue étrangère à la page, ce qui ne se
produit pas par accident.

Pour l'hébreu, le test est plus simple et plus sûr : une page ``-he`` dont le
corps compte plus de lettres latines que de lettres hébraïques n'est pas une
page hébraïque.

Deux échelles, parce que le défaut se présente sous deux formes
---------------------------------------------------------------
La **page entière** restée dans l'autre langue se voit à la domination. Mais le
défaut existe aussi en **bloc localisé** : dans les simanim 2, 3 et 4 de
``oh-quotidien``, cinq à six paragraphes de séifim étaient restés français au
milieu d'une page anglaise par ailleurs complète — la domination ne les voyait
pas, la page étant très majoritairement anglaise. On ajoute donc un second
test, ligne à ligne : un bloc qui compte au moins ``BLOC_MINIMUM`` mots-témoins
de la langue étrangère et **aucun** de la langue attendue est un bloc non
traduit. Le seuil est calibré sur la distribution réelle du site : à 4, les
5 037 pages saines n'en produisent aucun.

    python3 scripts/verifier-langues.py [--path sources] [--lignes]

``--lignes`` liste, pour chaque page fautive, les lignes concernées : c'est la
liste de travail du traducteur. Sortie non nulle s'il reste une page dans la
mauvaise langue — utilisable comme gate.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent

# Zones à neutraliser avant tout comptage : scripts (les dictionnaires i18n
# portent les trois langues dans *chaque* page), styles, et commentaires HTML
# (« <!-- BANDEAU DE DÉDICACE… --> » est français dans les 5 037 pages, sans
# qu'aucune ne soit fautive). On préserve les sauts de ligne pour que les
# numéros de ligne restent ceux du fichier.
RE_TETE = re.compile(r"<(script|style)[^>]*>.*?</\1>|<!--.*?-->", re.S | re.I)
RE_BALISE = re.compile(r"<[^>]+>", re.S)
# Le titre d'un article extérieur reste dans sa langue : « ← Chabad.org — The
# Shabbos Candle Lighting Campaign » n'est pas un bloc non traduit. On retire
# donc le texte des liens sortants avant de compter.
RE_LIEN_EXTERNE = re.compile(r"<a\b[^>]*href=\"https?://[^\"]+\"[^>]*>.*?</a>", re.S | re.I)

# Mots-témoins choisis pour ne jamais apparaître dans l'autre langue ni dans une
# translittération hébraïque. « on », « la », « son », « pas », « est » en sont
# écartés pour cette raison — « on » est anglais, « la » ouvre « la-akum ».
FR = re.compile(r"\b(?:qui|pour|dans|avec|sont|cette|aussi|alors|chaque|plusieurs"
                r"|lorsque|toujours|jamais|ainsi|donc|selon|entre|quand|très|peut"
                r"|doit|faut|était|seront|leurs|cela|sans|sous|après|avant|depuis"
                r"|pendant|même|autre|celui|celle|toutes|notre|votre|nous|vous"
                r"|elles|entre|entrée|règles|siman s|séif|seifim du|voir le)\b", re.I)
EN = re.compile(r"\b(?:the|and|are|for|with|that|this|from|which|when|they|their"
                r"|would|should|must|have|been|were|there|only|even|before|after"
                r"|without|between|according|therefore|whether|about|each|such)\b", re.I)
HE = re.compile(r"[א-ת]")
LAT = re.compile(r"[A-Za-zÀ-ÿ]")

# Seuil de déclenchement : en dessous, la page est trop courte ou trop technique
# pour qu'un comptage veuille dire quelque chose.
MINIMUM = 20
# Un bloc isolé non traduit : au moins autant de mots-témoins étrangers, et
# aucun mot-témoin de la langue attendue. Calibré pour ne rien sortir sur le
# site sain.
BLOC_MINIMUM = 3
# Idem pour une page hébraïque : nombre de lettres latines d'affilée sur une
# ligne au-delà duquel il ne s'agit plus d'un terme translittéré.
BLOC_LATIN = 40


def _blanc(m) -> str:
    """Remplace une zone par ses seuls sauts de ligne (numérotation préservée)."""
    return "\n" * m.group(0).count("\n")


def _neutraliser(html: str) -> str:
    """Retire scripts, styles, commentaires et liens sortants — en gardant les
    sauts de ligne, pour que la numérotation reste celle du fichier."""
    return RE_LIEN_EXTERNE.sub(_blanc, RE_TETE.sub(_blanc, html))


def _sans_balises(html: str) -> tuple[list[str], int]:
    """Lignes du document sans balises, et l'indice de la première du corps.

    Le retrait des balises doit se faire **avant** la découpe en lignes : une
    balise qui s'étend sur plusieurs lignes — c'est le cas du champ de recherche
    des pages d'index — laisserait sinon ses attributs
    (``data-i18n-placeholder="…"``) dans le texte, et un attribut latin
    passerait pour un bloc non traduit.

    Mais ce retrait efface aussi ``</head>``, et la frontière du corps devient
    introuvable *après* coup : le contrôle repartait alors de la ligne 1 et
    lisait l'entête. On calcule donc la frontière sur le texte **avant**
    suppression des balises, et on la rend avec les lignes.
    """
    neutre = _neutraliser(html)
    lignes_brutes = neutre.split("\n")
    debut = next((i for i, l in enumerate(lignes_brutes) if "</head>" in l), 0)
    return RE_BALISE.sub(_blanc, neutre).split("\n"), debut


def corps(chemin: pathlib.Path) -> str:
    html = _neutraliser(chemin.read_text(encoding="utf-8"))
    html = html.split("</head>", 1)[-1]
    return RE_BALISE.sub(" ", html)


def langue_attendue(chemin: pathlib.Path) -> str:
    nom = chemin.stem
    if nom.endswith("-he"):
        return "he"
    if nom.endswith("-en"):
        return "en"
    return "fr"


def examiner(chemin: pathlib.Path) -> tuple[str, str] | None:
    """Renvoie (attendue, dominante) si la page est dans la mauvaise langue."""
    attendue = langue_attendue(chemin)
    txt = corps(chemin)
    if attendue == "he":
        he, lat = len(HE.findall(txt)), len(LAT.findall(txt))
        if he + lat > 500 and lat > he:
            return ("he", "latin")
        return None
    fr, en = len(FR.findall(txt)), len(EN.findall(txt))
    if attendue == "en" and fr >= MINIMUM and fr > en:
        return ("en", "fr")
    if attendue == "fr" and en >= MINIMUM and en > fr:
        return ("fr", "en")
    return None


def lignes_fautives(chemin: pathlib.Path, intruse: str, seuil: int = 2) -> list[tuple[int, str]]:
    """Lignes où la langue étrangère domine — la liste de travail du traducteur."""
    etrangere, attendue = (FR, EN) if intruse == "fr" else (EN, FR)
    out = []
    # Les dictionnaires i18n (``const I18N = { fr: …, en: …, he: … }``) portent
    # les trois langues dans **chaque** page : les compter donnerait un faux
    # positif sur tous les index. On neutralise donc scripts et styles avant le
    # balayage, en préservant la numérotation des lignes.
    lignes, debut = _sans_balises(chemin.read_text(encoding="utf-8"))
    for i, nu in enumerate(lignes[debut:], debut + 1):
        if len(etrangere.findall(nu)) >= seuil and not attendue.search(nu):
            out.append((i, re.sub(r"\s+", " ", nu).strip()[:150]))
    return out


def blocs_latins(chemin: pathlib.Path) -> list[tuple[int, str]]:
    """Blocs restés en caractères latins dans une page hébraïque.

    Le seuil (``BLOC_LATIN`` lettres latines, et plus du triple des lettres
    hébraïques de la même ligne) laisse passer les termes translittérés glissés
    dans une phrase hébraïque, et ne retient que les paragraphes entiers restés
    en français.
    """
    out = []
    lignes, debut = _sans_balises(chemin.read_text(encoding="utf-8"))
    for i, nu in enumerate(lignes[debut:], debut + 1):
        lat, he = len(LAT.findall(nu)), len(HE.findall(nu))
        if lat >= BLOC_LATIN and lat > 3 * he:
            out.append((i, re.sub(r"\s+", " ", nu).strip()[:150]))
    return out


def blocs_non_traduits(chemin: pathlib.Path) -> list[tuple[int, str]]:
    """Blocs isolés restés dans l'autre langue, sur une page par ailleurs bonne."""
    attendue = langue_attendue(chemin)
    if attendue == "he":
        return blocs_latins(chemin)
    intruse = "fr" if attendue == "en" else "en"
    return lignes_fautives(chemin, intruse, seuil=BLOC_MINIMUM)


def relatif(p: pathlib.Path) -> str:
    try:
        return str(p.relative_to(RACINE))
    except ValueError:
        return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--path", default="sources", help="répertoire à parcourir")
    ap.add_argument("--lignes", action="store_true",
                    help="lister les lignes concernées de chaque page fautive")
    args = ap.parse_args()

    base = (RACINE / args.path) if not pathlib.Path(args.path).is_absolute() else pathlib.Path(args.path)
    pages = sorted(base.rglob("*.html"))
    fautives, partielles = [], []
    for p in pages:
        verdict = examiner(p)
        if verdict:
            fautives.append((p, *verdict))
            continue
        blocs = blocs_non_traduits(p)
        if blocs:
            partielles.append((p, blocs))

    for p, attendue, intruse in fautives:
        print(f"⚠ {relatif(p)} — page annoncée « {attendue} », corps « {intruse} »")
        if args.lignes and intruse in ("fr", "en"):
            for n, txt in lignes_fautives(p, intruse):
                print(f"     {n}: {txt}")

    for p, blocs in partielles:
        print(f"⚠ {relatif(p)} — {len(blocs)} bloc(s) non traduit(s)")
        if args.lignes:
            for n, txt in blocs:
                print(f"     {n}: {txt}")

    print(f"\n{len(pages)} page(s) examinée(s) dans {relatif(base)}")
    print(f"→ {len(fautives)} page(s) entièrement dans la mauvaise langue")
    print(f"→ {len(partielles)} page(s) avec des blocs non traduits")
    return 1 if (fautives or partielles) else 0


if __name__ == "__main__":
    raise SystemExit(main())
