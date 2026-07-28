# -*- coding: utf-8 -*-
"""Découpage d'une page en blocs identifiables (§6).

Identifiant stable : ``OH-268-BASE-FR-P014``
  ┌── section du Choulhan Aroukh (OH / YD)
  │   ┌── siman            ┌── langue
  │   │      ┌── niveau    │    ┌── type de bloc (1 lettre) + rang dans ce type
  OH-268-BASE-FR-P014

**Pourquoi un rang PAR TYPE et non un index global** : l'identifiant doit
rester stable quand la page bouge un peu (§6). Un index global se décale dès
qu'un paragraphe est inséré n'importe où ; un rang par type ne se décale que
si un bloc du MÊME type est inséré avant. Le type est déduit du balisage, pas
de la position — insérer une note ne renumérote pas les citations.

Compromis assumé : l'identifiant ne survit pas à une réorganisation profonde.
Le champ ``sha256`` du bloc permet alors de retrouver un contenu déplacé.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from .hashing import sha256_hex, normalize_whitespace
from .hebrew import HEBREW_LETTER
from .models import BlockType

# Lettre d'identifiant par type de bloc.
_TYPE_CODE = {
    BlockType.TITRE: "T",
    BlockType.SOUS_TITRE: "S",
    BlockType.PARAGRAPHE: "P",
    BlockType.CITATION_HEBRAIQUE: "H",
    BlockType.TRADUCTION: "R",
    BlockType.SOURCE: "O",
    BlockType.LISTE: "L",
    BlockType.TABLEAU: "B",
    BlockType.CAS_PRATIQUE: "C",
    BlockType.RESUME: "M",
    BlockType.CONCLUSION: "N",
    BlockType.QUIZ: "Q",
    BlockType.NOTE: "E",
}

# Éléments ignorés : navigation, pied de page, sélecteur de langue, et
# décorations qui ne sont pas du texte à auditer (filigrane, badges…).
# Les auditer produisait des signalements de pure forme sur du contenu que
# personne ne lit comme une phrase.
_SKIP_CLASSES = {
    "lang-switcher-float", "nav-level", "toc-item", "toc-num", "ornament",
    "page-break", "breadcrumb", "site-footer", "site-header",
    "yh-watermark", "next-siman-nav", "level-badge", "badge-top",
}
_SKIP_TAGS = {"script", "style", "noscript", "template", "nav", "footer", "header"}

# Mots-clés des titres de section, pour typer résumé / conclusion / quiz.
_SECTION_HINTS = (
    (BlockType.RESUME, ("synthèse", "résumé", "en bref", "récapitul", "tableau de synthèse")),
    (BlockType.CONCLUSION, ("conclusion", "à retenir", "en pratique", "halakha lemaassé")),
    (BlockType.QUIZ, ("question", "quiz", "compréhension", "vérifier")),
    (BlockType.CAS_PRATIQUE, ("cas pratique", "situations", "application", "piège")),
)


@dataclass
class Block:
    stable_id: str
    order_index: int
    block_type: BlockType
    raw_content: str
    normalized_content: str
    css_selector: str
    sha256: str
    # Attributs de l'élément lui-même. ``raw_content`` est le HTML *intérieur*
    # (``decode_contents``) : il ne peut par construction pas contenir la
    # classe ni le ``dir`` de la balise qui le porte. Un contrôle qui les
    # cherchait là ne pouvait que se tromper — d'où ces deux champs.
    css_classes: tuple[str, ...] = ()
    dir_attr: str | None = None       # ``dir`` propre ou hérité d'un ancêtre
    # Rang du titre (1 pour h1, 2 pour h2…), 0 si le bloc n'est pas un titre.
    # Le site distingue nettement les deux usages : h2 pour les sections
    # numérotées — un vrai changement de sujet —, h3 pour les intertitres
    # à l'intérieur d'une même sougya (« Enseignement A », « Enseignement B »).
    # Les confondre coupait le lien entre une citation et la source annoncée
    # quelques blocs plus haut.
    heading_level: int = 0


def _is_hebrew(text: str, threshold: float = 0.55) -> bool:
    """Le fragment est-il majoritairement hébreu ?"""
    heb = len(HEBREW_LETTER.findall(text))
    latin = len(re.findall(r"[A-Za-zÀ-ÿ]", text))
    return heb > 0 and heb >= threshold * (heb + latin)


def _skip(tag: Tag) -> bool:
    if tag.name in _SKIP_TAGS:
        return True
    classes = set(tag.get("class") or [])
    return bool(classes & _SKIP_CLASSES)


def _classify(tag: Tag, section_hint: BlockType | None) -> BlockType | None:
    """Type d'un élément, d'après son balisage — ou None s'il est ignoré."""
    classes = set(tag.get("class") or [])

    if tag.name in ("h1",):
        return BlockType.TITRE
    if tag.name in ("h2", "h3", "h4"):
        return BlockType.SOUS_TITRE
    if tag.name == "blockquote":
        # Le site place le texte du Choulhan Aroukh en blockquote.text-source.
        return BlockType.CITATION_HEBRAIQUE
    if tag.name == "table":
        return BlockType.TABLEAU
    if tag.name in ("ul", "ol"):
        return BlockType.LISTE

    if tag.name in ("p", "div"):
        if "translation" in classes:
            return BlockType.TRADUCTION
        if "sacred-text" in classes or "he" in classes:
            return BlockType.CITATION_HEBRAIQUE
        if "definition" in classes or "key-point" in classes:
            return BlockType.NOTE
        text = tag.get_text(" ", strip=True)
        if not text:
            return None
        if _is_hebrew(text):
            return BlockType.CITATION_HEBRAIQUE
        if _is_enumeration(text):
            # Un plan « 1. … 2. … » est une liste même quand il est balisé en
            # div : le typer en paragraphe le faisait juger comme une phrase,
            # et signaler à tort comme « inachevé » faute de point final.
            return BlockType.LISTE
        # Un paragraphe hérite du type de sa section (résumé, conclusion…).
        return section_hint or BlockType.PARAGRAPHE
    return None


_ENUM_START = re.compile(r"^\s*1\s*[.)]\s")


def _is_enumeration(text: str) -> bool:
    """Le bloc est-il une énumération numérotée (plan, sommaire) ?"""
    if not _ENUM_START.match(text):
        return False
    return bool(re.search(r"\s2\s*[.)]\s", text))


def _section_hint(title: str) -> BlockType | None:
    low = title.lower()
    for block_type, keywords in _SECTION_HINTS:
        if any(k in low for k in keywords):
            return block_type
    return None


def split_blocks(
    html: str, *, section: str = "OH", siman: int | str = 0,
    niveau: str = "base", langue: str = "fr",
) -> list[Block]:
    """Découpe une page en blocs typés, avec identifiants stables."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(list(_SKIP_TAGS)):
        tag.decompose()

    root = soup.find("main") or soup.body or soup
    prefix = f"{section.upper()}-{siman}-{niveau.upper()}-{langue.upper()}"

    blocks: list[Block] = []
    counters: dict[str, int] = {}
    order = 0
    hint: BlockType | None = None

    for tag in root.find_all(
        ["h1", "h2", "h3", "h4", "p", "div", "blockquote", "table", "ul", "ol"],
        recursive=True,
    ):
        if _skip(tag):
            continue
        # Un div qui contient d'autres blocs n'est pas un bloc lui-même :
        # ses enfants seront visités (évite les doublons imbriqués).
        if tag.name == "div" and tag.find(["p", "blockquote", "table", "ul", "ol", "h2", "h3"]):
            continue

        block_type = _classify(tag, hint)
        if block_type is None:
            continue

        raw = tag.decode_contents().strip()
        text = tag.get_text(" ", strip=True)
        if not text:
            continue

        if block_type is BlockType.SOUS_TITRE:
            hint = _section_hint(text)

        code = _TYPE_CODE[block_type]
        counters[code] = counters.get(code, 0) + 1
        order += 1

        normalized = normalize_whitespace(text)
        blocks.append(Block(
            stable_id=f"{prefix}-{code}{counters[code]:03d}",
            order_index=order,
            block_type=block_type,
            raw_content=raw,
            normalized_content=normalized,
            css_selector=_selector(tag),
            sha256=sha256_hex(normalized),
            css_classes=tuple(tag.get("class") or ()),
            dir_attr=_inherited_dir(tag),
            heading_level=int(tag.name[1]) if tag.name in ("h1", "h2", "h3", "h4") else 0,
        ))

    return blocks


def _inherited_dir(tag: Tag) -> str | None:
    """``dir`` de l'élément, ou du plus proche ancêtre qui en porte un.

    La direction est héritée en CSS : un bloc hébreu dans un conteneur
    ``dir="rtl"`` est correctement orienté même sans attribut propre.
    """
    current: Tag | None = tag
    while current is not None and getattr(current, "get", None):
        value = current.get("dir")
        if value:
            return value.lower()
        current = current.parent
    return None


def rtl_classes(html: str) -> set[str]:
    """Classes que la feuille de style de la page déclare en ``direction: rtl``.

    Déduit des règles CSS réellement présentes plutôt que d'une liste de noms
    supposés : c'est la page qui dit quelles classes orientent le texte.
    """
    found: set[str] = set()
    for style in BeautifulSoup(html, "lxml").find_all("style"):
        css = style.get_text()
        for selector, body in re.findall(r"([^{}]+)\{([^}]*)\}", css):
            if not re.search(r"direction\s*:\s*rtl", body, re.I):
                continue
            found.update(re.findall(r"\.([A-Za-z0-9_-]+)", selector))
    return found


def _selector(tag: Tag) -> str:
    """Sélecteur CSS lisible : ``section#id > p.classe:nth-of-type(3)``."""
    parts: list[str] = []
    current: Tag | None = tag
    while current is not None and current.name not in ("[document]", "html"):
        piece = current.name
        if current.get("id"):
            piece += f"#{current['id']}"
            parts.append(piece)
            break
        classes = [c for c in (current.get("class") or []) if c not in _SKIP_CLASSES]
        if classes:
            piece += "." + ".".join(classes[:2])
        siblings = [s for s in current.parent.find_all(current.name, recursive=False)] \
            if current.parent else []
        if len(siblings) > 1:
            piece += f":nth-of-type({siblings.index(current) + 1})"
        parts.append(piece)
        current = current.parent
        if len(parts) >= 4:
            break
    return " > ".join(reversed(parts))
