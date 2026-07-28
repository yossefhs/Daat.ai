# -*- coding: utf-8 -*-
"""Client HTTP du crawler : respectueux, identifiable, traçable (§5, §24).

- User-Agent explicite (« DaatTorah-AuditBot »), délai minimal entre deux
  requêtes — appliqué à CHAQUE requête sortante, y compris chaque saut de
  redirection et la vérification de liens.
- Les redirections ne sont jamais suivies silencieusement par httpx : le
  suivi est manuel, borné par ``settings.max_redirects``, et la chaîne
  complète est enregistrée (le cahier des charges demande de les détecter).
- ``transport`` injectable pour les tests (httpx.MockTransport) — aucun test
  ne touche le réseau.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import httpx

from ..config import Settings

_REDIRECT_CODES = (301, 302, 303, 307, 308)


@dataclass
class FetchResult:
    url: str
    final_url: str
    status: int | None = None
    html: str | None = None
    redirect_chain: list[str] = field(default_factory=list)
    error: str | None = None
    elapsed_ms: int | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.status is not None and 200 <= self.status < 300


class Fetcher:
    """Client HTTP à débit limité. À utiliser en gestionnaire de contexte."""

    def __init__(self, settings: Settings, transport: httpx.BaseTransport | None = None):
        self._settings = settings
        self._last_request_at = 0.0
        verify: bool | str = settings.ca_bundle or True
        self._client = httpx.Client(
            headers={"User-Agent": settings.user_agent},
            timeout=settings.request_timeout_seconds,
            follow_redirects=False,
            verify=verify,
            transport=transport,
        )

    def __enter__(self) -> "Fetcher":
        return self

    def __exit__(self, *exc) -> None:
        self._client.close()

    def _throttle(self) -> None:
        delay = self._settings.crawl_delay_seconds
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request_at = time.monotonic()

    def get(self, url: str) -> FetchResult:
        """GET avec suivi manuel des redirections (chaîne enregistrée).

        Invariants : ``status`` reflète toujours la DERNIÈRE réponse reçue
        (y compris un 3xx quand la chaîne dépasse ``max_redirects``), et
        ``elapsed_ms`` est renseigné sur tous les chemins, erreurs comprises.
        """
        result = FetchResult(url=url, final_url=url)
        current = url
        started = time.monotonic()
        try:
            for _ in range(self._settings.max_redirects + 1):
                self._throttle()
                response = self._client.get(current)
                result.status = response.status_code
                if response.status_code in _REDIRECT_CODES:
                    location = response.headers.get("location")
                    if not location:
                        result.error = "redirection sans en-tête Location"
                        break
                    nxt = str(httpx.URL(current).join(location))
                    result.redirect_chain.append(nxt)
                    current = nxt
                    result.final_url = current
                    continue
                result.final_url = current
                if response.status_code < 400:
                    result.html = response.text
                break
            else:
                result.error = f"trop de redirections (> {self._settings.max_redirects})"
        except httpx.HTTPError as exc:
            result.error = f"{type(exc).__name__}: {exc}"
        result.elapsed_ms = int((time.monotonic() - started) * 1000)
        return result

    def head_status(self, url: str) -> int | None:
        """Statut final d'un lien (vérification de liens internes).

        HEAD avec repli GET sur 405, redirections suivies MANUELLEMENT :
        chaque saut repasse par le throttle et le plafond est
        ``settings.max_redirects`` — pas les 20 sauts par défaut de httpx.
        """
        current = url
        try:
            for _ in range(self._settings.max_redirects + 1):
                self._throttle()
                response = self._client.head(current)
                if response.status_code == 405:
                    self._throttle()
                    response = self._client.get(current)
                if response.status_code in _REDIRECT_CODES:
                    location = response.headers.get("location")
                    if not location:
                        return response.status_code
                    current = str(httpx.URL(current).join(location))
                    continue
                return response.status_code
            return None  # boucle ou chaîne trop longue : lien considéré cassé
        except httpx.HTTPError:
            return None
