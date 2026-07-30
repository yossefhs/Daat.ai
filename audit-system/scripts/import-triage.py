#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Applique au workflow les décisions rendues dans le fichier de tri rapide.

    python3 scripts/import-triage.py --fichier decisions.txt [--dry-run]
    cat decisions.txt | python3 scripts/import-triage.py

Le format rendu par la page de tri :

    DAAT-TRIAGE v1 role=rav
    412 erreur
    418 variante
    421 faux

Chaque ligne devient une décision **tracée** : une entrée dans
``admin_decisions`` et une au journal ``audit_logs``, avec le rôle qui l'a
rendue. Rien n'est écrasé, et tout reste réversible — un retour arrière ajoute
une ligne, il n'en efface aucune.

La garantie centrale du §14 s'applique ici aussi, et c'est le point important :
si le tri a été fait **en tant qu'éditeur**, un « erreur réelle » sur un
signalement à risque halakhique n'est pas appliqué comme une approbation — il
est *escaladé au Rav*. Un tri rapide ne doit pas devenir un contournement.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from daat_audit.config import get_settings                       # noqa: E402
from daat_audit.db import make_engine, make_session_factory      # noqa: E402
from daat_audit.models import AuditFinding, Risk                 # noqa: E402
from daat_audit.workflow import (                                # noqa: E402
    Role,
    WorkflowError,
    appliquer,
)

# Réponse du tri → action du workflow.
ACTIONS = {
    "contenu": "approve",              # le texte de la page est fautif
    "reference": "approve",            # la référence est fausse — défaut réel
    "variante": "editorial_variant",   # variante d'édition ou d'orthographe
    "pas_citation": "false_positive",  # paraphrase, titre : la détection a tort
    "aucune_erreur": "false_positive", # texte ET référence justes : signalement infondé
    "rav": "escalate",
    # Anciennes réponses, conservées pour relire un tri déjà rendu.
    "erreur": "approve",
    "faux": "false_positive",
    "indecidable": "source_unavailable",
}


def lire(texte: str) -> tuple[Role, list[tuple[int, str]]]:
    role = Role.EDITOR
    decisions: list[tuple[int, str]] = []
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        if ligne.upper().startswith("DAAT-TRIAGE"):
            if "role=rav" in ligne:
                role = Role.RAV
            continue
        morceaux = ligne.split()
        if len(morceaux) != 2 or not morceaux[0].isdigit():
            raise ValueError(f"ligne illisible : « {ligne} »")
        code = morceaux[1].lower()
        if code not in ACTIONS:
            raise ValueError(
                f"réponse inconnue : « {code} ». Attendu : {', '.join(ACTIONS)}"
            )
        decisions.append((int(morceaux[0]), code))
    if not decisions:
        raise ValueError("aucune décision dans l'entrée")
    return role, decisions


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fichier", type=pathlib.Path)
    ap.add_argument("--user", default=None, help="nom porté au journal")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    texte = args.fichier.read_text(encoding="utf-8") if args.fichier else sys.stdin.read()
    try:
        role, decisions = lire(texte)
    except ValueError as exc:
        print(f"Entrée invalide : {exc}", file=sys.stderr)
        return 2

    user = args.user or role.value
    settings = get_settings()
    applique = escalade = echecs = 0

    with make_session_factory(make_engine(settings))() as session:
        for finding_id, code in decisions:
            finding = session.get(AuditFinding, finding_id)
            if finding is None:
                print(f"  ! signalement {finding_id} introuvable", file=sys.stderr)
                echecs += 1
                continue

            action = ACTIONS[code]
            # Un « erreur réelle » rendu par un éditeur sur un signalement
            # halakhique devient une escalade, jamais une approbation.
            if (action == "approve" and role is not Role.RAV
                    and finding.risk is Risk.HALAKHIC):
                action = "escalate"
                escalade += 1

            if args.dry_run:
                print(f"  {finding_id}: {code} → {action}")
                applique += 1
                continue
            try:
                appliquer(session, finding, action, role, user,
                          note=f"tri rapide ({code})")
                applique += 1
            except WorkflowError as exc:
                print(f"  ! {finding_id} : {exc}", file=sys.stderr)
                echecs += 1

    print(f"\n{applique} décision(s) {'simulée(s)' if args.dry_run else 'appliquée(s)'}"
          f" en tant que {role.value}")
    if escalade:
        print(f"{escalade} d'entre elles escaladées au Rav : un éditeur ne peut "
              "pas approuver seul un signalement halakhique.")
    if echecs:
        print(f"{echecs} en échec (voir ci-dessus).", file=sys.stderr)
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
