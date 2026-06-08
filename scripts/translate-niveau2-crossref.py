#!/usr/bin/env python3
"""Traduit en hébreu le bloc « Pour aller plus loin » des pages niveau-2 (Lamdan).

Ces pages sont en hébreu sauf ce bloc de renvoi vers les niveaux 3/4, resté en
français (titre « aller plus loin », descriptions Synthèse / Daat HaRav) + le
filigrane « רמה 2 — Lamdan ». On le remplace par une version hébraïque uniforme.

S'applique aux 3 variantes (FR/HE/EN, corps identique). Idempotent.

Usage : python3 scripts/translate-niveau2-crossref.py [--dry siman]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOB = "sources/shabbat/siman-*/niveau-2-lamdan*.html"

HEAD = re.compile(r"<h3>\s*(?:עבור\s*)?(?:Pour\s+)?aller plus loin\s*</h3>", re.IGNORECASE)
# Bloc des deux renvois : de « רמה 3 — Synthèse » jusqu'au </p> qui suit.
BLOCK = re.compile(r"<strong>\s*רמה 3 — Synthèse.*?</p>", re.IGNORECASE | re.DOTALL)

HEB_HEAD = "<h3>להעמקה</h3>"
HEB_BLOCK = (
    "<strong>רמה 3 — סיכום:</strong> ריכוז מובנה עם סימני זיכרון, עצי החלטה וכללי אצבע.<br>\n"
    "<strong>רמה 4 — דעת הרב:</strong> שיטת אדמו״ר הזקן (שולחן ערוך הרב).\n</p>"
)


def transform(text: str) -> str:
    text = HEAD.sub(HEB_HEAD, text)
    text = BLOCK.sub(HEB_BLOCK, text)
    text = text.replace("רמה 2 — Lamdan", "רמה 2 — למדן")
    return text


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--dry":
        siman = args[1]
        p = ROOT / f"sources/shabbat/siman-{siman}/niveau-2-lamdan.html"
        out = transform(p.read_text(encoding="utf-8"))
        import difflib
        before = p.read_text(encoding="utf-8").splitlines()
        for line in difflib.unified_diff(before, out.splitlines(), lineterm="", n=0):
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                print(line)
        return 0

    files = sorted(ROOT.glob(GLOB))
    changed = 0
    for f in files:
        t = f.read_text(encoding="utf-8")
        nt = transform(t)
        if nt != t:
            f.write_text(nt, encoding="utf-8")
            changed += 1
    print(f"Fichiers niveau-2 : {len(files)} | modifiés : {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
