#!/usr/bin/env python3
"""
Fix meta descriptions pour SEO Bing/Google : 25-160 caractères.
- Trop longues  → tronqué à ≤155 chars sur frontière de mot + …
- Trop courtes  → régénéré depuis <title> + niveau detecté + sujet
- Absentes      → ajouté depuis <title>

Mode dry-run par défaut. Passer --write pour appliquer.

Usage:
  python3 scripts/fix-meta-descriptions.py             # dry-run
  python3 scripts/fix-meta-descriptions.py --write     # applique
"""
import re, os, sys, html
from pathlib import Path

DRY_RUN = '--write' not in sys.argv
EXCLUDE_DIRS = {'.claude', 'node_modules', '.git', 'transcriptions', 'admin'}
MAX_LEN = 155   # marge sous le 160 de Bing
MIN_LEN = 50    # objectif descriptif (au-dessus du minimum 25)

META_DESC_RE = re.compile(r'(<meta\s+name=["\']description["\']\s+content=)(["\'])(.*?)(\2)([^>]*>)', re.I | re.S)
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.I | re.S)
H1_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.I | re.S)

def detect_lang(path):
    if '-he.html' in path: return 'he'
    if '-en.html' in path: return 'en'
    return 'fr'

def clean_text(s):
    """Décode entités HTML, supprime tags résiduels, compacte espaces."""
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def truncate_at_word(s, max_len):
    """Tronque à max_len en respectant la frontière de mot, ajoute …"""
    if len(s) <= max_len: return s
    cut = s[:max_len - 1].rstrip()
    # remonter à la dernière espace pour ne pas couper un mot
    sp = cut.rfind(' ')
    if sp > max_len * 0.6:  # garde au moins 60% du target
        cut = cut[:sp].rstrip()
    # nettoyer ponctuation finale
    cut = cut.rstrip('.,;:—–-')
    return cut + '…'

def generate_from_title(title, lang, path):
    """Génère une description à partir du title + sujet de la page."""
    t = clean_text(title)
    # Templates par section pour étoffer
    if '/sources/shabbat/siman-' in path:
        m = re.search(r'siman-(\d+)', path)
        n = m.group(1) if m else '?'
        if 'niveau-1' in path:
            return {
                'fr': f"Étude du Choulhan Aroukh Orah Haïm siman {n} — Niveau 1 (Base) : texte hébreu, traduction française, explication pédagogique. Plateforme DAAT.",
                'en': f"Study of Shulchan Aruch Orach Chayim siman {n} — Level 1 (Base): Hebrew text, English translation, pedagogical explanation. DAAT platform.",
                'he': f"לימוד שולחן ערוך אורח חיים סימן {n} — רמה 1 (יסוד): טקסט עברי מקורי, ביאור פדגוגי ומקורות מהראשונים והאחרונים. אתר דעת תורה.",
            }[lang]
        if 'niveau-2' in path:
            return {
                'fr': f"Étude approfondie Lamdan du siman {n} (Orah Haïm) : pilpoul des Rishonim et Acharonim, hakira et machloket. DAAT Torah, niveau 2.",
                'en': f"Lamdan in-depth study of siman {n} (Orach Chayim): pilpul of Rishonim and Acharonim, hakira and machloket. DAAT Torah, level 2.",
                'he': f"לימוד למדני מעמיק של סימן {n} (אורח חיים): פלפול הראשונים והאחרונים, חקירה ומחלוקת. דעת תורה, רמה 2.",
            }[lang]
        if 'niveau-3' in path:
            return {
                'fr': f"Synthèse structurée du siman {n} (Orah Haïm) : récapitulatif clair des positions, du pesak et des règles pratiques. DAAT Torah, niveau 3.",
                'en': f"Structured synthesis of siman {n} (Orach Chayim): clear summary of positions, pesak and practical rules. DAAT Torah, level 3.",
                'he': f"סיכום מובנה של סימן {n} (אורח חיים): ריכוז ברור של השיטות, הפסק והכללים המעשיים. דעת תורה, רמה 3.",
            }[lang]
        if 'niveau-4' in path:
            return {
                'fr': f"Daat HaRav siman {n} (Orah Haïm) : la chitah de l'Admour HaZaken — Choulhan Aroukh HaRav et Kountress Aharon. DAAT Torah, niveau 4.",
                'en': f"Daat HaRav siman {n} (Orach Chayim): the chitah of the Admour HaZaken — Shulchan Aruch HaRav and Kontress Aharon. DAAT Torah, level 4.",
                'he': f"דעת הרב סימן {n} (אורח חיים): שיטת אדמו\"ר הזקן — שולחן ערוך הרב וקונטרס אחרון. דעת תורה, רמה 4.",
            }[lang]
    if '/sources/yoreh-deah/siman-' in path:
        m = re.search(r'siman-(\d+)', path)
        n = m.group(1) if m else '?'
        return {
            'fr': f"Étude du Choulhan Aroukh Yoreh Deah siman {n} : sources, machloket des poskim et halakha pratique. DAAT Torah, plateforme d'étude trilingue.",
            'en': f"Study of Shulchan Aruch Yoreh Deah siman {n}: sources, machloket of the poskim and practical halacha. DAAT Torah trilingual study platform.",
            'he': f"לימוד שולחן ערוך יורה דעה סימן {n}: מקורות, מחלוקת הפוסקים והלכה למעשה. דעת תורה, אתר לימוד תלת-לשוני.",
        }[lang]
    if '/limoud/' in path:
        m = re.search(r'jour-(\d+)', path)
        d = m.group(1) if m else '?'
        return {
            'fr': f"Limoud du jour {d} sur DAAT Torah : étude halakhique programmée, une page par jour pour avancer dans le Choulhan Aroukh à ton rythme.",
            'en': f"Daily Limoud day {d} on DAAT Torah: programmed halachic study, one page per day to progress through Shulchan Aruch at your own pace.",
            'he': f"לימוד יום {d} בדעת תורה: לימוד הלכתי מתוכנן, עמוד אחד ביום להתקדם בשולחן ערוך בקצב שלך.",
        }[lang]
    # Fallback : title + suffixe DAAT
    suffix = {'fr': ' — DAAT Torah, plateforme d\'étude halakhique en français.',
              'en': ' — DAAT Torah, halachic study platform in English.',
              'he': ' — דעת תורה, אתר לימוד הלכה בעברית.'}[lang]
    return truncate_at_word(t + suffix, MAX_LEN)

# Stats
fixed_long, fixed_short, fixed_missing, errors = 0, 0, 0, 0
samples = {'long': [], 'short': [], 'missing': []}

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for f in files:
        if not f.endswith('.html'): continue
        p = os.path.join(root, f)
        rel = p.lstrip('./')
        try:
            content = Path(p).read_text(encoding='utf-8')
        except Exception as e:
            errors += 1; continue
        lang = detect_lang(rel)
        title_m = TITLE_RE.search(content)
        title = clean_text(title_m.group(1)) if title_m else ''
        meta_m = META_DESC_RE.search(content)

        new_desc = None
        kind = None

        if not meta_m:
            # Absente : ajouter
            new_desc = generate_from_title(title, lang, rel)
            kind = 'missing'
        else:
            current = html.unescape(meta_m.group(3)).strip()
            L = len(current)
            if L > 160:
                new_desc = truncate_at_word(current, MAX_LEN)
                kind = 'long'
            elif L < 25:
                new_desc = generate_from_title(title, lang, rel)
                kind = 'short'

        if new_desc is None: continue

        # Échapper pour HTML attribute (utiliser quote du original ou ")
        quote = meta_m.group(2) if meta_m else '"'
        if quote in new_desc:
            new_desc = new_desc.replace(quote, '&quot;' if quote == '"' else '&#39;')

        if meta_m:
            new_meta_tag = f'{meta_m.group(1)}{quote}{new_desc}{quote}{meta_m.group(5)}'
            new_content = content[:meta_m.start()] + new_meta_tag + content[meta_m.end():]
        else:
            # Insérer après le <title>
            if title_m:
                insert_at = title_m.end()
                new_tag = f'\n  <meta name="description" content="{new_desc}">'
                new_content = content[:insert_at] + new_tag + content[insert_at:]
            else:
                continue

        if kind == 'long': fixed_long += 1
        elif kind == 'short': fixed_short += 1
        elif kind == 'missing': fixed_missing += 1

        if len(samples[kind]) < 3:
            samples[kind].append((rel, new_desc))

        if not DRY_RUN:
            Path(p).write_text(new_content, encoding='utf-8')

print(f"{'DRY RUN — aucune modif appliquée' if DRY_RUN else '✏️  ÉCRITURE'}")
print(f"  ✏️  trop longues raccourcies  : {fixed_long}")
print(f"  ✏️  trop courtes régénérées   : {fixed_short}")
print(f"  ✏️  absentes ajoutées         : {fixed_missing}")
print(f"  ❌ erreurs lecture            : {errors}")
print()
for kind, items in samples.items():
    if not items: continue
    print(f"=== Échantillon — {kind.upper()} ===")
    for path, desc in items:
        print(f"  {path}")
        print(f"    [{len(desc)}] {desc}")
