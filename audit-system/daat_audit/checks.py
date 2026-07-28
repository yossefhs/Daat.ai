# -*- coding: utf-8 -*-
"""Contrôles techniques et éditoriaux (§10) — Phase 2.

Chaque contrôle est une fonction indépendante décorée par ``@check`` : elle
reçoit un contexte et rend des ``Finding``. Aucun contrôle ne corrige quoi
que ce soit — la Phase 1 comme la Phase 2 se contentent de PROPOSER (§13).

Le classement en gravité (§11) et en risque (§12) est porté par le contrôle
lui-même, parce que lui seul sait ce qu'il regarde : un espace double est
``P4/LOW`` ; une différence dans une citation est ``P1/HALAKHIC``, quelle que
soit la confiance de la détection.
"""
from __future__ import annotations

import json
import pathlib
import re
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

from .blocks import Block, rtl_classes
from .models import BlockType, Risk, Severity

# ── Contexte et résultat ─────────────────────────────────────────────────

@dataclass
class CheckContext:
    """Ce qu'un contrôle peut regarder."""

    blocks: list[Block]
    html: str = ""
    url: str = ""
    internal_links: list[str] = field(default_factory=list)
    broken_links: dict[str, int | None] = field(default_factory=dict)


@dataclass
class Finding:
    rule_code: str
    category: str
    subcategory: str | None
    block_id: str | None
    current_text: str
    explanation: str
    severity: Severity
    risk: Risk
    confidence: float
    proposed_correction: str | None = None
    rule_version: str = "1.0"


CheckFn = Callable[[CheckContext], Iterable[Finding]]
REGISTRY: dict[str, CheckFn] = {}


def check(code: str) -> Callable[[CheckFn], CheckFn]:
    def decorator(fn: CheckFn) -> CheckFn:
        REGISTRY[code] = fn
        fn.rule_code = code  # type: ignore[attr-defined]
        return fn
    return decorator


def run_all(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for fn in REGISTRY.values():
        findings.extend(fn(ctx))
    return findings


# ── Contrôles techniques ─────────────────────────────────────────────────

_INVISIBLE = {
    "​": "espace de largeur nulle (U+200B)",
    "‌": "antiliant (U+200C)",
    "‍": "liant (U+200D)",
    "﻿": "BOM en milieu de texte (U+FEFF)",
    "­": "trait d'union conditionnel (U+00AD)",
}


@check("TECH-001")
def espaces_multiples(ctx: CheckContext) -> Iterator[Finding]:
    """Espaces consécutifs dans le HTML source.

    Le contrôle lit les **nœuds de texte** du HTML, et non
    ``normalized_content`` : celui-ci a déjà réduit les suites d'espaces, si
    bien qu'y chercher un doublon ne pouvait jamais rien donner. Se limiter
    aux nœuds de texte évite par ailleurs de compter l'indentation entre
    balises, qui n'est pas du contenu.

    Défaut d'hygiène du source, pas d'affichage : le navigateur réduit ces
    espaces, le lecteur ne les voit pas. D'où P4/LOW — mais ils faussent la
    comparaison des citations, ce qui justifie de les signaler.
    """
    for block in ctx.blocks:
        for noeud in BeautifulSoup(block.raw_content, "lxml").find_all(string=True):
            m = re.search(r"\S(  +)\S", str(noeud))
            if not m:
                continue
            yield Finding(
                rule_code="TECH-001", category="technique", subcategory="espaces_multiples",
                block_id=block.stable_id,
                current_text=str(noeud)[max(0, m.start() - 20): m.end() + 20],
                explanation=f"{len(m.group(1))} espaces consécutifs",
                proposed_correction=re.sub(r"  +", " ", m.group(0)),
                severity=Severity.P4_SUGGESTION, risk=Risk.LOW, confidence=0.99,
            )
            break  # un signalement par bloc suffit


@check("TECH-002")
def caracteres_invisibles(ctx: CheckContext) -> Iterator[Finding]:
    """Caractères Unicode invisibles — invisibles à la relecture humaine,
    mais ils cassent les comparaisons de citations."""
    for block in ctx.blocks:
        for char, label in _INVISIBLE.items():
            if char in block.raw_content:
                yield Finding(
                    rule_code="TECH-002", category="technique",
                    subcategory="caractere_invisible", block_id=block.stable_id,
                    current_text=repr(block.normalized_content[:80]),
                    explanation=f"contient un {label}",
                    proposed_correction="retirer le caractère invisible",
                    severity=Severity.P3_MINOR, risk=Risk.LOW, confidence=0.99,
                )


@check("TECH-003")
def parentheses_desequilibrees(ctx: CheckContext) -> Iterator[Finding]:
    """Parenthèses ou crochets déséquilibrés dans un bloc."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    for block in ctx.blocks:
        text = block.normalized_content
        for opener, closer in pairs.items():
            delta = text.count(opener) - text.count(closer)
            if delta:
                yield Finding(
                    rule_code="TECH-003", category="technique",
                    subcategory="parentheses_desequilibrees", block_id=block.stable_id,
                    current_text=text[:120],
                    explanation=f"{abs(delta)} « {opener if delta > 0 else closer} » sans correspondance",
                    severity=Severity.P3_MINOR, risk=Risk.LOW, confidence=0.9,
                )


@check("TECH-004")
def guillemets_desequilibres(ctx: CheckContext) -> Iterator[Finding]:
    """Guillemets français ouvrants/fermants déséquilibrés.

    Les guillemets droits ne sont PAS comptés : en hébreu, le gershayim
    (״) et l'apostrophe servent d'abréviation, pas de citation — les
    compter produirait un bruit permanent.
    """
    for block in ctx.blocks:
        text = block.normalized_content
        delta = text.count("«") - text.count("»")
        if delta:
            yield Finding(
                rule_code="TECH-004", category="technique",
                subcategory="guillemets_desequilibres", block_id=block.stable_id,
                current_text=text[:120],
                explanation=f"{abs(delta)} guillemet(s) {'ouvrant' if delta > 0 else 'fermant'}(s) sans correspondance",
                severity=Severity.P3_MINOR, risk=Risk.LOW, confidence=0.92,
            )


@check("TECH-005")
def bloc_vide(ctx: CheckContext) -> Iterator[Finding]:
    """Titre sans contenu, ou page sans aucun bloc de contenu."""
    if not ctx.blocks:
        yield Finding(
            rule_code="TECH-005", category="technique", subcategory="page_vide",
            block_id=None, current_text=ctx.url,
            explanation="aucun bloc de contenu extrait de la page",
            severity=Severity.P1_MAJOR, risk=Risk.MEDIUM, confidence=0.95,
        )
        return
    if not any(b.block_type is BlockType.TITRE for b in ctx.blocks):
        yield Finding(
            rule_code="TECH-005", category="technique", subcategory="titre_manquant",
            block_id=None, current_text=ctx.url,
            explanation="la page ne comporte pas de titre principal (h1)",
            severity=Severity.P2_SIGNIFICANT, risk=Risk.LOW, confidence=0.9,
        )


@check("TECH-006")
def paragraphe_duplique(ctx: CheckContext) -> Iterator[Finding]:
    """Bloc au contenu strictement identique à un autre de la même page."""
    seen: dict[str, Block] = {}
    for block in ctx.blocks:
        if len(block.normalized_content) < 80:
            continue      # titres et libellés courts se répètent légitimement
        previous = seen.get(block.sha256)
        if previous is not None:
            yield Finding(
                rule_code="TECH-006", category="technique", subcategory="doublon_exact",
                block_id=block.stable_id,
                current_text=block.normalized_content[:150],
                explanation=f"contenu identique au bloc {previous.stable_id}",
                severity=Severity.P2_SIGNIFICANT, risk=Risk.LOW, confidence=0.97,
            )
        else:
            seen[block.sha256] = block


@check("TECH-007")
def lien_casse(ctx: CheckContext) -> Iterator[Finding]:
    """Lien interne renvoyant une erreur (alimenté par le crawler)."""
    for url, status in ctx.broken_links.items():
        yield Finding(
            rule_code="TECH-007", category="technique", subcategory="lien_casse",
            block_id=None, current_text=url,
            explanation=f"lien interne en échec (HTTP {status if status else 'injoignable'})",
            severity=Severity.P2_SIGNIFICANT, risk=Risk.LOW, confidence=0.95,
        )


@check("TECH-008")
def direction_rtl(ctx: CheckContext) -> Iterator[Finding]:
    """Bloc hébreu sans marquage de direction.

    Sans direction RTL, la ponctuation d'un texte hébreu s'affiche du mauvais
    côté sur une page ``dir="ltr"`` : un défaut visible par le lecteur.

    Le marquage est reconnu de deux façons, et les deux comptent : un ``dir``
    porté par l'élément **ou par un de ses ancêtres**, et toute classe que la
    feuille de style de la page déclare elle-même en ``direction: rtl``. Cette
    seconde source est lue dans le CSS de la page plutôt que devinée — le site
    oriente ses citations par ``.he``, ce qu'aucune liste écrite d'avance
    n'aurait à connaître.
    """
    orientantes = rtl_classes(ctx.html) if ctx.html else set()
    for block in ctx.blocks:
        if block.block_type is not BlockType.CITATION_HEBRAIQUE:
            continue
        if len(block.normalized_content) < 40:
            continue
        if block.dir_attr == "rtl":
            continue
        if orientantes.intersection(block.css_classes):
            continue
        yield Finding(
            rule_code="TECH-008", category="technique", subcategory="rtl_manquant",
            block_id=block.stable_id, current_text=block.normalized_content[:100],
            explanation="bloc hébreu sans dir=\"rtl\" ni classe orientée en direction: rtl",
            proposed_correction='ajouter dir="rtl" sur l\'élément',
            severity=Severity.P3_MINOR, risk=Risk.LOW, confidence=0.8,
        )


# ── Contrôles éditoriaux français ────────────────────────────────────────

def _charger_terminologie() -> dict[str, dict[str, int]]:
    """Groupes de graphies **dérivés du site** (scripts/build-terminologie.py).

    Ce contrôle n'a pas de forme canonique en dur, et c'est délibéré. La
    première version en avait une, écrite de mémoire : elle donnait *Mouktsé*
    pour correct et *Muktzeh* pour fautif alors que le site écrit *Muktzeh*
    plus souvent, et désignait comme canoniques sept graphies qu'il n'emploie
    nulle part. Trancher entre deux translittérations attestées est une
    décision éditoriale qui appartient au Rav (§4) ; l'outil se borne à
    montrer qu'une page hésite, avec les comptes du site à l'appui.
    """
    path = pathlib.Path(__file__).parent / "data" / "terminologie.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("groupes", {})


TERMINOLOGIE: dict[str, dict[str, int]] = _charger_terminologie()


@check("EDIT-001")
def terminologie_incoherente(ctx: CheckContext) -> Iterator[Finding]:
    """Une même page emploie deux graphies d'un même terme.

    Ne propose AUCUNE correction : l'incohérence est un fait constatable,
    le choix de la graphie ne l'est pas. Risque MEDIUM et non LOW, car une
    translittération flottante peut faire lire deux concepts là où il n'y
    en a qu'un.
    """
    for terme, formes in TERMINOLOGIE.items():
        presentes: dict[str, str] = {}      # graphie → premier bloc concerné
        for block in ctx.blocks:
            if block.block_type is BlockType.CITATION_HEBRAIQUE:
                continue      # l'hébreu ne se juge pas au dictionnaire français
            for forme in formes:
                if forme in presentes:
                    continue
                if re.search(rf"(?<![\w-]){re.escape(forme)}(?![\w-])",
                             block.normalized_content):
                    presentes[forme] = block.stable_id

        if len(presentes) < 2:
            continue

        detail = ", ".join(
            f"« {f} » ({formes.get(f, 0)} sur le site)"
            for f in sorted(presentes, key=lambda f: -formes.get(f, 0))
        )
        yield Finding(
            rule_code="EDIT-001", category="editorial",
            subcategory="translitteration_flottante",
            block_id=sorted(presentes.values())[0],
            current_text=" / ".join(sorted(presentes)),
            explanation=(
                f"la page emploie {len(presentes)} graphies de « {terme} » : {detail}. "
                "Le choix de la graphie revient à l'éditeur."
            ),
            proposed_correction=None,
            severity=Severity.P4_SUGGESTION, risk=Risk.MEDIUM, confidence=0.9,
        )


@check("EDIT-002")
def phrase_inachevee(ctx: CheckContext) -> Iterator[Finding]:
    """Paragraphe se terminant sans ponctuation finale."""
    for block in ctx.blocks:
        if block.block_type not in (BlockType.PARAGRAPHE, BlockType.TRADUCTION):
            continue
        text = block.normalized_content.rstrip()
        if len(text) < 60:
            continue
        if text[-1] in ".!?:;»)]…\"'":
            continue
        yield Finding(
            rule_code="EDIT-002", category="editorial", subcategory="phrase_inachevee",
            block_id=block.stable_id, current_text="…" + text[-70:],
            explanation="le paragraphe se termine sans ponctuation finale",
            severity=Severity.P3_MINOR, risk=Risk.LOW, confidence=0.7,
        )


@check("EDIT-003")
def repetition_de_mot(ctx: CheckContext) -> Iterator[Finding]:
    """Mot répété deux fois de suite (« de de », « la la »)."""
    for block in ctx.blocks:
        if block.block_type is BlockType.CITATION_HEBRAIQUE:
            continue
        for m in re.finditer(r"\b([A-Za-zÀ-ÿ]{2,})\s+\1\b", block.normalized_content, re.I):
            yield Finding(
                rule_code="EDIT-003", category="editorial", subcategory="repetition",
                block_id=block.stable_id, current_text=m.group(0),
                explanation=f"« {m.group(1)} » répété",
                proposed_correction=m.group(1),
                severity=Severity.P3_MINOR, risk=Risk.LOW, confidence=0.9,
            )
