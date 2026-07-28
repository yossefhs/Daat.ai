# -*- coding: utf-8 -*-
"""Configuration centrale du système d'audit.

Toutes les valeurs sont surchargables par variables d'environnement
préfixées ``AUDIT_`` (ou par un fichier ``.env`` local, jamais commité).

Le mode par défaut est ``audit_readonly`` : c'est le seul mode implémenté
en Phase 1, et les deux autres existent uniquement pour que la machine à
états soit posée dès le départ (voir ``daat_audit.safety``).
"""
from __future__ import annotations

import enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Racine du projet audit-system/ — les chemins par défaut y sont ANCRÉS pour
# qu'une exécution depuis un autre répertoire (racine du dépôt du site, cron…)
# ne crée jamais var/ ailleurs. Le dépôt étant déployé statiquement par Vercel,
# une base SQLite créée à la racine deviendrait une URL publique du site.
_PKG_ROOT = Path(__file__).resolve().parent.parent


class AuditMode(str, enum.Enum):
    """Les trois modes du cahier des charges (§4)."""

    AUDIT_READONLY = "audit_readonly"
    STAGING_REVIEW = "staging_review"
    PRODUCTION_PUBLISH = "production_publish"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUDIT_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ── Mode de fonctionnement ────────────────────────────────────────────
    mode: AuditMode = AuditMode.AUDIT_READONLY

    # ── Base de données ───────────────────────────────────────────────────
    # SQLite par défaut (développement, tests, environnements sans Docker) ;
    # PostgreSQL en déploiement : AUDIT_DATABASE_URL=postgresql+psycopg2://…
    # Le chemin par défaut est absolu (ancré sur audit-system/var/) : voir _PKG_ROOT.
    database_url: str = f"sqlite:///{_PKG_ROOT / 'var' / 'daat_audit.db'}"

    # ── Périmètre du crawl (MVP §2) ───────────────────────────────────────
    base_url: str = "https://daattorah.com"
    siman_start: int = 242
    siman_end: int = 269
    langue: str = "fr"
    niveau: str = "base"

    # ── Politesse du crawler (§5, §24) ────────────────────────────────────
    crawl_delay_seconds: float = 1.5
    request_timeout_seconds: float = 30.0
    max_redirects: int = 5
    user_agent: str = (
        "DaatTorah-AuditBot/0.1 (audit interne du site ; "
        "+https://github.com/yossefhs/Daat.ai ; contact: yossefhs@gmail.com)"
    )

    # Vérification des liens internes (optionnelle : multiplie les requêtes)
    check_links: bool = False
    max_links_checked: int = 200

    # Faisceau CA pour environnements derrière un proxy TLS d'entreprise.
    # Vide → certificats système par défaut.
    ca_bundle: str = ""


def get_settings() -> Settings:
    """Instancie la configuration (pas de cache : les tests la surchargent)."""
    return Settings()
