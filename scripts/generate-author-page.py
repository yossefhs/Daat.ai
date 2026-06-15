#!/usr/bin/env python3
"""generate-author-page.py — page auteur E-E-A-T trilingue pour le Rav Y. H. Samama.

Crée /auteur/rav-yossef-haim-samama{,-he,-en}.html avec schema Person.
Levier E-E-A-T n°1 (site YMYL). N'utilise QUE des informations fournies par
l'auteur — aucun profil externe inventé (pas de sameAs fabriqué).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "auteur"
BASE = "https://daattorah.com"
SLUG = "rav-yossef-haim-samama"

PERSON = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Rav Yossef Haim Samama",
    "alternateName": "הרב יוסף חיים סממה",
    "jobTitle": "Rabbin, auteur halakhique",
    "url": f"{BASE}/auteur/{SLUG}.html",
    "sameAs": ["https://www.wikidata.org/wiki/Q140226680"],
    "description": "Rabbin issu des yechivot et collelim Habad, titulaire de la semikha de Tomhei Tmimim, fondateur de DaatTorah — plateforme d'étude de la halakha.",
    "alumniOf": {"@type": "EducationalOrganization", "name": "Tomhei Tmimim (Habad)"},
    "hasCredential": {
        "@type": "EducationalOccupationalCredential",
        "credentialCategory": "Semikha (ordination rabbinique)",
        "recognizedBy": {"@type": "EducationalOrganization", "name": "Tomhei Tmimim"},
    },
    "knowsAbout": ["Halakha", "Choulhan Aroukh", "Hilkhot Shabbat",
                   "Choulhan Aroukh HaRav", "Hassidout Habad"],
    "worksFor": {
        "@type": "Organization",
        "name": "DAAT — דעת",
        "url": BASE,
        "sameAs": [
            "https://www.wikidata.org/wiki/Q140170943",
            "https://www.linkedin.com/company/daattorah",
        ],
    },
}

L = {
    "fr": {
        "lang": "fr", "dir": "ltr", "file": f"{SLUG}.html",
        "title": "Rav Yossef Haim Samama — auteur de Daat Torah",
        "desc": "Biographie du Rav Yossef Haim Samama : parcours dans les yechivot Habad, semikha de Tomhei Tmimim, et la vision de DaatTorah.",
        "nav": {"shabbat": "Hilkhot Shabbat", "chat": "💬 IA Daat", "comm": "Communauté",
                "about": "À propos", "soutenir": "♥ Soutenir", "home": "Accueil"},
        "crumb": "L'auteur",
        "hero_meta": "דעת תורה · L'auteur",
        "h1": "Rav Yossef Haim Samama",
        "subtitle": "Fondateur de DaatTorah — au service d'une étude de la Torah claire, vivante et fidèle aux sources.",
        "body": [
            "Le Rav Yossef Haim Samama est issu des yechivot et collelim Habad, où il a étudié durant de longues années avec assiduité la Torah, la Halakha et la ’Hassidout.",
            "Titulaire de la semikha de Tomhei Tmimim, et ayant eu le mérite d’être élève du Rav Abichid, il s’inscrit dans une démarche de limoud fondée sur la profondeur, la fidélité aux sources et la volonté de transmettre avec clarté.",
            "À travers DaatTorah, il met cette expérience au service d’une vision : ouvrir un accès plus clair, plus vivant et plus structuré à l’étude de la Torah, en s’appuyant à la fois sur la tradition du limoud et sur les outils technologiques actuels.",
            "Le projet a pour vocation d’accompagner chacun dans son étude, ses recherches et ses interrogations, avec sérieux, authenticité et exigence.",
        ],
        "creds_title": "Formation & parcours",
        "creds": ["Yechivot et collelim Habad — Torah, Halakha et ’Hassidout",
                  "Semikha (ordination) de Tomhei Tmimim",
                  "Élève du Rav Abichid",
                  "Fondateur et auteur de DaatTorah"],
        "back": "Découvrir l’étude par siman",
    },
    "en": {
        "lang": "en", "dir": "ltr", "file": f"{SLUG}-en.html",
        "title": "Rav Yossef Haim Samama — author of Daat Torah",
        "desc": "Biography of Rav Yossef Haim Samama: training in the Chabad yeshivot, semikha of Tomchei Temimim, and the vision behind DaatTorah.",
        "nav": {"shabbat": "Hilkhot Shabbat", "chat": "💬 Daat AI", "comm": "Community",
                "about": "About", "soutenir": "♥ Support", "home": "Home"},
        "crumb": "The author",
        "hero_meta": "דעת תורה · The author",
        "h1": "Rav Yossef Haim Samama",
        "subtitle": "Founder of DaatTorah — serving a study of Torah that is clear, vivid and faithful to the sources.",
        "body": [
            "Rav Yossef Haim Samama comes from the Chabad yeshivot and kollelim, where he studied Torah, Halakha and Chassidut diligently for many years.",
            "Holder of the semikha of Tomchei Temimim, and having had the merit of being a student of Rav Abichid, his approach to limoud is founded on depth, fidelity to the sources, and the will to transmit with clarity.",
            "Through DaatTorah, he places this experience at the service of a vision: to open a clearer, more vivid and more structured access to the study of Torah, drawing both on the tradition of limoud and on today’s technological tools.",
            "The project aims to accompany each person in their study, their research and their questions — with seriousness, authenticity and rigor.",
        ],
        "creds_title": "Training & background",
        "creds": ["Chabad yeshivot and kollelim — Torah, Halakha and Chassidut",
                  "Semikha (ordination) from Tomchei Temimim",
                  "Student of Rav Abichid",
                  "Founder and author of DaatTorah"],
        "back": "Explore the study siman by siman",
    },
    "he": {
        "lang": "he", "dir": "rtl", "file": f"{SLUG}-he.html",
        "title": "הרב יוסף חיים סממה — מחבר דעת תורה",
        "desc": "תולדות הרב יוסף חיים סממה: לימוד בישיבות חב״ד, סמיכה מתומכי תמימים, והחזון שמאחורי דעת תורה.",
        "nav": {"shabbat": "הלכות שבת", "chat": "💬 דעת AI", "comm": "קהילה",
                "about": "אודות", "soutenir": "♥ תמיכה", "home": "דף הבית"},
        "crumb": "המחבר",
        "hero_meta": "דעת תורה · המחבר",
        "h1": "הרב יוסף חיים סממה",
        "subtitle": "מייסד דעת תורה — למען לימוד תורה בהיר, חי ונאמן למקורות.",
        "body": [
            "הרב יוסף חיים סממה גדל בישיבות ובכוללי חב״ד, שם למד במשך שנים רבות ובהתמדה תורה, הלכה וחסידות.",
            "בעל סמיכה מתומכי תמימים, ואשר זכה להיות תלמידו של הרב אבישיד, הוא הולך בדרך לימוד המושתתת על עומק, נאמנות למקורות ורצון להעביר את הדברים בבהירות.",
            "באמצעות דעת תורה, הוא מעמיד ניסיון זה בשירות חזון: לפתוח גישה בהירה, חיה ומסודרת יותר ללימוד התורה, תוך הישענות הן על מסורת הלימוד והן על הכלים הטכנולוגיים של ימינו.",
            "מטרת המיזם היא ללוות כל אדם בלימודו, בחקירותיו ובשאלותיו — ברצינות, באותנטיות ובדקדקנות.",
        ],
        "creds_title": "לימודים ורקע",
        "creds": ["ישיבות וכוללי חב״ד — תורה, הלכה וחסידות",
                  "סמיכה מתומכי תמימים",
                  "תלמידו של הרב אבישיד",
                  "מייסד ומחבר דעת תורה"],
        "back": "ללימוד סימן אחר סימן",
    },
}

FONTS = ("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400"
         "&family=Frank+Ruhl+Libre:wght@300;400;500;700;900&family=Inter:wght@300;400;500;600&display=swap")


def page(t: dict) -> str:
    alts = "".join(
        f'\n  <link rel="alternate" hreflang="{o["lang"]}" href="{BASE}/auteur/{o["file"]}">'
        for o in L.values()
    )
    alts += f'\n  <link rel="alternate" hreflang="x-default" href="{BASE}/auteur/{L["fr"]["file"]}">'
    body_html = "\n".join(f"      <p>{p}</p>" for p in t["body"])
    creds_html = "\n".join(f"        <li>{c}</li>" for c in t["creds"])
    person = json.dumps(PERSON, ensure_ascii=False, indent=2).replace("\n", "\n  ")
    he_hero = '<div class="hero-title-he" aria-hidden="true">דעת תורה</div>' if t["lang"] != "he" else ""
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}"{' dir="rtl"' if t['dir']=='rtl' else ''}>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <title>{t['title']}</title>
  <meta name="description" content="{t['desc']}">
  <meta name="author" content="Rav Yossef Haim Samama">
  <link rel="canonical" href="{BASE}/auteur/{t['file']}">{alts}
  <meta property="og:type" content="profile">
  <meta property="og:title" content="{t['title']}">
  <meta property="og:description" content="{t['desc']}">
  <meta property="og:url" content="{BASE}/auteur/{t['file']}">
  <meta property="og:image" content="{BASE}/assets/img/og/og-default.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style" href="{FONTS}" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="{FONTS}"></noscript>
  <link rel="stylesheet" href="/assets/css/daat.css">
  <link rel="stylesheet" href="/assets/css/daat-enhance.css">
  <script type="application/ld+json">
  {person}
  </script>
  <!-- PWA / app installable -->
  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#1A1F3A">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Daat Torah">
  <script src="/assets/js/pwa.js" defer></script>
</head>
<body>
  <header>
    <a href="/{'index-he.html' if t['lang']=='he' else 'index-en.html' if t['lang']=='en' else ''}" class="logo">
      <span class="logo-he">דעת</span>
      <span class="logo-en">Daat Torah</span>
    </a>
    <nav>
      <a href="/oh/{'he' if t['lang']=='he' else 'en' if t['lang']=='en' else ''}">{t['nav']['shabbat']}</a>
      <a href="/chat{'-he' if t['lang']=='he' else '-en' if t['lang']=='en' else ''}.html">{t['nav']['chat']}</a>
      <a href="/about{'-he' if t['lang']=='he' else '-en' if t['lang']=='en' else ''}.html">{t['nav']['about']}</a>
      <a href="/soutenir{'-he' if t['lang']=='he' else '-en' if t['lang']=='en' else ''}.html" class="cta-soutenir">{t['nav']['soutenir']}</a>
    <span class="lang-switcher"><a href="/auteur/{SLUG}.html" hreflang="fr">FR</a><a href="/auteur/{SLUG}-he.html" hreflang="he">HE</a><a href="/auteur/{SLUG}-en.html" hreflang="en">EN</a></span></nav>
  </header>

  <div class="page-hero">
    <div class="hero-inner">
      <div class="hero-meta">{t['hero_meta']}</div>
      {he_hero}
      <h1 class="hero-title-fr">{t['h1']}</h1>
      <p class="hero-subtitle">{t['subtitle']}</p>
    </div>
  </div>

  <main id="main" class="content">
    <article>
{body_html}
      <h2>{t['creds_title']}</h2>
      <ul>
{creds_html}
      </ul>
      <p style="margin-top:2rem"><a class="cta-soutenir" href="/oh/{'he' if t['lang']=='he' else 'en' if t['lang']=='en' else ''}">{t['back']} →</a></p>
    </article>
  </main>

  <footer>
    <p>
      DAAT דעת — © 5786 / 2026 ·
      <a href="/{'index-he.html' if t['lang']=='he' else 'index-en.html' if t['lang']=='en' else ''}">{t['nav']['home']}</a> ·
      <a href="/about{'-he' if t['lang']=='he' else '-en' if t['lang']=='en' else ''}.html">{t['nav']['about']}</a> ·
      <a href="/chat{'-he' if t['lang']=='he' else '-en' if t['lang']=='en' else ''}.html">{t['nav']['chat']}</a>
    </p>
  </footer>
</body>
</html>
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for t in L.values():
        (OUT / t["file"]).write_text(page(t), encoding="utf-8")
        print("✓", "auteur/" + t["file"])


if __name__ == "__main__":
    main()
