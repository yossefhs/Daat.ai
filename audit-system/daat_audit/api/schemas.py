# -*- coding: utf-8 -*-
"""Schémas Pydantic de l'API (documentés dans OpenAPI, §18)."""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class HealthOut(BaseModel):
    status: str
    mode: str
    version: str


class CrawlIn(BaseModel):
    simanim: str | None = Field(
        default=None, description="Ex. « 242-269 » ou « 242,243 ». Défaut : périmètre configuré.",
        examples=["242-269"], max_length=200, pattern=r"^[0-9,\-\s]+$",
    )
    # Tri-état : None = valeur du serveur ; True/False = choix explicite du client.
    # (Un booléen à défaut False confondrait « non précisé » et « désactivé ».)
    check_links: bool | None = Field(
        default=None, description="Vérifier aussi les liens internes (défaut : configuration serveur)."
    )


class CrawlJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    mode: str | None
    started_at: dt.datetime
    finished_at: dt.datetime | None
    pages_total: int
    pages_ok: int
    pages_failed: int
    pages_changed: int
    pages_missing: int
    broken_links: int


class PageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    siman: int | None
    langue: str
    niveau: str
    titre: str | None
    http_status: int | None
    redirect_target: str | None
    audit_status: str
    first_seen_at: dt.datetime
    last_crawled_at: dt.datetime | None
    last_modified_at: dt.datetime | None
    current_text_sha256: str | None


class PageVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fetched_at: dt.datetime
    http_status: int | None
    text_sha256: str | None
    html_sha256: str | None
    is_change: bool
    text_clean: str | None = None
    html_raw: str | None = None


class PageDetailOut(PageOut):
    versions: list[PageVersionOut] = []


class FindingOut(BaseModel):
    """Un signalement. ``proposed_correction`` reste nul pour tout ce qui
    touche au contenu : le système propose un constat, jamais une réécriture."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    page_id: int
    block_id: int | None
    rule_code: str
    category: str
    subcategory: str | None
    severity: str
    risk: str
    status: str
    confidence: float
    current_text: str
    source_text: str | None
    proposed_correction: str | None
    explanation: str
    sources: str | None
    created_at: dt.datetime | None


class RuleStatsOut(BaseModel):
    """Fiabilité d'une règle. ``precision`` vaut ``null`` tant qu'aucune
    décision humaine n'a été rendue — jamais 0 ni 1 par défaut."""

    code: str
    alerts: int
    judged: int
    validated: int
    rejected: int
    false_positives: int
    pending: int
    precision: float | None


class DecisionIn(BaseModel):
    """Une décision. Le rôle n'y figure pas : il vient du secret présenté."""

    action: str = Field(description="approve, reject, false_positive, escalate…")
    note: str | None = Field(default=None, max_length=4000)
    source_attached: str | None = Field(
        default=None, max_length=4000,
        description="Source justifiant la décision (§4 : afficher les sources utilisées)",
    )


class DecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    finding_id: int
    user: str
    action: str
    note: str | None
    source_attached: str | None
    previous_status: str | None
    new_status: str | None
    decided_at: dt.datetime | None


class RabbinicAnswerIn(BaseModel):
    answer: str = Field(min_length=1, max_length=8000)
    confirme: bool = Field(description="Le Rav confirme-t-il le signalement ?")


class RabbinicReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    finding_id: int
    reviewer: str | None
    question: str | None
    answer: str | None
    status: str
    asked_at: dt.datetime | None
    answered_at: dt.datetime | None


class FindingDetailOut(FindingOut):
    """Détail d'un signalement : son état, son historique, et ce qui est
    possible pour le rôle qui regarde."""

    available_actions: list[str] = []
    decisions: list[DecisionOut] = []
    rabbinic_reviews: list[RabbinicReviewOut] = []
