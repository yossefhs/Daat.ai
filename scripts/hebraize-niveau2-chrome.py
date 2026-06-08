#!/usr/bin/env python3
"""Hébraïse le chrome de structure restant des pages niveau-2 (Lamdan).

PR #94 avait traduit le pilpoul mais laissé en français/latin : le badge
« NIVEAU 2 — LAMDAN », le sous-titre « Études approfondies », le h2 « Pilpoul
approfondi », les labels (« Base talmudique », « Rédaction et iyun »,
« Mishnah Berurah », « Sujet »…) et « N Seifim (extraits) ».

S'applique aux 3 variantes (corps identique). Idempotent.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOB = "sources/shabbat/siman-*/niveau-2-lamdan*.html"

FIXED = [
    ("DAAT · NIVEAU 2 — LAMDAN", "DAAT · רמה 2 — למדן"),
    ("DAAT · LEVEL 2 — LAMDAN", "DAAT · רמה 2 — למדן"),
    ("DAAT · רמה 2 — LAMDAN", "DAAT · רמה 2 — למדן"),
    ("NIVEAU 2 — LAMDAN", "רמה 2 — למדן"),
    ("LEVEL 2 — LAMDAN", "רמה 2 — למדן"),
    ("הלכות שבת — Études approfondies", "הלכות שבת — עיון מעמיק"),
    ("הלכות שבת — In-depth studies", "הלכות שבת — עיון מעמיק"),
    ("הלכות שבת — In-depth study", "הלכות שבת — עיון מעמיק"),
    (">Pilpoul approfondi<", ">פלפול מעמיק<"),
    (">In-depth pilpul<", ">פלפול מעמיק<"),
    ("Sources talmudiques,", "מקורות התלמוד,"),
    ("Sources talmudiques :", "מקורות התלמוד:"),
    ("<strong>Rédaction et iyun :</strong>", "<strong>עריכה ועיון:</strong>"),
    ("<strong>Rédaction et Iyun :</strong>", "<strong>עריכה ועיון:</strong>"),
    ("<strong>Mishnah Berurah :</strong>", "<strong>משנה ברורה:</strong>"),
    ("<strong>Mishna Beroura :</strong>", "<strong>משנה ברורה:</strong>"),
    ("<strong>Base talmudique :</strong>", "<strong>בסיס תלמודי:</strong>"),
    ("<strong>Rédaction :</strong>", "<strong>עריכה:</strong>"),
    ("<strong>Sujet :</strong>", "<strong>נושא:</strong>"),
    ("Le texte du Choulhan Aroukh", "לשון השולחן ערוך"),
    ("(extraits)", "(נבחרים)"),
]

# Regex : « N Seifim » → « N סעיפים » ; « Seifim »/« Seif » isolés.
REGEX = [
    (re.compile(r"\bSeifim\b"), "סעיפים"),
    (re.compile(r"\bSeif\b"), "סעיף"),
]


def transform(t: str) -> str:
    for a, b in FIXED:
        t = t.replace(a, b)
    for rx, rep in REGEX:
        t = rx.sub(rep, t)
    return t


def main() -> int:
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
