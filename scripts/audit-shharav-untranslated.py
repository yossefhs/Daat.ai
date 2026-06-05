#!/usr/bin/env python3
"""Audit : pour chaque niveau-4-daat-harav*.html, compte les blocs
`<p class="sa-he">` (texte SHHaRav hébreu) et vérifie qu'ils ont une
traduction (`sa-fr` / `sa-en` / `sa-translation` ou autre) ajacente.

Détecte les zones SHHaRav non traduites.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"


# Pattern qui isole le bloc <div class="sa-block">…</div>
BLOCK_PAT = re.compile(r'<div class="sa-block"[^>]*>(.*?)</div>', re.DOTALL)

# Patterns de paragraphes à l'intérieur d'un bloc
HE_PAT = re.compile(r'<p[^>]*class="sa-he"[^>]*>', re.IGNORECASE)
FR_PAT = re.compile(r'<p[^>]*class="sa-fr"[^>]*>', re.IGNORECASE)
EN_PAT = re.compile(r'<p[^>]*class="sa-en"[^>]*>', re.IGNORECASE)
# Variantes possibles
ANY_TRANS_PAT = re.compile(r'<p[^>]*class="sa-(fr|en|translation)"', re.IGNORECASE)


def analyze(html: str, expected_lang: str) -> dict:
    """expected_lang in {'fr', 'en', 'he'}."""
    blocks = BLOCK_PAT.findall(html)
    total = len(blocks)
    he_blocks = sum(1 for b in blocks if HE_PAT.search(b))

    if expected_lang == "fr":
        with_trans = sum(1 for b in blocks if HE_PAT.search(b) and FR_PAT.search(b))
        missing = he_blocks - with_trans
    elif expected_lang == "en":
        with_trans = sum(1 for b in blocks if HE_PAT.search(b) and EN_PAT.search(b))
        missing = he_blocks - with_trans
    else:  # he
        # Pour le HE, le sa-he est l'original. Pas de traduction attendue
        # mais il peut y avoir une glose. On rapporte juste les blocs.
        with_trans = he_blocks
        missing = 0

    return {
        "total_blocks": total,
        "he_blocks": he_blocks,
        "with_trans": with_trans,
        "missing": missing,
    }


def main():
    print("=" * 90)
    print("AUDIT SHHaRav non traduit (niveau-4-daat-harav)")
    print("=" * 90)
    print()

    issues = {"fr": [], "en": [], "he": []}
    nb_total = {"fr": 0, "en": 0, "he": 0}

    for num in range(242, 366):
        folder = SHABBAT / f"siman-{num}"
        if not folder.exists():
            continue
        for lang, fname in [
            ("fr", "niveau-4-daat-harav.html"),
            ("en", "niveau-4-daat-harav-en.html"),
            ("he", "niveau-4-daat-harav-he.html"),
        ]:
            f = folder / fname
            if not f.exists():
                continue
            text = f.read_text(encoding="utf-8")
            res = analyze(text, lang)
            nb_total[lang] += 1
            if lang in ("fr", "en") and res["missing"] > 0:
                issues[lang].append((num, res))

    print(f"📊 RÉSUMÉ\n")
    print(f"  FR : {len(issues['fr']):3d} simanim avec blocs sa-he sans sa-fr (sur {nb_total['fr']} N4)")
    print(f"  EN : {len(issues['en']):3d} simanim avec blocs sa-he sans sa-en (sur {nb_total['en']} N4)")
    print()

    for lang in ("fr", "en"):
        if not issues[lang]:
            print(f"\n✅ Aucun bloc SHHaRav non traduit en {lang.upper()}")
            continue
        print(f"\n## {lang.upper()} — Détail des manques ({len(issues[lang])} simanim) :\n")
        for num, res in issues[lang]:
            print(f"  siman-{num} : {res['missing']}/{res['he_blocks']} blocs sa-he sans traduction "
                  f"(total blocks: {res['total_blocks']})")


if __name__ == "__main__":
    main()
