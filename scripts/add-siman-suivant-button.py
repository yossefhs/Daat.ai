#!/usr/bin/env python3
"""Ajoute un bouton « Siman suivant → » a la fin de chaque niveau-1-base.html.

Cible les 124 simanim (242 a 365) dans les 3 langues. Le bouton est insere
juste avant le .yh-watermark de fin. Style en ligne pour fonctionner meme
sur les fichiers qui n'ont pas la classe .next-seif-nav.

Pour le siman 365 (dernier), aucun bouton.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

FIRST_SIMAN = 242
LAST_SIMAN = 365

# Style inline (independant des CSS de chaque page)
NAV_STYLE = (
    "margin:40px 0 20px 0;padding:20px 24px;"
    "background:linear-gradient(135deg,#1A1F3A 0%,#2a3050 100%);"
    "border-radius:8px;display:flex;align-items:center;justify-content:space-between;"
    "gap:16px;page-break-inside:avoid;"
)
LABEL_STYLE = "color:#d4c89a;font-size:11pt;font-style:italic;"
LINK_STYLE = (
    "color:#C5A55A;text-decoration:none;font-family:'Cormorant Garamond','Georgia',serif;"
    "font-size:15pt;font-weight:bold;"
)
LINK_STYLE_HE = (
    "color:#C5A55A;text-decoration:none;font-family:'Frank Ruhl Libre','David',serif;"
    "font-size:16pt;font-weight:bold;"
)

LABELS = {
    "fr": ("Pour continuer l'étude — siman suivant", "Siman {n} →", "borderLeft"),
    "he": ("להמשך הלימוד — הסימן הבא", "סימן {n} ←", "borderRight"),
    "en": ("Continue the study — next siman", "Siman {n} →", "borderLeft"),
}

# Numerotation hebraique des simanim (242 = רמ״ב, 243 = רמ״ג, etc.)
HE_DIGITS = {
    1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט",
    10: "י", 20: "כ", 30: "ל", 40: "מ", 50: "נ", 60: "ס", 70: "ע", 80: "פ",
    90: "צ", 100: "ק", 200: "ר", 300: "ש", 400: "ת",
}


def num_to_he(n: int) -> str:
    """Convertit un nombre en gematria simple avec geresh/gershayim."""
    parts = []
    while n >= 400:
        parts.append("ת")
        n -= 400
    if n >= 100:
        h = (n // 100) * 100
        parts.append(HE_DIGITS[h])
        n -= h
    if n == 15:
        parts.append("ט״ו")
        return "".join(parts) if len(parts) > 1 else "ט״ו"
    if n == 16:
        parts.append("ט״ז")
        return "".join(parts) if len(parts) > 1 else "ט״ז"
    if n >= 10:
        tens = (n // 10) * 10
        parts.append(HE_DIGITS[tens])
        n -= tens
    if n >= 1:
        parts.append(HE_DIGITS[n])
    s = "".join(parts)
    if len(s) == 1:
        return f"{s}׳"
    return s[:-1] + "״" + s[-1]


def build_button(current_num: int, lang: str) -> str:
    if current_num >= LAST_SIMAN:
        return ""
    next_num = current_num + 1
    label_text, link_template, border = LABELS[lang]

    if lang == "he":
        next_label_num = num_to_he(next_num)
        link_label = link_template.format(n=next_label_num)
        nav_style = NAV_STYLE + "direction:rtl;border-right:6px solid #C5A55A;"
        link_style = LINK_STYLE_HE
        href_suffix = "-he.html"
    elif lang == "en":
        link_label = link_template.format(n=next_num)
        nav_style = NAV_STYLE + "border-left:6px solid #C5A55A;"
        link_style = LINK_STYLE
        href_suffix = "-en.html"
    else:
        link_label = link_template.format(n=next_num)
        nav_style = NAV_STYLE + "border-left:6px solid #C5A55A;"
        link_style = LINK_STYLE
        href_suffix = ".html"

    href = f"../siman-{next_num}/niveau-1-base{href_suffix}"
    return (
        f'<div class="next-siman-nav" style="{nav_style}">'
        f'<span style="{LABEL_STYLE}">{label_text}</span>'
        f'<a href="{href}" style="{link_style}">{link_label}</a>'
        f'</div>'
    )


WATERMARK_RE = re.compile(r'(<div class="yh-watermark">)', re.IGNORECASE)


def process_file(path: Path, num: int, lang: str) -> bool:
    if not path.exists():
        return False
    try:
        html = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    # Idempotence : si deja present, on retire avant de re-ajouter (au cas ou).
    html_clean = re.sub(
        r'<div class="next-siman-nav"[^>]*>.*?</div>\s*',
        '',
        html,
        flags=re.DOTALL,
    )

    button = build_button(num, lang)
    if not button:
        # Dernier siman : on a retire l'eventuel bouton mais on ne rajoute rien.
        if html_clean != html:
            path.write_text(html_clean, encoding="utf-8")
            return True
        return False

    if "yh-watermark" not in html_clean:
        # Pas de watermark : on insere avant </body>
        new_html, n = re.subn(
            r'(</body>)',
            f'{button}\n\\1',
            html_clean,
            count=1,
        )
    else:
        new_html, n = WATERMARK_RE.subn(
            f'{button}\n\n\\1',
            html_clean,
            count=1,
        )

    if n == 0 or new_html == html:
        return False
    path.write_text(new_html, encoding="utf-8")
    return True


def main():
    print("=== Ajout des boutons « Siman suivant → » sur niveau-1-base.html ===\n")
    total_modified = 0
    by_lang = {"fr": 0, "he": 0, "en": 0}
    for num in range(FIRST_SIMAN, LAST_SIMAN + 1):
        folder = SHABBAT / f"siman-{num}"
        if not folder.exists():
            continue
        files = [
            (folder / "niveau-1-base.html", "fr"),
            (folder / "niveau-1-base-he.html", "he"),
            (folder / "niveau-1-base-en.html", "en"),
        ]
        for path, lang in files:
            if process_file(path, num, lang):
                total_modified += 1
                by_lang[lang] += 1
    print(f"\nTotal : {total_modified} fichiers modifies")
    print(f"  FR : {by_lang['fr']}")
    print(f"  HE : {by_lang['he']}")
    print(f"  EN : {by_lang['en']}")


if __name__ == "__main__":
    main()
