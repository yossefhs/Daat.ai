# -*- coding: utf-8 -*-
"""Workflow de validation (§13, §14, §20)."""
import pytest
from sqlalchemy import select

from daat_audit.models import (
    AdminDecision,
    AuditFinding,
    AuditLog,
    FindingStatus,
    Page,
    RabbinicReview,
    Risk,
    Severity,
)
from daat_audit.workflow import (
    TRANSITIONS,
    Role,
    WorkflowError,
    actions_possibles,
    appliquer,
    historique,
    repondre_rav,
)


@pytest.fixture()
def finding(session):
    page = Page(url="https://daattorah.com/oh/242/base", siman=242,
                langue="fr", niveau="base")
    session.add(page)
    session.commit()

    def creer(risk: Risk = Risk.LOW) -> AuditFinding:
        f = AuditFinding(
            page_id=page.id, category="citation", current_text="טקסט",
            explanation="écart constaté", confidence=0.9,
            severity=Severity.P2_SIGNIFICANT, risk=risk, rule_code="CIT-001",
        )
        session.add(f)
        session.commit()
        return f
    return creer


# ── La règle centrale ────────────────────────────────────────────────────

def test_un_signalement_halakhique_ne_peut_pas_etre_approuve_par_un_editeur(
        session, finding):
    """La garantie qui justifie tout le module. Le refus est dans la
    transition — pas dans l'interface, qu'un appel direct contournerait."""
    f = finding(Risk.HALAKHIC)
    with pytest.raises(WorkflowError, match="risque halakhique"):
        appliquer(session, f, "approve", Role.EDITOR, "yossef")
    assert f.status is FindingStatus.NEW, "l'état ne doit pas avoir bougé"


def test_le_rav_peut_approuver_un_signalement_halakhique(session, finding):
    f = finding(Risk.HALAKHIC)
    appliquer(session, f, "approve", Role.RAV, "rav")
    assert f.status is FindingStatus.EDITOR_APPROVED


def test_un_editeur_peut_approuver_un_signalement_technique(session, finding):
    f = finding(Risk.LOW)
    appliquer(session, f, "approve", Role.EDITOR, "yossef")
    assert f.status is FindingStatus.EDITOR_APPROVED


def test_lediteur_doit_passer_par_lescalade(session, finding):
    """Le chemin légitime pour un signalement halakhique."""
    f = finding(Risk.HALAKHIC)
    assert "approve" not in actions_possibles(f, Role.EDITOR)
    assert "escalate" in actions_possibles(f, Role.EDITOR)

    appliquer(session, f, "escalate", Role.EDITOR, "yossef", note="quel est l'avis ?")
    assert f.status is FindingStatus.RABBINIC_REVIEW_REQUIRED


def test_lediteur_ne_peut_pas_approuver_au_nom_du_rav(session, finding):
    f = finding(Risk.HALAKHIC)
    appliquer(session, f, "escalate", Role.EDITOR, "yossef")
    with pytest.raises(WorkflowError, match="réservé au rôle rav"):
        appliquer(session, f, "rabbinic_approve", Role.EDITOR, "yossef")


# ── Aucune publication ───────────────────────────────────────────────────

def test_aucune_transition_ne_mene_a_publie():
    """La publication n'est pas implémentée : l'état ne doit être atteignable
    par aucun chemin du workflow."""
    cibles = {t.target for t in TRANSITIONS.values()}
    assert FindingStatus.PUBLISHED not in cibles


def test_le_workflow_sarrete_a_la_preproduction(session, finding):
    f = finding(Risk.LOW)
    appliquer(session, f, "approve", Role.EDITOR, "yossef")
    appliquer(session, f, "ready_for_staging", Role.EDITOR, "yossef")
    assert f.status is FindingStatus.READY_FOR_STAGING
    assert "publish" not in actions_possibles(f, Role.RAV)


def test_la_preproduction_exige_une_approbation_prealable(session, finding):
    f = finding(Risk.LOW)
    with pytest.raises(WorkflowError, match="n'est possible que depuis"):
        appliquer(session, f, "ready_for_staging", Role.EDITOR, "yossef")


# ── Traçabilité et retour arrière ────────────────────────────────────────

def test_chaque_decision_est_tracee_deux_fois(session, finding):
    """Une ligne de décision *et* une entrée au journal (§4)."""
    f = finding(Risk.LOW)
    appliquer(session, f, "approve", Role.EDITOR, "yossef", note="vérifié")

    decision = session.execute(select(AdminDecision)).scalars().one()
    assert decision.user == "yossef"
    assert decision.previous_status == "NEW"
    assert decision.new_status == "EDITOR_APPROVED"
    assert decision.note == "vérifié"

    entrees = [a for a in session.execute(select(AuditLog)).scalars().all()
               if a.action.startswith("decision.")]
    assert len(entrees) == 1
    assert "NEW → EDITOR_APPROVED" in entrees[0].justification
    assert "rôle editor" in entrees[0].justification


def test_la_source_justifiant_la_decision_est_conservee(session, finding):
    """§4 : afficher les sources utilisées."""
    f = finding(Risk.LOW)
    appliquer(session, f, "reject", Role.EDITOR, "yossef",
              source_attached="Beitsa 15b, éd. Vilna")
    assert session.execute(select(AdminDecision)).scalars().one().source_attached \
        == "Beitsa 15b, éd. Vilna"


def test_le_retour_arriere_ajoute_une_ligne_et_nen_efface_aucune(session, finding):
    """§4 : permettre un retour arrière, conserver toutes les versions."""
    f = finding(Risk.LOW)
    appliquer(session, f, "approve", Role.EDITOR, "yossef")
    appliquer(session, f, "reopen", Role.EDITOR, "yossef", note="doute")

    assert f.status is FindingStatus.ADMIN_REVIEW_REQUIRED
    chaine = historique(session, f)
    assert [d.action for d in chaine] == ["approve", "reopen"]
    assert chaine[0].new_status == "EDITOR_APPROVED"   # la trace est intacte


def test_un_signalement_reouvert_reste_soumis_a_la_regle_halakhique(session, finding):
    """Le retour arrière ne doit pas ouvrir une porte dérobée."""
    f = finding(Risk.HALAKHIC)
    appliquer(session, f, "escalate", Role.EDITOR, "yossef")
    appliquer(session, f, "reopen", Role.EDITOR, "yossef")
    with pytest.raises(WorkflowError, match="risque halakhique"):
        appliquer(session, f, "approve", Role.EDITOR, "yossef")


# ── Avis du Rav ──────────────────────────────────────────────────────────

def test_lescalade_ouvre_une_question_au_rav(session, finding):
    f = finding(Risk.HALAKHIC)
    appliquer(session, f, "escalate", Role.EDITOR, "yossef",
              note="la citation diffère de l'édition Vilna")
    review = session.execute(select(RabbinicReview)).scalars().one()
    assert review.status == "pending"
    assert "édition Vilna" in review.question


def test_la_reponse_du_rav_cloture_la_question_et_lentourage(session, finding):
    f = finding(Risk.HALAKHIC)
    appliquer(session, f, "escalate", Role.EDITOR, "yossef")
    repondre_rav(session, f, "Rav Samama", "confirmé, corriger", confirme=True)

    review = session.execute(select(RabbinicReview)).scalars().one()
    assert review.status == "answered"
    assert review.reviewer == "Rav Samama" and review.answered_at
    assert f.status is FindingStatus.RABBINIC_APPROVED


def test_le_rav_peut_ecarter_le_signalement(session, finding):
    f = finding(Risk.HALAKHIC)
    appliquer(session, f, "escalate", Role.EDITOR, "yossef")
    repondre_rav(session, f, "Rav Samama", "variante d'édition", confirme=False)
    assert f.status is FindingStatus.REJECTED


def test_repondre_sans_question_ouverte_echoue(session, finding):
    f = finding(Risk.LOW)
    with pytest.raises(WorkflowError, match="aucune question en attente"):
        repondre_rav(session, f, "Rav Samama", "…", confirme=True)


# ── Divers ───────────────────────────────────────────────────────────────

def test_action_inconnue_refusee(session, finding):
    with pytest.raises(WorkflowError, match="action inconnue"):
        appliquer(session, finding(), "supprimer", Role.EDITOR, "yossef")


def test_appliquer_deux_fois_la_meme_action_echoue(session, finding):
    f = finding(Risk.LOW)
    appliquer(session, f, "reject", Role.EDITOR, "yossef")
    with pytest.raises(WorkflowError, match="déjà en"):
        appliquer(session, f, "reject", Role.EDITOR, "yossef")


def test_actions_possibles_depend_du_role(session, finding):
    f = finding(Risk.HALAKHIC)
    appliquer(session, f, "escalate", Role.EDITOR, "yossef")
    assert "rabbinic_approve" not in actions_possibles(f, Role.EDITOR)
    assert "rabbinic_approve" in actions_possibles(f, Role.RAV)
