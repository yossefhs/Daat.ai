# -*- coding: utf-8 -*-
"""Schéma et énumérations (§11, §12, §14, §17, §21)."""
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from daat_audit.models import (
    AuditFinding,
    AuditRule,
    BlockType,
    ContentBlock,
    FindingStatus,
    Page,
    PageVersion,
    Risk,
    Severity,
)

TABLES_ATTENDUES = {
    "pages", "page_versions", "content_blocks", "parsed_references",
    "source_texts", "audit_findings", "suggested_corrections",
    "admin_decisions", "rabbinic_reviews", "audit_logs",
    "terminology_dictionary", "source_providers", "audit_rules", "crawl_jobs",
}


def test_les_quatorze_tables_du_cahier_des_charges_existent(engine):
    assert TABLES_ATTENDUES <= set(inspect(engine).get_table_names())


def test_enumerations_du_cahier_des_charges():
    assert {s.value for s in Severity} == {
        "P0_CRITICAL", "P1_MAJOR", "P2_SIGNIFICANT", "P3_MINOR", "P4_SUGGESTION"
    }
    assert {r.value for r in Risk} == {"LOW", "MEDIUM", "HIGH", "HALAKHIC"}
    assert FindingStatus.RABBINIC_REVIEW_REQUIRED.value == "RABBINIC_REVIEW_REQUIRED"
    assert len(FindingStatus) == 13
    assert len(BlockType) == 13


def test_url_de_page_unique(session):
    session.add(Page(url="https://daattorah.com/oh/242/base", siman=242))
    session.commit()
    session.add(Page(url="https://daattorah.com/oh/242/base", siman=242))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_stable_id_unique_par_version(session):
    page = Page(url="https://daattorah.com/oh/268/base", siman=268)
    version = PageVersion(page=page)
    session.add_all([
        page, version,
        ContentBlock(page_version=version, stable_id="OH-268-BASE-FR-P014",
                     order_index=14, block_type=BlockType.PARAGRAPHE),
        ContentBlock(page_version=version, stable_id="OH-268-BASE-FR-P014",
                     order_index=15, block_type=BlockType.PARAGRAPHE),
    ])
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_confiance_et_risque_sont_deux_axes_independants(session):
    """§12 : le modèle porte confiance ET risque comme colonnes distinctes,
    et un finding naît en statut NEW (défaut de colonne). NB : ce test ne
    vérifie PAS la politique d'autocorrection — aucune logique
    d'autocorrection n'existe en Phase 1, c'est précisément l'invariant
    (voir test_safety et AuditRule.autocorrect_allowed=False)."""
    finding = AuditFinding(
        category="citation", subcategory="attribution_incorrecte",
        confidence=0.99, severity=Severity.P0_CRITICAL, risk=Risk.HALAKHIC,
    )
    session.add(finding)
    session.commit()
    assert finding.status is FindingStatus.NEW
    assert (finding.confidence, finding.risk) == (0.99, Risk.HALAKHIC)


def test_precision_de_regle(session):
    rule = AuditRule(code="TECH-001", name="Espace double",
                     alerts_total=100, validated_total=98,
                     rejected_total=1, false_positives_total=1)
    session.add(rule)
    session.commit()
    assert rule.precision == pytest.approx(0.98)
    assert rule.autocorrect_allowed is False, "jamais d'autocorrection par défaut"

    vierge = AuditRule(code="TECH-002", name="Sans historique")
    assert vierge.precision is None
