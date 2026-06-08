#!/usr/bin/env python3
"""
DAAT — Corrections d'accessibilité (a11y) sur les pages racines.

Applique les fixes suivants page par page :
  1. Skip-link "Aller au contenu principal" (FR/EN/HE) après <body>.
  2. id="main" sur l'élément <main> / <div class="main"> / <div class="content">.
  3. CSS .skip-link injecté en fin de <style> existant.
  4. aria-label + hreflang sur les <a class="lang-switcher a"> FR/EN/HE.
  5. Substitution rgba(255,255,255,0.7) → 0.9 dans la nav.
  6. <link rel="alternate" hreflang="x-default" …> si absent.

NB : exclut /admin/, /mockup/, /api/, /sources/shabbat/siman-*/, 404*.html, poc-corpus.html.
"""

import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Pages cibles (racine + sources/shabbat/index*).
TARGET_FILES = [
    "index.html", "index-en.html", "index-he.html",
    "about.html", "about-en.html", "about-he.html",
    "chat.html", "chat-en.html", "chat-he.html",
    "faq.html", "faq-en.html", "faq-he.html",
    "communaute.html", "communaute-en.html", "communaute-he.html",
    "soutenir.html", "soutenir-en.html", "soutenir-he.html",
    "chitah-admour-hazaken.html",
    "chitah-admour-hazaken-en.html",
    "chitah-admour-hazaken-he.html",
    "sources/shabbat/index.html",
    "sources/shabbat/index-en.html",
    "sources/shabbat/index-he.html",
]

SKIP_LABEL = {
    "fr": "Aller au contenu principal",
    "en": "Skip to main content",
    "he": "דלג לתוכן הראשי",
}

SKIP_CSS = (
    "    .skip-link { position: absolute; top: -40px; left: 0; "
    "background: var(--navy); color: var(--gold); padding: 8px 16px; "
    "z-index: 9999; text-decoration: none; font-family: 'Inter', sans-serif; "
    "font-size: 13px; }\n"
    "    .skip-link:focus { top: 0; }\n"
)

ARIA_LANG = {"FR": "Français", "EN": "English", "HE": "עברית"}
HREFLANG_FOR = {"FR": "fr", "EN": "en", "HE": "he"}


def detect_lang(filename):
    """Retourne 'fr', 'en' ou 'he' selon le suffixe du nom de fichier."""
    base = os.path.basename(filename)
    if base.endswith("-en.html"):
        return "en"
    if base.endswith("-he.html"):
        return "he"
    return "fr"


def add_skip_link(html, lang):
    """Insère <a href="#main" class="skip-link">…</a> juste après <body>."""
    if 'class="skip-link"' in html:
        return html, False
    label = SKIP_LABEL[lang]
    skip_html = f'\n  <a href="#main" class="skip-link">{label}</a>\n'
    # Insère juste après la première balise <body...>
    new_html, n = re.subn(
        r"(<body[^>]*>)",
        lambda m: m.group(1) + skip_html,
        html,
        count=1,
    )
    return new_html, n > 0


def ensure_main_id(html):
    """Ajoute id="main" sur le premier conteneur principal trouvé."""
    if 'id="main"' in html:
        return html, False
    # Essai 1 : <main …> sans id
    m = re.search(r"<main\b([^>]*)>", html)
    if m:
        attrs = m.group(1)
        if "id=" not in attrs:
            new_open = f'<main id="main"{attrs}>'
            html = html[: m.start()] + new_open + html[m.end():]
            return html, True
        # main a un id différent (rare) : ne touche pas
    # Essai 2 : <div class="main…"> (ex: chat.html .main-area, etc.)
    m = re.search(r'<div\s+class="(main(?:-[a-z]+)?)"', html)
    if m:
        start = m.start()
        end = m.end()
        new_open = f'<div id="main" class="{m.group(1)}"'
        html = html[:start] + new_open + html[end:]
        return html, True
    # Essai 3 : <div class="content"> (ex: sources/shabbat/index.html)
    m = re.search(r'<div\s+class="content"', html)
    if m:
        start = m.start()
        end = m.end()
        new_open = '<div id="main" class="content"'
        html = html[:start] + new_open + html[end:]
        return html, True
    return html, False


def inject_skip_css(html):
    """Ajoute la CSS .skip-link en tête du premier <style> (si pas déjà là)."""
    if ".skip-link" in html and "position: absolute; top: -40px" in html:
        return html, False
    # Inject juste après la première balise <style…>
    m = re.search(r"(<style[^>]*>)", html)
    if not m:
        return html, False
    insertion = m.group(1) + "\n" + SKIP_CSS
    html = html[: m.start()] + insertion + html[m.end():]
    return html, True


EMOJI_PATTERN = re.compile(
    r'<a(?P<attrs>[^>]*?)>(?P<text>\s*(?:💬|♥|📚|❤)[^<]*?)</a>'
)


def fix_emoji_links(html):
    """Ajoute aria-label sur les liens contenant 💬, ♥, 📚 (header/footer).

    Le texte visible contient déjà l'emoji + un libellé textuel ; on extrait
    le libellé textuel (sans l'emoji) comme aria-label. Idempotent : ne
    touche pas les liens déjà annotés aria-label.
    """
    count = [0]

    def upgrade(am):
        attrs = am.group("attrs")
        text = am.group("text")
        if "aria-label" in attrs:
            return am.group(0)
        label = re.sub(r'[💬♥📚❤]', '', text).strip()
        label = re.sub(r'\s+', ' ', label)
        if not label:
            return am.group(0)
        label = label.replace('"', '&quot;')
        count[0] += 1
        return f'<a{attrs} aria-label="{label}">{text}</a>'

    new_html = EMOJI_PATTERN.sub(upgrade, html)
    return new_html, count[0]


def fix_lang_switcher(html):
    """Ajoute aria-label et hreflang sur les liens FR/EN/HE du lang-switcher."""
    changed = 0
    # Pattern : <a href="..." [class="..."]>FR|EN|HE</a> à l'intérieur ou
    # juste après <span class="lang-switcher">. On opère après ce span.
    # Approche simple : trouver chaque <span class="lang-switcher"> et
    # traiter son contenu balisé jusqu'au </span> correspondant.
    def process_span(match):
        nonlocal changed
        inner = match.group(2)
        # Pour chaque <a … >FR|EN|HE</a> à l'intérieur, on enrichit.
        def upgrade_anchor(am):
            txt = am.group("txt").strip()
            if txt not in ARIA_LANG:
                return am.group(0)
            attrs = am.group("attrs")
            # déjà fait ?
            if "aria-label=" in attrs and "hreflang=" in attrs:
                return am.group(0)
            new_attrs = attrs
            if "hreflang=" not in new_attrs:
                new_attrs += f' hreflang="{HREFLANG_FOR[txt]}"'
            if "aria-label=" not in new_attrs:
                new_attrs += f' aria-label="{ARIA_LANG[txt]}"'
            nonlocal changed
            changed += 1
            return f"<a{new_attrs}>{am.group('txt')}</a>"

        new_inner = re.sub(
            r'<a(?P<attrs>[^>]*?)>(?P<txt>\s*(?:FR|EN|HE)\s*)</a>',
            upgrade_anchor,
            inner,
        )
        return f'<span{match.group(1)}>{new_inner}</span>'

    # Note: lang-switcher peut être imbriqué dans plusieurs niveaux.
    # On utilise une regex non-greedy. Les .lang-switcher rencontrés en
    # pratique ne contiennent que des <a> simples, pas d'autres <span>.
    html = re.sub(
        r'<span(\s[^>]*class="[^"]*\blang-switcher\b[^"]*"[^>]*)>(.*?)</span>',
        process_span,
        html,
        flags=re.S,
    )
    return html, changed > 0


def fix_contrast(html):
    """Remplace rgba(255,255,255,0.7) → 0.9 dans la CSS inline.

    Cible uniquement les déclarations avec 0.7 — on laisse 0.85/0.5/etc.
    intactes. Substitution globale dans le bloc <style>.
    """
    style_match = re.search(r"(<style[^>]*>)(.*?)(</style>)", html, re.S)
    if not style_match:
        return html, 0
    open_tag, body, close_tag = style_match.groups()
    new_body, n = re.subn(
        r'rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.7\s*\)',
        'rgba(255,255,255,0.9)',
        body,
    )
    if n == 0:
        return html, 0
    html = (
        html[: style_match.start()]
        + open_tag + new_body + close_tag
        + html[style_match.end():]
    )
    return html, n


def add_xdefault_hreflang(html, file_rel):
    """Ajoute <link rel="alternate" hreflang="x-default" …> si absent."""
    if 'hreflang="x-default"' in html:
        return html, False
    # On cherche la version FR pour servir de cible x-default.
    # Pattern : <link rel="alternate" hreflang="fr" href="…">
    m = re.search(
        r'<link\s+rel="alternate"\s+hreflang="fr"\s+href="([^"]+)"\s*/?>',
        html,
    )
    if not m:
        return html, False
    fr_url = m.group(1)
    insertion = (
        f'\n  <link rel="alternate" hreflang="x-default" href="{fr_url}">'
    )
    # Insère juste après le bloc hreflang he ou en (le dernier des deux).
    last_alt = None
    for am in re.finditer(
        r'<link\s+rel="alternate"\s+hreflang="(?:en|he)"[^>]*>', html
    ):
        last_alt = am
    if last_alt is None:
        # fallback : juste après hreflang fr
        last_alt = m
    html = (
        html[: last_alt.end()]
        + insertion
        + html[last_alt.end():]
    )
    return html, True


def process(path):
    rel = os.path.relpath(path, ROOT)
    with open(path, encoding="utf-8") as f:
        html = f.read()
    original = html
    lang = detect_lang(path)
    report = {}

    html, did_main = ensure_main_id(html)
    report["main_id"] = did_main

    html, did_skip = add_skip_link(html, lang)
    report["skip_link"] = did_skip

    html, did_css = inject_skip_css(html)
    report["skip_css"] = did_css

    html, did_ls = fix_lang_switcher(html)
    report["lang_switcher"] = did_ls

    html, emoji_n = fix_emoji_links(html)
    report["emoji_count"] = emoji_n

    html, contrast_n = fix_contrast(html)
    report["contrast_count"] = contrast_n

    html, did_xdef = add_xdefault_hreflang(html, rel)
    report["xdefault"] = did_xdef

    if html != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        report["modified"] = True
    else:
        report["modified"] = False
    return rel, report


def main():
    summary = {
        "modified": 0,
        "skip_link": 0,
        "main_id": 0,
        "skip_css": 0,
        "lang_switcher": 0,
        "contrast": 0,
        "xdefault": 0,
    }
    rows = []
    for rel in TARGET_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            print(f"  [skip] absent : {rel}")
            continue
        relname, r = process(path)
        rows.append((relname, r))
        if r["modified"]:
            summary["modified"] += 1
        summary["skip_link"] += int(r["skip_link"])
        summary["main_id"] += int(r["main_id"])
        summary["skip_css"] += int(r["skip_css"])
        summary["lang_switcher"] += int(r["lang_switcher"])
        summary["emoji_links"] = summary.get("emoji_links", 0) + r["emoji_count"]
        summary["contrast"] += 1 if r["contrast_count"] else 0
        summary["xdefault"] += int(r["xdefault"])

    print()
    print("Détail :")
    for rel, r in rows:
        flags = []
        if r["skip_link"]:
            flags.append("skip-link")
        if r["main_id"]:
            flags.append("id=main")
        if r["skip_css"]:
            flags.append("css")
        if r["lang_switcher"]:
            flags.append("lang-aria")
        if r["emoji_count"]:
            flags.append(f"emoji×{r['emoji_count']}")
        if r["contrast_count"]:
            flags.append(f"contrast×{r['contrast_count']}")
        if r["xdefault"]:
            flags.append("x-default")
        if flags:
            print(f"  ✓ {rel}  →  {', '.join(flags)}")
        else:
            print(f"  · {rel}  →  (déjà conforme)")

    print()
    print("Résumé :")
    for k, v in summary.items():
        print(f"  {k:>15} : {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
