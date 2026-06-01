#!/usr/bin/env python3
"""Ajoute un bouton « Imprimer / Sauver en PDF » aux pages niveau-*.html.

Beaucoup de pages de niveau ont déjà ce bouton (window.print()), mais ~471
ne l'avaient pas (surtout les niveau-4). Ce script complète celles qui
manquent, avec le libellé adapté à la langue (FR/HE/EN), en reproduisant
exactement le markup déjà utilisé ailleurs.

Le bouton ouvre la boîte d'impression du navigateur → « Enregistrer au format
PDF » : aucun fichier à stocker, fonctionne sur tous les simanim/niveaux/langues.

Idempotent : une page qui contient déjà window.print() est ignorée.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources" / "shabbat"

LABELS = {
    "fr": "📄 Imprimer / Sauver en PDF",
    "he": "📄 הדפס / שמור כ-PDF",
    "en": "📄 Print / Save as PDF",
}

BTN_STYLE = (
    "font-family:'Inter',sans-serif;font-size:13px;font-weight:600;"
    "letter-spacing:1px;background:#1A1F3A;color:#C5A55A;padding:10px 22px;"
    "border:1px solid #C5A55A;border-radius:2px;cursor:pointer;"
    "text-transform:uppercase;"
)
PRINT_HIDE_CSS = (
    "<style>@media print { .print-btn, .daat-khavroutha-fab, "
    ".daat-chat-fab { display: none !important; } }</style>"
)


def block_for(lang: str) -> str:
    label = LABELS[lang]
    return (
        '\n<div style="text-align:center;margin:20px 0;">\n'
        f'  <button onclick="window.print()" class="print-btn" style="{BTN_STYLE}">{label}</button>\n'
        "</div>\n"
        f"{PRINT_HIDE_CSS}\n"
    )


def lang_of(name: str) -> str:
    if name.endswith("-he.html"):
        return "he"
    if name.endswith("-en.html"):
        return "en"
    return "fr"


def patch(p: Path) -> bool:
    html = p.read_text(encoding="utf-8")
    # Déjà un bouton d'impression → on ne touche pas
    if "window.print()" in html:
        return False
    if "</body>" not in html:
        return False
    block = block_for(lang_of(p.name))
    html = html.replace("</body>", block + "</body>", 1)
    p.write_text(html, encoding="utf-8")
    return True


def main() -> None:
    counts = {"fr": 0, "he": 0, "en": 0}
    for p in SOURCES.rglob("niveau-*.html"):
        if patch(p):
            counts[lang_of(p.name)] += 1
    total = sum(counts.values())
    print(f"Bouton PDF ajouté : FR={counts['fr']}, HE={counts['he']}, EN={counts['en']} (total {total})")


if __name__ == "__main__":
    main()
