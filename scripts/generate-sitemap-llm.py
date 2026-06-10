#!/usr/bin/env python3
"""
DAAT — Génère sitemap-llm.xml, dédié à l'indexation par les LLM.

Référence :
- llms.txt (à la racine) — manifeste de découverte de contenu
- sources/shabbat/siman-N/index.md (124 fichiers) — représentation Markdown
  compacte de chaque siman, générée par scripts/generate-siman-markdown.py

Format : XML sitemap standard (sitemaps.org/schemas/sitemap/0.9). Les URLs
pointent vers les ressources « LLM-friendly » (Markdown ou text/plain).
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://daattorah.com"
TODAY = dt.date.today().isoformat()

ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
ET.register_namespace("", ns)


def add_url(parent: ET.Element, loc: str, lastmod: str, priority: str,
            changefreq: str = "weekly") -> None:
    url = ET.SubElement(parent, f"{{{ns}}}url")
    ET.SubElement(url, f"{{{ns}}}loc").text = loc
    ET.SubElement(url, f"{{{ns}}}lastmod").text = lastmod
    ET.SubElement(url, f"{{{ns}}}changefreq").text = changefreq
    ET.SubElement(url, f"{{{ns}}}priority").text = priority


def main() -> int:
    urlset = ET.Element(f"{{{ns}}}urlset")

    # Top-level LLM resources
    add_url(urlset, f"{BASE_URL}/llms.txt", TODAY, "1.0", "weekly")

    # Per-siman Markdown
    siman_dirs = sorted(
        d for d in (ROOT / "sources" / "shabbat").iterdir()
        if d.is_dir() and d.name.startswith("siman-")
    )
    for d in siman_dirs:
        md = d / "index.md"
        if not md.exists():
            continue
        num = d.name.removeprefix("siman-")
        # Short canonical form (rewritten by vercel.json):
        loc = f"{BASE_URL}/oh/{num}/index.md"
        add_url(urlset, loc, TODAY, "0.8", "weekly")

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    out = ROOT / "sitemap-llm.xml"
    with out.open("wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding="utf-8", xml_declaration=False)
    print(f"OK — {out.relative_to(ROOT)} ({len(siman_dirs) + 1} URLs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
