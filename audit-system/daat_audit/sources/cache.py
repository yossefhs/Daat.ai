# -*- coding: utf-8 -*-
"""Cache en base des textes sources (§15, table ``source_texts``).

Un même passage est cité par plusieurs simanim et par les trois langues d'une
même page : sans cache, une campagne de vérification redemanderait cent fois
le même folio à Sefaria. Le cache est **daté** (``fetched_at``) et conserve le
titre des éditions ayant répondu, pour qu'un signalement reste rattachable au
texte exact sur lequel il a été rendu.
"""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..hashing import sha256_hex
from ..models import SourceText
from .base import SearchHit, SourceDocument


class CachedProvider:
    """Enveloppe un fournisseur et mémorise ses réponses en base."""

    def __init__(self, provider, session: Session, refresh: bool = False):
        self._provider = provider
        self._session = session
        self._refresh = refresh
        self.name = provider.name
        self.hits = 0
        self.misses = 0
        # Références déjà connues comme absentes, pour cette exécution. Un séif
        # qui n'existe pas ne se met pas à exister ; sans ce garde, la même
        # requête 404 partait des dizaines de fois vers un service tiers
        # gratuit. Volontairement en mémoire et non en base : une absence peut
        # tenir à un incident, et elle ne doit pas se figer d'une session à
        # l'autre.
        self._absentes: set[str] = set()

    def fetch(self, ref: str) -> SourceDocument | None:
        if ref in self._absentes:
            return None
        if not self._refresh:
            ligne = self._session.execute(
                select(SourceText).where(
                    SourceText.provider == self.name, SourceText.ref == ref
                )
            ).scalars().first()
            if ligne is not None:
                self.hits += 1
                return SourceDocument(
                    ref=ref,
                    segments=json.loads(ligne.content),
                    versions=(ligne.version_title or "").split(" | ") if ligne.version_title else [],
                    provider=self.name,
                )

        self.misses += 1
        document = self._provider.fetch(ref)
        if document is None:
            self._absentes.add(ref)
            return None

        contenu = json.dumps(document.segments, ensure_ascii=False)
        self._session.add(SourceText(
            provider=self.name,
            ref=ref,
            lang="he",
            version_title=" | ".join(document.versions) or None,
            content=contenu,
            sha256=sha256_hex(contenu),
        ))
        self._session.flush()
        return document

    def search(self, text: str) -> list[SearchHit]:
        """Non mise en cache : une recherche n'est faite qu'une fois par
        citation absente, et son résultat dépend de l'index de Sefaria."""
        return self._provider.search(text)
