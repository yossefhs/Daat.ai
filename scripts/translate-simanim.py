#!/usr/bin/env python3
"""Generate -he.html and -en.html variants for every siman HTML file.

Usage : python3 scripts/translate-simanim.py

Pour chaque fichier .html sous sources/shabbat/, ce script :
  1. Lit le fichier source (français).
  2. Applique un dictionnaire de traductions (chrome, labels, navigation).
  3. Met a jour les attributs lang/dir.
  4. Met a jour les liens internes vers les variantes traduites.
  5. Ajoute un selecteur de langue dans le header (si <header> present).
  6. Ecrit les fichiers <nom>-he.html et <nom>-en.html.

Les textes hebreux deja presents (versets, sources, citations) sont preserves
tels quels. Le contenu unique a chaque siman (textes de Seif, explications
specifiques) reste en francais avec un bandeau indiquant que la traduction
est en cours.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources" / "shabbat"

# =============================================================================
# DICTIONNAIRES DE TRADUCTION
# =============================================================================
# Liste de couples (regex, remplacement). L'ordre compte : les phrases longues
# doivent etre traduites avant les mots seuls. Tous les motifs sont sensibles
# a la casse pour eviter les conflits.

# Traductions communes (chrome, navigation, labels) — FR -> HE
FR_TO_HE = [
    # Header / nav
    (r"\bAccueil\b", "עמוד הבית"),
    (r"\bRetour à l'accueil\b", "חזרה לעמוד הבית"),
    (r"\bCommunauté\b", "קהילה"),
    (r"\bIA Daat\b", "דעת AI"),
    (r"\bSoutenir le projet\b", "תמיכה בפרויקט"),
    (r"\bSoutenir\b", "תמיכה"),
    (r"\bÉtudier\b", "ללמוד"),
    (r"\bÉtude\b", "לימוד"),
    (r"\bÉtudier ce niveau\b", "ללמוד את הרמה הזו"),
    (r"\bRejoindre la khavroutha\b", "להצטרף לחברותא"),
    (r"\bTrouver une khavroutha pour ce siman\b", "מציאת חברותא לסימן זה"),

    # Breadcrumb
    (r"\bOrah Haïm\b", "אורח חיים"),
    (r"\bHilkhot Shabbat\b", "הלכות שבת"),

    # Labels niveaux
    (r"\bLes 4 niveaux d'étude\b", "ארבע רמות הלימוד"),
    (r"\bLes 3 niveaux d'étude\b", "שלוש רמות הלימוד"),
    (r"\b3 niveaux disponibles\b", "3 רמות זמינות"),
    (r"\b4 niveaux disponibles\b", "4 רמות זמינות"),
    (r"\bNiveau 1\b", "רמה 1"),
    (r"\bNiveau 2\b", "רמה 2"),
    (r"\bNiveau 3\b", "רמה 3"),
    (r"\bNiveau 4\b", "רמה 4"),
    (r"\bBase — Débutant &amp; Intermédiaire\b", "בסיס — מתחיל וביניים"),
    (r"\bBase — Débutant & Intermédiaire\b", "בסיס — מתחיל וביניים"),
    (r"\bLamdan — Pilpoul Avancé\b", "למדן — פלפול מתקדם"),
    (r"\bSynthèse Magistrale\b", "סיכום מגיסטרלי"),
    (r"\bDaat HaRav — Chitah de l'Admour HaZaken\b", "דעת הרב — שיטת אדמו״ר הזקן"),
    (r"\bÉtude selon mes Poskim\b", "לימוד לפי הפוסקים שלי"),

    # Badges et status
    (r"\bDisponible\b", "זמין"),
    (r"\bPersonnalisé\b", "מותאם אישית"),
    (r"\bBientôt\b", "בקרוב"),
    (r"\bEn cours\b", "בעיצומו"),
    (r"\bFutur\b", "עתיד"),
    (r"\bContenu en préparation\b", "התוכן בהכנה"),
    (r"\bChargement\b", "טוען"),

    # Boutons et actions
    (r"\bConstruire mon siman\b", "בנה את הסימן שלי"),
    (r"\bPDF Base\b", "PDF בסיס"),
    (r"\bPDF Lamdan\b", "PDF למדן"),
    (r"\bPDF Synthèse\b", "PDF סיכום"),
    (r"\bVoir\b", "ראה"),
    (r"\bTélécharger\b", "הורד"),

    # FAQ et questions
    (r"\bQuestions fréquentes\b", "שאלות נפוצות"),
    (r"\bQuestion(s)? de compréhension\b", "שאלות הבנה"),

    # Sections communes
    (r"\bTexte du Seif\b", "מקור הסעיף"),
    (r"\bLe texte du Choul'han Aroukh\b", "מקור השולחן ערוך"),
    (r"\bLe texte du Choulhan Aroukh\b", "מקור השולחן ערוך"),
    (r"\bTraduction française\b", "תרגום"),
    (r"\bTexte original\b", "מקור"),
    (r"\bRécapitulatif\b", "סיכום"),
    (r"\bSynthèse pratique\b", "סיכום מעשי"),
    (r"\bRègles à retenir\b", "כללים לזכור"),

    # Mots et phrases courts
    (r"\bSemaine\b", "שבוע"),
    (r"\bAnnée\b", "שנה"),
    (r"\bSeif Alef\b", "סעיף א׳"),
    (r"\bSelon\b", "לפי"),
    (r"\bPour\b", "עבור"),
    (r"\bSource(s)?\b", "מקורות"),
    (r"\bSujet\b", "נושא"),
    (r"\bChapitre\b", "פרק"),

    # Footer
    (r"\bInitié par le Rav\b", "ביוזמת הרב"),
    (r"\bRav Yossef Haim Samama\b", "הרב יוסף חיים סממה"),
    (r"© 5786 / 2026", "תשפ״ו / 2026 ©"),

    # Phrases d'introduction (niveau-1 etc)
    (r"\bPour découvrir et comprendre\b", "להכרה והבנה"),
    (r"\bPour qui veut comprendre en profondeur\b", "למי שמבקש להעמיק"),
    (r"\bL'idée centrale en une phrase\b", "הרעיון המרכזי במשפט אחד"),
    (r"\bUne approche progressive\b", "גישה הדרגתית"),
]

# Traductions communes (chrome, navigation, labels) — FR -> EN
FR_TO_EN = [
    # Header / nav
    (r"\bAccueil\b", "Home"),
    (r"\bRetour à l'accueil\b", "Back to home"),
    (r"\bCommunauté\b", "Community"),
    (r"\bIA Daat\b", "Daat AI"),
    (r"\bSoutenir le projet\b", "Support the project"),
    (r"\bSoutenir\b", "Support"),
    (r"\bÉtudier\b", "Study"),
    (r"\bÉtude\b", "Study"),
    (r"\bÉtudier ce niveau\b", "Study this level"),
    (r"\bRejoindre la khavroutha\b", "Join the khavroutha"),
    (r"\bTrouver une khavroutha pour ce siman\b", "Find a khavroutha for this siman"),

    # Breadcrumb
    (r"\bOrah Haïm\b", "Orah Haim"),
    (r"\bHilkhot Shabbat\b", "Hilkhot Shabbat"),

    # Labels niveaux
    (r"\bLes 4 niveaux d'étude\b", "The 4 levels of study"),
    (r"\bLes 3 niveaux d'étude\b", "The 3 levels of study"),
    (r"\b3 niveaux disponibles\b", "3 levels available"),
    (r"\b4 niveaux disponibles\b", "4 levels available"),
    (r"\bNiveau 1\b", "Level 1"),
    (r"\bNiveau 2\b", "Level 2"),
    (r"\bNiveau 3\b", "Level 3"),
    (r"\bNiveau 4\b", "Level 4"),
    (r"\bBase — Débutant &amp; Intermédiaire\b", "Base — Beginner &amp; Intermediate"),
    (r"\bBase — Débutant & Intermédiaire\b", "Base — Beginner & Intermediate"),
    (r"\bLamdan — Pilpoul Avancé\b", "Lamdan — Advanced Pilpul"),
    (r"\bSynthèse Magistrale\b", "Master Synthesis"),
    (r"\bDaat HaRav — Chitah de l'Admour HaZaken\b", "Daat HaRav — Shitah of the Alter Rebbe"),
    (r"\bÉtude selon mes Poskim\b", "Study according to my Poskim"),

    # Badges et status
    (r"\bDisponible\b", "Available"),
    (r"\bPersonnalisé\b", "Personalized"),
    (r"\bBientôt\b", "Soon"),
    (r"\bEn cours\b", "In progress"),
    (r"\bFutur\b", "Future"),
    (r"\bContenu en préparation\b", "Content in preparation"),
    (r"\bChargement\b", "Loading"),

    # Boutons et actions
    (r"\bConstruire mon siman\b", "Build my siman"),
    (r"\bVoir\b", "View"),
    (r"\bTélécharger\b", "Download"),

    # FAQ et questions
    (r"\bQuestions fréquentes\b", "Frequently asked questions"),
    (r"\bQuestion(s)? de compréhension\b", "Comprehension questions"),

    # Sections communes
    (r"\bTexte du Seif\b", "Seif text"),
    (r"\bLe texte du Choul'han Aroukh\b", "The Shulchan Aroukh text"),
    (r"\bLe texte du Choulhan Aroukh\b", "The Shulchan Aroukh text"),
    (r"\bTraduction française\b", "Translation"),
    (r"\bTexte original\b", "Original text"),
    (r"\bRécapitulatif\b", "Summary"),
    (r"\bSynthèse pratique\b", "Practical synthesis"),
    (r"\bRègles à retenir\b", "Rules to remember"),

    # Mots courts
    (r"\bSemaine\b", "Week"),
    (r"\bAnnée\b", "Year"),
    (r"\bSeif Alef\b", "Seif Alef"),
    (r"\bSelon\b", "According to"),
    (r"\bSource(s)?\b", "Source(s)"),
    (r"\bSujet\b", "Subject"),
    (r"\bChapitre\b", "Chapter"),

    # Footer
    (r"\bInitié par le Rav\b", "Initiated by Rav"),
    (r"© 5786 / 2026", "© 5786 / 2026"),

    # Phrases d'introduction
    (r"\bPour découvrir et comprendre\b", "To discover and understand"),
    (r"\bPour qui veut comprendre en profondeur\b", "For those who want to understand in depth"),
    (r"\bL'idée centrale en une phrase\b", "The central idea in one sentence"),
    (r"\bUne approche progressive\b", "A progressive approach"),
]

# =============================================================================
# CSS et HTML supplementaires injectes
# =============================================================================

LANG_SWITCHER_CSS = """
    .lang-switcher { display: flex; gap: 6px; align-items: center; margin-left: 12px; }
    .lang-switcher a {
      font-family: 'Inter', sans-serif; font-size: 11px;
      padding: 3px 7px; border-radius: 2px; letter-spacing: 1px;
      color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.15);
      text-decoration: none; text-transform: none;
    }
    .lang-switcher a.active { color: var(--gold, #C5A55A); border-color: var(--gold, #C5A55A); }
    .lang-switcher a:hover { color: var(--gold, #C5A55A); border-color: var(--gold, #C5A55A); }
"""

# Banner indiquant que la traduction du contenu specifique est en cours.
# Inclut un selecteur FR / HE / EN pour les pages de niveau (sans <nav>).
WIP_BANNER_HE = """<div class="wip-banner" style="background:#FFF8E5;border:1px solid #C5A55A;border-left:4px solid #C5A55A;padding:10px 16px;margin:0 0 12px;font-family:'Frank Ruhl Libre',sans-serif;font-size:14px;color:#5a4a1a;direction:rtl;text-align:right;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
<span>ℹ️ עמוד זה מתורגם — מקורות עבריים נשמרו במלואם. הסבר ייחודי עשוי להישאר חלקית בצרפתית.</span>
<span style="font-family:'Inter',sans-serif;font-size:12px;letter-spacing:1px;"><a href="LANG_FR_LINK" style="color:#8C6F1E;padding:2px 8px;border:1px solid #C5A55A;text-decoration:none;">FR</a> <a href="#" style="color:#1A1F3A;padding:2px 8px;border:1px solid #1A1F3A;background:#FFF8E5;text-decoration:none;font-weight:600;">HE</a> <a href="LANG_EN_LINK" style="color:#8C6F1E;padding:2px 8px;border:1px solid #C5A55A;text-decoration:none;">EN</a></span>
</div>
"""

WIP_BANNER_EN = """<div class="wip-banner" style="background:#FFF8E5;border:1px solid #C5A55A;border-left:4px solid #C5A55A;padding:10px 16px;margin:0 0 12px;font-family:'Inter',sans-serif;font-size:14px;color:#5a4a1a;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
<span>ℹ️ This page is being translated — Hebrew sources are fully preserved. Specific commentary may remain partially in French.</span>
<span style="font-size:12px;letter-spacing:1px;"><a href="LANG_FR_LINK" style="color:#8C6F1E;padding:2px 8px;border:1px solid #C5A55A;text-decoration:none;">FR</a> <a href="LANG_HE_LINK" style="color:#8C6F1E;padding:2px 8px;border:1px solid #C5A55A;text-decoration:none;">HE</a> <a href="#" style="color:#1A1F3A;padding:2px 8px;border:1px solid #1A1F3A;background:#FFF8E5;text-decoration:none;font-weight:600;">EN</a></span>
</div>
"""

# =============================================================================
# TRAITEMENT DES FICHIERS
# =============================================================================

def get_hreflang_links(rel_path: str) -> str:
    """Genere les liens hreflang pour les 3 langues a partir du chemin relatif."""
    base = rel_path.replace("\\", "/")
    if base.endswith(".html"):
        stem = base[:-5]
    else:
        stem = base
    return (
        f'<link rel="alternate" hreflang="fr" href="https://daattorah.com/{base}">\n'
        f'<link rel="alternate" hreflang="en" href="https://daattorah.com/{stem}-en.html">\n'
        f'<link rel="alternate" hreflang="he" href="https://daattorah.com/{stem}-he.html">\n'
    )


def update_internal_links(html: str, lang_suffix: str) -> str:
    """Met a jour les liens internes vers les variantes traduites.

    lang_suffix est '-he' ou '-en'.
    """
    # 1. Liens vers les pages principales (relatifs ou absolus avec ../../../)
    # Pattern : href="(../../../)?(index|chat|communaute|soutenir|chitah-admour-hazaken)\.html"
    main_pages = [
        "index", "chat", "communaute", "soutenir", "chitah-admour-hazaken", "404",
    ]
    for page in main_pages:
        # Avec chemin relatif
        html = re.sub(
            rf'href="((?:\.\./)*)({page})\.html(?=[#?"])',
            rf'href="\1\2{lang_suffix}.html',
            html,
        )
        # Avec slash absolu
        html = re.sub(
            rf'href="/({page})\.html(?=[#?"])',
            rf'href="/\1{lang_suffix}.html',
            html,
        )

    # 2. Liens vers /sources/shabbat/index.html ou sources/shabbat/index.html ou sources/shabbat/
    html = re.sub(
        r'href="((?:\.\./)*)sources/shabbat/(?:index\.html)?(?=["#?])',
        rf'href="\1sources/shabbat/index{lang_suffix}.html',
        html,
    )
    html = re.sub(
        r'href="/sources/shabbat/(?:index\.html)?(?=["#?])',
        rf'href="/sources/shabbat/index{lang_suffix}.html',
        html,
    )

    # 3. Liens vers siman-XXX/ ou siman-XXX/index.html (depuis sources/shabbat/index.html)
    html = re.sub(
        r'href="(siman-\d+)/(?:index\.html)?(?=["#?])',
        rf'href="\1/index{lang_suffix}.html',
        html,
    )
    # Avec chemins relatifs ../../sources/shabbat/siman-XXX/...
    html = re.sub(
        r'href="((?:\.\./)+sources/shabbat/siman-\d+)/(?:index\.html)?(?=["#?])',
        rf'href="\1/index{lang_suffix}.html',
        html,
    )
    html = re.sub(
        r'href="(/sources/shabbat/siman-\d+)/(?:index\.html)?(?=["#?])',
        rf'href="\1/index{lang_suffix}.html',
        html,
    )

    # 4. Liens vers niveau-X-*.html (depuis l'index d'un siman vers ses niveaux)
    # Restreint aux noms valides pour eviter le double suffixe (-he-he).
    niveau_pattern = r'(niveau-\d-(?:base|lamdan|synthese|daat-harav))'
    html = re.sub(
        rf'href="(?:\./)?{niveau_pattern}\.html(?=[#?"])',
        rf'href="\1{lang_suffix}.html',
        html,
    )

    # 5. Liens vers /oh/ (alias de sources/shabbat)
    html = re.sub(
        r'href="/oh/(?=["#?])',
        rf'href="/oh/index{lang_suffix}.html',
        html,
    )

    return html


def apply_translations(html: str, dictionary: list) -> str:
    """Applique le dictionnaire FR -> lang sur le HTML.

    Le HTML est traite tel quel (chaine globale). Les regex sont sensibles a
    la casse et utilisent des word boundaries pour eviter les faux positifs.
    Les motifs sont tries par longueur decroissante pour que les phrases
    longues soient traduites avant les mots qu'elles contiennent.
    """
    sorted_dict = sorted(dictionary, key=lambda kv: -len(kv[0]))
    for pattern, replacement in sorted_dict:
        html = re.sub(pattern, replacement, html)
    return html


def add_lang_switcher_css(html: str) -> str:
    """Injecte le CSS du selecteur de langue avant </style>."""
    if "</style>" in html and ".lang-switcher" not in html:
        # Inserer avant le PREMIER </style>
        html = html.replace("</style>", LANG_SWITCHER_CSS + "\n</style>", 1)
    return html


def add_lang_switcher_nav(html: str, current_lang: str, base_name: str) -> str:
    """Ajoute le selecteur de langue HTML dans le <nav> du header.

    base_name est le nom de fichier sans suffixe ni extension : 'index', 'chat', etc.
    current_lang est 'fr', 'he' ou 'en'.
    """
    # Construire les URLs FR, HE, EN
    url_fr = f"{base_name}.html"
    url_he = f"{base_name}-he.html"
    url_en = f"{base_name}-en.html"

    cls_fr = ' class="active"' if current_lang == "fr" else ""
    cls_he = ' class="active"' if current_lang == "he" else ""
    cls_en = ' class="active"' if current_lang == "en" else ""

    switcher = (
        f'<span class="lang-switcher">'
        f'<a href="{url_fr}"{cls_fr}>FR</a>'
        f'<a href="{url_he}"{cls_he}>HE</a>'
        f'<a href="{url_en}"{cls_en}>EN</a>'
        f'</span>'
    )

    # Inserer juste avant la fin du <nav>...</nav>
    # On cible le premier </nav> rencontre apres le premier <nav
    nav_match = re.search(r'(<nav[^>]*>)(.*?)(</nav>)', html, re.DOTALL)
    if nav_match and "lang-switcher" not in nav_match.group(2):
        new_nav = nav_match.group(1) + nav_match.group(2) + switcher + nav_match.group(3)
        html = html[:nav_match.start()] + new_nav + html[nav_match.end():]

    return html


def update_html_attributes(html: str, lang: str) -> str:
    """Met a jour l'attribut lang= et dir= de la balise <html>."""
    if lang == "he":
        html = re.sub(r'<html[^>]*>', '<html lang="he" dir="rtl">', html, count=1)
        # og:locale
        html = re.sub(
            r'<meta property="og:locale" content="[^"]*">',
            '<meta property="og:locale" content="he_IL">',
            html,
        )
        # JSON-LD inLanguage
        html = re.sub(
            r'"inLanguage"\s*:\s*"[^"]*"',
            '"inLanguage": "he-IL"',
            html,
        )
    elif lang == "en":
        html = re.sub(r'<html[^>]*>', '<html lang="en">', html, count=1)
        html = re.sub(
            r'<meta property="og:locale" content="[^"]*">',
            '<meta property="og:locale" content="en_US">',
            html,
        )
        html = re.sub(
            r'"inLanguage"\s*:\s*"[^"]*"',
            '"inLanguage": "en-US"',
            html,
        )
    return html


def add_hreflang_links(html: str, rel_path: str) -> str:
    """Ajoute les balises <link rel="alternate" hreflang=...> dans le <head>."""
    if 'hreflang=' in html:
        return html
    links = get_hreflang_links(rel_path)
    # Inserer apres la balise <link rel="canonical"> si presente, sinon
    # apres le premier <link rel="icon">
    if '<link rel="canonical"' in html:
        html = re.sub(
            r'(<link rel="canonical"[^>]*>)',
            rf'\1\n  {links.strip()}',
            html,
            count=1,
        )
    else:
        html = re.sub(
            r'(<link rel="icon"[^>]*>)',
            rf'\1\n  {links.strip()}',
            html,
            count=1,
        )
    return html


def add_wip_banner_if_relevant(html: str, lang: str, rel_path: str) -> str:
    """Ajoute le bandeau WIP au debut du <main> ou <body>, pour les pages
    de niveau (niveau-1, niveau-2, niveau-3, niveau-4) ou le contenu specifique
    reste majoritairement en francais.
    """
    fname = Path(rel_path).name
    if not fname.startswith("niveau-"):
        return html

    # Lien vers la version FR
    fr_link = fname.replace("-he.html", ".html").replace("-en.html", ".html")
    banner = (WIP_BANNER_HE if lang == "he" else WIP_BANNER_EN).replace(
        "LANG_FR_LINK", fr_link
    )

    # Inserer juste apres <body>
    html = re.sub(r'(<body[^>]*>)', rf'\1\n{banner}', html, count=1)
    return html


def force_body_font_he(html: str) -> str:
    """Pour la version HE, ajoute Frank Ruhl Libre en premier sur body."""
    return re.sub(
        r'(\bbody\s*\{[^}]*font-family:\s*)([^;]+)',
        r"\1'Frank Ruhl Libre', \2",
        html,
        count=1,
    )


def process_file(src: Path, rel_path: str):
    """Traite un fichier source et genere les variantes -he et -en."""
    try:
        original = src.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"  SKIP (encoding) : {rel_path}")
        return

    fname = src.name
    if fname.endswith("-he.html") or fname.endswith("-en.html"):
        return  # deja une variante traduite

    # Determiner le nom de base
    if fname == "index.html":
        base_name = "index"
    else:
        base_name = fname.replace(".html", "")

    rel_dir = Path(rel_path).parent.as_posix()
    if rel_dir == ".":
        rel_dir = ""

    # --- Variante HE ---
    he = original
    he = update_html_attributes(he, "he")
    he = add_hreflang_links(he, rel_path)
    he = apply_translations(he, FR_TO_HE)
    he = add_lang_switcher_css(he)
    # IMPORTANT : update_internal_links AVANT add_lang_switcher_nav,
    # sinon le lien FR du switcher est reecrit en -he par erreur.
    he = update_internal_links(he, "-he")
    he = add_lang_switcher_nav(he, "he", base_name)
    he = force_body_font_he(he)
    he = add_wip_banner_if_relevant(he, "he", rel_path)

    he_path = src.parent / f"{base_name}-he.html"
    he_path.write_text(he, encoding="utf-8")

    # --- Variante EN ---
    en = original
    en = update_html_attributes(en, "en")
    en = add_hreflang_links(en, rel_path)
    en = apply_translations(en, FR_TO_EN)
    en = add_lang_switcher_css(en)
    en = update_internal_links(en, "-en")
    en = add_lang_switcher_nav(en, "en", base_name)
    en = add_wip_banner_if_relevant(en, "en", rel_path)

    en_path = src.parent / f"{base_name}-en.html"
    en_path.write_text(en, encoding="utf-8")


def main():
    if not SOURCES_DIR.exists():
        print(f"ERROR : {SOURCES_DIR} introuvable", file=sys.stderr)
        sys.exit(1)

    count = 0
    skipped = 0
    for src in sorted(SOURCES_DIR.rglob("*.html")):
        fname = src.name
        # Eviter les variantes deja traduites
        if fname.endswith("-he.html") or fname.endswith("-en.html"):
            skipped += 1
            continue

        rel_path = src.relative_to(ROOT).as_posix()
        process_file(src, rel_path)
        count += 1
        if count % 50 == 0:
            print(f"  {count} fichiers traites…")

    print(f"\nTermine : {count} fichiers source traduits (HE + EN), {skipped} variantes ignorees")


if __name__ == "__main__":
    main()
