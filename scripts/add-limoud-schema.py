#!/usr/bin/env python3
"""add-limoud-schema.py — ajoute un JSON-LD LearningResource aux pages /limoud/jour-*.

Les 582 pages jour (194 × 3 langues) n'ont aucun schema. On ajoute un
`LearningResource` rattaché au `Course` « Daat Yomi » (limoud/index.html),
localisé (fr/he/en). Éligible au rich result « Cours » et renforce l'autorité
topique. Idempotent (skip si un application/ld+json existe déjà).

    python3 scripts/add-limoud-schema.py [--dry-run]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMOUD = ROOT / "limoud"

COURSE = {
    "fr": "Daat Yomi — Hilkhot Shabbat",
    "he": "דעת יומי — הלכות שבת",
    "en": "Daat Yomi — Laws of Shabbat",
}
TEACHES = {
    "fr": "Hilkhot Shabbat — Siman {s}",
    "he": "הלכות שבת — סימן {s}",
    "en": "Laws of Shabbat — Siman {s}",
}


def field(html: str, pattern: str) -> str | None:
    m = re.search(pattern, html)
    return m.group(1) if m else None


def main() -> None:
    dry = "--dry-run" in sys.argv
    added = skipped = 0

    for path in sorted(LIMOUD.glob("jour-*.html")):
        html = path.read_text(encoding="utf-8")
        if "application/ld+json" in html:
            skipped += 1
            continue
        lang = field(html, r'<html[^>]*\blang="([a-z]{2})"') or "fr"
        canonical = field(html, r'<link rel="canonical" href="([^"]*)"')
        desc = field(html, r'<meta name="description" content="([^"]*)"') or ""
        title = field(html, r"<h1[^>]*>([^<]*)</h1>") or path.stem
        day = re.search(r"jour-(\d+)", path.name)
        # Siman via lien /oh/N, sinon via le titre (« Siman 304 » / « סימן 304 »).
        siman = field(html, r"/oh/(\d+)") or field(html, r"(?:[Ss]iman|סימן)\s+(\d+)")
        if not (canonical and siman and day):
            skipped += 1
            continue
        daynum = int(day.group(1))

        node = {
            "@context": "https://schema.org",
            "@type": "LearningResource",
            "name": title.strip(),
            "url": canonical,
            "inLanguage": lang,
            "learningResourceType": "Lesson",
            "position": daynum,
            "teaches": TEACHES[lang].format(s=siman),
            "description": desc,
            "isPartOf": {
                "@type": "Course",
                "name": COURSE[lang],
                "url": f"https://daattorah.com/limoud/",
            },
            "provider": {
                "@type": "Organization",
                "name": "DAAT",
                "url": "https://daattorah.com",
            },
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

    print(f"Schema LearningResource ajouté : {added}")
    print(f"Ignoré (déjà schema / incomplet) : {skipped}")
    if dry:
        print("(dry-run)")


if __name__ == "__main__":
    main()
