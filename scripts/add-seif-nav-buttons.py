#!/usr/bin/env python3
"""Ajoute des boutons « Seif suivant → » a la fin de chaque seif dans niveau-1-base.

Cible siman-242 niveau-1-base.html (FR/HE/EN). Pour chaque seif Bet à Yod-Gimel :
 - ajoute un id="seif-X" sur le titre de section
 - insère un bouton de navigation vers le seif suivant après la question-box

Aussi : un bouton à la fin du Seif Alef (avant Partie II) pour aller au Seif Bet,
et un bouton à la fin du Seif Yod-Gimel pour passer au siman 243.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIMAN_DIR = ROOT / "sources" / "shabbat" / "siman-242"

# Tuples : (id, num_section, label_FR, label_HE, label_EN)
SEIFIM = [
    ("bet",        9,  "Seif Bet",        "סעיף ב'",       "Seif Bet"),
    ("gimel",      10, "Seif Guimel",     "סעיף ג'",       "Seif Gimel"),
    ("dalet",      11, "Seif Dalet",      "סעיף ד'",       "Seif Dalet"),
    ("he",         12, "Seif Hé",         "סעיף ה'",       "Seif Heh"),
    ("vav",        13, "Seif Vav",        "סעיף ו'",       "Seif Vav"),
    ("zayin",      14, "Seif Zayin",      "סעיף ז'",       "Seif Zayin"),
    ("het",        15, "Seif 'Het",       "סעיף ח'",       "Seif Ches"),
    ("tet",        16, "Seif Tet",        "סעיף ט'",       "Seif Tes"),
    ("yod",        17, "Seif Yod",        "סעיף י'",       "Seif Yud"),
    ("yod-alef",   18, "Seif Yod-Alef",   'סעיף י"א',      "Seif Yud-Alef"),
    ("yod-bet",    19, "Seif Yod-Bet",    'סעיף י"ב',      "Seif Yud-Bet"),
    ("yod-gimel",  20, "Seif Yod-Guimel", 'סעיף י"ג',      "Seif Yud-Gimel"),
]

# CSS commun a injecter avant </style>
CSS_BLOCK = """
  /* Bouton de navigation vers le seif suivant */
  .next-seif-nav {
    margin: 28px 0 18px 0;
    padding: 16px 22px;
    background: linear-gradient(135deg, #1A1F3A 0%, #2a3050 100%);
    border-left: 6px solid #C5A55A;
    border-radius: 6px;
    page-break-inside: avoid;
  }
  .next-seif-nav .row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
  }
  .next-seif-nav .label {
    color: #d4c89a;
    font-size: 10.5pt;
    font-style: italic;
  }
  .next-seif-nav a {
    color: #C5A55A;
    text-decoration: none;
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-size: 14pt;
    font-weight: bold;
    transition: color 0.2s;
  }
  .next-seif-nav a:hover { color: #fff; }
"""

CSS_BLOCK_HE = """
  /* כפתור ניווט לסעיף הבא */
  .next-seif-nav {
    margin: 28px 0 18px 0;
    padding: 16px 22px;
    background: linear-gradient(135deg, #1A1F3A 0%, #2a3050 100%);
    border-right: 6px solid #C5A55A;
    border-left: none;
    border-radius: 6px;
    page-break-inside: avoid;
  }
  .next-seif-nav .row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    direction: rtl;
  }
  .next-seif-nav .label {
    color: #d4c89a;
    font-size: 10.5pt;
    font-style: italic;
  }
  .next-seif-nav a {
    color: #C5A55A;
    text-decoration: none;
    font-family: 'Frank Ruhl Libre', 'David', serif;
    font-size: 15pt;
    font-weight: bold;
    transition: color 0.2s;
  }
  .next-seif-nav a:hover { color: #fff; }
"""


def build_button(href: str, label_text: str, target_label: str, lang: str) -> str:
    """Construit le HTML d'un bouton de navigation."""
    if lang == "he":
        # En RTL la fleche pointe a gauche : ←
        arrow = "←"
        return (
            f'<div class="next-seif-nav"><div class="row">'
            f'<span class="label">{label_text}</span>'
            f'<a href="{href}">{target_label} {arrow}</a>'
            f'</div></div>'
        )
    # FR / EN — LTR, fleche pointe a droite
    arrow = "→"
    return (
        f'<div class="next-seif-nav"><div class="row">'
        f'<span class="label">{label_text}</span>'
        f'<a href="{href}">{target_label} {arrow}</a>'
        f'</div></div>'
    )


def get_labels(lang: str) -> dict:
    """Renvoie les libelles UI par langue."""
    if lang == "fr":
        return {
            "next": "Pour continuer l'étude",
            "synth": "Synthèse pratique",
            "next_siman": "Siman 243",
            "to_synth_label": "Synthèse du siman",
        }
    if lang == "he":
        return {
            "next": "להמשך הלימוד",
            "synth": "סיכום מעשי",
            "next_siman": "סימן רמ\"ג",
            "to_synth_label": "סיכום הסימן",
        }
    return {
        "next": "Continue the study",
        "synth": "Practical synthesis",
        "next_siman": "Siman 243",
        "to_synth_label": "Siman synthesis",
    }


def get_seif_label(idx: int, lang: str) -> str:
    """Renvoie le label du seif a l'index donne dans la langue donnee."""
    _id, _num, fr, he, en = SEIFIM[idx]
    return {"fr": fr, "he": he, "en": en}[lang]


def inject_css(html: str, lang: str) -> str:
    """Injecte le bloc CSS du bouton avant </style>."""
    if ".next-seif-nav" in html:
        return html
    block = CSS_BLOCK_HE if lang == "he" else CSS_BLOCK
    return html.replace("</style>", block + "</style>", 1)


def add_ids_to_headings(html: str, lang: str) -> str:
    """Ajoute id='seif-X' aux titres de section (9. à 20.) et id='seif-alef' au 1.

    Modifie aussi le titre 'Partie II' avec id='partie-ii' et '21. Synthèse' avec id='synthese'.
    """
    # 1. Seif Alef (section 1)
    html = re.sub(
        r'<h2 class="section-title">(1\. )',
        r'<h2 class="section-title" id="seif-alef">\1',
        html,
        count=1,
    )
    # 2. Seifim Bet à Yod-Gimel (sections 9 à 20)
    for sid, num, *_ in SEIFIM:
        pattern = rf'<h2 class="section-title">({num}\. )'
        replacement = rf'<h2 class="section-title" id="seif-{sid}">\1'
        html = re.sub(pattern, replacement, html, count=1)
    # 3. Synthèse pratique (section 21)
    html = re.sub(
        r'<h2 class="section-title">(21\. )',
        r'<h2 class="section-title" id="synthese">\1',
        html,
        count=1,
    )
    return html


def insert_button_before_section(html: str, num: int, button_html: str) -> tuple[str, bool]:
    """Insere le bouton juste avant `<div class="page-break"></div>` qui precede
    la section numerotee `num`.

    Strategie : on cherche le marqueur du h2 cible, puis on remonte au plus proche
    `<div class="page-break">` avant lui et on insere le bouton avant ce page-break.
    """
    # Marqueur du h2 cible (avec id deja ajoute)
    h2_pattern = rf'<h2 class="section-title"[^>]*>{num}\. '
    m = re.search(h2_pattern, html)
    if not m:
        return html, False
    h2_pos = m.start()
    # Cherche le dernier `<div class="page-break"></div>` avant h2_pos
    page_break_marker = '<div class="page-break"></div>'
    pb_pos = html.rfind(page_break_marker, 0, h2_pos)
    if pb_pos == -1:
        # pas de page-break, on insere juste avant le h2
        before = html[:h2_pos]
        after = html[h2_pos:]
        return before + button_html + "\n\n" + after, True
    before = html[:pb_pos]
    after = html[pb_pos:]
    return before + button_html + "\n\n" + after, True


def insert_button_before_synthese(html: str, button_html: str) -> tuple[str, bool]:
    """Insere le bouton avant la section 21 (Synthèse pratique)."""
    h2_pattern = r'<h2 class="section-title"[^>]*>21\. '
    m = re.search(h2_pattern, html)
    if not m:
        return html, False
    h2_pos = m.start()
    page_break_marker = '<div class="page-break"></div>'
    pb_pos = html.rfind(page_break_marker, 0, h2_pos)
    if pb_pos == -1:
        return html[:h2_pos] + button_html + "\n\n" + html[h2_pos:], True
    return html[:pb_pos] + button_html + "\n\n" + html[pb_pos:], True


def process_file(file_path: Path, lang: str) -> bool:
    if not file_path.exists():
        print(f"  ! Fichier introuvable : {file_path.name}")
        return False
    html = file_path.read_text(encoding="utf-8")
    original = html

    # 1. Injecter le CSS
    html = inject_css(html, lang)

    # 2. Ajouter les id aux titres
    html = add_ids_to_headings(html, lang)

    labels = get_labels(lang)

    # 3. Inserer le bouton avant chaque section 9..20
    for idx, (sid, num, *_) in enumerate(SEIFIM):
        target_label = get_seif_label(idx, lang)
        button = build_button(
            href=f"#seif-{sid}",
            label_text=labels["next"],
            target_label=target_label,
            lang=lang,
        )
        html, ok = insert_button_before_section(html, num, button)
        if not ok:
            print(f"  ! Section {num} introuvable dans {file_path.name}")

    # 4. Bouton avant la Synthèse (section 21) — apres Seif Yod-Gimel
    button_synth = build_button(
        href="#synthese",
        label_text=labels["next"],
        target_label=labels["to_synth_label"],
        lang=lang,
    )
    html, _ = insert_button_before_synthese(html, button_synth)

    if html == original:
        print(f"  = Aucune modification : {file_path.name}")
        return False
    file_path.write_text(html, encoding="utf-8")
    print(f"  ✓ Modifie : {file_path.name}")
    return True


def main():
    files = [
        (SIMAN_DIR / "niveau-1-base.html", "fr"),
        (SIMAN_DIR / "niveau-1-base-he.html", "he"),
        (SIMAN_DIR / "niveau-1-base-en.html", "en"),
    ]
    print("=== Ajout des boutons de navigation seif par seif (siman 242) ===\n")
    for path, lang in files:
        print(f"[{lang.upper()}] {path.relative_to(ROOT)}")
        process_file(path, lang)
    print("\nTermine.")


if __name__ == "__main__":
    main()
