# -*- coding: utf-8 -*-
"""Extraction des fragments présentés comme des **citations littérales** (§8).

Ce module porte la convention typographique du dépôt, sans laquelle la
vérification des citations n'a aucun sens :

> Les guillemets sont réservés au texte **littéral**. Une condensation d'un
> séif est annoncée par ``<em>résumé</em> :`` (``תמצית`` / ``summary``) et
> n'est pas jugée.

C'est cette règle qui rend un verdict possible. Avant elle, chaque cellule de
tableau portait des guillemets qu'elle citât ou qu'elle paraphrasât, et une
citation fabriquée ressemblait exactement à ses quarante voisines légitimes.
Voir ``CLAUDE.md`` et ``scripts/README.md`` à la racine du dépôt.

Chaque détail de l'extraction vient d'un faux positif constaté sur le site :

- **appariement séquentiel** des guillemets droits — un appariement par
  expression régulière avec longueur minimale saute les paires trop courtes et
  décale toutes les suivantes, si bien que la « citation » extraite devient la
  prose *située entre* deux citations ;
- **ligne par ligne** — un guillemet non apparié ailleurs dans le bloc ne doit
  pas décaler l'appariement de tout ce qui suit ;
- **le JSON-LD est écarté** — son champ ``description`` cite souvent un
  fragment, mais c'est une métadonnée SEO, pas du contenu affiché ;
- **un marqueur d'annonce est exigé** hors bloc cité — sans ``וז״ל``, ``תנן``,
  ``שנאמר`` ou une référence collée juste avant, des guillemets encadrent tout
  aussi bien une formule de l'auteur qu'une citation.
"""
from __future__ import annotations

import html as html_lib
import re
from dataclasses import dataclass

# En deçà, un fragment est trop court pour conclure quoi que ce soit.
MIN_LETTRES = 12
# Une vraie citation est une phrase. En deçà, on a affaire à un terme technique
# mis entre guillemets (« תשמישי קדושה »), que rien n'oblige à figurer mot pour
# mot dans la source voisine.
MIN_CITATION = 25

LATIN = re.compile(r"[A-Za-zÀ-ÿ]")
HEBREW = re.compile(r"[א-ת]")

# Condensation assumée : annoncée, donc pas jugée.
RESUME = re.compile(r"<em>\s*(?:résumé|תמצית|summary)\s*</em>\s*:?\s*$", re.I)

# Marqueurs présentant explicitement ce qui suit comme une citation.
CUE = re.compile(
    "גמ[׳']|תנן|תניא|תנו רבנן|ת[״\"]ר|דתניא|דתנן|איתא|ברייתא|במשנה|משנת|"
    "וז[״\"]ל|וזה לשון|לשון ה|כלשון|שנאמר|כתיב|דכתיב|אמרו|ואמר|אמר ר|"
    "מקור|לשון המחבר|לשון הרמ|ע[״\"]פ|כדאיתא|וכלשון|הגמרא|הסוגיא|"
    r"[א-ת][״\"][א-ת]\s*[:.]\s*$|\d\s*[:.]\s*$|[.:]\s*$"
)

RE_GUILL = re.compile(r"«([^«»]{5,900})»|„([^„”]{5,900})”")
RE_PREFIX = re.compile(r'^[^"«„]{0,90}?[:—–-]\s*(?=["«„])')
SCRIPT_LD = re.compile(r"<script[^>]+application/ld\+json[^>]*>.*?</script>", re.S | re.I)
# Toutes les balises SAUF <em> : le marqueur de convention doit survivre à
# l'aplatissement, sans quoi ``RESUME`` ne pourrait plus rien reconnaître et
# toute condensation annoncée serait jugée comme une citation littérale.
RE_TAG_SAUF_EM = re.compile(r"<(?!/?em\b)[^>]+>")
RE_EM_RESUME = re.compile(r"<em[^>]*>\s*(résumé|תמצית|summary)\s*</em>", re.I)
RE_EM_TAG = re.compile(r"</?em[^>]*>")


@dataclass
class Quote:
    """Un fragment présenté comme littéral, avec son contexte."""

    text: str
    line: int
    context: str


def n_letters(text: str) -> int:
    return len(HEBREW.findall(text))


def straight_pairs(text: str) -> list[str]:
    """Contenus entre guillemets droits, appariés **séquentiellement**."""
    positions = [m.start() for m in re.finditer(r'"', text)]
    return [
        text[a + 1: b]
        for a, b in zip(positions[0::2], positions[1::2])
        if 0 < b - a - 1 <= 900
    ]


def flatten_html(fragment: str) -> str:
    """Texte visible, en **conservant** le marqueur ``<em>résumé</em>``."""
    normalise = RE_EM_RESUME.sub(lambda m: f"<em>{m.group(1)}</em>", fragment)
    return html_lib.unescape(RE_TAG_SAUF_EM.sub(" ", normalise))


def is_hebrew_quote(fragment: str) -> bool:
    """Écarte la prose française : une citation doit être majoritairement hébraïque."""
    hebreu, latin = n_letters(fragment), len(LATIN.findall(fragment))
    return hebreu >= MIN_LETTRES and hebreu >= 2 * latin


def has_cue(before: str) -> bool:
    """Le contexte immédiat annonce-t-il une citation ?

    Le guillemet ouvrant est retiré avant l'examen : il se glisse en fin de
    contexte et masque le deux-points qui, lui, annonce la citation —
    « רש״י (שמות כ ח): " … » n'était pas reconnu pour ce seul motif.
    """
    return bool(CUE.search(before.rstrip(" \t\"«„'").rstrip()[-90:]))


# Un jeton à gershayim est une abréviation d'ouvrage (שו״ע, ט״ז, מג״א), pas un
# mot de texte cité.
_ABREV = re.compile(r"[א-ת]{1,4}[\"״][א-ת]")
_MOT = re.compile(r"[א-ת]+")

# Intertitre rédactionnel du site : un mot d'appareil (« חידוש », « יסוד »,
# « עיקרון »…), sa lettre d'ordre, puis un tiret et l'énoncé. C'est l'auteur
# qui numérote son propre exposé — « חידוש ד — הבחנה בין כלים, בהמה, ושדה
# (246:6-7) ». Comparé à une source, un tel titre en est évidemment absent :
# sept des soixante-huit faux positifs relus par le Rav n'étaient que cela.
#
# Le motif est volontairement étroit : le mot d'appareil, UNE lettre d'ordre
# isolée, et le tiret. « חידוש גדול בדברי הרמב״ם » — une vraie phrase — ne
# correspond pas, la lettre y étant suivie d'autres mots hébreux.
TITRE_REDACTIONNEL = re.compile(
    r"^(?:חידוש|יסוד|עיקרון|כלל|שלב|נקודה|מבנה|הבחנה|סיכום|מסקנה)"
    r"\s+[א-י]\s*[—–-]"
)


def est_etiquette(texte: str) -> bool:
    """Ce fragment est-il une **étiquette** plutôt qu'une citation ?

    Deux formes reviennent constamment sur le site, et toutes deux se logent
    dans un bloc typé « citation hébraïque » sans guillemets :

    - l'en-tête de référence — « שולחן ערוך אורח חיים סימן רמ״ב סעיף א' » ;
    - la légende bibliographique — « עם נושאי כלים: ביאורי שו״ע, ט״ז, מג״א ».

    Les juger comme des citations littérales revenait à demander à Sefaria de
    contenir mot pour mot le titre d'un siman : un premier passage sur les
    quatre niveaux a produit 408 signalements pour 539 citations, dont une
    grande part de ce seul défaut.

    Deux critères, tous deux fondés sur ce qui reste une fois retirées les
    références et les abréviations d'ouvrages : s'il ne subsiste pas de quoi
    faire une phrase, ce n'était pas une citation.
    """
    from .references import extract_references

    reste = texte
    for ref in extract_references(texte):
        reste = reste.replace(ref.raw_text, " ")
    reste = _ABREV.sub(" ", reste)
    if n_letters(reste) < MIN_CITATION:
        return True

    # Un intertitre rédactionnel : « חידוש ד — הבחנה בין כלים, בהמה, ושדה
    # (246:6-7) ». C'est l'auteur qui parle de la source, pas la source.
    if TITRE_REDACTIONNEL.search(texte.strip()):
        return True

    # Une légende énumère des ouvrages : forte densité d'abréviations et de
    # séparateurs, peu de texte suivi.
    mots = _MOT.findall(texte)
    abrevs = len(_ABREV.findall(texte))
    return bool(mots) and abrevs >= 3 and abrevs >= len(mots) / 4


def extract_quotes(fragment_html: str, *, marked: bool = False) -> list[Quote]:
    """Fragments hébreux présentés comme des citations littérales.

    ``marked`` dit que le **conteneur lui-même** annonce une citation : c'est
    le cas d'un bloc typé ``CITATION_HEBRAIQUE`` (``blockquote.text-source``,
    ``div.sacred-text``). Le balisage joue alors le rôle du marqueur d'annonce,
    et des guillemets ne sont pas exigés en plus.
    """
    fragment_html = SCRIPT_LD.sub(lambda m: "\n" * m.group(0).count("\n"), fragment_html)
    trouves: list[Quote] = []

    for lineno, ligne in enumerate(fragment_html.split("\n"), 1):
        plain = flatten_html(ligne)
        if not HEBREW.search(plain):
            continue

        marques = [
            next(g for g in m.groups() if g is not None).strip()
            for m in RE_GUILL.finditer(plain)
        ]
        dehors = plain
        for bloc in marques:
            dehors = dehors.replace(bloc, " ")

        blocs = [(b, True) for b in marques] + [(b, False) for b in straight_pairs(dehors)]
        # Aucun guillemet, mais un conteneur qui annonce déjà une citation :
        # le bloc entier est le fragment cité.
        if marked and not blocs:
            blocs = [(RE_EM_RESUME.sub(" ", plain), True)]

        for bloc, annonce in blocs:
            annonce = annonce or marked
            # Un bloc cité contient souvent un préfixe de référence, la citation
            # entre guillemets droits, puis un commentaire de l'auteur : seule la
            # portion entre guillemets est alors la citation.
            interne = [s for s in straight_pairs(bloc) if is_hebrew_quote(s)]
            for brut in (interne or [bloc]):
                brut = RE_PREFIX.sub("", brut).strip(" —–-:.«»")
                if not is_hebrew_quote(brut):
                    continue
                if re.fullmatch(r"[\wא-ת֐-׿-]+", brut):
                    continue      # identifiant d'ancre, pas une phrase
                if n_letters(brut) < MIN_CITATION:
                    continue      # terme technique entre guillemets
                if est_etiquette(brut):
                    continue      # en-tête de référence ou légende, pas une citation

                # Position calculée sur le texte NON nettoyé : ``plain``
                # conserve encore les <em>, et c'est d'eux que dépendent le
                # marqueur de condensation et le contexte d'annonce.
                at = plain.find(brut)
                # Le guillemet ouvrant est retiré du contexte : il en occupe la
                # fin et masque aussi bien le deux-points d'annonce que le
                # marqueur « résumé » qui le précède.
                avant = (plain[:at] if at > 0 else "").rstrip(" \t\"«„'")
                if RESUME.search(avant):
                    continue      # condensation annoncée : jamais jugée
                if at > 0 and not (annonce or has_cue(avant)):
                    continue

                # Les <em> ont été conservés jusqu'ici pour ces deux contrôles ;
                # ils n'ont plus lieu d'être dans le texte cité lui-même.
                texte = RE_EM_TAG.sub("", brut).strip(" —–-:.«»")
                if any(q.text == texte for q in trouves):
                    continue
                trouves.append(Quote(text=texte, line=lineno,
                                     context=RE_EM_TAG.sub("", plain)[:400]))

    return trouves
