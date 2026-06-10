#!/usr/bin/env python3
"""
add-internal-linking.py — Enrichit le maillage interne du site DAAT.

Sur chaque page index de siman (FR/HE/EN) :
  1. Insère un bloc <aside class="related-blog"> si un article de blog traite
     du siman (mapping ci-dessous).
  2. Insère un <nav class="siman-neighbors"> avec le siman précédent et/ou
     suivant (selon position dans 242–365).

Sur chaque article de blog (FR/HE/EN) :
  3. Insère un bloc « Voir aussi sur ce sujet » qui pointe vers le siman
     principal + 2–3 simanim voisins thématiques.

Et ajoute, dans /assets/css/blog.css, les styles correspondants si absents.

Idempotent : ne réinsère pas un bloc déjà présent (détecté par la classe).

Usage :
    python3 scripts/add-internal-linking.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources" / "shabbat"
BLOG = ROOT / "blog"
CATALOG = ROOT / "data" / "limoud-simanim-catalog.json"
BLOG_CSS = ROOT / "assets" / "css" / "blog.css"

# ─────────────────────────────────────────────────────────────────────────────
# Mapping siman → article de blog (slug, hors -he / -en)
# Mapping inverse : pour un siman, retrouver TOUS les articles qui le traitent
# ─────────────────────────────────────────────────────────────────────────────

SIMAN_TO_BLOG: dict[int, list[str]] = {
    242: ["honorer-shabbat-kavod-oneg"],
    243: ["louer-bien-non-juif-shabbat"],
    244: ["travaux-non-juif-pour-juif-shabbat"],
    245: ["association-juif-non-juif-shabbat"],
    246: ["pret-location-non-juif-shabbat"],
    247: ["livraison-colis-shabbat"],
    261: ["bougies-shabbat-horaire-allumage"],
    308: ["muktse-telephone-argent-shabbat"],
    312: ["papier-toilette-shabbat"],
    318: ["rechauffer-plat-shabbat"],
    319: ["trier-aliments-borer-shabbat"],
    326: ["se-doucher-laver-shabbat"],
    327: ["cremes-cosmetiques-shabbat"],
}

# Mapping article (slug) → siman principal traité
BLOG_TO_SIMAN: dict[str, int] = {
    arts[0]: siman for siman, arts in SIMAN_TO_BLOG.items()
}

# Groupes thématiques de simanim voisins (utilisés pour le bloc « voir aussi »
# des articles blog : on prend le siman principal + 2-3 simanim voisins du même
# groupe).
THEMATIC_GROUPS: list[list[int]] = [
    # Travaux par un non-juif (Shabbat) — simanim 243 à 247
    [243, 244, 245, 246, 247],
    # Bougies + horaires d'entrée de Shabbat
    [261, 263],
    # Muktsé (objets interdits au déplacement)
    [308, 309, 310, 311],
    # Mélakhot pratiques (réchauffer, trier, se laver, cosmétiques, papier WC…)
    [312, 318, 319, 326, 327],
]


def thematic_neighbors(siman: int, max_count: int = 3) -> list[int]:
    """Renvoie jusqu'à `max_count` simanim voisins thématiques (hors siman lui-même)."""
    for grp in THEMATIC_GROUPS:
        if siman in grp:
            return [s for s in grp if s != siman][:max_count]
    return []


# ─────────────────────────────────────────────────────────────────────────────
# Catalogue siman → titre (court) FR/HE/EN
# ─────────────────────────────────────────────────────────────────────────────

_HE_HUNDREDS = {1: "ק", 2: "ר", 3: "ש", 4: "ת"}
_HE_TENS = {
    1: "י", 2: "כ", 3: "ל", 4: "מ", 5: "נ", 6: "ס", 7: "ע", 8: "פ", 9: "צ"
}
_HE_UNITS = {1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט"}


def to_gematria(n: int) -> str:
    """Convertit un nombre 100-499 en gematria avec geresh/gershayim
    (ex. 247 → רמ״ז, 300 → ש׳)."""
    if not (100 <= n <= 499):
        return str(n)
    h = n // 100
    rem = n - h * 100
    # 15 et 16 : conventions טו / טז (au lieu de יה / יו)
    if rem == 15:
        tens_units = "טו"
    elif rem == 16:
        tens_units = "טז"
    else:
        t = rem // 10
        u = rem - t * 10
        tens_units = (_HE_TENS.get(t, "") + _HE_UNITS.get(u, ""))
    letters = _HE_HUNDREDS[h] + tens_units
    # Gershayim si ≥ 2 lettres, sinon geresh
    if len(letters) >= 2:
        return letters[:-1] + "״" + letters[-1]
    return letters + "׳"


def load_catalog() -> dict[int, dict[str, str]]:
    raw = json.loads(CATALOG.read_text(encoding="utf-8"))
    out: dict[int, dict[str, str]] = {}
    for s in raw["simanim"]:
        num_he = s.get("numHe") or ""
        # Si le catalogue donne un nombre arabe ou rien, on calcule la gematria
        if not num_he or num_he.isdigit():
            num_he = to_gematria(s["num"])
        out[s["num"]] = {
            "fr": s.get("title", f"Siman {s['num']}"),
            "he": s.get("titleHe", f"סימן {num_he}"),
            "en": s.get("titleEn", f"Siman {s['num']}"),
            "numHe": num_he,
        }
    return out


def short_title(title: str, max_len: int = 60) -> str:
    """Tronque proprement un titre trop long pour le bloc de navigation."""
    if len(title) <= max_len:
        return title
    cut = title[: max_len - 1].rsplit(" ", 1)[0]
    return cut + "…"


# ─────────────────────────────────────────────────────────────────────────────
# Titres FR/HE/EN des articles blog (pour libellés des liens)
# ─────────────────────────────────────────────────────────────────────────────

BLOG_TITLES: dict[str, dict[str, str]] = {
    "honorer-shabbat-kavod-oneg": {
        "fr": "Honorer le Shabbat — Kavod et Oneg",
        "he": "כבוד ועונג שבת",
        "en": "Honoring Shabbat — Kavod & Oneg",
    },
    "louer-bien-non-juif-shabbat": {
        "fr": "Louer un bien à un non-juif pour Shabbat",
        "he": "השכרת נכס לגוי בשבת",
        "en": "Renting property to a non-Jew for Shabbat",
    },
    "travaux-non-juif-pour-juif-shabbat": {
        "fr": "Quels travaux le non-juif peut faire pour un Juif Shabbat",
        "he": "אילו מלאכות הגוי יכול לעשות עבור היהודי",
        "en": "Which labors a non-Jew may do for a Jew on Shabbat",
    },
    "association-juif-non-juif-shabbat": {
        "fr": "Association entre Juif et non-juif (שותפות)",
        "he": "שותפות בין יהודי וגוי בשבת",
        "en": "Partnership between Jew and non-Jew on Shabbat",
    },
    "pret-location-non-juif-shabbat": {
        "fr": "Prêt et location à un non-juif pour Shabbat",
        "he": "השאלה והשכרה לגוי בשבת",
        "en": "Lending and renting to a non-Jew on Shabbat",
    },
    "livraison-colis-shabbat": {
        "fr": "Peut-on se faire livrer un colis pendant Shabbat ?",
        "he": "האם מותר לקבל משלוח חבילה בשבת ?",
        "en": "Can you have a package delivered on Shabbat?",
    },
    "bougies-shabbat-horaire-allumage": {
        "fr": "Bougies de Shabbat — horaire d'allumage",
        "he": "נרות שבת — זמן הדלקה",
        "en": "Shabbat candles — lighting time",
    },
    "muktse-telephone-argent-shabbat": {
        "fr": "Muktsé — téléphone, argent et objets interdits",
        "he": "מוקצה — טלפון, כסף וחפצים אסורים",
        "en": "Muktzeh — phones, money and forbidden items",
    },
    "papier-toilette-shabbat": {
        "fr": "Papier toilette pendant Shabbat",
        "he": "נייר טואלט בשבת",
        "en": "Toilet paper on Shabbat",
    },
    "rechauffer-plat-shabbat": {
        "fr": "Réchauffer un plat pendant Shabbat",
        "he": "חימום מאכל בשבת",
        "en": "Reheating food on Shabbat",
    },
    "trier-aliments-borer-shabbat": {
        "fr": "Trier des aliments — בורר pendant Shabbat",
        "he": "בורר — מיון מאכלים בשבת",
        "en": "Sorting food — borer on Shabbat",
    },
    "se-doucher-laver-shabbat": {
        "fr": "Se doucher et se laver pendant Shabbat",
        "he": "רחיצה בשבת",
        "en": "Showering and bathing on Shabbat",
    },
    "cremes-cosmetiques-shabbat": {
        "fr": "Crèmes et cosmétiques pendant Shabbat",
        "he": "קרמים וקוסמטיקה בשבת",
        "en": "Creams and cosmetics on Shabbat",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Libellés des sections (i18n)
# ─────────────────────────────────────────────────────────────────────────────

LABELS: dict[str, dict[str, str]] = {
    "related_blog_heading": {
        "fr": "Articles pratiques sur ce siman",
        "he": "מאמרים מעשיים על סימן זה",
        "en": "Practical articles on this siman",
    },
    "see_also_heading": {
        "fr": "Voir aussi sur ce sujet",
        "he": "ראו גם בנושא זה",
        "en": "See also on this topic",
    },
    "study_siman_label": {
        "fr": "Étudier le siman",
        "he": "ללמוד את הסימן",
        "en": "Study the siman",
    },
    "prev_arrow": {"fr": "←", "he": "→", "en": "←"},
    "next_arrow": {"fr": "→", "he": "←", "en": "→"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Liens — calcul des URLs FR/HE/EN
# ─────────────────────────────────────────────────────────────────────────────

def siman_url(num: int, lang: str) -> str:
    if lang == "fr":
        return f"/oh/{num}/"
    return f"/oh/{num}/{lang}"


def blog_url(slug: str, lang: str) -> str:
    if lang == "fr":
        return f"/blog/{slug}.html"
    return f"/blog/{slug}-{lang}.html"


# ─────────────────────────────────────────────────────────────────────────────
# Construction des blocs HTML
# ─────────────────────────────────────────────────────────────────────────────

def build_related_blog_block(siman: int, lang: str) -> str | None:
    slugs = SIMAN_TO_BLOG.get(siman)
    if not slugs:
        return None
    heading = LABELS["related_blog_heading"][lang]
    items = []
    for slug in slugs:
        title = BLOG_TITLES[slug][lang]
        url = blog_url(slug, lang)
        items.append(f'      <li><a href="{url}">{title}</a></li>')
    items_html = "\n".join(items)
    return (
        "\n"
        '    <aside class="related-blog">\n'
        f"      <h3>{heading}</h3>\n"
        "      <ul>\n"
        f"{items_html}\n"
        "      </ul>\n"
        "    </aside>\n"
    )


def build_siman_neighbors_block(
    siman: int, catalog: dict[int, dict[str, str]], lang: str
) -> str | None:
    # Voisins immédiats existants dans la plage 242-365
    prev_num = siman - 1 if siman > 242 else None
    next_num = siman + 1 if siman < 365 else None

    # Skip si aucun voisin
    if prev_num is None and next_num is None:
        return None

    prev_arrow = LABELS["prev_arrow"][lang]
    next_arrow = LABELS["next_arrow"][lang]
    parts = []

    if prev_num and prev_num in catalog:
        title = short_title(catalog[prev_num][lang])
        url = siman_url(prev_num, lang)
        if lang == "he":
            label = f'סימן {catalog[prev_num]["numHe"]} — {title}'
            parts.append(f'      <a href="{url}" class="prev">{label} {prev_arrow}</a>')
        else:
            parts.append(
                f'      <a href="{url}" class="prev">{prev_arrow} Siman {prev_num} — {title}</a>'
            )
    else:
        parts.append("      <span></span>")

    if next_num and next_num in catalog:
        title = short_title(catalog[next_num][lang])
        url = siman_url(next_num, lang)
        if lang == "he":
            label = f'סימן {catalog[next_num]["numHe"]} — {title}'
            parts.append(f'      <a href="{url}" class="next">{next_arrow} {label}</a>')
        else:
            parts.append(
                f'      <a href="{url}" class="next">Siman {next_num} — {title} {next_arrow}</a>'
            )
    else:
        parts.append("      <span></span>")

    inner = "\n".join(parts)
    return f'\n    <nav class="siman-neighbors" aria-label="Navigation entre simanim">\n{inner}\n    </nav>\n'


def build_blog_see_also_block(
    slug: str, lang: str, catalog: dict[int, dict[str, str]]
) -> str | None:
    main_siman = BLOG_TO_SIMAN.get(slug)
    if main_siman is None:
        return None

    heading = LABELS["see_also_heading"][lang]
    items = []

    # 1. Lien vers le siman principal
    main_title = short_title(catalog[main_siman][lang], max_len=70)
    main_url = siman_url(main_siman, lang)
    if lang == "he":
        items.append(
            f'      <li><a href="{main_url}"><strong>סימן {catalog[main_siman]["numHe"]}</strong> — {main_title}</a></li>'
        )
    else:
        items.append(
            f'      <li><a href="{main_url}"><strong>Siman {main_siman}</strong> — {main_title}</a></li>'
        )

    # 2. Liens vers 2-3 simanim voisins thématiques
    for neighbor in thematic_neighbors(main_siman, max_count=3):
        if neighbor not in catalog:
            continue
        n_title = short_title(catalog[neighbor][lang], max_len=70)
        n_url = siman_url(neighbor, lang)
        if lang == "he":
            items.append(
                f'      <li><a href="{n_url}">סימן {catalog[neighbor]["numHe"]} — {n_title}</a></li>'
            )
        else:
            items.append(
                f'      <li><a href="{n_url}">Siman {neighbor} — {n_title}</a></li>'
            )

    items_html = "\n".join(items)
    return (
        "\n"
        '    <aside class="related-blog see-also">\n'
        f"      <h3>{heading}</h3>\n"
        "      <ul>\n"
        f"{items_html}\n"
        "      </ul>\n"
        "    </aside>\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Détecte la langue d'un fichier siman index à partir de son nom
# ─────────────────────────────────────────────────────────────────────────────

def detect_siman_lang(name: str) -> str | None:
    if name == "index.html":
        return "fr"
    if name == "index-he.html":
        return "he"
    if name == "index-en.html":
        return "en"
    return None


def detect_blog_lang(name: str) -> str | None:
    if name.endswith("-he.html"):
        return "he"
    if name.endswith("-en.html"):
        return "en"
    if name.endswith(".html"):
        return "fr"
    return None


def blog_slug(name: str) -> str:
    if name.endswith("-he.html"):
        return name[: -len("-he.html")]
    if name.endswith("-en.html"):
        return name[: -len("-en.html")]
    return name[: -len(".html")]


# ─────────────────────────────────────────────────────────────────────────────
# Insertion idempotente dans une page siman
# ─────────────────────────────────────────────────────────────────────────────

# Marqueur de fin de zone d'insertion sur les pages siman index : juste avant </main>.
# Sur les simanim « legacy » (242-246) la structure n'utilise pas <main> ; on
# retombe alors sur le </div> qui ferme <div class="content"> (juste avant
# <footer>).
SIMAN_INSERT_BEFORE_MAIN = re.compile(r"\n?(\s*</main>)", re.IGNORECASE)
SIMAN_INSERT_BEFORE_FOOTER = re.compile(
    r"\n?(\s*</div>\s*\n\s*<footer\b)", re.IGNORECASE
)


def _insert_before_main_or_footer(html: str, block: str) -> tuple[str, int]:
    new_html, n = SIMAN_INSERT_BEFORE_MAIN.subn(block + r"\1", html, count=1)
    if n:
        return new_html, n
    return SIMAN_INSERT_BEFORE_FOOTER.subn(block + r"\1", html, count=1)


# Patterns pour retirer d'anciens blocs déjà insérés (idempotence + upgrade)
RELATED_BLOCK_RE = re.compile(
    r"\s*<aside class=\"related-blog(?:\s+see-also)?\">.*?</aside>",
    re.DOTALL,
)
NEIGHBORS_BLOCK_RE = re.compile(
    r"\s*<nav class=\"siman-neighbors\".*?</nav>",
    re.DOTALL,
)


def patch_siman_index(path: Path, catalog: dict[int, dict[str, str]]) -> tuple[bool, int]:
    lang = detect_siman_lang(path.name)
    if lang is None:
        return False, 0

    m = re.search(r"siman-(\d+)", str(path.parent.name))
    if not m:
        return False, 0
    siman = int(m.group(1))

    html = path.read_text(encoding="utf-8")
    orig = html
    links_added = 0

    # 1) Articles de blog liés — calcule le bloc cible
    target_related = build_related_blog_block(siman, lang) or ""
    # 2) Voisins — calcule le bloc cible
    target_neighbors = build_siman_neighbors_block(siman, catalog, lang) or ""

    # Extrait les blocs existants
    existing_related_m = RELATED_BLOCK_RE.search(html)
    existing_neighbors_m = NEIGHBORS_BLOCK_RE.search(html)
    existing_related = existing_related_m.group() if existing_related_m else ""
    existing_neighbors = existing_neighbors_m.group() if existing_neighbors_m else ""

    # Compare en ignorant l'indentation/espaces de fin de bloc
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.strip())

    related_ok = norm(existing_related) == norm(target_related.strip())
    neighbors_ok = norm(existing_neighbors) == norm(target_neighbors.strip())

    if related_ok and neighbors_ok:
        return False, 0

    # Sinon : retire les blocs existants et ré-insère les corrects
    if existing_related_m:
        html = html[: existing_related_m.start()] + html[existing_related_m.end():]
    # Recompute neighbors match after potential removal of related
    if existing_neighbors_m:
        new_m = NEIGHBORS_BLOCK_RE.search(html)
        if new_m:
            html = html[: new_m.start()] + html[new_m.end():]

    # Réinsère neighbors d'abord, puis related (ordre logique)
    if target_neighbors:
        new_html, n = _insert_before_main_or_footer(html, target_neighbors)
        if n:
            html = new_html
            links_added += target_neighbors.count("<a ")
    if target_related:
        new_html, n = _insert_before_main_or_footer(html, target_related)
        if n:
            html = new_html
            links_added += target_related.count("<li>")

    if html != orig:
        path.write_text(html, encoding="utf-8")
        return True, links_added
    return False, 0


# ─────────────────────────────────────────────────────────────────────────────
# Insertion idempotente dans un article de blog
# Insère le bloc « voir aussi » juste avant la <section class="newsletter-box">
# (et, à défaut, juste avant </main>).
# ─────────────────────────────────────────────────────────────────────────────

BLOG_INSERT_BEFORE_NEWSLETTER = re.compile(
    r"\n?(\s*<section class=\"newsletter-box\">)", re.IGNORECASE
)
BLOG_INSERT_BEFORE_MAIN_CLOSE = re.compile(r"\n?(\s*</main>)", re.IGNORECASE)


def patch_blog_article(path: Path, catalog: dict[int, dict[str, str]]) -> tuple[bool, int]:
    lang = detect_blog_lang(path.name)
    if lang is None:
        return False, 0
    slug = blog_slug(path.name)
    if slug not in BLOG_TO_SIMAN:
        return False, 0

    html = path.read_text(encoding="utf-8")
    orig = html

    target = build_blog_see_also_block(slug, lang, catalog)
    if not target:
        return False, 0

    # Cherche un bloc « see-also » déjà inséré
    existing_m = RELATED_BLOCK_RE.search(html)

    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.strip())

    if existing_m and norm(existing_m.group()) == norm(target.strip()):
        return False, 0

    if existing_m:
        html = html[: existing_m.start()] + html[existing_m.end():]

    new_html, n = BLOG_INSERT_BEFORE_NEWSLETTER.subn(target + r"\1", html, count=1)
    if not n:
        new_html, n = BLOG_INSERT_BEFORE_MAIN_CLOSE.subn(target + r"\1", html, count=1)
    if not n:
        return False, 0

    if new_html != orig:
        path.write_text(new_html, encoding="utf-8")
        return True, target.count("<a ")
    return False, 0


# ─────────────────────────────────────────────────────────────────────────────
# CSS — ajoute les styles à blog.css si absents
# ─────────────────────────────────────────────────────────────────────────────

CSS_BLOCK = """
/* Maillage interne — bloc « articles de blog liés » + navigation entre simanim
   (ajouté par scripts/add-internal-linking.py — idempotent) */
.related-blog {
  margin: 32px 0;
  padding: 18px 22px;
  background: linear-gradient(to right, #FAF6EE, #FFFFFF);
  border-left: 4px solid #C5A55A;
  border-radius: 4px;
}
.related-blog h3 { color: #1A1F3A; margin: 0 0 10px; font-size: 1.1em; }
.related-blog ul { list-style: none; padding: 0; margin: 0; }
.related-blog li { padding: 4px 0; }
.related-blog a { color: #1A1F3A; text-decoration: underline dotted #C5A55A; }
.related-blog a:hover { color: #C5A55A; }
.siman-neighbors { display: flex; justify-content: space-between; gap: 18px; margin: 28px 0; padding: 14px 0; border-top: 1px solid #C5A55A; }
.siman-neighbors a { color: #1A1F3A; text-decoration: none; font-size: 0.95em; }
.siman-neighbors a:hover { color: #C5A55A; }
.siman-neighbors .prev { text-align: left; }
.siman-neighbors .next { text-align: right; }
[dir="rtl"] .related-blog { border-left: none; border-right: 4px solid #C5A55A; }
[dir="rtl"] .siman-neighbors .prev { text-align: right; }
[dir="rtl"] .siman-neighbors .next { text-align: left; }
"""


def ensure_css() -> bool:
    txt = BLOG_CSS.read_text(encoding="utf-8")
    if ".related-blog" in txt and ".siman-neighbors" in txt:
        return False
    if not txt.endswith("\n"):
        txt += "\n"
    txt += CSS_BLOCK
    BLOG_CSS.write_text(txt, encoding="utf-8")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    catalog = load_catalog()

    siman_changed = 0
    siman_total = 0
    siman_skipped = 0
    siman_links = 0

    siman_dirs = sorted(SOURCES.glob("siman-*"))
    for d in siman_dirs:
        for name in ("index.html", "index-he.html", "index-en.html"):
            p = d / name
            if not p.exists():
                continue
            siman_total += 1
            changed, n_links = patch_siman_index(p, catalog)
            if changed:
                siman_changed += 1
                siman_links += n_links
            else:
                siman_skipped += 1

    blog_changed = 0
    blog_total = 0
    blog_links = 0
    for p in sorted(BLOG.glob("*.html")):
        if p.name.startswith("index"):
            continue
        blog_total += 1
        changed, n_links = patch_blog_article(p, catalog)
        if changed:
            blog_changed += 1
            blog_links += n_links

    css_added = ensure_css()

    print("=== add-internal-linking — résumé ===")
    print(f"Pages siman parcourues : {siman_total}")
    print(f"  → enrichies          : {siman_changed}")
    print(f"  → déjà à jour        : {siman_skipped}")
    print(f"  liens ajoutés (siman): {siman_links}")
    print(f"Pages blog parcourues  : {blog_total}")
    print(f"  → enrichies          : {blog_changed}")
    print(f"  liens ajoutés (blog) : {blog_links}")
    print(f"CSS blog.css           : {'mis à jour' if css_added else 'déjà à jour'}")
    print(f"Total liens internes   : {siman_links + blog_links}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
