# -*- coding: utf-8 -*-
"""Garde-fous du cahier des charges (§4, §13).

Invariants de la Phase 1 :

1. Le système n'écrit QUE dans sa propre base de données. Aucun code de ce
   paquet n'écrit dans les sources du site (``sources/``), ni sur le site
   public, ni dans un quelconque fichier du dépôt DaatTorah.
2. Aucune fonctionnalité de publication n'existe. La fonction
   ``ensure_site_write_allowed`` est l'unique point de passage prévu pour
   une future publication, et elle échoue TOUJOURS en Phase 1 — y compris
   en mode ``production_publish`` — parce que la publication n'est pas
   implémentée. C'est délibéré : le jour où elle le sera, ce point de
   passage unique portera la validation humaine obligatoire.
"""
from __future__ import annotations

from .config import AuditMode, Settings


class ModeError(RuntimeError):
    """Action interdite dans le mode de fonctionnement courant."""


class PublicationNotImplementedError(ModeError):
    """La publication n'existe pas en Phase 1 (MVP audit_readonly)."""


def ensure_site_write_allowed(settings: Settings) -> None:
    """Point de passage unique et obligatoire avant TOUTE écriture vers le site.

    Phase 1 : échoue systématiquement.

    - en ``audit_readonly`` et ``staging_review`` : le mode l'interdit ;
    - en ``production_publish`` : le mode l'autoriserait en théorie, mais la
      publication n'est pas implémentée — on refuse explicitement plutôt que
      de laisser croire qu'un chemin d'écriture existe.
    """
    if settings.mode is not AuditMode.PRODUCTION_PUBLISH:
        raise ModeError(
            f"Écriture vers le site interdite en mode « {settings.mode.value} ». "
            "Seul le mode production_publish pourra l'autoriser, après validation humaine."
        )
    raise PublicationNotImplementedError(
        "La publication vers le site n'est pas implémentée (Phase 1 : audit_readonly). "
        "Aucune correction n'est appliquée automatiquement au site public."
    )


def is_readonly(settings: Settings) -> bool:
    return settings.mode is AuditMode.AUDIT_READONLY
