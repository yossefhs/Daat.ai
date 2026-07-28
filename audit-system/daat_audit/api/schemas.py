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
