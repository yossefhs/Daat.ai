#!/usr/bin/env python3
"""Audit Rama global sur les 124 simanim Hilkhot Shabbat (242-365).

Detecte les hagahot du Rama dans toutes les structures connues :
- <blockquote class="text-source"> contenant הגה / הַגָּהּ
- <div class="rama-text">
- <div class="rama-translation">
- Mentions "Rama" / "Glose du Rama" / "Hagahah of the Rema" dans la prose

Pour chaque siman, evalue :
- Combien de seifim ont un Rama dans la citation (blockquote ou rama-div)
- Si le Rama est seulement evoque en prose (gap potentiel)
- Si aucun Rama present (= peut-etre legitime si pas de Rama dans le standard)

Sortie : tableau et liste des candidats a corriger.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

RAMA_HE = re.compile(
    r'הַגָּ?הּ|הַגָּהָה|הגה(?=[<\s:,.ֻ-ׇ])|הג["״]ה|רמ["״]א|הרמ["״]א|אַשְׁכְּנַזִּים'
)
RAMA_FR_MARKER = re.compile(r'\bRama\b|Hagaha du Rama|Glose du Rama|Ashkén', re.IGNORECASE)
RAMA_EN_MARKER = re.compile(r'\bRema\b|Hagahah of the Rema|Rema gloss|Ashkenazi', re.IGNORECASE)
RAMA_HE_PROSE = re.compile(r'הרמ["״]א|רמ["״]א|אַשְׁכְּנַזִּים')

# Mention explicite « le Rama n'a pas de hagaha sur ce siman »
RAMA_ABSENT_DOCUMENTED = re.compile(
    r"n'ajoute (?:aucune|pas de|pas)|n'a pas (?:de )?glos|"
    r"pas de glose ashkénaze|adds? no (?:gloss|hagahah)|does not add|"
    r"no specific Ashkenaz|"
    r"suivent la même halakha|pratique (?:est )?commune|"
    r"לֹא הוֹסִיף|לא הוסיף|לא מוסיף|אינו מוסיף|"
    r"unifié|signe d'unanimité|the Mechaber and the Rama are unified|"
    r"מאוחדים|מוסכם",
    re.IGNORECASE,
)


def analyze(html: str, lang: str) -> dict:
    """Analyse un fichier HTML pour Rama."""
    # Citations blockquote
    blocks = re.findall(r'<blockquote[^>]*>(.*?)</blockquote>', html, re.DOTALL)
    blk_total = len(blocks)
    blk_with_rama_he = sum(1 for b in blocks if RAMA_HE.search(b))

    # Divs rama-text et rama-translation
    rama_text_divs = len(re.findall(r'<div class="rama-text"[^>]*>', html))
    rama_trans_divs = len(re.findall(r'<div class="rama-translation"[^>]*>', html))

    # Toute presence Hebraique de Rama
    any_rama_he = bool(RAMA_HE.search(html))

    # Mention en prose
    if lang == "fr":
        prose_marker = bool(RAMA_FR_MARKER.search(html))
    elif lang == "en":
        prose_marker = bool(RAMA_EN_MARKER.search(html))
    else:  # he
        prose_marker = bool(RAMA_HE_PROSE.search(html))

    has_rama_anywhere = blk_with_rama_he > 0 or rama_text_divs > 0 or any_rama_he

    return {
        "blocks": blk_total,
        "blocks_with_rama": blk_with_rama_he,
        "rama_text_divs": rama_text_divs,
        "rama_translation_divs": rama_trans_divs,
        "has_rama_anywhere": has_rama_anywhere,
        "prose_marker": prose_marker,
    }


def categorize(stats_fr, stats_he, stats_en, fr_html) -> str:
    """Categorise le siman :
    - OK : Rama present dans citations dans les 3 langues
    - NO_RAMA_DOCUMENTED : le N1 documente explicitement « pas de Rama »
    - GAP_CITATIONS : prose mais pas dans citations (vrai gap potentiel)
    - INCOMPLET : Rama partiel entre langues
    - NO_RAMA : aucune trace de Rama nulle part
    """
    has_prose = all(s["prose_marker"] for s in [stats_fr, stats_he, stats_en])
    has_citation = all(
        s["blocks_with_rama"] > 0 or s["rama_text_divs"] > 0
        for s in [stats_fr, stats_he, stats_en]
    )

    if has_citation:
        return "OK"

    # Documented "no Rama" : le N1 explique que le Rama n'a pas de hagaha
    if RAMA_ABSENT_DOCUMENTED.search(fr_html):
        return "NO_RAMA_DOCUMENTED"

    if has_prose and not has_citation:
        return "GAP_CITATIONS"

    if any(s["has_rama_anywhere"] for s in [stats_fr, stats_he, stats_en]):
        return "INCOMPLET"

    return "NO_RAMA"


def main():
    print("=== AUDIT RAMA GLOBAL — simanim 242-365 ===\n")

    categories = {
        "OK": [],
        "NO_RAMA_DOCUMENTED": [],
        "GAP_CITATIONS": [],
        "NO_RAMA": [],
        "INCOMPLET": [],
    }

    for num in range(242, 366):
        folder = SHABBAT / f"siman-{num}"
        if not folder.exists():
            continue
        fr_file = folder / "niveau-1-base.html"
        he_file = folder / "niveau-1-base-he.html"
        en_file = folder / "niveau-1-base-en.html"
        if not (fr_file.exists() and he_file.exists() and en_file.exists()):
            continue

        fr = fr_file.read_text(encoding="utf-8")
        he = he_file.read_text(encoding="utf-8")
        en = en_file.read_text(encoding="utf-8")

        sfr = analyze(fr, "fr")
        she = analyze(he, "he")
        sen = analyze(en, "en")
        cat = categorize(sfr, she, sen, fr)
        categories[cat].append((num, sfr, she, sen))

    # Affichage par categorie
    for cat in ["GAP_CITATIONS", "INCOMPLET", "NO_RAMA", "NO_RAMA_DOCUMENTED", "OK"]:
        items = categories[cat]
        print(f"\n## {cat} : {len(items)} simanim")
        if cat in ("OK", "NO_RAMA_DOCUMENTED"):
            print(f"  {[n for n,*_ in items]}")
        else:
            for num, sfr, she, sen in items:
                print(f"  siman-{num} : FR(blk={sfr['blocks']}/+R={sfr['blocks_with_rama']}/"
                      f"rama_div={sfr['rama_text_divs']}/prose={sfr['prose_marker']}) "
                      f"HE(blk={she['blocks']}/+R={she['blocks_with_rama']}/"
                      f"rama_div={she['rama_text_divs']}/prose={she['prose_marker']}) "
                      f"EN(blk={sen['blocks']}/+R={sen['blocks_with_rama']}/"
                      f"rama_div={sen['rama_text_divs']}/prose={sen['prose_marker']})")

    print("\n=== RÉSUMÉ ===")
    for cat in ["OK", "NO_RAMA_DOCUMENTED", "GAP_CITATIONS", "INCOMPLET", "NO_RAMA"]:
        print(f"  {cat:20} : {len(categories[cat]):3} simanim")


if __name__ == "__main__":
    main()
