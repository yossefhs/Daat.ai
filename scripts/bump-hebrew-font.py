#!/usr/bin/env python3
"""Augmente legerement la police du texte hebreu dans les simanim.

Cible la classe `.text-source` (citations Mehaber/Rama en hebreu) qui
contient le gros du texte hebreu pedagogique.

Augmentation : ~15-20% pour ameliorer la lisibilite sans casser la mise
en page.

Modifications :
- 12pt -> 14pt
- 13pt -> 15pt
- 17px -> 19px
- 18px -> 20px
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

# Mapping ancien -> nouveau (font-size text-source)
SIZE_BUMP = {
    "12pt": "14pt",
    "13pt": "15pt",
    "12.5pt": "14.5pt",
    "17px": "19px",
    "18px": "20px",
    "16px": "18px",
    "15px": "17px",
}

# Patterns a chercher dans les regles CSS
# On vise specifiquement la regle `text-source` ou `blockquote.text-source`
# Le defi : la regle peut etre multi-ligne. On utilise re.DOTALL.

# Pattern : trouve le bloc `.text-source { ... font-size: NNN ... }` et remplace NNN
def bump_text_source_font(html: str) -> tuple[str, int]:
    """Renvoie (html_modifie, nb_modifs)."""
    count = 0

    def replace_in_block(m):
        nonlocal count
        block = m.group(0)
        # Cherche font-size: NNNunit; dans le bloc
        m2 = re.search(r'(font-size:\s*)([\d.]+)(pt|px|em|rem)', block)
        if not m2:
            return block
        old_size = f"{m2.group(2)}{m2.group(3)}"
        new_size = SIZE_BUMP.get(old_size)
        if not new_size:
            return block
        new_block = block.replace(f"font-size: {old_size}", f"font-size: {new_size}")
        if new_block == block:
            new_block = block.replace(f"font-size:{old_size}", f"font-size:{new_size}")
        if new_block != block:
            count += 1
        return new_block

    # Bloc CSS text-source (avec ou sans `blockquote.` prefix)
    pattern = re.compile(
        r'(blockquote\.text-source|\.text-source)\s*\{[^}]*\}',
        re.DOTALL,
    )
    new_html = pattern.sub(replace_in_block, html)
    return new_html, count


def main():
    print(f"=== Bump police hebreu (.text-source) ===\n")
    total_files = 0
    total_modified = 0
    by_lang = {"fr": 0, "he": 0, "en": 0}

    for siman_dir in sorted(SHABBAT.glob("siman-*")):
        for level in ["niveau-1-base", "niveau-2-lamdan", "niveau-3-synthese", "niveau-4-daat-harav"]:
            for suffix, lang in [("", "fr"), ("-he", "he"), ("-en", "en")]:
                f = siman_dir / f"{level}{suffix}.html"
                if not f.exists():
                    continue
                total_files += 1
                try:
                    html = f.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                new_html, n = bump_text_source_font(html)
                if n > 0 and new_html != html:
                    f.write_text(new_html, encoding="utf-8")
                    total_modified += 1
                    by_lang[lang] += 1

    print(f"Total fichiers scannes : {total_files}")
    print(f"Total fichiers modifies : {total_modified}")
    for lang, n in by_lang.items():
        print(f"  {lang.upper()} : {n}")


if __name__ == "__main__":
    main()
