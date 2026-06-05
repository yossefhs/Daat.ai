#!/usr/bin/env python3
"""Supprime le bloc <details> placeholder « הגהות וציונים — À transcrire »
dans tous les fichiers niveau-4-daat-harav*.html.

Le bloc complet commence par `<details style="margin-top: 18px; background: rgba(245, 200, 100...`
et finit par `</details>`. Strategy : on parse ligne par ligne, on identifie
le marker dans le summary puis on remonte au <details ouvrant et descend
jusqu'au </details> fermant correspondant.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

MARKER = "הגהות וציונים — À transcrire depuis l'édition imprimée Kehot"


def remove_block(text: str) -> tuple[str, bool]:
    """Trouve et supprime le bloc <details>...</details> autour du marker.

    Renvoie (nouveau_texte, modifié).
    """
    idx = text.find(MARKER)
    if idx == -1:
        return text, False

    # Remonte pour trouver l'ouverture <details
    open_marker = '<details style="margin-top: 18px; background: rgba(245, 200, 100'
    open_idx = text.rfind(open_marker, 0, idx)
    if open_idx == -1:
        return text, False

    # Descend pour trouver le </details> qui ferme (premier après idx)
    close_marker = "</details>"
    close_idx = text.find(close_marker, idx)
    if close_idx == -1:
        return text, False
    end_idx = close_idx + len(close_marker)

    # On enlève aussi la ligne vide qui suit (jusqu'au \n suivant inclus)
    if end_idx < len(text) and text[end_idx] == "\n":
        end_idx += 1
    # Si après le bloc il y a une ligne vide on l'enlève aussi
    if end_idx < len(text) and text[end_idx:end_idx + 1] == "\n":
        end_idx += 1

    # On remonte aussi l'indentation/espaces du <details (sur sa ligne)
    line_start = text.rfind("\n", 0, open_idx) + 1
    new_text = text[:line_start] + text[end_idx:]
    return new_text, True


def main():
    modified = []
    skipped = []

    for path in sorted(SHABBAT.glob("siman-*/niveau-4-daat-harav*.html")):
        text = path.read_text(encoding="utf-8")
        new_text, changed = remove_block(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            modified.append(path.relative_to(ROOT))
        elif MARKER in text:
            skipped.append(path.relative_to(ROOT))

    print(f"Fichiers modifiés : {len(modified)}")
    print(f"Fichiers skip (marker présent mais bloc non identifié) : {len(skipped)}")
    if skipped:
        print("\nÀ vérifier manuellement :")
        for p in skipped:
            print(f"  - {p}")


if __name__ == "__main__":
    main()
