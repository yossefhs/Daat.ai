# -*- coding: utf-8 -*-
"""Périmètre du crawl (§2) : /oh/{siman}/{niveau}, simanim 242 à 269.

Le français est la langue par défaut du site : /oh/N/base sert la version
française (les variantes portent /he ou /en). Les URL sont construites, pas
découvertes : le périmètre est fermé et connu d'avance.

Les quatre niveaux d'étude ne se valent pas du point de vue de l'audit :
le niveau 2 (*lamdan*) est très largement en hébreu et cite bien plus de
sources que le niveau 1, et le niveau 4 (*daat-harav*) porte la shita de
l'Admour HaZaken. C'est là que se trouvent les citations les plus nombreuses,
donc le plus grand risque d'écart — s'en tenir au niveau 1 revenait à
n'inspecter que la vitrine.

**Le niveau 4 n'existe pas partout** : les simanim 304 et 322 n'en ont pas —
l'Admour HaZaken ne les a pas écrits dans le Choulhan Aroukh HaRav, et ces
pages portent une « page-pont » à la place. Le crawler ne les demande donc
pas : un 404 attendu n'est pas une anomalie à signaler.
"""
from __future__ import annotations

from ..config import Settings

# Bornes de sécurité : le périmètre d'un job est toujours un ensemble FERMÉ et
# PETIT de simanim. Ces limites protègent à la fois l'API (allocation mémoire)
# et le site (un « 1-100000 » lancerait ~42 h de requêtes en tâche de fond).
SIMAN_MIN = 1
SIMAN_MAX = 999
MAX_SIMANIM_PER_JOB = 200


# Niveaux d'étude, dans l'ordre des URL du site.
NIVEAUX = ("base", "lamdan", "synthese", "daat-harav")

# Simanim dépourvus de niveau 4 (voir docstring du module).
SANS_DAAT_HARAV = frozenset({304, 322})


def niveaux_demandes(settings: Settings) -> list[str]:
    """Niveaux à crawler : ``settings.niveau`` peut valoir « base »,
    une liste séparée par des virgules, ou « all »."""
    brut = (settings.niveau or "base").strip().lower()
    if brut in ("all", "tous", "*"):
        return list(NIVEAUX)
    demandes = [n.strip() for n in brut.split(",") if n.strip()]
    inconnus = [n for n in demandes if n not in NIVEAUX]
    if inconnus:
        raise ValueError(
            f"niveau inconnu : {', '.join(inconnus)}. Attendu : {', '.join(NIVEAUX)}"
        )
    return demandes or ["base"]


def perimeter_urls(
    settings: Settings,
    simanim: list[int] | None = None,
    niveaux: list[str] | None = None,
) -> list[tuple[int, str]]:
    """Retourne [(siman, url)] pour le périmètre configuré.

    L'ordre est siman par siman, niveau par niveau : le crawl progresse ainsi
    de façon lisible, et une interruption laisse des simanim complets.
    """
    numbers = simanim or list(range(settings.siman_start, settings.siman_end + 1))
    demandes = niveaux or niveaux_demandes(settings)
    base = settings.base_url.rstrip("/")
    return [
        (n, f"{base}/oh/{n}/{niveau}")
        for n in numbers
        for niveau in demandes
        if not (niveau == "daat-harav" and n in SANS_DAAT_HARAV)
    ]


def niveau_de_url(url: str) -> str:
    """Niveau porté par une URL du périmètre (« …/oh/242/lamdan » → lamdan)."""
    dernier = url.rstrip("/").rsplit("/", 1)[-1]
    return dernier if dernier in NIVEAUX else "base"


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
