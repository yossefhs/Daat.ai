#!/usr/bin/env python3
"""Nettoie automatiquement les niveau-1 des simanim contamines en supprimant :
- Les sections h2 "Nbis" ou "Nb." ou "Nא." (sections bonus SHHaRav apres section N)
- Les blocs h3 SHHaRav embarques dans la section 1
- Les entrees TOC correspondantes
- Les titres h1 mixtes "X Seifim / Y SHHaRav"

Approche : pour chaque siman cible, on identifie les bornes de la section
problematique et on supprime le bloc entre la fin de la section precedente
(page-break) et le debut de la section suivante (page-break ou h2).
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

# Patterns pour reperer les h2 "bis" SHHaRav (FR/HE/EN)
H2_BIS_RE = re.compile(
    r'<h2 class="section-title">\s*(\d+)(?:bis|b|а|א)\.\s*[^<]*</h2>',
    re.IGNORECASE,
)

# Patterns pour reperer les blocs h3 SHHaRav embarques
H3_SHHARAV_RE = re.compile(
    r'<h3>[^<]*(?:Admour HaZaken|Admur HaZaken|Admor HaZaken|'
    r'Choulhan Aroukh HaRav|Shulchan Aruch HaRav|SHHaRav|'
    r'אדמו.ר הזקן|שו..ע הרב|שולחן ערוך הרב)[^<]*</h3>',
    re.IGNORECASE,
)

PAGE_BREAK = '<div class="page-break"></div>'


def find_section_boundaries(html: str, h2_match: re.Match) -> tuple[int, int]:
    """Pour un h2 bis matche, trouve les bornes a supprimer :
    - debut : le page-break qui precede (ou le h2 lui-meme)
    - fin : juste avant le page-break suivant qui precede la section suivante,
            ou avant le prochain h2 si pas de page-break.
    """
    h2_start = h2_match.start()
    # Cherche le dernier page-break AVANT le h2
    pb_before = html.rfind(PAGE_BREAK, 0, h2_start)
    start_del = pb_before if pb_before != -1 else h2_start

    # Cherche le prochain h2 ou page-break apres le h2
    after_h2 = h2_match.end()
    # On cherche le prochain <h2 ... section-title qui n'est PAS un bis
    next_h2 = re.search(r'<h2 class="section-title">\s*\d+\.', html[after_h2:])
    if not next_h2:
        return start_del, after_h2
    next_h2_pos = after_h2 + next_h2.start()
    # On cherche le dernier page-break entre after_h2 et next_h2
    pb_after = html.rfind(PAGE_BREAK, after_h2, next_h2_pos)
    if pb_after != -1:
        end_del = pb_after + len(PAGE_BREAK)
    else:
        end_del = next_h2_pos
    return start_del, end_del


def find_h3_section_boundaries(html: str, h3_match: re.Match) -> tuple[int, int]:
    """Pour un h3 SHHaRav embarque, trouve les bornes a supprimer :
    - debut : le h3 lui-meme (la section 1 du Mehaber doit rester intacte avant)
    - fin : juste avant le page-break qui precede la section suivante.
    """
    h3_start = h3_match.start()
    after_h3 = h3_match.end()
    next_h2 = re.search(r'<h2 class="section-title">\s*\d+\.', html[after_h3:])
    if not next_h2:
        return h3_start, after_h3
    next_h2_pos = after_h3 + next_h2.start()
    pb_after = html.rfind(PAGE_BREAK, after_h3, next_h2_pos)
    if pb_after != -1:
        end_del = pb_after + len(PAGE_BREAK)
    else:
        end_del = next_h2_pos
    return h3_start, end_del


def clean_html(html: str) -> tuple[str, dict[str, int]]:
    """Nettoie un fichier HTML. Renvoie (html_nettoye, stats)."""
    stats = {"h2_bis": 0, "h3_shharav": 0, "toc_bis": 0}

    # 1. Retirer les h3 SHHaRav embarques (en boucle car les positions changent)
    while True:
        m = H3_SHHARAV_RE.search(html)
        if not m:
            break
        start, end = find_h3_section_boundaries(html, m)
        html = html[:start] + html[end:]
        stats["h3_shharav"] += 1

    # 2. Retirer les sections h2 "bis"
    while True:
        m = H2_BIS_RE.search(html)
        if not m:
            break
        start, end = find_section_boundaries(html, m)
        html = html[:start] + html[end:]
        stats["h2_bis"] += 1

    # 3. Retirer les entrees TOC "bis"
    toc_re = re.compile(
        r'<div class="toc-item">\s*<span class="toc-num">\d+(?:bis|b|а|א)\.</span>[^<]*'
        r'(?:<[^>]+>[^<]*)*</div>\s*',
        re.IGNORECASE,
    )
    new_html, n_toc = toc_re.subn('', html)
    if n_toc > 0:
        stats["toc_bis"] = n_toc
        html = new_html

    return html, stats


CONTAMINATED = [253, 254, 255, 257, 258, 259, 260, 261]


def main():
    total_stats = {"h2_bis": 0, "h3_shharav": 0, "toc_bis": 0}
    for num in CONTAMINATED:
        folder = SHABBAT / f"siman-{num}"
        if not folder.exists():
            continue
        print(f"\n=== siman-{num} ===")
        for lang_suffix in ["", "-he", "-en"]:
            f = folder / f"niveau-1-base{lang_suffix}.html"
            if not f.exists():
                continue
            try:
                html = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            original_lines = html.count("\n")
            new_html, stats = clean_html(html)
            if new_html == html:
                continue
            f.write_text(new_html, encoding="utf-8")
            new_lines = new_html.count("\n")
            tag = lang_suffix.replace("-", "") or "fr"
            print(
                f"  [{tag}] {original_lines} -> {new_lines} lignes "
                f"(supprime {original_lines - new_lines})"
            )
            for k, v in stats.items():
                total_stats[k] += v

    print(f"\n=== TOTAL ===")
    for k, v in total_stats.items():
        print(f"  {k} : {v} blocs supprimes")


if __name__ == "__main__":
    main()
