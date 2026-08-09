# -*- coding: utf-8 -*-
"""Extraction du contenu d'une page HTML (§5).

Phase 1 : titre, texte nettoyé, liens internes. Le découpage en blocs
identifiables (§6) arrive en Phase 2 — la structure des pages DaatTorah
(sections numérotées, blockquote, tableaux, he-q) s'y prête bien.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# Balises dont le contenu n'est pas du texte visible.
_NON_CONTENT_TAGS = ("script", "style", "noscript", "template")


@dataclass
class ExtractResult:
    title: str | None = None
    text: str = ""
    internal_links: list[str] = field(default_factory=list)
    canonical: str | None = None


def extract_page(html: str, page_url: str, site_host: str | None = None) -> ExtractResult:
    """Extrait titre, texte visible et liens internes d'une page.

    ``site_host`` : hôte considéré comme « interne » (par défaut, celui de
    ``page_url``). Les ancres (#…), mailto:, tel: et hôtes tiers sont exclus.
    """
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all(_NON_CONTENT_TAGS):
        tag.decompose()

    # Titre : <title>, sinon premier <h1>.
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.h1:
        title = soup.h1.get_text(" ", strip=True)

    # Canonical (utile pour détecter les incohérences siman/URL en Phase 2).
    canonical = None
    link_canon = soup.find("link", rel="canonical")
    if link_canon and link_canon.get("href"):
        canonical = link_canon["href"].strip()

    text = soup.get_text("\n", strip=True)

    host = site_host or urlparse(page_url).netloc
    links: list[str] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(page_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https") or parsed.netloc != host:
            continue
        absolute = absolute.split("#", 1)[0]
        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)

    return ExtractResult(title=title, text=text, internal_links=links, canonical=canonical)
