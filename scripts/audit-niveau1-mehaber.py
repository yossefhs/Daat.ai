#!/usr/bin/env python3
"""Audit les niveau-1 de tous les simanim pour identifier ceux qui contiennent
encore du contenu SHHaRav (Admour HaZaken / Choulhan Aroukh HaRav) en violation
de la strategie PR #88 (niveau-1 = Mehaber seul).

Identifie les patterns suivants :
- Sections `<h2 class="section-title">.bis|.א|.b\\.\\>` (sections bonus SHHaRav)
- Blocs `<h3>.*Admour HaZaken|Choulhan Aroukh HaRav|SHHaRav|אדמו.ר הזקן|שו..ע הרב`
- Mentions du SHHaRav dans le contenu (au-dela de la cross-ref legitime vers niveau-4)
- Titres h1 mentionnant `Choulhan Aroukh / SHHaRav`
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

PATTERNS = {
    "h2_bis": re.compile(
        r'<h2 class="section-title">[^<]*(?:\dbis|\d[abא]\b)\.', re.IGNORECASE
    ),
    "h3_shharav": re.compile(
        r'<h3>[^<]*(?:Admour HaZaken|Admur HaZaken|Admor HaZaken|'
        r'Choulhan Aroukh HaRav|Shulchan Aruch HaRav|SHHaRav|'
        r'אדמו.ר הזקן|שו..ע הרב|שולחן ערוך הרב)'
    ),
    "h1_mixed": re.compile(
        r'<h1>[^<]*(?:Choulhan Aroukh.*SHHaRav|Shulchan Aruch.*SHHaRav|'
        r'SA.*SHHaRav|שו..ע.*שו..ע הרב)'
    ),
    "toc_bis": re.compile(
        r'<div class="toc-item">[^<]*<span[^>]*>\d(?:bis|[abא]\b)\.</span>'
    ),
}


def audit_file(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    try:
        html = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {}
    return {name: len(p.findall(html)) for name, p in PATTERNS.items()}


def total(counts: dict[str, int]) -> int:
    return sum(counts.values())


def main():
    contaminated = []
    for num in range(242, 366):
        folder = SHABBAT / f"siman-{num}"
        if not folder.exists():
            continue
        all_counts = {}
        for lang_suffix in ["", "-he", "-en"]:
            f = folder / f"niveau-1-base{lang_suffix}.html"
            counts = audit_file(f)
            for k, v in counts.items():
                all_counts[k] = all_counts.get(k, 0) + v
        if total(all_counts) > 0:
            contaminated.append((num, all_counts))

    print(f"=== AUDIT NIVEAU-1 vs STRATEGIE Mehaber-only ===\n")
    print(f"Simanim contamines : {len(contaminated)}\n")
    print(f"{'Siman':<7} {'h2_bis':>7} {'h3_SHH':>7} {'h1_mix':>7} {'toc_bis':>8} {'Total':>6}")
    print("-" * 50)
    for num, counts in contaminated:
        t = total(counts)
        print(
            f"{num:<7} "
            f"{counts.get('h2_bis', 0):>7} "
            f"{counts.get('h3_shharav', 0):>7} "
            f"{counts.get('h1_mixed', 0):>7} "
            f"{counts.get('toc_bis', 0):>8} "
            f"{t:>6}"
        )
    print(f"\nTotal : {len(contaminated)} simanim a nettoyer")


if __name__ == "__main__":
    main()
