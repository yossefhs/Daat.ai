#!/usr/bin/env python3
"""Passe les pages niveau-2 (Lamdan) FR et EN en RTL.

Le corps de ces pages est déjà 100% hébreu (copié depuis la version HE en
PR #94) ; seul le <html> restait en dir="ltr" (ou sans dir), ce qui affichait
l'hébreu de gauche à droite. On force dir="rtl" sur la balise <html>, en
conservant l'attribut lang (pour ne pas casser hreflang/canonical).

Idempotent. La variante -he est déjà en rtl (ignorée).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOBS = [
    "sources/shabbat/siman-*/niveau-2-lamdan.html",
    "sources/shabbat/siman-*/niveau-2-lamdan-en.html",
]
HTML_RE = re.compile(r"<html\b([^>]*)>", re.IGNORECASE)


def fix_attrs(attrs: str) -> str:
    # Retire un éventuel dir existant, puis impose dir="rtl".
    attrs = re.sub(r'\s*dir\s*=\s*"[^"]*"', "", attrs, flags=re.IGNORECASE)
    return attrs.rstrip() + ' dir="rtl"'


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    m = HTML_RE.search(text)
    if not m:
        return False
    new_tag = f"<html{fix_attrs(m.group(1))}>"
    if new_tag == m.group(0):
        return False  # déjà correct
    new_text = text[: m.start()] + new_tag + text[m.end():]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    files = []
    for g in GLOBS:
        files += sorted(ROOT.glob(g))
    changed = sum(1 for f in files if process(f))
    print(f"Fichiers niveau-2 FR/EN : {len(files)}")
    print(f"  Passés en dir=rtl     : {changed}")
    print(f"  Déjà rtl / inchangés  : {len(files) - changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
