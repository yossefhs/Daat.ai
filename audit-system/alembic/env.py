# -*- coding: utf-8 -*-
"""Environnement Alembic : l'URL vient de AUDIT_DATABASE_URL si présente."""
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from daat_audit.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from daat_audit.config import get_settings  # noqa: E402

env_url = os.environ.get("AUDIT_DATABASE_URL") or get_settings().database_url
config.set_main_option("sqlalchemy.url", env_url)

# Même garantie que daat_audit.db.make_engine : le parent d'une base SQLite
# fichier est créé si besoin (clone frais, var/ git-ignoré).
if env_url.startswith("sqlite:///"):
    from pathlib import Path

    db_path = Path(env_url.removeprefix("sqlite:///"))
    if db_path.name and db_path.name != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
