# -*- coding: utf-8 -*-
"""Contrat commun aux fournisseurs de textes sources (§15).

Un fournisseur sait faire deux choses, et la seconde est facultative :

``fetch(ref)``    le texte de la référence demandée ;
``search(texte)`` où ce texte se trouve *ailleurs* dans le corpus.

La recherche sert à distinguer deux situations que « absent de la source
citée » recouvre et qui n'appellent pas la même correction : une citation
**fabriquée** (introuvable nulle part) et une citation **exacte rattachée à
la mauvaise référence**. Un fournisseur qui ne sait pas chercher retourne une
liste vide — le système signale alors l'absence sans se prononcer sur sa cause.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class SourceDocument:
    """Texte d'une référence, **toutes éditions réunies**.

    ``segments`` réunit les segments de toutes les éditions hébraïques
    disponibles, et ``versions`` dit lesquelles ont répondu. Cette pluralité
    n'est pas un luxe : Sefaria sert par défaut l'édition Davidson du Talmud,
    dont le texte diffère par endroits du Vilna imprimé auquel se réfèrent les
    pages du site. Comparer à une seule édition fabrique des faux positifs.
    """

    ref: str
    segments: list[str] = field(default_factory=list)
    versions: list[str] = field(default_factory=list)
    provider: str = ""

    @property
    def text(self) -> str:
        return "\n".join(self.segments)

    def __bool__(self) -> bool:
        return bool(self.segments)


@dataclass
class SearchHit:
    ref: str
    text: str = ""


@runtime_checkable
class TextSourceProvider(Protocol):
    """Ce que tout fournisseur doit savoir faire."""

    name: str

    def fetch(self, ref: str) -> SourceDocument | None:
        """Texte de la référence, ou ``None`` si elle n'existe pas."""
        ...

    def search(self, text: str) -> list[SearchHit]:
        """Où ce texte apparaît-il ailleurs ? Liste vide si non supporté."""
        ...
