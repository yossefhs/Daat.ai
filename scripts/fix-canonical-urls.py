#!/usr/bin/env python3
"""Harmonise les <link rel="canonical"> (et og:url) des pages siman.

Convention (déjà appliquée aux niveaux 1/2/3) : toutes les variantes de langue
d'une page pointent vers la jolie URL canonique /oh/N/... — pas vers l'URL
.html brute ni vers /sources/shabbat/... Cela évite le contenu dupliqué entre
la version .html (servie en 200 via les rewrites Vercel) et la jolie URL.

Idempotent : relancer ne change rien si tout est déjà conforme.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"
BASE = "https://daattorah.com"

# filename (sans suffixe de langue) -> segment de jolie URL
LEVEL_SEGMENT = {
    "niveau-1-base": "base",
    "niveau-2-lamdan": "lamdan",
    "niveau-3-synthese": "synthese",
    "niveau-4-daat-harav": "daat-harav",
}


def pretty_url(siman_num: int, filename: str) -> str | None:
    """Renvoie la jolie URL canonique pour un fichier donné, ou None si hors scope."""
    stem = filename[:-5] if filename.endswith(".html") else filename
    # retire le suffixe de langue (-he / -en)
    stem = re.sub(r"-(he|en)$", "", stem)
    if stem == "index":
        return f"{BASE}/oh/{siman_num}/"
    seg = LEVEL_SEGMENT.get(stem)
    if seg:
        return f"{BASE}/oh/{siman_num}/{seg}"
    return None


def main() -> int:
    changed = 0
    scanned = 0
    for siman_dir in sorted(SHABBAT.glob("siman-*")):
        m = re.match(r"siman-(\d+)$", siman_dir.name)
        if not m:
            continue
        siman_num = int(m.group(1))
        for html_path in siman_dir.glob("*.html"):
            target = pretty_url(siman_num, html_path.name)
            if not target:
                continue
            scanned += 1
            text = html_path.read_text(encoding="utf-8")
            new = text
            new = re.sub(
                r'(<link\s+rel="canonical"\s+href=")[^"]*(")',
                lambda mm: mm.group(1) + target + mm.group(2),
                new,
                count=1,
            )
            new = re.sub(
                r'(<meta\s+property="og:url"\s+content=")[^"]*(")',
                lambda mm: mm.group(1) + target + mm.group(2),
                new,
                count=1,
            )
            if new != text:
                html_path.write_text(new, encoding="utf-8")
                changed += 1

    print(f"Pages siman scannées : {scanned}")
    print(f"Pages corrigées      : {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
