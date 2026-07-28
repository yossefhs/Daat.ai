# -*- coding: utf-8 -*-
"""Moteur SQLAlchemy et fabrique de sessions.

SQLite par défaut (dev/tests, aucun service externe requis), PostgreSQL en
déploiement via ``AUDIT_DATABASE_URL``. Le schéma est géré par Alembic ;
``create_all`` ne sert qu'aux tests.
"""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import Settings


def make_engine(settings: Settings) -> Engine:
    kwargs: dict = {"future": True}
    url = settings.database_url
    if url.startswith("sqlite"):
        # Le crawl tourne dans un thread de fond (FastAPI BackgroundTasks).
        kwargs["connect_args"] = {"check_same_thread": False}
        # SQLite ne crée pas le répertoire parent : sur un clone frais,
        # var/ n'existe pas (git-ignoré) et toutes les commandes échoueraient.
        if url.startswith("sqlite:///"):
            db_path = Path(url.removeprefix("sqlite:///"))
            if db_path.name and db_path.name != ":memory:":
                db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url, **kwargs)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)
