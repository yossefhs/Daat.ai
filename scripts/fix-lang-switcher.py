#!/usr/bin/env python3
"""Corrige le selecteur de langue (lang-switcher) sur les pages -he.html et -en.html.

Bug : sur ces pages, le lien FR pointe sur soi-meme et le class='active'
est sur FR au lieu de HE/EN.

Avant (sur index-he.html par exemple) :
  <a href="index-he.html" class="active">FR</a><a href="index-he.html">HE</a><a href="index-en.html">EN</a>

Apres :
  <a href="index.html">FR</a><a href="index-he.html" class="active">HE</a><a href="index-en.html">EN</a>
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Regex qui matche le selecteur de langue en une ligne.
# Capture les trois liens (FR, HE, EN) avec leurs href et classes eventuelles.
SWITCHER_RE = re.compile(
    r'<span class="lang-switcher">'
    r'<a href="([^"]+)"(?:\s+class="active")?>FR</a>'
    r'<a href="([^"]+)"(?:\s+class="active")?>HE</a>'
    r'<a href="([^"]+)"(?:\s+class="active")?>EN</a>'
    r'</span>'
)


def build_switcher(fr_url: str, he_url: str, en_url: str, current: str) -> str:
    """Construit le switcher avec la langue active correcte."""
    fr_class = ' class="active"' if current == "fr" else ""
    he_class = ' class="active"' if current == "he" else ""
    en_class = ' class="active"' if current == "en" else ""
    return (
        f'<span class="lang-switcher">'
        f'<a href="{fr_url}"{fr_class}>FR</a>'
        f'<a href="{he_url}"{he_class}>HE</a>'
        f'<a href="{en_url}"{en_class}>EN</a>'
        f'</span>'
    )


def get_correct_urls(filename: str) -> tuple[str, str, str, str]:
    """Renvoie (fr_url, he_url, en_url, current_lang) selon le nom de fichier.

    On reconstruit les URLs en partant du nom canonique FR sans suffixe.
    """
    if filename.endswith("-he.html"):
        base = filename[: -len("-he.html")]
        current = "he"
    elif filename.endswith("-en.html"):
        base = filename[: -len("-en.html")]
        current = "en"
    else:
        base = filename[: -len(".html")]
        current = "fr"

    fr_url = f"{base}.html"
    he_url = f"{base}-he.html"
    en_url = f"{base}-en.html"
    return fr_url, he_url, en_url, current


def fix_file(path: Path) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    if 'class="lang-switcher"' not in original:
        return False

    fr_url, he_url, en_url, current = get_correct_urls(path.name)
    new_switcher = build_switcher(fr_url, he_url, en_url, current)

    # Remplacer le selecteur — on accepte n'importe quels href existants
    new_html, n = SWITCHER_RE.subn(new_switcher, original)
    if n == 0:
        return False

    if new_html != original:
        path.write_text(new_html, encoding="utf-8")
        return True
    return False


def main():
    targets = []
    for p in ROOT.rglob("*.html"):
        if any(part in {"node_modules", ".git"} for part in p.parts):
            continue
        targets.append(p)

    modified = 0
    for p in targets:
        if fix_file(p):
            modified += 1

    print(f"Termine : {modified}/{len(targets)} fichiers corriges")


if __name__ == "__main__":
    main()
