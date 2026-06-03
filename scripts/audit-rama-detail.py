#!/usr/bin/env python3
"""Audit détaillé des 15 GAP_CITATIONS Rama.

Pour chaque siman flaggé comme GAP, examine :
1. Section "Position du Rama" du N1 FR (qu'y est-il documenté ?)
2. Hagahot Rama réelles dans les blockquotes (citation explicite)
3. Mentions « Rama n'ajoute pas / no gloss » dans la prose
4. Verdict : VRAI GAP / FAUX POSITIF / NO_RAMA / À EXAMINER
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

GAP_SIMANIM = [255, 258, 267, 278, 283, 294, 300, 332, 341, 342, 344, 347, 348, 349, 350]

# Mots-clés "pas de Rama"
NEGATIF = re.compile(
    r"n'ajoute (?:aucune|pas de|pas)|n'a pas (?:de )?glos|adds? no (?:gloss|hagahah)|does not add|"
    r"pas de glose ashkénaze|no specific Ashkenaz|"
    r"suivent la même halakha|pratique (?:est )?commune|"
    r"לֹא הוֹסִיף|לא הוסיף|לא מוסיף|אינו מוסיף|"
    r"unifié|signe d'unanimité|the Mechaber and the Rama are unified|מאוחדים|מוסכם",
    re.IGNORECASE,
)

# Mots-clés "Rama divergent / ajoute"
RAMA_PRESENT = re.compile(
    r"Rama (?:ajoute|précise|insiste|impose|recommande|distingue|divergent)|"
    r"(?:ajoute|précise) une hagaha|Hagahah of the Rema|"
    r"Rema (?:adds|states|insists|holds|requires)",
    re.IGNORECASE,
)

# Pattern strict : hagaha dans blockquote
RAMA_BLOCK = re.compile(r'<blockquote[^>]*class="text-source"[^>]*>(.*?)</blockquote>', re.DOTALL)
RAMA_MARKER = re.compile(r'הַגָּ?הּ|הַגָּהָה|הגה(?=[<\s:,.ֻ-ׇ])|הג["״]ה')


def analyze_siman(num: int) -> dict:
    folder = SHABBAT / f"siman-{num}"
    if not folder.exists():
        return None

    fr_file = folder / "niveau-1-base.html"
    if not fr_file.exists():
        return None
    fr = fr_file.read_text(encoding="utf-8")

    # Comptage hagahot dans blockquotes
    blocks = RAMA_BLOCK.findall(fr)
    blocks_with_rama = sum(1 for b in blocks if RAMA_MARKER.search(b))

    # Recherche section "Position du Rama"
    pos_match = re.search(
        r"(?:Position du Rama|La position du Rama|Position du Rama)\s*[:—]?"
        r".*?</?(?:p|div|section|h\d)",
        fr,
        re.DOTALL | re.IGNORECASE,
    )
    position_section = ""
    # Plus simple : juste extraire le paragraphe Position du Rama
    section_match = re.search(
        r'<h2[^>]*>[^<]*Position du Rama[^<]*</h2>\s*(.*?)(?=<h2|<footer)',
        fr, re.DOTALL | re.IGNORECASE,
    )
    if section_match:
        section_text = re.sub(r'<[^>]+>', ' ', section_match.group(1))
        section_text = re.sub(r'\s+', ' ', section_text).strip()[:300]
        position_section = section_text

    has_negatif = bool(NEGATIF.search(fr))
    has_rama_present = bool(RAMA_PRESENT.search(fr))

    # Verdict
    if blocks_with_rama > 0:
        verdict = "OK (Rama dans blocks)"
    elif has_negatif and not has_rama_present:
        verdict = "✓ NO_RAMA confirmé"
    elif has_rama_present and not has_negatif:
        verdict = "⚠ VRAI GAP (Rama mentionné mais pas dans blocks)"
    elif has_negatif and has_rama_present:
        verdict = "🤔 AMBIGU"
    else:
        verdict = "? À EXAMINER"

    return {
        "num": num,
        "blocks": len(blocks),
        "blocks_with_rama": blocks_with_rama,
        "has_negatif": has_negatif,
        "has_rama_present": has_rama_present,
        "verdict": verdict,
        "position_section": position_section,
    }


def main():
    print("=" * 90)
    print(f"AUDIT DETAILLE — 15 GAP_CITATIONS Rama")
    print("=" * 90)

    summary = {"OK": 0, "NO_RAMA": 0, "VRAI GAP": 0, "AMBIGU": 0, "À EXAMINER": 0}

    for num in GAP_SIMANIM:
        r = analyze_siman(num)
        if not r:
            continue
        print(f"\n## siman-{num}")
        print(f"  Blockquotes : {r['blocks']} (avec Rama : {r['blocks_with_rama']})")
        print(f"  Négatif : {r['has_negatif']} | Rama présent : {r['has_rama_present']}")
        print(f"  → {r['verdict']}")
        if r["position_section"]:
            print(f"  Position du Rama (extrait) : {r['position_section'][:200]}...")

        if "OK" in r["verdict"]:
            summary["OK"] += 1
        elif "NO_RAMA" in r["verdict"]:
            summary["NO_RAMA"] += 1
        elif "VRAI GAP" in r["verdict"]:
            summary["VRAI GAP"] += 1
        elif "AMBIGU" in r["verdict"]:
            summary["AMBIGU"] += 1
        else:
            summary["À EXAMINER"] += 1

    print("\n" + "=" * 90)
    print("RÉSUMÉ")
    print("=" * 90)
    for k, v in summary.items():
        print(f"  {k:18} : {v}")


if __name__ == "__main__":
    main()
