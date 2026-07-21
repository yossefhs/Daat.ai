#!/usr/bin/env python3
"""Génère les variantes -he.html et -en.html des pages niveau-2-lamdan du Yoreh De'ah.

Le corps de ces pages est du pilpoul déjà rédigé à 99 % en HÉBREU (16 caractères
latins sur 13 000 dans le siman 89). Il n'y a donc RIEN à traduire dans le corps :
seules les métadonnées (title, description, og/twitter, canonical, JSON-LD) et le
sélecteur de langue sont en français.

Ce script ne touche QUE le <head> et le sélecteur de langue. Le corps — textes du
Choulhan Aroukh, citations du Shach et du Taz, sougyot — est copié à l'octet près.
Les titres de siman traduits sont LUS depuis data/simanim-disponibles-{he,en}.json
(traductions déjà validées) : le script n'en invente aucune.

Usage : python3 scripts/generate-yd-niveau2-variants.py [--dry-run]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "yoreh-deah"
DRY = "--dry-run" in sys.argv

def load_titles(suffix=""):
    p = ROOT / "data" / f"simanim-disponibles{suffix}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    def walk(o):
        if isinstance(o, dict):
            if o.get("num") and o.get("section") == "yoreh-deah":
                out[int(o["num"])] = o
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(data)
    return out

T_FR, T_HE, T_EN = load_titles(), load_titles("-he"), load_titles("-en")

def sub1(s, pattern, repl, label, path):
    """Remplace une occurrence unique ; signale si l'ancre est absente/ambiguë."""
    new, n = re.subn(pattern, repl, s, count=1)
    if n != 1:
        warnings.append(f"{path.name}: ancre « {label} » introuvable")
    return new

LANG_SWITCHER = (
    '<div class="lang-switcher-float" role="navigation" aria-label="Langue / Language">\n'
    '    <a href="/yd/{n}/lamdan" hreflang="fr"{a_fr}>FR</a>\n'
    '    <a href="/yd/{n}/lamdan/he" hreflang="he"{a_he}>HE</a>\n'
    '    <a href="/yd/{n}/lamdan/en" hreflang="en"{a_en}>EN</a>\n'
    '  </div>'
)

def build(src_html, num, lang):
    he = lang == "he"
    numHe = (T_FR.get(num) or {}).get("numHe", "")
    title = (T_HE if he else T_EN).get(num, {}).get("title") or (T_FR.get(num) or {}).get("title", "")
    s = src_html

    if he:
        new_title = f"סימן {numHe} · רמה 2 (למדן) — {title} | יורה דעה"
        desc = f"רמה 2 (למדן) של סימן {numHe} ביורה דעה — {title}. פלפול ועיון מעמיק : מקורות הש״ס, שיטות הראשונים, חקירות, מחלוקות ונפקא מינות."
        og_t = f"סימן {numHe} · רמה 2 למדן — {title}"
        og_d = f"פלפול ועיון מעמיק בסימן {numHe} ביורה דעה."
        author, locale, inlang = "הרב יוסף חיים סממה", "he_IL", "he-IL"
    else:
        new_title = f"Siman {numHe} · Level 2 (Lamdan) — {title} | Yoreh De'ah"
        desc = f"Level 2 (Lamdan) of Siman {numHe} in Yoreh De'ah — {title}. In-depth pilpul: Talmudic sources, shitos of the Rishonim, chakiros, machlokos and nafka minos."
        og_t = f"Siman {numHe} · Level 2 Lamdan — {title}"
        og_d = f"In-depth pilpul on Siman {numHe} of Yoreh De'ah."
        author, locale, inlang = "Rav Yossef Haim Samama", "en_US", "en-US"

    esc = lambda t: t.replace('"', "&quot;")
    p = Path(f"siman-{num}")
    s = sub1(s, r"<title>[\s\S]*?</title>", lambda m: f"<title>{new_title}</title>", "title", p)
    s = sub1(s, r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{esc(desc)}">', "description", p)
    s = sub1(s, r'<meta name="author" content="[^"]*">', lambda m: f'<meta name="author" content="{author}">', "author", p)
    s = sub1(s, r'<link rel="canonical" href="[^"]*">', lambda m: f'<link rel="canonical" href="https://daattorah.com/yd/{num}/lamdan/{lang}">', "canonical", p)
    s = sub1(s, r'<meta property="og:title" content="[^"]*">', lambda m: f'<meta property="og:title" content="{esc(og_t)}">', "og:title", p)
    s = sub1(s, r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{esc(og_d)}">', "og:description", p)
    s = sub1(s, r'<meta property="og:url" content="[^"]*">', lambda m: f'<meta property="og:url" content="https://daattorah.com/yd/{num}/lamdan/{lang}">', "og:url", p)
    s = sub1(s, r'<meta property="og:locale" content="[^"]*">', lambda m: f'<meta property="og:locale" content="{locale}">', "og:locale", p)
    s = sub1(s, r'<meta name="twitter:title" content="[^"]*">', lambda m: f'<meta name="twitter:title" content="{esc(og_t)}">', "twitter:title", p)
    s = sub1(s, r'<meta name="twitter:description" content="[^"]*">', lambda m: f'<meta name="twitter:description" content="{esc(og_d)}">', "twitter:description", p)

    # JSON-LD
    s = s.replace(f'"@id": "https://daattorah.com/yd/{num}/lamdan#article"', f'"@id": "https://daattorah.com/yd/{num}/lamdan/{lang}#article"')
    s = s.replace(f'"url": "https://daattorah.com/yd/{num}/lamdan"', f'"url": "https://daattorah.com/yd/{num}/lamdan/{lang}"')
    s = re.sub(r'"headline": "[^"]*"', f'"headline": "{esc(new_title)}"', s, count=1)
    s = re.sub(r'"inLanguage": "[^"]*"', f'"inLanguage": "{inlang}"', s, count=1)

    # Balise <html> : la langue de l'INTERFACE change, la direction reste RTL
    # (le corps est du pilpoul hébreu dans les trois variantes).
    s = re.sub(r'<html lang="[^"]*"', f'<html lang="{lang}"', s, count=1)

    # Sélecteur de langue : ajouté s'il est absent (les niveaux 2 YD n'en ont pas).
    act = {"fr": "", "he": "", "en": ""}
    act[lang] = ' class="active"'
    sw = LANG_SWITCHER.format(n=num, a_fr=act["fr"], a_he=act["he"], a_en=act["en"])
    if 'class="lang-switcher-float"' in s:
        s = re.sub(r'<div class="lang-switcher-float"[\s\S]*?</div>', lambda m: sw, s, count=1)
    else:
        s = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + "\n  " + sw, s, count=1)
    return s

warnings = []
written = 0
simanim = sorted(int(d.name.split("-")[1]) for d in SRC.glob("siman-*") if (d / "niveau-2-lamdan.html").exists())
for num in simanim:
    src = (SRC / f"siman-{num}" / "niveau-2-lamdan.html").read_text(encoding="utf-8")
    for lang in ("he", "en"):
        out = SRC / f"siman-{num}" / f"niveau-2-lamdan-{lang}.html"
        html = build(src, num, lang)
        if not DRY:
            out.write_text(html, encoding="utf-8")
        written += 1

print(f"{'[dry-run] ' if DRY else ''}{written} fichiers générés pour {len(simanim)} simanim")
if warnings:
    print(f"\n⚠️  {len(warnings)} avertissements :")
    for w in warnings[:20]: print("   ", w)
else:
    print("Aucune ancre manquante.")
