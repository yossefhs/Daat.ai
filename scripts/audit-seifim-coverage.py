#!/usr/bin/env python3
"""Audit les seifim présents dans chaque siman du niveau-1-base.

Compare avec le nombre de seifim attendu (du SHHaRav qui est exhaustif).
Identifie les simanim où le niveau-1 ne couvre que Seif Alef et où il y a
d'autres seifim dans le SHHaRav qui ne sont pas traités.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources" / "shabbat"


def count_seifim(file_path: Path) -> int:
    """Compte les seifim distincts mentionnes dans un fichier."""
    if not file_path.exists():
        return 0
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        return 0

    # Format Latin : "Seif Alef", "Seif Bet"...
    latin_seifim = set(re.findall(r"Seif[- ]([A-Za-z]+)\b", text))

    # Format mixte : "Seif א", "Seif ב" — translittération + lettre hébraïque
    mixed_seifim = set(re.findall(r"Seif\s+([א-ת]['׳״\"׳״]?)", text))

    # Format hébreu pur : "סעיף א'"
    he_seifim = set(re.findall(r"סעיף\s+([א-ת]['׳״\"׳״]?)", text))

    # Format français : "Séif א" ou "Séif aleph"
    fr_seifim_he = set(re.findall(r"S[ée]if\s+([א-ת]['׳״\"׳״]?)", text))

    return max(
        len(latin_seifim),
        len(mixed_seifim),
        len(he_seifim),
        len(fr_seifim_he),
    )


def audit_siman(num: int) -> dict:
    """Audite un siman et renvoie les comptes par niveau."""
    folder = SOURCES / f"siman-{num}"
    if not folder.exists():
        return None
    return {
        "n1_fr": count_seifim(folder / "niveau-1-base.html"),
        "n3_fr": count_seifim(folder / "niveau-3-synthese.html"),
        "n4_fr": count_seifim(folder / "niveau-4-daat-harav.html"),
    }


def main():
    print(f"{'Siman':6} {'N1':>4} {'N3':>4} {'N4':>4}  Note")
    print("-" * 50)
    for num in range(242, 366):
        result = audit_siman(num)
        if not result:
            continue
        n1, n3, n4 = result["n1_fr"], result["n3_fr"], result["n4_fr"]
        note = ""
        if n1 < n4 and n4 > 1:
            note = f"⚠ niveau-1 manque seifim (a {n1}, devrait avoir {n4})"
        print(f"{num:6} {n1:>4} {n3:>4} {n4:>4}  {note}")


if __name__ == "__main__":
    main()
