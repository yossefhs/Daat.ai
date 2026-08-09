# -*- coding: utf-8 -*-
"""Fixtures des tests : base SQLite en mémoire, configuration isolée, HTML réel.

Aucun test ne touche le réseau : le crawler est exercé via httpx.MockTransport.
"""
from __future__ import annotations

import pathlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from daat_audit.config import Settings
from daat_audit.models import Base

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture()
def settings() -> Settings:
    """Configuration de test : délai nul (transport simulé), périmètre réduit."""
    return Settings(
        _env_file=None,
        database_url="sqlite://",
        crawl_delay_seconds=0.0,
        siman_start=242,
        siman_end=244,
    )


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture()
def session(engine):
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as s:
        yield s


@pytest.fixture()
def sample_html() -> str:
    """Page réelle du site (siman 242, niveau base, FR), archivée en fixture."""
    return (FIXTURES / "siman-242-base.html").read_text(encoding="utf-8")
