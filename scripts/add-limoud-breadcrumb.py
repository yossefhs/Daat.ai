#!/usr/bin/env python3
"""add-limoud-breadcrumb.py — ajoute un BreadcrumbList aux pages /limoud/.

Les 587 pages du plan Daat Yomi n'ont aucun fil d'Ariane structuré.
Ajout : Accueil › Daat Yomi › (Jour N) — localisé fr/he/en. Idempotent.

    python3 scripts/add-limoud-breadcrumb.py [--dry-run]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMOUD = ROOT / "limoud"
BASE = "https://daattorah.com"

HOME = {"fr": (f"{BASE}/", "Accueil"), "he": (f"{BASE}/index-he.html", "דף הבית"),
        "en": (f"{BASE}/index-en.html", "Home")}
YOMI = {"fr": (f"{BASE}/limoud/index.html", "Daat Yomi"),
        "he": (f"{BASE}/limoud/index-he.html", "דעת יומי"),
        "en": (f"{BASE}/limoud/index-en.html", "Daat Yomi")}


def field(html: str, pat: str) -> str | None:
    m = re.search(pat, html)
    return m.group(1) if m else None


def main() -> None:
    dry = "--dry-run" in sys.argv
    added = skipped = 0
    for path in sorted(LIMOUD.glob("*.html")):
        if path.name in ("mon-plan.html", "personnaliser.html"):
            skipped += 1
            continue
        html = path.read_text(encoding="utf-8")
        if "BreadcrumbList" in html:
            skipped += 1
            continue
        lang = field(html, r'<html[^>]*\blang="([a-z]{2})"') or "fr"
        lang = lang if lang in HOME else "fr"
        canonical = field(html, r'<link rel="canonical" href="([^"]*)"')
        title = field(html, r"<h1[^>]*>([^<]*)</h1>")
        if not canonical:
            skipped += 1
            continue

        items = [HOME[lang], YOMI[lang]]
        is_index = path.stem in ("index", "index-he", "index-en")
        if not is_index and title:
            items.append((canonical, title.strip()))

        node = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
                for i, (url, name) in enumerate(items)
            ],
        }
        block = ('  <script type="application/ld+json">\n  '
                 + json.dumps(node, ensure_ascii=False, indent=2).replace("\n", "\n  ")
                 + "\n  </script>\n")
        new = html.replace("</head>", block + "</head>", 1)
        if new == html:
            skipped += 1
            continue
        added += 1
        if not dry:
            path.write_text(new, encoding="utf-8")
    print(f"BreadcrumbList ajouté : {added}")
    print(f"Ignoré               : {skipped}")
    if dry:
        print("(dry-run)")


if __name__ == "__main__":
    main()
