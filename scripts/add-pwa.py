#!/usr/bin/env python3
"""add-pwa.py — injecte les balises PWA (manifest, icônes, theme-color) et le
script /assets/js/pwa.js dans le <head> de toutes les pages HTML du site.

Idempotent : ré-exécutable sans dupliquer (détection via le marqueur manifest).
N'agit que sur les fichiers possédant un </head>. Ignore node_modules.

Usage :
    python3 scripts/add-pwa.py            # applique
    python3 scripts/add-pwa.py --dry-run  # liste sans écrire
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "/manifest.webmanifest"

BLOCK = """  <!-- PWA / app installable -->
  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#1A1F3A">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Daat Torah">
  <script src="/assets/js/pwa.js" defer></script>
"""

SKIP_DIRS = {"node_modules", ".git", ".vercel"}


def iter_html(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".html"):
                yield os.path.join(dirpath, name)


def main():
    dry = "--dry-run" in sys.argv
    changed = skipped = nohead = 0
    for path in iter_html(ROOT):
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        if MARKER in html:
            skipped += 1
            continue
        if "</head>" not in html:
            nohead += 1
            continue
        new = html.replace("</head>", BLOCK + "</head>", 1)
        changed += 1
        if not dry:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)

    rel = lambda n: n
    print(f"PWA injecté   : {changed}")
    print(f"Déjà présent  : {skipped}")
    print(f"Sans <head>   : {nohead}")
    if dry:
        print("(dry-run — aucun fichier écrit)")


if __name__ == "__main__":
    main()
