#!/usr/bin/env python3
"""Audit detaille : pour chaque siman, compte les seifim presents dans
chaque niveau, identifie les lacunes par rapport au Choulhan Aroukh Mehaber.

Le Mehaber suit la numerotation traditionnelle. Le SHHaRav (Admour HaZaken)
a souvent plus de seifim car il subdivise. On compare :
 - niveau-1-base : pedagogique (doit couvrir le Mehaber)
 - niveau-4-daat-harav : SHHaRav complet
 - et on signale ce qui semble incomplet.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources" / "shabbat"

# Comptes officiels du Choulhan Aroukh Mehaber pour Hilchos Shabbos.
# (Source : edition standard. Approximatif pour les simanim non-Hilchos Shabbat.)
MEHABER_SEIFIM = {
    242: 1, 243: 3, 244: 6, 245: 2, 246: 5, 247: 6, 248: 4, 249: 4,
    250: 2, 251: 2, 252: 7, 253: 5, 254: 9, 255: 3, 256: 1, 257: 8,
    258: 1, 259: 4, 260: 2, 261: 4, 262: 3, 263: 11, 264: 9, 265: 4,
    266: 13, 267: 3, 268: 13, 269: 1, 270: 2, 271: 12, 272: 9, 273: 7,
    274: 4, 275: 12, 276: 5, 277: 5, 278: 1, 279: 7, 280: 2, 281: 1,
    282: 7, 283: 1, 284: 7, 285: 7, 286: 4, 287: 1, 288: 9, 289: 2,
    290: 2, 291: 8, 292: 2, 293: 3, 294: 1, 295: 1, 296: 8, 297: 1,
    298: 14, 299: 10, 300: 1, 301: 60, 302: 11, 303: 27, 304: 22, 305: 21,
    306: 13, 307: 22, 308: 52, 309: 4, 310: 8, 311: 8, 312: 9, 313: 9,
    314: 12, 315: 13, 316: 12, 317: 5, 318: 19, 319: 17, 320: 21, 321: 19,
    322: 6, 323: 7, 324: 14, 325: 14, 326: 13, 327: 2, 328: 47, 329: 9,
    330: 10, 331: 9, 332: 4, 333: 1, 334: 27, 335: 5, 336: 13, 337: 3,
    338: 8, 339: 8, 340: 14, 341: 3, 342: 1, 343: 1, 344: 1, 345: 19,
    346: 3, 347: 4, 348: 3, 349: 5, 350: 2, 351: 1, 352: 6, 353: 1,
    354: 2, 355: 2, 356: 4, 357: 3, 358: 13, 359: 4, 360: 1, 361: 1,
    362: 11, 363: 36, 364: 4, 365: 8,
}


def count_seifim_in_file(file_path: Path) -> int:
    """Compte les seifim distincts presents dans un fichier HTML.

    Cherche des marqueurs comme :
    - "Seif Alef", "Seif Bet", "Seif Gimel"...
    - "Seif 1", "Seif 2"...
    - "סעיף א", "סעיף ב"...
    """
    if not file_path.exists():
        return 0
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        return 0

    # Latin transliterations (Alef, Bet, ...) — format "Seif Alef"
    LATIN_LETTERS = [
        "Alef", "Bet", "Gimel", "Dalet", "He", "Hei", "Vav", "Zayin",
        "Het", "Chet", "Tet", "Yod",
        "Yod Alef", "Yod Bet", "Yod Gimel", "Yod Dalet", "Yod He",
        "Yod Vav", "Yod Zayin", "Yod Het", "Yod Tet",
        "Kaf", "Lamed", "Mem", "Nun", "Samech", "Ayin", "Pe", "Tzadi",
    ]
    latin_count = 0
    for letter in LATIN_LETTERS:
        if re.search(rf"\bSeif {letter}\b", text):
            latin_count += 1

    # Format mixte : "Seif א", "Seif ב" — translit + lettre hébraïque
    mixed_count = len(set(re.findall(r"\bSeif\s+([א-ת]['׳״\"]?[א-ת]?['׳״\"]?)", text)))

    # Format français : "Séif א"
    fr_mixed_count = len(set(re.findall(r"\bSéif\s+([א-ת]['׳״\"]?[א-ת]?['׳״\"]?)", text)))

    # Hebrew letter sequence (sequential count) — format "סעיף א"
    HE_LETTERS = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י']
    he_count = 0
    for letter in HE_LETTERS:
        if re.search(rf'סעיף\s+{letter}[\'״]?\b', text):
            he_count += 1

    # Numerical Seif (Seif 1, Seif 2, ...)
    num_count = len(set(re.findall(r"\bSeif (\d+)\b", text)))

    return max(
        latin_count, mixed_count, fr_mixed_count, he_count, num_count,
        1 if text else 0,
    )


def main():
    print(f"{'Siman':<6} {'Mehaber':>8} {'N1-FR':>6} {'N3-FR':>6} {'N4-FR':>6}  Note")
    print("-" * 70)
    total = 0
    incomplete = 0
    for num in sorted(MEHABER_SEIFIM.keys()):
        folder = SOURCES / f"siman-{num}"
        if not folder.exists():
            continue
        total += 1
        mehaber = MEHABER_SEIFIM[num]
        n1 = count_seifim_in_file(folder / "niveau-1-base.html")
        n3 = count_seifim_in_file(folder / "niveau-3-synthese.html")
        n4 = count_seifim_in_file(folder / "niveau-4-daat-harav.html")
        note = ""
        if n1 < mehaber and mehaber >= 2:
            note = f"⚠ N1 manque {mehaber - n1} seifim"
            incomplete += 1
        print(f"{num:<6} {mehaber:>8} {n1:>6} {n3:>6} {n4:>6}  {note}")
    print(f"\nTotal : {total} simanim audites · {incomplete} incomplets en N1")


if __name__ == "__main__":
    main()
