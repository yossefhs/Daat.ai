# -*- coding: utf-8 -*-
"""Empreintes SHA-256 et normalisation minimale pour la détection de changement.

Deux empreintes par version de page :

- ``sha256_html`` : le HTML brut, tel que servi. Change à chaque variation
  d'infrastructure (attributs injectés, horodatages) — utile pour l'archive.
- ``sha256_text`` : le texte visible, blancs normalisés. C'est CETTE
  empreinte qui déclenche la détection « le contenu a changé » (§5), pour
  ne pas créer une fausse version à chaque re-déploiement identique.

La normalisation ici est volontairement minimale (blancs uniquement) : la
normalisation hébraïque fine du §9 (nikoud, te'amim, guillemets…) relève du
moteur de comparaison de citations (Phase 2), pas de l'archivage.
"""
from __future__ import annotations

import hashlib
import re

_WS = re.compile(r"[ \t\r\f\v]+")
_BLANK_LINES = re.compile(r"\n{3,}")


def normalize_whitespace(text: str) -> str:
    """Réduit les suites d'espaces et les lignes vides surnuméraires."""
    text = _WS.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip()


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def text_fingerprint(text: str) -> str:
    """Empreinte de contenu : SHA-256 du texte à blancs normalisés."""
    return sha256_hex(normalize_whitespace(text))
