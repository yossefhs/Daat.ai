# -*- coding: utf-8 -*-
"""Résolution du rôle décisionnaire (§14).

Le rôle vient **du secret présenté**, pas d'un paramètre de la requête : sans
quoi il suffirait d'écrire ``role=rav`` pour approuver seul un signalement
halakhique, et la garantie centrale du workflow ne vaudrait rien.

Deux secrets distincts, donc deux rôles distincts :

    AUDIT_ADMIN_SECRET → editor
    AUDIT_RAV_SECRET   → rav

**Fail closed** : si aucun secret n'est configuré, toute décision est refusée
(503). Un outil qui laisse décider sans savoir qui décide ne trace rien
d'utile — et la traçabilité est une exigence, pas un confort.
"""
from __future__ import annotations

import hmac

from fastapi import Header, HTTPException

from ..config import Settings
from ..workflow import Role


def _egal(a: str, b: str) -> bool:
    """Comparaison à temps constant."""
    return bool(a) and bool(b) and hmac.compare_digest(a, b)


def resolve_role(settings: Settings, secret: str | None) -> Role:
    if not settings.admin_secret and not settings.rav_secret:
        raise HTTPException(
            503,
            "aucun secret d'administration configuré : définir AUDIT_ADMIN_SECRET "
            "et/ou AUDIT_RAV_SECRET. Les décisions sont refusées tant qu'on ne "
            "peut pas savoir qui décide.",
        )
    if secret is None:
        raise HTTPException(401, "en-tête X-Admin-Secret manquant")
    # Le rav est testé en premier : si le même secret servait aux deux rôles,
    # ce serait une erreur de configuration, et le rôle le plus élevé ne doit
    # pas être obtenu par accident.
    if _egal(secret, settings.rav_secret):
        return Role.RAV
    if _egal(secret, settings.admin_secret):
        return Role.EDITOR
    raise HTTPException(403, "secret invalide")


def make_role_dependency(settings: Settings):
    """Dépendance FastAPI : rend (rôle, identifiant d'utilisateur)."""
    def dependency(
        x_admin_secret: str | None = Header(default=None, alias="X-Admin-Secret"),
        x_admin_user: str | None = Header(default=None, alias="X-Admin-User"),
    ) -> tuple[Role, str]:
        role = resolve_role(settings, x_admin_secret)
        # L'identifiant nominatif est facultatif mais recommandé : à défaut, la
        # trace porte le rôle, ce qui reste vérifiable.
        return role, (x_admin_user or role.value)
    return dependency
