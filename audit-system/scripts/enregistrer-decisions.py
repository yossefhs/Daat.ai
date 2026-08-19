#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consigne au registre les décisions rendues sur un lot de signalements.

    python3 scripts/enregistrer-decisions.py --triage triage.html \\
                                             --decisions decisions.txt

``--triage`` est la page de tri produite par ``export-triage.py`` : elle porte,
dans son bloc ``const ITEMS``, le siman, le niveau, la règle, le texte cité et
la référence de chaque signalement. ``--decisions`` est le bloc rendu par le
relecteur, une ligne par identifiant.

Le script ne touche à aucun contenu du site. Il n'écrit que le registre
``daat_audit/data/triage-decisions.json``, et il y **ajoute** : une décision
nouvelle sur un signalement déjà jugé s'empile sur la précédente, aucune n'est
effacée, et la dernière fait foi.

Il existe parce qu'une décision de relecture doit survivre à la base de
données. ``import-triage.py`` applique les décisions au workflow — il lui faut
Postgres, les identifiants de la campagne, et il rend les signalements
résolus ; le registre, lui, est un fichier versionné avec le dépôt, que le
moteur relit à chaque passe pour ne pas resservir ce qui a été tranché.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from daat_audit.decisions import (      # noqa: E402
    Decision,
    Registre,
    compter,
    empreinte,
)

# Réponse du relecteur → décision consignée, et si le dossier est clos.
TRADUCTION: dict[str, tuple[str, bool]] = {
    "erreur": ("error", True),
    "contenu": ("error", True),
    "reference": ("reference_error", True),
    "variante": ("accepted_variant", True),
    "faux": ("false_positive", True),
    "pas_citation": ("false_positive", True),
    "aucune_erreur": ("false_positive", True),
    # Seule réponse qui laisse le dossier ouvert.
    "rav": ("needs_rav_review", False),
    "indecidable": ("needs_source_verification", False),
}

NOTES = {
    "false_positive": "signalement infondé — le contenu Torah n'est pas modifié",
    "accepted_variant": (
        "variante d'édition légitime — le contenu n'est pas modifié ; la décision "
        "vaut pour ce passage seul, aucune normalisation globale"
    ),
    "needs_rav_review": "reste ouvert — aucune conclusion automatique, aucune modification",
    "needs_source_verification": "source à vérifier — aucune conclusion sur le texte",
    "error": "erreur confirmée — contenu et/ou référence corrigés",
    "reference_error": "texte authentique, référence fautive — référence corrigée",
}

RE_ITEMS = re.compile(r"const ITEMS\s*=\s*(\[.*?\]);", re.S)


def lire_items(chemin: pathlib.Path) -> dict[int, dict]:
    """Signalements du lot, depuis la page de tri ou un JSON équivalent."""
    texte = chemin.read_text(encoding="utf-8")
    if chemin.suffix == ".json":
        brut = json.loads(texte)
    else:
        m = RE_ITEMS.search(texte)
        if not m:
            raise ValueError(f"aucun bloc « const ITEMS » dans {chemin}")
        brut = json.loads(m.group(1))
    return {int(i["id"]): i for i in brut}


def lire_decisions(chemin: pathlib.Path) -> tuple[str, list[tuple[int, str]]]:
    role, rendues = "editor", []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        if ligne.upper().startswith("DAAT-TRIAGE"):
            if "role=rav" in ligne:
                role = "rav"
            continue
        morceaux = ligne.split()
        if len(morceaux) != 2 or not morceaux[0].isdigit():
            raise ValueError(f"ligne illisible : « {ligne} »")
        code = morceaux[1].lower()
        if code not in TRADUCTION:
            raise ValueError(
                f"réponse inconnue : « {code} ». Attendu : {', '.join(TRADUCTION)}"
            )
        rendues.append((int(morceaux[0]), code))
    if not rendues:
        raise ValueError("aucune décision dans l'entrée")
    return role, rendues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--triage", required=True, type=pathlib.Path)
    ap.add_argument("--decisions", required=True, type=pathlib.Path)
    ap.add_argument("--source", default="DAAT-TRIAGE v1",
                    help="d'où vient ce lot de décisions (tracé tel quel)")
    ap.add_argument("--registre", type=pathlib.Path, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    items = lire_items(args.triage)
    role, rendues = lire_decisions(args.decisions)

    inconnus = [i for i, _ in rendues if i not in items]
    if inconnus:
        print(f"⚠ {len(inconnus)} identifiant(s) sans signalement correspondant : "
              f"{inconnus[:10]}", file=sys.stderr)
        return 1

    registre = Registre.charger(args.registre)
    avant = len(registre)
    ajoutees: list[Decision] = []
    for ident, code in rendues:
        it = items[ident]
        decision, resolue = TRADUCTION[code]
        d = Decision(
            id=ident, decision=decision, reviewer_role=role, source=args.source,
            resolved=resolue,
            empreinte=empreinte(siman=it.get("siman"), niveau=it.get("niveau"),
                                regle=it.get("regle", "CIT-001"),
                                citation=it.get("citation", ""), ref=it.get("ref")),
            siman=it.get("siman"), niveau=it.get("niveau"),
            regle=it.get("regle", "CIT-001"), ref=it.get("ref"),
            note=NOTES.get(decision, ""),
        )
        registre.ajouter(d)
        ajoutees.append(d)

    comptes = compter(ajoutees)
    print(f"{len(ajoutees)} décision(s) rendue(s) par « {role} » :")
    for code, n in sorted(comptes.items()):
        print(f"   {n:4d}  {code}")
    ouverts = [d.id for d in registre.ouverts()]
    print(f"→ {len(ouverts)} cas laissé(s) à la décision du Rav : {ouverts}")
    print(f"→ registre : {avant} → {len(registre)} décision(s) conservée(s)")

    if args.dry_run:
        print("(--dry-run : rien n'a été écrit)")
        return 0
    registre.ecrire(args.registre)
    print(f"écrit dans {(args.registre or pathlib.Path('daat_audit/data/triage-decisions.json'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
