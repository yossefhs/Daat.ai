# -*- coding: utf-8 -*-
"""Métriques de fiabilité par règle (§21, §20)."""
from sqlalchemy import select

from daat_audit.metrics import compute, format_table, sync_rules
from daat_audit.models import (
    AuditFinding,
    AuditRule,
    FindingStatus,
    Page,
    Risk,
    Severity,
)


def _finding(page, code: str, statut: FindingStatus) -> AuditFinding:
    return AuditFinding(
        page_id=page.id, category="citation", current_text="x",
        explanation="x", confidence=0.9, severity=Severity.P2_SIGNIFICANT,
        risk=Risk.HALAKHIC, rule_code=code, status=statut,
    )


def _page(session) -> Page:
    page = Page(url="https://daattorah.com/oh/242/base", siman=242,
                langue="fr", niveau="base")
    session.add(page)
    session.commit()
    return page


def test_une_regle_jamais_jugee_na_pas_de_precision(session):
    """Afficher « 100 % » pour une règle non éprouvée serait une hypothèse
    présentée comme une preuve (§4)."""
    page = _page(session)
    session.add(_finding(page, "CIT-001", FindingStatus.NEW))
    session.commit()

    stats = compute(session)[0]
    assert stats.alerts == 1 and stats.judged == 0
    assert stats.precision is None
    assert "—" in format_table([stats])


def test_precision_calculee_sur_les_seuls_signalements_juges(session):
    page = _page(session)
    for statut in (FindingStatus.RABBINIC_APPROVED, FindingStatus.RABBINIC_APPROVED,
                   FindingStatus.FALSE_POSITIVE, FindingStatus.NEW):
        session.add(_finding(page, "CIT-001", statut))
    session.commit()

    stats = compute(session)[0]
    assert (stats.alerts, stats.judged, stats.validated) == (4, 3, 2)
    assert abs(stats.precision - 2 / 3) < 1e-9
    assert stats.pending == 1


def test_source_indisponible_nest_pas_un_faux_positif(session):
    """Elle ne dit rien sur la règle, seulement sur le fournisseur."""
    page = _page(session)
    session.add(_finding(page, "CIT-001", FindingStatus.RABBINIC_APPROVED))
    session.add(_finding(page, "CIT-001", FindingStatus.SOURCE_UNAVAILABLE))
    session.commit()

    stats = compute(session)[0]
    assert stats.judged == 1 and stats.false_positives == 0
    assert stats.precision == 1.0


def test_variante_editoriale_compte_comme_rejet(session):
    """Le signalement était réel mais l'écart est une variante : la règle a
    parlé pour rien, cela doit peser sur sa précision."""
    page = _page(session)
    session.add(_finding(page, "EDIT-001", FindingStatus.EDITORIAL_VARIANT))
    session.commit()
    stats = compute(session)[0]
    assert stats.rejected == 1 and stats.precision == 0.0


def test_sync_ecrit_les_compteurs_sans_autoriser_lautocorrection(session):
    page = _page(session)
    session.add(_finding(page, "CIT-001", FindingStatus.RABBINIC_APPROVED))
    session.commit()
    sync_rules(session)

    regle = session.execute(select(AuditRule)).scalars().one()
    assert regle.code == "CIT-001"
    assert regle.validated_total == 1
    assert regle.precision == 1.0
    # Une précision de 100 % n'autorise pas la machine à corriger seule (§4).
    assert regle.autocorrect_allowed is False


def test_sync_est_idempotente(session):
    page = _page(session)
    session.add(_finding(page, "CIT-001", FindingStatus.RABBINIC_APPROVED))
    session.commit()
    sync_rules(session)
    sync_rules(session)
    regles = session.execute(select(AuditRule)).scalars().all()
    assert len(regles) == 1 and regles[0].alerts_total == 1
