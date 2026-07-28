# -*- coding: utf-8 -*-
"""Métriques de fiabilité par règle (§21).

Une règle d'audit n'a de valeur que si l'on sait à quelle fréquence elle a
raison. Ce module recalcule, à partir des décisions humaines déjà rendues, la
précision de chaque règle — et permet ainsi de retirer ou d'amender celles qui
produisent surtout du bruit.

Deux précautions de fond :

- **Une règle sans décision humaine n'a pas de précision**, et le champ vaut
  ``None`` plutôt que 0 ou 1. Afficher « 100 % » pour une règle jamais jugée
  serait exactement le genre d'hypothèse présentée comme une preuve que le
  cahier des charges proscrit (§4).
- **Une source indisponible n'est pas un faux positif.** Un signalement classé
  ``SOURCE_UNAVAILABLE`` n'est pas comptabilisé : il ne dit rien sur la règle,
  seulement sur la disponibilité du fournisseur ce jour-là.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import AuditFinding, AuditRule, FindingStatus

# Le signalement a été retenu comme réel par un humain.
VALIDES = {
    FindingStatus.EDITOR_APPROVED,
    FindingStatus.RABBINIC_APPROVED,
    FindingStatus.READY_FOR_STAGING,
    FindingStatus.PUBLISHED,
}
# Le signalement a été écarté sur le fond.
REJETES = {FindingStatus.REJECTED, FindingStatus.EDITORIAL_VARIANT}
# La détection elle-même était fautive.
FAUX_POSITIFS = {FindingStatus.FALSE_POSITIVE}
# Ni l'un ni l'autre : en attente, ou indécidable faute de source.
NEUTRES = {
    FindingStatus.NEW,
    FindingStatus.AUTOMATICALLY_ANALYZED,
    FindingStatus.ADMIN_REVIEW_REQUIRED,
    FindingStatus.RABBINIC_REVIEW_REQUIRED,
    FindingStatus.SOURCE_UNAVAILABLE,
    FindingStatus.CLOSED,
}


@dataclass
class RuleStats:
    code: str
    alerts: int = 0
    validated: int = 0
    rejected: int = 0
    false_positives: int = 0
    pending: int = 0

    @property
    def judged(self) -> int:
        return self.validated + self.rejected + self.false_positives

    @property
    def precision(self) -> float | None:
        """Part des signalements jugés qui se sont révélés réels.

        ``None`` tant qu'aucun humain n'a tranché : une règle non éprouvée
        n'a pas de précision, et prétendre le contraire serait une hypothèse
        présentée comme une preuve.
        """
        return self.validated / self.judged if self.judged else None


def compute(session: Session) -> list[RuleStats]:
    """Statistiques par règle, calculées depuis les signalements archivés."""
    lignes = session.execute(
        select(AuditFinding.rule_code, AuditFinding.status, func.count())
        .group_by(AuditFinding.rule_code, AuditFinding.status)
    ).all()

    par_code: dict[str, RuleStats] = {}
    for code, statut, total in lignes:
        stats = par_code.setdefault(code, RuleStats(code=code))
        stats.alerts += total
        if statut in VALIDES:
            stats.validated += total
        elif statut in REJETES:
            stats.rejected += total
        elif statut in FAUX_POSITIFS:
            stats.false_positives += total
        else:
            stats.pending += total

    return sorted(par_code.values(), key=lambda s: s.code)


def sync_rules(session: Session) -> list[RuleStats]:
    """Reporte les statistiques dans la table ``audit_rules``.

    ``autocorrect_allowed`` n'est jamais activé ici, quelle que soit la
    précision constatée : l'autorisation de corriger seul est une décision
    humaine, pas une conséquence d'un compteur.
    """
    stats = compute(session)
    existantes = {
        r.code: r for r in session.execute(select(AuditRule)).scalars().all()
    }

    for s in stats:
        regle = existantes.get(s.code)
        if regle is None:
            regle = AuditRule(code=s.code, name=s.code,
                              category=s.code.split("-")[0].lower(), version="1.0")
            session.add(regle)
        regle.alerts_total = s.alerts
        regle.validated_total = s.validated
        regle.rejected_total = s.rejected
        regle.false_positives_total = s.false_positives

    session.commit()
    return stats


def format_table(stats: list[RuleStats]) -> str:
    """Rendu lisible en console."""
    if not stats:
        return "Aucun signalement archivé : aucune précision à calculer."
    lignes = [f"{'Règle':<12} {'Alertes':>8} {'Jugés':>7} {'Réels':>7} {'Précision':>10}"]
    for s in stats:
        precision = "—" if s.precision is None else f"{s.precision:.0%}"
        lignes.append(
            f"{s.code:<12} {s.alerts:>8} {s.judged:>7} {s.validated:>7} {precision:>10}"
        )
    lignes.append("\n« — » : aucune décision humaine encore rendue sur cette règle.")
    return "\n".join(lignes)
