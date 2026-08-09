# -*- coding: utf-8 -*-
"""Fournisseur local — textes en dur, pour les tests et le hors-ligne (§15).

Permet d'exercer toute la chaîne de vérification des citations sans réseau,
et de rejouer un cas précis (une citation litigieuse, une édition donnée)
sans dépendre de la disponibilité de Sefaria.
"""
from __future__ import annotations

from .base import SearchHit, SourceDocument


class LocalProvider:
    """Fournisseur alimenté par un dictionnaire ``{référence: texte}``."""

    name = "local"

    def __init__(self, textes: dict[str, str | list[str]] | None = None):
        self._textes: dict[str, list[str]] = {}
        for ref, contenu in (textes or {}).items():
            self._textes[ref] = [contenu] if isinstance(contenu, str) else list(contenu)

    def add(self, ref: str, texte: str | list[str]) -> None:
        self._textes[ref] = [texte] if isinstance(texte, str) else list(texte)

    def fetch(self, ref: str) -> SourceDocument | None:
        segments = self._textes.get(ref)
        if not segments:
            return None
        return SourceDocument(ref=ref, segments=list(segments),
                              versions=["local"], provider=self.name)

    def search(self, text: str) -> list[SearchHit]:
        from ..hebrew import letters_only
        aiguille = letters_only(text)
        if not aiguille:
            return []
        return [SearchHit(ref=ref) for ref, segments in self._textes.items()
                if aiguille in letters_only("\n".join(segments))]
