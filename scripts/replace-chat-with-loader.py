#!/usr/bin/env python3
"""
replace-chat-with-loader.py — INP 2026 optimization

Remplace les inclusions de `chat-widget.min.js` (et `chat-widget.js`) par
`chat-loader.js` (mini-bootstrap qui ne charge le vrai widget qu'à la
première interaction utilisateur).

Cible : pages siman uniquement (sources/shabbat/). Ne touche pas le blog
(autre agent en parallèle), ni les pages racine (index, about, faq, etc.)
pour minimiser le scope. Le loader fonctionne pour toutes les pages mais
on ne migre que là où le gain est le plus mesurable (pages siman lourdes
= jusqu'à 274 KB de HTML, voir docs/PERFORMANCE-2026.md).

Le loader est rétrocompatible : il garde le même nom de classe CSS pour
le bouton FAB (`.daat-chat-button`), et inclut le vrai widget dès qu'une
interaction est détectée.

Usage :
    python3 scripts/replace-chat-with-loader.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIR = ROOT / "sources" / "shabbat"

# On accepte :
#   <script src="...chat-widget.min.js" defer></script>
#   <script src="...chat-widget.js" defer></script>
# avec n'importe quel chemin relatif/absolu.
PATTERN = re.compile(
    r'(<script\s+src="[^"]*?)chat-widget(?:\.min)?\.js("\s+defer\s*></script>)'
)


def transform(html: str) -> tuple[str, int]:
    """Return (new_html, n_substitutions)."""
    new_html, count = PATTERN.subn(r"\1chat-loader.js\2", html)
    return new_html, count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Show what would change without writing.")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    if not TARGET_DIR.exists():
        print(f"ERROR: {TARGET_DIR} not found", file=sys.stderr)
        return 1

    files = sorted(TARGET_DIR.rglob("*.html"))
    n_files_changed = 0
    n_subs_total = 0

    for f in files:
        try:
            html = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"SKIP (non-utf8): {f}", file=sys.stderr)
            continue

        new_html, n = transform(html)
        if n == 0:
            continue
        n_subs_total += n
        n_files_changed += 1
        if args.verbose:
            print(f"  {f.relative_to(ROOT)}: {n} sub(s)")
        if not args.dry_run:
            f.write_text(new_html, encoding="utf-8")

    verb = "would change" if args.dry_run else "changed"
    print(f"{n_files_changed} file(s) {verb}, {n_subs_total} substitution(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
