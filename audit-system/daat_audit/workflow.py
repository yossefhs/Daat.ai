# -*- coding: utf-8 -*-
"""Workflow de validation des signalements (§13, §14).

La règle qui gouverne tout ce module :

    **Un signalement à risque halakhique ne peut jamais être approuvé par un
    éditeur seul.** Il doit passer par le Rav.

Ce n'est pas une précaution d'usage, c'est la raison d'être du système. Une
plateforme d'étude halakhique dont un outil automatique pourrait faire entrer
une correction de contenu sans qu'un rav l'ait vue ne vaut pas mieux que
l'erreur qu'elle prétend corriger. Le contrôle n'est donc pas dans l'interface
— où il suffirait d'un appel direct à l'API pour le contourner — mais ici,
dans la transition d'état elle-même, et il est verrouillé par un test.

Trois autres garanties du cahier des charges sont portées par ce module :

- **Traçabilité** : toute décision écrit une ligne dans ``admin_decisions``
  *et* dans le journal ``audit_logs``. Aucune ne modifie une décision passée.
- **Retour arrière** : ``reopen`` ramène un signalement à l'examen. L'historique
  n'est jamais effacé — on ajoute une décision, on n'en retire aucune.
- **Aucune publication** : ``PUBLISHED`` n'est atteignable par aucune
  transition. Le workflow s'arrête à ``READY_FOR_STAGING``, et la publication
  n'est pas implémentée (``safety.ensure_site_write_allowed``).
"""
from __future__ import annotations

import enum
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    AdminDecision,
    AuditFinding,
    AuditLog,
    FindingStatus,
    RabbinicReview,
    Risk,
    utcnow,
)


class Role(str, enum.Enum):
    """Qui décide. Le rôle vient du secret présenté, pas d'un champ envoyé."""

    EDITOR = "editor"
    RAV = "rav"


class WorkflowError(Exception):
    """Transition refusée. Le message est destiné à l'utilisateur."""


@dataclass(frozen=True)
class Transition:
    action: str
    target: FindingStatus
    roles: frozenset[Role]
    depuis: frozenset[FindingStatus] | None      # None = depuis n'importe quel état
    libelle: str


# États depuis lesquels un signalement est encore « en cours d'examen ».
OUVERTS = frozenset({
    FindingStatus.NEW,
    FindingStatus.AUTOMATICALLY_ANALYZED,
    FindingStatus.ADMIN_REVIEW_REQUIRED,
})

_TOUS = frozenset(Role)
_RAV = frozenset({Role.RAV})

TRANSITIONS: dict[str, Transition] = {
    t.action: t for t in [
        Transition("approve", FindingStatus.EDITOR_APPROVED, _TOUS, OUVERTS,
                   "retenir le signalement comme réel"),
        Transition("reject", FindingStatus.REJECTED, _TOUS, None,
                   "écarter le signalement sur le fond"),
        Transition("false_positive", FindingStatus.FALSE_POSITIVE, _TOUS, None,
                   "la détection elle-même était fautive"),
        Transition("editorial_variant", FindingStatus.EDITORIAL_VARIANT, _TOUS, None,
                   "écart réel mais variante éditoriale légitime"),
        Transition("source_unavailable", FindingStatus.SOURCE_UNAVAILABLE, _TOUS, None,
                   "source indisponible : indécidable en l'état"),
        Transition("escalate", FindingStatus.RABBINIC_REVIEW_REQUIRED, _TOUS, None,
                   "soumettre au Rav"),
        Transition("rabbinic_approve", FindingStatus.RABBINIC_APPROVED, _RAV,
                   frozenset({FindingStatus.RABBINIC_REVIEW_REQUIRED}),
                   "le Rav confirme le signalement"),
        Transition("rabbinic_reject", FindingStatus.REJECTED, _RAV,
                   frozenset({FindingStatus.RABBINIC_REVIEW_REQUIRED}),
                   "le Rav écarte le signalement"),
        Transition("ready_for_staging", FindingStatus.READY_FOR_STAGING, _TOUS,
                   frozenset({FindingStatus.EDITOR_APPROVED,
                              FindingStatus.RABBINIC_APPROVED}),
                   "préparer pour la préproduction (aucune publication)"),
        Transition("close", FindingStatus.CLOSED, _TOUS, None, "clore sans suite"),
        Transition("reopen", FindingStatus.ADMIN_REVIEW_REQUIRED, _TOUS, None,
                   "revenir en arrière et réexaminer"),
    ]
}

# Risques pour lesquels l'approbation d'un éditeur ne suffit pas.
RISQUES_RESERVES_AU_RAV = frozenset({Risk.HALAKHIC})


def actions_possibles(finding: AuditFinding, role: Role) -> list[str]:
    """Actions que ce rôle peut appliquer à ce signalement, ici et maintenant."""
    possibles = []
    for action, transition in TRANSITIONS.items():
        try:
            _verifier(finding, transition, role)
        except WorkflowError:
            continue
        possibles.append(action)
    return possibles


def _verifier(finding: AuditFinding, transition: Transition, role: Role) -> None:
    if role not in transition.roles:
        raise WorkflowError(
            f"« {transition.action} » est réservé au rôle "
            + " ou ".join(sorted(r.value for r in transition.roles))
        )
    if transition.depuis is not None and finding.status not in transition.depuis:
        attendus = ", ".join(sorted(s.value for s in transition.depuis))
        raise WorkflowError(
            f"« {transition.action} » n'est possible que depuis {attendus} "
            f"(état actuel : {finding.status.value})"
        )
    if finding.status == transition.target:
        raise WorkflowError(f"le signalement est déjà en {transition.target.value}")

    # La règle centrale du module.
    if (transition.target is FindingStatus.EDITOR_APPROVED
            and finding.risk in RISQUES_RESERVES_AU_RAV
            and role is not Role.RAV):
        raise WorkflowError(
            "un signalement à risque halakhique ne peut pas être approuvé par un "
            "éditeur : utiliser « escalate » pour le soumettre au Rav"
        )


def appliquer(
    session: Session,
    finding: AuditFinding,
    action: str,
    role: Role,
    user: str,
    note: str | None = None,
    source_attached: str | None = None,
) -> AdminDecision:
    """Applique une décision, la trace, et retourne la ligne de décision."""
    transition = TRANSITIONS.get(action)
    if transition is None:
        raise WorkflowError(
            f"action inconnue : {action}. Actions : {', '.join(sorted(TRANSITIONS))}"
        )
    _verifier(finding, transition, role)

    precedent = finding.status
    finding.status = transition.target

    decision = AdminDecision(
        finding_id=finding.id, user=user, action=action, note=note,
        source_attached=source_attached,
        previous_status=precedent.value, new_status=transition.target.value,
    )
    session.add(decision)

    # Une escalade ouvre une question au Rav, avec la note comme énoncé.
    if transition.target is FindingStatus.RABBINIC_REVIEW_REQUIRED:
        session.add(RabbinicReview(
            finding_id=finding.id, reviewer=None,
            question=note or finding.explanation,
            status="pending",
        ))

    session.add(AuditLog(
        user=user, action=f"decision.{action}",
        source=f"finding:{finding.id}",
        justification=(
            f"{precedent.value} → {transition.target.value} "
            f"(rôle {role.value}, risque {finding.risk.value})"
            + (f" — {note}" if note else "")
        ),
    ))
    session.commit()
    return decision


def repondre_rav(
    session: Session, finding: AuditFinding, reviewer: str, answer: str,
    confirme: bool,
) -> RabbinicReview:
    """Enregistre la réponse du Rav sur la question ouverte d'un signalement."""
    review = session.execute(
        select(RabbinicReview)
        .where(RabbinicReview.finding_id == finding.id,
               RabbinicReview.status == "pending")
        .order_by(RabbinicReview.id.desc())
    ).scalars().first()
    if review is None:
        raise WorkflowError("aucune question en attente pour ce signalement")

    review.reviewer = reviewer
    review.answer = answer
    review.status = "answered"
    review.answered_at = utcnow()

    appliquer(
        session, finding,
        "rabbinic_approve" if confirme else "rabbinic_reject",
        Role.RAV, reviewer, note=answer,
    )
    return review


def historique(session: Session, finding: AuditFinding) -> list[AdminDecision]:
    """Chaîne complète des décisions, de la plus ancienne à la plus récente."""
    return list(session.execute(
        select(AdminDecision)
        .where(AdminDecision.finding_id == finding.id)
        .order_by(AdminDecision.id)
    ).scalars().all())
