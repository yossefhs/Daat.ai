# -*- coding: utf-8 -*-
"""Fournisseur Sefaria (§15).

Porte la logique éprouvée par ``scripts/verifier-citations.py`` à la racine du
dépôt, dont chaque détail vient d'un faux positif constaté :

1. **Toutes les éditions hébraïques, pas seulement celle par défaut.** Sefaria
   sert le Talmud dans l'édition Davidson ; les pages du site citent le Vilna
   imprimé. Sur ברכות ג׳ ע״א, Davidson porte « אוי שהחרבתי » là où le Vilna
   porte « אוי לבנים שבעונותיהם החרבתי » — comparer à une seule édition
   transforme une citation exacte en falsification supposée.
2. **Débit limité et agent identifiable**, comme pour le crawl du site : on
   interroge un service tiers gratuit, on ne le martèle pas.
3. **Transport injectable** : aucun test ne touche le réseau.

Ce module ne fait que LIRE. Il n'écrit rien, ni sur Sefaria, ni sur le site.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.parse

import httpx

from ..config import Settings
from .base import SearchHit, SourceDocument

logger = logging.getLogger("daat_audit.sources.sefaria")

_BASE = "https://www.sefaria.org"
_MAX_VERSIONS = 6          # au-delà, l'URL enfle sans rien apporter
_MIN_SEARCH_LETTERS = 12


def _flatten(value, out: list[str]) -> list[str]:
    """Sefaria imbrique les segments à profondeur variable selon la référence."""
    if isinstance(value, str):
        if value.strip():
            out.append(value)
    elif isinstance(value, list):
        for item in value:
            _flatten(item, out)
    return out


class SefariaProvider:
    """Accès en lecture à l'API Sefaria, à débit limité."""

    name = "sefaria"

    def __init__(
        self,
        settings: Settings,
        transport: httpx.BaseTransport | None = None,
        delay_seconds: float | None = None,
    ):
        self._settings = settings
        self._delay = settings.crawl_delay_seconds if delay_seconds is None else delay_seconds
        self._last_request_at = 0.0
        self._versions_cache: dict[str, list[str]] = {}
        verify: bool | str = settings.ca_bundle or True
        self._client = httpx.Client(
            base_url=_BASE,
            headers={"User-Agent": settings.user_agent},
            timeout=settings.request_timeout_seconds,
            follow_redirects=True,
            verify=verify,
            transport=transport,
        )

    def __enter__(self) -> "SefariaProvider":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # ── Politesse ────────────────────────────────────────────────────────
    def _throttle(self) -> None:
        if self._delay <= 0:
            return
        ecoule = time.monotonic() - self._last_request_at
        if ecoule < self._delay:
            time.sleep(self._delay - ecoule)
        self._last_request_at = time.monotonic()

    def _get_json(self, path: str):
        self._throttle()
        try:
            response = self._client.get(path)
        except httpx.HTTPError as exc:
            logger.warning("Sefaria injoignable (%s) : %s", path, exc)
            return None
        if response.status_code != 200:
            logger.info("Sefaria a répondu %s pour %s", response.status_code, path)
            return None
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError):
            logger.warning("réponse Sefaria illisible pour %s", path)
            return None

    # ── Éditions ─────────────────────────────────────────────────────────
    def hebrew_versions(self, book: str) -> list[str]:
        """Titres des éditions hébraïques d'un ouvrage (voir §1 de la docstring)."""
        if book in self._versions_cache:
            return self._versions_cache[book]
        data = self._get_json(
            "/api/texts/versions/" + urllib.parse.quote(book, safe=",._-")
        )
        titles = [
            v["versionTitle"] for v in data
            if isinstance(v, dict) and v.get("language") == "he" and v.get("versionTitle")
        ] if isinstance(data, list) else []
        self._versions_cache[book] = titles
        return titles

    @staticmethod
    def book_of(ref: str) -> str:
        """Ouvrage d'une référence : « Berakhot.34a » → « Berakhot »."""
        import re
        return re.split(r"[.]\d|[.][א-ת]", ref)[0].replace("_", " ")

    # ── Contrat TextSourceProvider ───────────────────────────────────────
    def fetch(self, ref: str) -> SourceDocument | None:
        titles = self.hebrew_versions(self.book_of(ref))
        query = "?return_format=text_only&version=hebrew"
        for title in titles[:_MAX_VERSIONS]:
            query += "&version=" + urllib.parse.quote("hebrew|" + title)

        data = self._get_json(
            "/api/v3/texts/" + urllib.parse.quote(ref, safe=",._-") + query
        )
        if not isinstance(data, dict) or "error" in data:
            return None

        segments: list[str] = []
        versions: list[str] = []
        for version in data.get("versions") or []:
            if version.get("language") != "he":
                continue
            _flatten(version.get("text"), segments)
            if version.get("versionTitle"):
                versions.append(version["versionTitle"])

        if not segments:
            return None
        return SourceDocument(ref=ref, segments=segments,
                              versions=versions, provider=self.name)

    def search(self, text: str) -> list[SearchHit]:
        """Recherche exacte : où ce fragment se trouve-t-il réellement ?

        Sert uniquement à qualifier une absence — citation fabriquée ou
        citation exacte mal référencée. Ne sert jamais à « corriger » une
        référence automatiquement : c'est une information portée au dossier,
        que l'humain tranche.
        """
        import re
        propre = re.sub(r"\s+", " ", re.sub(r"[«»\"„”\[\]]", "", text)).strip()
        propre = max((p.strip() for p in re.split(r"…|\.\.\.", propre)),
                     key=len, default="")[:180]
        if len(re.findall(r"[א-ת]", propre)) < _MIN_SEARCH_LETTERS:
            return []

        self._throttle()
        try:
            response = self._client.post(
                "/api/search-wrapper",
                json={"query": propre, "type": "text", "field": "exact", "size": 4},
            )
        except httpx.HTTPError as exc:
            logger.warning("recherche Sefaria injoignable : %s", exc)
            return []
        if response.status_code != 200:
            return []
        try:
            data = response.json()
        except (json.JSONDecodeError, ValueError):
            return []

        hits = []
        for hit in (data.get("hits", {}).get("hits") or []):
            ref = hit.get("_source", {}).get("ref") or hit.get("_id", "")
            if ref:
                hits.append(SearchHit(ref=str(ref)))
        return hits
