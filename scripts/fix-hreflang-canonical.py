#!/usr/bin/env python3
"""fix-hreflang-canonical.py — rend les pages siman HE/EN auto-canoniques.

Bug SEO : les pages `*-he.html` / `*-en.html` de sources/shabbat se canonicalisent
vers la version FR (ex. niveau-2-lamdan-he.html → canonical /oh/N/lamdan). Or elles
déclarent déjà un hreflang correct. Tant que canonical pointe vers le FR, Google
IGNORE le hreflang et n'indexe PAS le HE/EN.

Correctif : pour chaque page HE/EN, on met le <link rel="canonical"> = la valeur de
son propre <link rel="alternate" hreflang="{he|en}">. Idempotent.

    python3 scripts/fix-hreflang-canonical.py [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "shabbat"

CANON_RE = re.compile(r'(<link\s+rel="canonical"\s+href=")([^"]*)(")')


def hreflang_href(html: str, lang: str) -> str | None:
    m = re.search(
        r'<link\s+rel="alternate"\s+hreflang="' + lang + r'"\s+href="([^"]*)"',
        html,
    )
    return m.group(1) if m else None


def main() -> None:
    dry = "--dry-run" in sys.argv
    fixed = already = nocanon = nohreflang = 0

    for path in SRC.rglob("*.html"):
        name = path.name
        if name.endswith("-he.html"):
            lang = "he"
        elif name.endswith("-en.html"):
            lang = "en"
        else:
            continue

        html = path.read_text(encoding="utf-8")
        target = hreflang_href(html, lang)
        if not target:
            nohreflang += 1
            continue
        m = CANON_RE.search(html)
        if not m:
            nocanon += 1
            continue
        if m.group(2) == target:
            already += 1
            continue

        new = html[: m.start()] + m.group(1) + target + m.group(3) + html[m.end():]
        fixed += 1
        if not dry:
            path.write_text(new, encoding="utf-8")

    print(f"Canonical corrigé (→ auto-canonique) : {fixed}")
    print(f"Déjà auto-canonique                  : {already}")
    print(f"Sans hreflang {{he|en}}                : {nohreflang}")
    print(f"Sans canonical                       : {nocanon}")
    if dry:
        print("(dry-run — aucun fichier écrit)")


if __name__ == "__main__":
    main()
