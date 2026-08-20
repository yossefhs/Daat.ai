# -*- coding: utf-8 -*-
"""Registre des décisions de relecture, et son application au moteur (§14).

Une décision rendue sur un signalement doit valoir pour **ce signalement-là**,
et pour lui seul. C'est la contrainte qui commande tout ce module.

Un exemple le montre mieux qu'une règle. Au siman 263, la relecture a jugé
qu'entre ``חביות`` et ``גרבי`` — deux mots pour des récipients — l'écart est une
variante d'édition et non une erreur. Inscrire ce couple dans la table des
variantes connues aurait été commode et faux : ailleurs, la substitution peut
porter un sens. Une décision de relecture porte sur un passage, pas sur un mot.

Le registre identifie donc chaque signalement par une **empreinte** calculée
sur ce qui le définit — la page, la règle, le texte cité, la référence mise en
cause. Le même texte cité à un autre endroit, ou confronté à une autre source,
donne une autre empreinte et reste examiné.

Quatre décisions, et une seule ferme le dossier :

===========================  ===========================================
``error``                    erreur réelle ; le contenu a été corrigé
``accepted_variant``         variante d'édition légitime ; ne pas modifier
``false_positive``           le moteur avait tort ; ne pas modifier
``needs_rav_review``         **reste ouvert** — aucune conclusion automatique
===========================  ===========================================

``needs_rav_review`` ne masque rien : le signalement continue d'être produit et
de figurer dans les rapports. Une question laissée au Rav n'est pas une
question réglée, et le registre ne doit jamais pouvoir la clore de lui-même.

L'historique est cumulatif : une décision nouvelle s'ajoute, aucune n'est
effacée. ``decisions`` conserve la suite complète pour chaque signalement, et
c'est la dernière qui fait foi.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from dataclasses import dataclass, field
from typing import Iterable

REGISTRE = pathlib.Path(__file__).resolve().parent / "data" / "triage-decisions.json"

#: Décisions qui closent un signalement — le moteur cesse de le produire.
CLOSES = {"accepted_variant", "false_positive", "error"}
#: Décision qui laisse le dossier ouvert, quoi qu'il arrive.
OUVERTE = "needs_rav_review"

_ESPACES = re.compile(r"\s+")
_BALISES = re.compile(r"<[^>]+>")


def empreinte(*, siman: int | str | None, niveau: str | None, regle: str,
              citation: str, ref: str | None) -> str:
    """Identifiant stable d'un signalement.

    Volontairement calculée sur le **texte cité** et non sur un identifiant de
    base : les identifiants sont réattribués à chaque campagne, alors qu'un
    signalement est le même tant que la page dit la même chose de la même
    source. Volontairement calculée aussi sur la **référence** : la même
    citation confrontée à une autre source est une autre question.
    """
    citation = _ESPACES.sub(" ", _BALISES.sub(" ", citation or "")).strip()
    graine = "\x1f".join([
        str(siman or ""), (niveau or ""), regle or "",
        citation, (ref or ""),
    ])
    return hashlib.sha256(graine.encode("utf-8")).hexdigest()[:32]


@dataclass
class Decision:
    id: int | None
    decision: str
    reviewer_role: str
    source: str
    resolved: bool
    empreinte: str
    siman: int | None = None
    niveau: str | None = None
    regle: str = "CIT-001"
    ref: str | None = None
    note: str = ""

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "decision": self.decision,
            "reviewer_role": self.reviewer_role,
            "source": self.source,
            "resolved": self.resolved,
            "fingerprint": self.empreinte,
            "siman": self.siman,
            "niveau": self.niveau,
            "rule": self.regle,
            "ref": self.ref,
            "note": self.note,
        }

    @classmethod
    def from_json(cls, d: dict) -> "Decision":
        return cls(
            id=d.get("id"), decision=d["decision"],
            reviewer_role=d.get("reviewer_role", ""), source=d.get("source", ""),
            resolved=bool(d.get("resolved")), empreinte=d["fingerprint"],
            siman=d.get("siman"), niveau=d.get("niveau"),
            regle=d.get("rule", "CIT-001"), ref=d.get("ref"),
            note=d.get("note", ""),
        )


@dataclass
class Registre:
    """Décisions connues, indexées par empreinte. La dernière fait foi."""

    par_empreinte: dict[str, list[Decision]] = field(default_factory=dict)

    @classmethod
    def charger(cls, chemin: pathlib.Path | None = None) -> "Registre":
        chemin = chemin or REGISTRE
        if not chemin.exists():
            return cls()
        brut = json.loads(chemin.read_text(encoding="utf-8"))
        reg = cls()
        for d in brut.get("decisions", []):
            reg.ajouter(Decision.from_json(d))
        return reg

    def ajouter(self, decision: Decision) -> None:
        self.par_empreinte.setdefault(decision.empreinte, []).append(decision)

    def derniere(self, emp: str) -> Decision | None:
        suite = self.par_empreinte.get(emp)
        return suite[-1] if suite else None

    def est_close(self, emp: str) -> bool:
        """Ce signalement a-t-il été tranché, et le dossier est-il fermé ?

        ``needs_rav_review`` rend toujours ``False`` : une question laissée au
        Rav reste posée, et le registre ne peut pas la clore.
        """
        derniere = self.derniere(emp)
        if derniere is None:
            return False
        return derniere.decision in CLOSES and derniere.decision != OUVERTE

    def ouverts(self) -> list[Decision]:
        """Signalements laissés à la décision du Rav, dans l'ordre des ids."""
        restants = [d for suite in self.par_empreinte.values()
                    if (d := suite[-1]).decision == OUVERTE]
        return sorted(restants, key=lambda d: (d.id is None, d.id))

    def ecrire(self, chemin: pathlib.Path | None = None, *, version: str = "1") -> None:
        chemin = chemin or REGISTRE
        chemin.parent.mkdir(parents=True, exist_ok=True)
        toutes: list[Decision] = [d for suite in self.par_empreinte.values() for d in suite]
        toutes.sort(key=lambda d: (d.id is None, d.id, d.decision))
        chemin.write_text(
            json.dumps(
                {"version": version,
                 "note": ("Historique cumulatif : une décision s'ajoute, aucune "
                          "n'est effacée. La dernière de chaque empreinte fait foi."),
                 "decisions": [d.to_json() for d in toutes]},
                ensure_ascii=False, indent=1,
            ) + "\n",
            encoding="utf-8",
        )

    def __len__(self) -> int:
        return sum(len(s) for s in self.par_empreinte.values())


def compter(decisions: Iterable[Decision]) -> dict[str, int]:
    out: dict[str, int] = {}
    for d in decisions:
        out[d.decision] = out.get(d.decision, 0) + 1
    return out
