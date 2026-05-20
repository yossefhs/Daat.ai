#!/usr/bin/env python3
"""Ajoute un selecteur de langue flottant aux pages niveau-X-*.html (FR).

Les pages de niveau (niveau-1-base, niveau-2-lamdan, niveau-3-synthese,
niveau-4-daat-harav) n'ont pas de <header>/<nav>, juste un body avec un
contenu PDF-style. Pour permettre a l'utilisateur FR de basculer vers
HE/EN, on injecte un selecteur fixe en haut a droite.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources" / "shabbat"

FLOATING_SWITCHER_CSS = """
  .lang-switcher-float {
    position: fixed;
    top: 12px;
    right: 12px;
    z-index: 9999;
    display: flex;
    gap: 4px;
    background: rgba(255,255,255,0.95);
    border: 1px solid #C5A55A;
    padding: 4px 6px;
    border-radius: 3px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    font-family: 'Inter', sans-serif;
  }
  .lang-switcher-float a {
    font-size: 11px; letter-spacing: 1px;
    padding: 3px 7px; border-radius: 2px;
    color: #5a4a1a; text-decoration: none;
    border: 1px solid transparent;
  }
  .lang-switcher-float a.active {
    color: #1A1F3A; background: #FFF8E5;
    border-color: #1A1F3A; font-weight: 600;
  }
  .lang-switcher-float a:hover { color: #1A1F3A; border-color: #C5A55A; }
  @media print { .lang-switcher-float { display: none; } }
"""


def make_switcher(base_name: str, current: str) -> str:
    classes = {"fr": "", "he": "", "en": ""}
    classes[current] = " class=\"active\""
    return (
        f'<div class="lang-switcher-float" role="navigation" aria-label="Language">'
        f'<a href="{base_name}.html"{classes["fr"]}>FR</a>'
        f'<a href="{base_name}-he.html"{classes["he"]}>HE</a>'
        f'<a href="{base_name}-en.html"{classes["en"]}>EN</a>'
        f'</div>'
    )


def patch_file(p: Path, current_lang: str):
    """Patch un fichier niveau-X-*.html avec le switcher flottant."""
    try:
        html = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    # Skip si deja patche
    if "lang-switcher-float" in html:
        return False

    fname = p.name
    if current_lang == "he":
        base_name = fname.replace("-he.html", "")
    elif current_lang == "en":
        base_name = fname.replace("-en.html", "")
    else:
        base_name = fname.replace(".html", "")

    # Verifier que c'est bien une page niveau
    if not base_name.startswith("niveau-"):
        return False

    # Injecter le CSS dans le </style>
    if "</style>" in html:
        html = html.replace("</style>", FLOATING_SWITCHER_CSS + "\n</style>", 1)
    else:
        # Pas de <style> ? Injecter avant </head>
        html = html.replace(
            "</head>",
            f"<style>{FLOATING_SWITCHER_CSS}</style>\n</head>",
            1,
        )

    # Injecter le switcher juste apres <body>
    switcher = make_switcher(base_name, current_lang)
    html = re.sub(r'(<body[^>]*>)', rf'\1\n{switcher}', html, count=1)

    p.write_text(html, encoding="utf-8")
    return True


def main():
    count_fr = count_he = count_en = 0
    for p in SOURCES.rglob("niveau-*.html"):
        name = p.name
        if name.endswith("-he.html"):
            if patch_file(p, "he"):
                count_he += 1
        elif name.endswith("-en.html"):
            if patch_file(p, "en"):
                count_en += 1
        else:
            if patch_file(p, "fr"):
                count_fr += 1

    print(f"Switcher flottant ajoute : FR={count_fr}, HE={count_he}, EN={count_en}")


if __name__ == "__main__":
    main()
