# -*- coding: utf-8 -*-
"""Périmètre du MVP (§2) : /oh/{siman}/base, simanim 242 à 269, français.

Le français est la langue par défaut du site : /oh/N/base sert la version
française (les variantes portent /he ou /en). Les URL sont construites, pas
découvertes : le périmètre est fermé et connu d'avance.
"""
from __future__ import annotations

from ..config import Settings

# Bornes de sécurité : le périmètre d'un job est toujours un ensemble FERMÉ et
# PETIT de simanim. Ces limites protègent à la fois l'API (allocation mémoire)
# et le site (un « 1-100000 » lancerait ~42 h de requêtes en tâche de fond).
SIMAN_MIN = 1
SIMAN_MAX = 999
MAX_SIMANIM_PER_JOB = 200


def perimeter_urls(settings: Settings, simanim: list[int] | None = None) -> list[tuple[int, str]]:
    """Retourne [(siman, url)] pour le périmètre configuré."""
    numbers = simanim or list(range(settings.siman_start, settings.siman_end + 1))
    base = settings.base_url.rstrip("/")
    return [(n, f"{base}/oh/{n}/{settings.niveau}") for n in numbers]


def parse_simanim_arg(arg: str) -> list[int]:
    """« 242-269 » ou « 242,243,250 » → liste d'entiers, bornée.

    Lève ``ValueError`` (message en français, réutilisable en 422 côté API)
    pour : entrée non numérique, siman hors [SIMAN_MIN, SIMAN_MAX], plage
    inversée, ou périmètre dépassant MAX_SIMANIM_PER_JOB.
    """
    def _num(token: str) -> int:
        token = token.strip()
        if not token.isdigit():
            raise ValueError(f"siman invalide : « {token} » (nombre attendu)")
        value = int(token)
        if not (SIMAN_MIN <= value <= SIMAN_MAX):
            raise ValueError(f"siman hors bornes : {value} (attendu {SIMAN_MIN}–{SIMAN_MAX})")
        return value

    out: set[int] = set()
    for part in arg.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo_s, hi_s = part.split("-", 1)
            lo, hi = _num(lo_s), _num(hi_s)
            if hi < lo:
                raise ValueError(f"plage inversée : {lo}-{hi}")
            out.update(range(lo, hi + 1))
        else:
            out.add(_num(part))
        if len(out) > MAX_SIMANIM_PER_JOB:
            raise ValueError(f"périmètre trop large (> {MAX_SIMANIM_PER_JOB} simanim par job)")
    if not out:
        raise ValueError("aucun siman fourni")
    return sorted(out)
