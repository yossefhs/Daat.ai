#!/usr/bin/env python3
"""generate-sitemap.py — génère sitemap.xml COMPLET et canonique pour daattorah.com.

Principe : on scanne toutes les pages HTML, on lit leur <link rel="canonical">,
on saute les pages noindex, et on dédoublonne par URL canonique. Conséquences :
  - les pages siman HE/EN (qui se canonicalisent vers le FR) se replient sur l'URL FR
    → /oh/ n'apparaît qu'en français (stratégie « FR d'abord ») ;
  - racine, /limoud/ et /blog/ s'auto-canonicalisent → présents dans les 3 langues.

Le sitemap reflète ainsi EXACTEMENT les canoniques (bonne pratique SEO : ne jamais
lister d'URL non-canonique). Couvre racine + /oh/ + /limoud/ (194 jours) + /blog/.

lastmod = date du dernier commit git touchant le fichier (max si plusieurs fichiers
partagent une canonique). Lancer après ajout/suppression de pages :
    python3 scripts/generate-sitemap.py
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://daattorah.com"
OUT = ROOT / "sitemap.xml"

# Répertoires/pages jamais indexables.
SKIP_DIRS = {"node_modules", ".git", ".vercel", "data", "emails", "mockup",
             "transcriptions", "admin", "api", "scripts", "docs"}
SKIP_FILES = {"404.html", "404-he.html", "404-en.html", "offline.html",
              "poc-corpus.html"}

CANON_RE = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', re.I)
CANON_RE2 = re.compile(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', re.I)
NOINDEX_RE = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', re.I)


def git_dates() -> dict[str, str]:
    """Map chemin-relatif -> date (YYYY-MM-DD) du dernier commit, en un seul appel."""
    out = subprocess.run(
        ["git", "log", "--no-renames", "--date=short", "--format=@%cd", "--name-only"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout
    dates: dict[str, str] = {}
    cur = None
    for line in out.splitlines():
        if line.startswith("@"):
            cur = line[1:].strip()
        elif line.strip() and cur and line not in dates:
            dates[line] = cur  # première occurrence = commit le plus récent
    return dates


def priority_and_freq(url: str) -> tuple[str, str]:
    path = url[len(BASE):] or "/"
    if path == "/":
        return "1.0", "weekly"
    if path in ("/oh/", "/oh"):
        return "0.9", "weekly"
    if path.startswith("/chat"):
        return "0.9", "weekly"
    if path.startswith("/oh/"):
        # /oh/N/ (index siman) vs /oh/N/base… (niveaux)
        return ("0.8", "monthly") if path.rstrip("/").count("/") == 2 else ("0.7", "monthly")
    if path.startswith("/limoud/"):
        return ("0.8", "monthly") if "jour-" not in path else ("0.6", "monthly")
    if path.startswith("/blog/"):
        return ("0.8", "weekly") if path in ("/blog/", "/blog/index.html") else ("0.7", "monthly")
    if path.startswith("/index-"):  # accueil HE/EN
        return "0.9", "weekly"
    return "0.6", "monthly"  # about/faq/soutenir/communaute/chitah…


def main() -> None:
    dates = git_dates()
    # canonique -> meilleure date connue
    canon: dict[str, str] = {}
    scanned = skipped_noindex = 0

    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if set(rel.parts) & SKIP_DIRS or path.name in SKIP_FILES:
            continue
        if rel.parts and rel.parts[0].startswith("."):
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        if NOINDEX_RE.search(html):
            skipped_noindex += 1
            continue
        m = CANON_RE.search(html) or CANON_RE2.search(html)
        if not m:
            continue
        url = m.group(1).strip()
        if not url.startswith(BASE):
            continue
        scanned += 1
        d = dates.get(str(rel).replace("\\", "/"), "")
        if url not in canon or (d and d > canon[url]):
            canon[url] = d

    urls = sorted(canon)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        prio, freq = priority_and_freq(url)
        lastmod = canon[url]
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Récap
    def count(pred):
        return sum(1 for u in urls if pred(u[len(BASE):] or "/"))
    print(f"Pages indexables scannées : {scanned}")
    print(f"Pages noindex ignorées    : {skipped_noindex}")
    print(f"URLs canoniques uniques   : {len(urls)}")
    print(f"  racine/info : {count(lambda p: not p.startswith(('/oh', '/limoud', '/blog')))}")
    print(f"  /oh/        : {count(lambda p: p.startswith('/oh'))}")
    print(f"  /limoud/    : {count(lambda p: p.startswith('/limoud'))}")
    print(f"  /blog/      : {count(lambda p: p.startswith('/blog'))}")
    print(f"→ {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
