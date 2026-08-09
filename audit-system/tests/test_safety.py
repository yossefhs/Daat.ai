# -*- coding: utf-8 -*-
"""Garde-fous (§4, §20) : aucune écriture vers le site n'est possible."""
import pytest

from daat_audit.config import AuditMode, Settings
from daat_audit.safety import (
    ModeError,
    PublicationNotImplementedError,
    ensure_site_write_allowed,
    is_readonly,
)


def _settings(mode: AuditMode) -> Settings:
    return Settings(_env_file=None, mode=mode)


def test_mode_par_defaut_est_readonly():
    assert Settings(_env_file=None).mode is AuditMode.AUDIT_READONLY


def test_ecriture_interdite_en_readonly():
    with pytest.raises(ModeError):
        ensure_site_write_allowed(_settings(AuditMode.AUDIT_READONLY))


def test_ecriture_interdite_en_staging():
    with pytest.raises(ModeError):
        ensure_site_write_allowed(_settings(AuditMode.STAGING_REVIEW))


def test_publication_non_implementee_meme_en_mode_publish():
    """Phase 1 : même production_publish refuse — la publication n'existe pas."""
    with pytest.raises(PublicationNotImplementedError):
        ensure_site_write_allowed(_settings(AuditMode.PRODUCTION_PUBLISH))


def test_is_readonly():
    assert is_readonly(_settings(AuditMode.AUDIT_READONLY))
    assert not is_readonly(_settings(AuditMode.STAGING_REVIEW))


def test_aucun_code_du_paquet_ne_reference_les_sources_du_site():
    """Défense en profondeur, portée EXACTE : vérifie que le paquet ne
    référence jamais les répertoires sources du site (littéraux). Ne prétend
    pas détecter un chemin construit dynamiquement — l'invariant principal
    est porté par ensure_site_write_allowed, testé ci-dessus, et par
    l'assertion de méthode HTTP (GET/HEAD) dans les handlers simulés."""
    import pathlib

    package_dir = pathlib.Path(__file__).resolve().parents[1] / "daat_audit"
    for py in package_dir.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        for interdit in ("sources/shabbat", "sources/orah-haim", "sources/yoreh-deah"):
            assert interdit not in text, f"{py} référence les sources du site"
