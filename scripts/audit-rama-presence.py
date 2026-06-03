#!/usr/bin/env python3
"""Audit detaille de la presence du Rama dans les niveau-1 Mehaber-only.

Pour chaque siman, identifie :
1. Les seifim cites dans des <blockquote class="text-source">
2. Pour chaque seif, verifie si le Rama (הגה / הַגָּהּ / הגה'ה / Hagaha du Rama / Rema gloss) est present
3. Verifie si le Rama est evoque dans la prose (sections "Position du Rama", "La Hagaha du Rama", etc.)

Sortie : tableau qui liste pour chaque siman :
- Nombre de seifim
- Nombre de seifim ayant un Rama dans le blockquote (Hebrew)
- Nombre de seifim ayant un Rama discute dans la prose
- Statut : OK / MANQUE
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

# Patterns Rama
RAMA_IN_HEB = re.compile(r'הַגָּ?הּ|הַגָּהָה|הגה(?:[ ״״\']|״)?|הג"ה')
RAMA_FR_MARKER = re.compile(r'(?:Glose|Hagaha|Position) du Rama|Rama (?:dit|ajoute)|Rama:|Rama\s*\(')
RAMA_EN_MARKER = re.compile(r'(?:Hagahah|Rema gloss|Rema:|Rema\s+states|Rema\s+adds|Rema\s+brings|the Rema)')

# Comptes connus de séifim du Mehaber
MEHABER_SEIFIM = {
    242: 1, 243: 3, 244: 6, 245: 2, 246: 5, 247: 6, 248: 4, 249: 4,
    250: 2, 251: 2, 252: 7, 253: 5, 254: 9, 255: 3, 256: 1, 257: 8,
    258: 1, 259: 4, 260: 2, 261: 4,
}


def count_blockquote_with_rama(html: str) -> tuple[int, int]:
    """Renvoie (total_blockquotes, blockquotes_avec_rama_he)."""
    blocks = re.findall(r'<blockquote[^>]*>(.*?)</blockquote>', html, re.DOTALL)
    with_rama = sum(1 for b in blocks if RAMA_IN_HEB.search(b))
    return len(blocks), with_rama


def has_rama_in_prose_fr(html: str) -> bool:
    return bool(RAMA_FR_MARKER.search(html))


def has_rama_in_prose_en(html: str) -> bool:
    return bool(RAMA_EN_MARKER.search(html))


def has_rama_in_prose_he(html: str) -> bool:
    # Pour HE, on cherche des mentions explicites du Rama (rema-a)
    return bool(re.search(r'הרמ״?א|רמ״?א', html))


def main():
    print(f"=== AUDIT RAMA — niveau-1 par siman ===\n")
    print(f"Légende :")
    print(f"  blocks = nombre de blockquotes (citations Mehaber)")
    print(f"  +Rama  = blockquotes contenant un Rama (הגה)")
    print(f"  prose  = oui/non (Rama mentionné dans la prose)")
    print(f"  exp    = nombre de séifim attendus (Mehaber)")
    print(f"  GAP    = blocks < exp (peut-être incomplet) ou Rama prose mais pas en bloc\n")

    print(f"{'Siman':6} {'exp':>3} | "
          f"{'FR':>4} {'+R':>3} {'pr':>3} | "
          f"{'HE':>4} {'+R':>3} {'pr':>3} | "
          f"{'EN':>4} {'+R':>3} {'pr':>3}  Note")
    print("-" * 90)

    candidates_for_rama_add = []

    for num in sorted(MEHABER_SEIFIM.keys()):
        folder = SHABBAT / f"siman-{num}"
        if not folder.exists():
            continue
        exp = MEHABER_SEIFIM[num]

        fr = (folder / "niveau-1-base.html").read_text(encoding="utf-8")
        he = (folder / "niveau-1-base-he.html").read_text(encoding="utf-8")
        en = (folder / "niveau-1-base-en.html").read_text(encoding="utf-8")

        fr_b, fr_r = count_blockquote_with_rama(fr)
        he_b, he_r = count_blockquote_with_rama(he)
        en_b, en_r = count_blockquote_with_rama(en)
        fr_pr = "Y" if has_rama_in_prose_fr(fr) else "N"
        he_pr = "Y" if has_rama_in_prose_he(he) else "N"
        en_pr = "Y" if has_rama_in_prose_en(en) else "N"

        note = ""
        # Cas où Rama mentionné en prose mais pas dans les blocks → manque potentiel
        if fr_pr == "Y" and fr_r == 0:
            note = "Rama prose mais 0 dans blocks"
            candidates_for_rama_add.append(num)
        # Cas où le HE n'a pas de Rama du tout
        if he_pr == "N" and he_r == 0:
            note = (note + " ; pas de Rama HE").strip(" ;")

        print(f"{num:<6} {exp:>3} | "
              f"{fr_b:>4} {fr_r:>3} {fr_pr:>3} | "
              f"{he_b:>4} {he_r:>3} {he_pr:>3} | "
              f"{en_b:>4} {en_r:>3} {en_pr:>3}  {note}")

    print()
    print(f"=== Simanim candidats pour ajout Rama : {len(candidates_for_rama_add)} ===")
    print(f"  {candidates_for_rama_add}")


if __name__ == "__main__":
    main()
