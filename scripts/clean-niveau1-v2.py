#!/usr/bin/env python3
"""Nettoie chirurgicalement les niveau-1 contamines.

Strategie ultra-simple : pour chaque langue d'un siman donne, on recoit
les patterns exacts a supprimer. On ne touche que ce qui est explicitement
identifie pour eviter les degats du script v1.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"


def find_bis_h2(html: str) -> tuple[int, int, str] | None:
    """Trouve le premier h2 'bis' SHHaRav.
    Renvoie (line_num_0based, end_offset, label) ou None."""
    pattern = re.compile(
        r'<h2 class="section-title">\s*(\d+(?:bis|b|а|א))\.[^<]*</h2>',
    )
    m = pattern.search(html)
    if not m:
        return None
    return m.start(), m.end(), m.group(1)


def find_next_section_h2(html: str, start_pos: int) -> int | None:
    """Trouve le prochain h2 'N.' (sans bis) apres start_pos."""
    pattern = re.compile(r'<h2 class="section-title">\s*(\d+)\.\s')
    m = pattern.search(html, start_pos)
    return m.start() if m else None


def find_h3_shharav(html: str) -> tuple[int, int] | None:
    """Trouve un h3 SHHaRav embarque."""
    pattern = re.compile(
        r'<h3>[^<]*(?:Admour HaZaken|Admur HaZaken|Admor HaZaken|'
        r'Choulhan Aroukh HaRav|Shulchan Aruch HaRav|SHHaRav|'
        r'אדמו.ר הזקן|שו..ע הרב|שולחן ערוך הרב)[^<]*</h3>',
        re.IGNORECASE,
    )
    m = pattern.search(html)
    if not m:
        return None
    return m.start(), m.end()


PAGE_BREAK = '<div class="page-break"></div>'


def clean(html: str) -> tuple[str, dict]:
    stats = {"h2_bis_removed": 0, "h3_removed": 0, "toc_removed": 0}

    # 1. Supprimer h3 SHHaRav embarques (boucle, mais 1 seul par fichier max attendu)
    while True:
        found = find_h3_shharav(html)
        if not found:
            break
        h3_start, h3_end = found
        # Trouver la prochaine section_title h2 N.
        next_h2_pos = find_next_section_h2(html, h3_end)
        if next_h2_pos is None:
            break  # ne pas risquer de supprimer trop
        # Bornes : du h3 lui-meme (PAS de page-break a inclure car il etait au milieu
        # de la section 1) jusqu'a la page-break qui precede next_h2 (inclus si present).
        pb_before_next = html.rfind(PAGE_BREAK, h3_end, next_h2_pos)
        if pb_before_next != -1:
            end_del = pb_before_next + len(PAGE_BREAK)
        else:
            end_del = next_h2_pos
        html = html[:h3_start] + html[end_del:]
        stats["h3_removed"] += 1

    # 2. Supprimer sections h2 'bis'
    while True:
        found = find_bis_h2(html)
        if not found:
            break
        h2_start, h2_end, label = found
        next_h2_pos = find_next_section_h2(html, h2_end)
        if next_h2_pos is None:
            print(f"  ! Pas de section suivante apres '{label}.', skip")
            break  # securite
        # Bornes : page-break AVANT h2 (inclus) jusqu'a page-break AVANT next_h2 (inclus)
        pb_before = html.rfind(PAGE_BREAK, 0, h2_start)
        # On doit valider que pb_before est proche du h2_start (sinon c'est le pb d'une
        # section anterieure et on supprimerait trop)
        if pb_before == -1 or h2_start - pb_before > 200:
            start_del = h2_start
        else:
            start_del = pb_before
        pb_before_next = html.rfind(PAGE_BREAK, h2_end, next_h2_pos)
        if pb_before_next != -1:
            end_del = pb_before_next + len(PAGE_BREAK)
        else:
            end_del = next_h2_pos
        html = html[:start_del] + html[end_del:]
        stats["h2_bis_removed"] += 1

    # 3. Supprimer entrees TOC bis
    toc_re = re.compile(
        r'<div class="toc-item">\s*<span class="toc-num">\d+(?:bis|b|а|א)\.[^<]*</span>'
        r'[^<]*(?:<[^>]+>[^<]*)*?</div>\s*',
    )
    new_html, n = toc_re.subn('', html)
    if n > 0:
        stats["toc_removed"] = n
        html = new_html

    return html, stats


CONTAMINATED = [254, 255, 257, 258, 259, 260, 261]
# 253 deja traite manuellement


def main():
    print(f"=== NETTOYAGE NIVEAU-1 v2 (script prudent) ===\n")
    for num in CONTAMINATED:
        folder = SHABBAT / f"siman-{num}"
        if not folder.exists():
            continue
        print(f"--- siman-{num} ---")
        for lang_suffix in ["", "-he", "-en"]:
            f = folder / f"niveau-1-base{lang_suffix}.html"
            if not f.exists():
                continue
            try:
                html = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            original_lines = html.count("\n")
            new_html, stats = clean(html)
            if new_html == html:
                continue
            new_lines = new_html.count("\n")
            # Securite : refuser si on supprime plus de 50% du fichier
            if new_lines < original_lines * 0.5:
                tag = lang_suffix.replace("-", "") or "fr"
                print(
                    f"  [{tag}] DANGER: {original_lines} -> {new_lines} (-{original_lines - new_lines}), SKIP"
                )
                continue
            f.write_text(new_html, encoding="utf-8")
            tag = lang_suffix.replace("-", "") or "fr"
            print(
                f"  [{tag}] {original_lines} -> {new_lines} lignes "
                f"({stats}, supprime {original_lines - new_lines})"
            )


if __name__ == "__main__":
    main()
