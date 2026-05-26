#!/usr/bin/env python3
"""Ajoute le selecteur de langue aux pages francaises originales.

Pour chaque fichier .html (hors -he.html / -en.html), insere :
  - Les liens hreflang dans le <head>
  - Le CSS du selecteur de langue
  - Le selecteur dans le <nav> du header avec FR comme actif
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LANG_SWITCHER_CSS = """
    .lang-switcher { display: flex; gap: 6px; align-items: center; margin-left: 12px; }
    .lang-switcher a {
      font-family: 'Inter', sans-serif; font-size: 11px;
      padding: 3px 7px; border-radius: 2px; letter-spacing: 1px;
      color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.15);
      text-decoration: none; text-transform: none;
    }
    .lang-switcher a.active { color: var(--gold, #C5A55A); border-color: var(--gold, #C5A55A); }
    .lang-switcher a:hover { color: var(--gold, #C5A55A); border-color: var(--gold, #C5A55A); }
"""


def add_hreflang(html: str, rel_path: str) -> str:
    if 'hreflang=' in html:
        return html
    base = rel_path.replace("\\", "/")
    stem = base[:-5] if base.endswith(".html") else base
    links = (
        f'<link rel="alternate" hreflang="fr" href="https://daattorah.com/{base}">\n'
        f'  <link rel="alternate" hreflang="en" href="https://daattorah.com/{stem}-en.html">\n'
        f'  <link rel="alternate" hreflang="he" href="https://daattorah.com/{stem}-he.html">'
    )
    if '<link rel="canonical"' in html:
        html = re.sub(
            r'(<link rel="canonical"[^>]*>)',
            rf'\1\n  {links}',
            html, count=1,
        )
    elif '<link rel="icon"' in html:
        html = re.sub(
            r'(<link rel="icon"[^>]*>)',
            rf'\1\n  {links}',
            html, count=1,
        )
    return html


def add_lang_switcher_css(html: str) -> str:
    if "</style>" in html and ".lang-switcher" not in html:
        html = html.replace("</style>", LANG_SWITCHER_CSS + "\n</style>", 1)
    return html


def add_lang_switcher_nav(html: str, base_name: str) -> str:
    """Insere le selecteur dans le <nav> avec FR comme actif."""
    switcher = (
        f'<span class="lang-switcher">'
        f'<a href="{base_name}.html" class="active">FR</a>'
        f'<a href="{base_name}-he.html">HE</a>'
        f'<a href="{base_name}-en.html">EN</a>'
        f'</span>'
    )
    nav_match = re.search(r'(<nav[^>]*>)(.*?)(</nav>)', html, re.DOTALL)
    if nav_match and "lang-switcher" not in nav_match.group(2):
        new_nav = nav_match.group(1) + nav_match.group(2) + switcher + nav_match.group(3)
        html = html[:nav_match.start()] + new_nav + html[nav_match.end():]
    return html


def process_file(src: Path):
    fname = src.name
    if fname.endswith("-he.html") or fname.endswith("-en.html"):
        return
    try:
        original = src.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    rel_path = src.relative_to(ROOT).as_posix()
    base_name = "index" if fname == "index.html" else fname.replace(".html", "")

    new = original
    new = add_hreflang(new, rel_path)
    new = add_lang_switcher_css(new)
    new = add_lang_switcher_nav(new, base_name)

    if new != original:
        src.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    targets = []
    # Pages principales a la racine
    for fname in [
        "index.html", "404.html", "chat.html", "communaute.html",
        "soutenir.html", "chitah-admour-hazaken.html",
    ]:
        p = ROOT / fname
        if p.exists():
            targets.append(p)
    # Tout sous sources/shabbat/
    sources = ROOT / "sources" / "shabbat"
    if sources.exists():
        for p in sources.rglob("*.html"):
            if p.name.endswith("-he.html") or p.name.endswith("-en.html"):
                continue
            targets.append(p)

    count = 0
    for src in targets:
        if process_file(src):
            count += 1

    print(f"Termine : {count}/{len(targets)} pages francaises mises a jour")


if __name__ == "__main__":
    main()
