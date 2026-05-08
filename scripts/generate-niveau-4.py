#!/usr/bin/env python3
"""
Génère une page niveau-4-daat-harav.html pour un siman donné.

Modelée sur les pages finalisées de 242, 243, 246. Récupère le texte
SA HaRav depuis Sefaria, construit les 5 sections avec contenu
spécifique par siman fourni en input.

Usage interne : appelée depuis un script wrapper qui fournit la spec.
"""
import json, urllib.request, re, os, sys
from pathlib import Path

try:
    ROOT = Path(__file__).parent.parent
except NameError:
    ROOT = Path('/Users/admin/Documents/Claude/Projects/daat-ai/.claude/worktrees/beautiful-hellman-1e9412')
HEB_LETTERS = ['','א','ב','ג','ד','ה','ו','ז','ח','ט','י','יא','יב','יג','יד','טו','טז','יז','יח','יט','כ','כא','כב','כג','כד','כה','כו','כז','כח','כט','ל','לא','לב','לג','לד','לה','לו','לז','לח','לט','מ','מא','מב','מג','מד','מה','מו','מז','מח','מט','נ','נא','נב','נג','נד','נה','נו','נז','נח','נט','ס','סא','סב','סג','סד','סה','סו','סז','סח','סט','ע','עא','עב','עג','עד','עה','עו','עז','עח','עט','פ','פא','פב','פג','פד','פה','פו','פז','פח','פט','צ','צא','צב','צג','צד','צה','צו','צז','צח','צט','ק']

def fetch_sefaria(siman_n):
    """Fetch SA HaRav text + KA from Sefaria."""
    def fetch(url):
        req = urllib.request.Request(url, headers={'Accept':'application/json'})
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    def clean(s):
        if not isinstance(s, str): return ''
        s = re.sub(r'<i [^>]*>\s*</i>', '', s)
        s = re.sub(r'<b>(.*?)</b>', r'\1', s)
        return s.replace('<br>', '\n').strip()
    main = fetch(f'https://www.sefaria.org/api/texts/Shulchan_Arukh_HaRav,_Orach_Chayim.{siman_n}?context=0&pad=0')
    ka = fetch(f'https://www.sefaria.org/api/texts/Kuntres_Acharon_on_Shulchan_Arukh_HaRav,_Orach_Chayim.{siman_n}?context=0&pad=0')
    return {
        'seifim': [clean(s) for s in (main.get('he') or [])],
        'ka': [clean(s if isinstance(s, str) else (s[0] if s else '')) for s in (ka.get('he') or [])],
    }

def build_seifim_html(seifim):
    blocks = []
    for i, seif in enumerate(seifim, 1):
        clean = seif.replace('\n', '<br><br>')
        blocks.append(f'''    <div class="sa-block">
      <p class="sa-he"><span class="seif-num">{HEB_LETTERS[i]}.</span> {clean}</p>
    </div>''')
    return '\n\n'.join(blocks)

def build_ka_html(ka_entries):
    blocks = []
    for i, ka in enumerate(ka_entries, 1):
        clean = ka.replace('\n', '<br><br>')
        blocks.append(f'''      <div class="sa-block" style="margin-top: 14px;">
        <p style="font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--habad); margin-bottom: 10px;">קונטרס אחרון, אות {HEB_LETTERS[i]}</p>
        <p class="sa-he" style="font-size: 17px;">{clean}</p>
      </div>''')
    return '\n\n'.join(blocks)

def apply_hebrew_glosses(content):
    """Apply Hebrew gloss convention (first occurrence only)."""
    HEB = '֐-׿'
    mapping = [
        ('mahadoura batra', 'מהדורא בתרא'),
        ('kountress aharon', 'קונטרס אחרון'),
        ('mishna berurah', 'משנה ברורה'),
        ('beit yossef', 'בית יוסף'),
        ('beit shamai', 'בית שמאי'),
        ('beit hillel', 'בית הלל'),
        ('admour hazaken', 'אדמו״ר הזקן'),
        ('séoudot', 'סעודות'), ('séouda', 'סעודה'),
        ('seifim', 'סעיפים'), ('seif', 'סעיף'),
        ('mitzvot', 'מצוות'), ('mitzva', 'מצוה'),
        ('minhagim', 'מנהגים'), ('minhag', 'מנהג'),
        ('hidushim', 'חידושים'), ('hidoush', 'חידוש'),
        ('rishonim', 'ראשונים'), ('aharonim', 'אחרונים'),
        ('simanim', 'סימנים'),
        ('igrot', 'אגרות'), ('igeret', 'אגרת'),
        ('maamarim', 'מאמרים'), ('maamar', 'מאמר'),
        ('sichot', 'שיחות'), ('sikha', 'שיחה'),
        ('poskim', 'פוסקים'),
        ('kavod', 'כבוד'), ('oneg', 'עונג'),
        ('deorayta', 'דאורייתא'), ('dérabanan', 'דרבנן'),
        ('pilpoul', 'פלפול'), ('tzedaka', 'צדקה'),
        ('halakha', 'הלכה'), ('shabbat', 'שבת'),
        ('siman', 'סימן'), ('hidur', 'הידור'),
        ('chitah', 'שיטה'), ('mahloket', 'מחלוקת'),
        ('hassidout', 'חסידות'), ('hassid', 'חסיד'),
        ('lemaaseh', 'למעשה'), ('mehaber', 'מחבר'),
        ('marit ayin', 'מראית עין'),
        ("amira l'akum", 'אמירה לעכו״ם'),
        ('Maguid de Mezeritch', 'המגיד ממעזריטש'),
        ('Tanya', 'תניא'),
        ('Likkutei Sichot', 'ליקוטי שיחות'),
        ('Tossafot', 'תוספות'),
        ('Rama', 'רמ״א'), ('Tour', 'טור'),
        ('Rambam', 'רמב״ם'), ('Rashi', 'רש״י'),
    ]
    case_sensitive = {'Rama','Tour','Tossafot','Maguid de Mezeritch','Tanya',
                      'Likkutei Sichot','Rambam','Rashi','Beit Shamai',
                      'Beit Hillel','Beit Yossef'}
    for fr, he in mapping:
        flags = 0 if fr in case_sensitive else re.IGNORECASE
        pattern = (
            r'(?<![="\'\-/#])'
            r'\b(' + re.escape(fr) + r')\b'
            r'(?![\-"\':/])'
            r'(?!\s*\([^)]*[' + HEB + r'])'
        )
        content = re.sub(pattern, r'\1 (' + he + ')', content, count=1, flags=flags)
    # Cleanup attributes
    def clean_attr(m):
        return re.sub(r' \([' + HEB + r'״׳]+\)', '', m.group(0))
    content = re.sub(r'<meta[^>]+content="[^"]*"', clean_attr, content)
    return content

def cleanup_residual_sa_harav(content):
    """Replace any 'SA HaRav' with 'Choulhan Aroukh HaRav'."""
    return re.sub(r'(?<!Choulhan Aroukh )\bSA HaRav\b', 'Choulhan Aroukh HaRav', content)

def apply_modern_convention(content, n, siman_he):
    """
    Apply the project conventions:
    1. 'Siman {n}' → 'Siman {siman_he}' (gematria) — body text only
    2. 'Orah Haïm {n}' → 'Orah Haïm {siman_he}' (gematria)
    3. 'Choulhan Aroukh HaRav' → 'Choulhan Aroukh de l'Admour HaZaken'
       Preserves Sefaria official labels and URLs.
    """
    # 1. Preserve Sefaria official label + URL — they keep numeric siman
    SEFARIA_LABEL = f'Sefaria — Shulchan Arukh HaRav, Orach Chayim {n}'
    SEFARIA_URL_FRAGMENT = f'Shulchan_Arukh_HaRav%2C_Orach_Chayim.{n}'
    SEFARIA_URL_FRAGMENT2 = f'Shulchan_Arukh_HaRav,_Orach_Chayim.{n}'
    TOKEN_LABEL = '___SEFARIA_LABEL_TOKEN___'
    TOKEN_URL = '___SEFARIA_URL_TOKEN___'
    TOKEN_URL2 = '___SEFARIA_URL_TOKEN2___'
    content = content.replace(SEFARIA_LABEL, TOKEN_LABEL)
    content = content.replace(SEFARIA_URL_FRAGMENT, TOKEN_URL)
    content = content.replace(SEFARIA_URL_FRAGMENT2, TOKEN_URL2)

    # 2. Convert all variants of 'SA HaRav' to 'de l'Admour HaZaken'
    content = content.replace('Choulhan Aroukh HaRav', "Choulhan Aroukh de l'Admour HaZaken")
    content = content.replace('Shulhan Aroukh HaRav', "Choulhan Aroukh de l'Admour HaZaken")
    content = content.replace('Choulchan Aroukh HaRav', "Choulhan Aroukh de l'Admour HaZaken")

    # 3. Convert 'Siman {n}' → 'Siman {siman_he}' in body text
    # Avoid touching URLs (siman-{n}/), JSON keys, etc. — only matches 'Siman ' followed by space then digits
    content = re.sub(rf'\bSiman {n}\b', f'Siman {siman_he}', content)
    content = re.sub(rf'\bsiman {n}\b', f'siman {siman_he}', content)

    # 4. Convert 'Orah Haïm {n}' / 'Orach Chayim {n}' (only inside body text — URLs preserved by token)
    content = re.sub(rf'\bOrah Haïm {n}\b', f'Orah Haïm {siman_he}', content)
    content = re.sub(rf'\bOrach Chayim {n}\b', f'Orach Chayim {siman_he}', content)

    # 5. Convert 'de l'Admour HaZaken {n}:X' → 'de l'Admour HaZaken {siman_he}:X' (references)
    content = re.sub(
        rf"(de l'Admour HaZaken ){n}([:\b])",
        rf'\1{siman_he}\2', content
    )
    content = re.sub(
        rf"(de l'Admour HaZaken ){n}\b(?!\d)",
        rf'\1{siman_he}', content
    )

    # 6. Restore preserved fragments — Sefaria label gets gematria number
    content = content.replace(TOKEN_LABEL, f'Sefaria — Shulchan Arukh HaRav, Orach Chayim {siman_he}')
    content = content.replace(TOKEN_URL, SEFARIA_URL_FRAGMENT)
    content = content.replace(TOKEN_URL2, SEFARIA_URL_FRAGMENT2)
    return content

def generate_niveau4(spec):
    """
    spec = {
        'siman': 244,
        'siman_he': 'רמ"ד',
        'title_he': 'איזו מלאכות יכול הנכרי לעשות בעד הישראל',
        'title_fr': 'Quels travaux le non-juif peut faire pour le Juif',
        'subtitle_fr': '...',
        'description': '...',
        'compare_table_rows': [...],  # list of dict {sujet, mehaber, rama, mb, harav, harav_class}
        'hidushim': [...],  # list of dict {num_he, title_he, title_fr, classique, hidoush, consequence}
        'lemaaseh_points': [...],  # list of strings (HTML allowed)
        'rebbe_refs_intro': '...',  # short note about availability of sikhot
        'rebbe_refs_table': [...],  # list of dict {ref, sujet, lien}
        'siman_count': 22,  # len(seifim)
        'ka_count': 10,  # len(ka)
    }
    """
    n = spec['siman']
    siman_he = spec['siman_he']
    sf = fetch_sefaria(n)
    seifim_html = build_seifim_html(sf['seifim'])
    ka_html = build_ka_html(sf['ka'])

    # Build compare table rows
    compare_rows = []
    for r in spec['compare_table_rows']:
        cls = ' class="harav"' if r.get('harav_class') else ''
        compare_rows.append(f'''        <tr{cls}>
          <td>{r["sujet"]}</td>
          <td>{r["mehaber"]}</td>
          <td>{r["rama"]}</td>
          <td>{r["mb"]}</td>
          <td>{r["harav"]}</td>
        </tr>''')
    compare_table_html = '\n'.join(compare_rows)

    # Build hidushim blocks
    hidushim_blocks = []
    for h in spec['hidushim']:
        hidushim_blocks.append(f'''    <div class="sa-block">
      <p class="sa-he" style="font-size: 19px; font-weight: 700; margin-bottom: 12px; color: var(--habad-deep);">{h["num_he"]}</p>
      <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 19px; font-weight: 600; color: var(--navy); margin-bottom: 10px;">{h["title_fr"]}</h3>
      <p style="margin-bottom: 10px;"><strong>Position classique :</strong> {h["classique"]}</p>
      <p style="margin-bottom: 10px;"><strong>Le hidoush du Rav :</strong> {h["hidoush"]}</p>
      <p><strong>Conséquence pratique :</strong> {h["consequence"]}</p>
    </div>''')
    hidushim_html = '\n\n'.join(hidushim_blocks)

    # Build lemaaseh
    lemaaseh_html = '\n        '.join([f'<li>{p}</li>' for p in spec['lemaaseh_points']])

    # Build Rebbe refs table
    refs_rows = []
    for i, r in enumerate(spec['rebbe_refs_table']):
        cls = ' class="harav"' if i % 2 else ''
        refs_rows.append(f'''        <tr{cls}>
          <td>{r["ref"]}</td>
          <td>{r["sujet"]}</td>
          <td>{r["lien"]}</td>
        </tr>''')
    refs_table_html = '\n'.join(refs_rows)

    # Final HTML
    html = f'''<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<link rel="icon" type="image/svg+xml" href="../../../favicon.svg">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Siman {n} · Niveau 4 Daat HaRav — Chitah de l'Admour HaZaken | DAAT</title>
<meta name="description" content="Niveau 4 (Daat HaRav) du Siman {n} — La chitah de l'Admour HaZaken sur {spec["title_fr"]}. Texte du Choulhan Aroukh HaRav, force du psak, חידוש du Rav, sikhot du Rabbi.">
<meta name="author" content="Rav Yossef Haim Samama">
<link rel="canonical" href="https://daattorah.com/sources/shabbat/siman-{n}/niveau-4-daat-harav.html">
<meta property="og:type" content="article">
<meta property="og:site_name" content="DAAT דעת">
<meta property="og:title" content="Siman {n} · Niveau 4 Daat HaRav">
<meta property="og:description" content="La chitah de l'Admour HaZaken sur {spec["title_fr"]}.">
<meta property="og:url" content="https://daattorah.com/sources/shabbat/siman-{n}/niveau-4-daat-harav.html">
<meta property="og:image" content="https://daattorah.com/assets/img/og/siman-{n}.svg">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Siman {n} · Niveau 4 Daat HaRav">
<meta name="twitter:description" content="Chitah de l'Admour HaZaken sur {spec['title_fr']}.">
<meta name="twitter:image" content="https://daattorah.com/assets/img/og/siman-{n}.svg">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Frank+Ruhl+Libre:wght@300;400;500;700;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
  :root {{
    --navy: #1A1F3A; --gold: #C5A55A; --gold-light: #D4B97A; --gold-dark: #8C6F1E;
    --cream: #FAF6EE; --cream-dark: #F0EAD8;
    --text: #1A1F3A; --text-mid: #3D4266; --text-muted: #7A7F9A;
    --white: #FFFFFF; --border: #E4DDD0;
    --habad: #3851A3; --habad-soft: #5A72C2; --habad-deep: #243669;
    --habad-tint: rgba(56, 81, 163, 0.06);
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Cormorant Garamond', Georgia, serif; background: var(--cream); color: var(--text); line-height: 1.7; }}
  header {{ background: var(--navy); padding: 0 40px; display: flex; align-items: center; justify-content: space-between; height: 70px; border-bottom: 2px solid var(--gold); }}
  .logo {{ display: flex; align-items: baseline; gap: 12px; text-decoration: none; }}
  .logo-he {{ font-family: 'Frank Ruhl Libre', serif; font-size: 26px; font-weight: 700; color: var(--gold); }}
  .logo-en {{ font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #fff; letter-spacing: 3px; }}
  nav {{ display: flex; gap: 24px; align-items: center; }}
  nav a {{ font-family: 'Inter', sans-serif; font-size: 13px; color: rgba(255,255,255,0.7); text-decoration: none; letter-spacing: 1px; }}
  nav a:hover {{ color: var(--gold); }}
  .breadcrumb {{ background: var(--navy); padding: 12px 40px; border-bottom: 1px solid rgba(197,165,90,0.15); }}
  .breadcrumb-inner {{ max-width: 1100px; margin: 0 auto; }}
  .breadcrumb a, .breadcrumb span {{ font-family: 'Inter', sans-serif; font-size: 12px; color: rgba(255,255,255,0.4); text-decoration: none; letter-spacing: 0.5px; }}
  .breadcrumb a:hover {{ color: var(--gold); }}
  .breadcrumb .sep {{ margin: 0 8px; color: rgba(255,255,255,0.2); }}
  .breadcrumb .current {{ color: var(--gold); }}
  .page-hero {{ background: linear-gradient(135deg, var(--habad-deep) 0%, var(--habad) 60%, var(--habad-soft) 100%); padding: 56px 40px; border-bottom: 3px solid var(--gold); }}
  .hero-inner {{ max-width: 1100px; margin: 0 auto; }}
  .hero-meta {{ font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 4px; text-transform: uppercase; color: var(--gold); margin-bottom: 14px; }}
  .hero-title-he {{ font-family: 'Frank Ruhl Libre', serif; font-size: 44px; font-weight: 700; color: var(--gold); direction: rtl; margin-bottom: 6px; letter-spacing: 1px; }}
  .hero-title {{ font-family: 'Cormorant Garamond', serif; font-size: 32px; font-weight: 400; color: #fff; margin-bottom: 8px; }}
  .hero-subtitle {{ font-size: 17px; color: rgba(255,255,255,0.78); font-style: italic; max-width: 800px; }}
  main {{ max-width: 1000px; margin: 0 auto; padding: 50px 40px 60px; }}
  .intro-block {{ background: var(--white); border: 1px solid var(--border); border-left: 4px solid var(--habad); padding: 22px 26px; margin-bottom: 40px; }}
  .intro-block p {{ color: var(--text-mid); }}
  .intro-block p + p {{ margin-top: 10px; }}
  .intro-block strong {{ color: var(--navy); }}
  .section-block {{ margin-bottom: 56px; }}
  .section-num {{ display: inline-block; font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--habad); background: var(--habad-tint); padding: 5px 12px; border-radius: 2px; margin-bottom: 12px; }}
  .section-title-he {{ font-family: 'Frank Ruhl Libre', serif; direction: rtl; font-size: 26px; color: var(--navy); margin-bottom: 6px; font-weight: 700; }}
  .section-title-fr {{ font-family: 'Cormorant Garamond', serif; font-size: 26px; font-weight: 500; color: var(--navy); margin-bottom: 18px; }}
  .section-divider {{ width: 60px; height: 2px; background: var(--gold); margin-bottom: 24px; }}
  .sa-block {{ background: var(--white); border: 1px solid var(--border); border-right: 4px solid var(--habad); padding: 24px 28px; margin-bottom: 18px; }}
  .sa-block .seif-num {{ font-family: 'Frank Ruhl Libre', serif; font-weight: 700; color: var(--habad); margin-left: 4px; }}
  .sa-he {{ font-family: 'Frank Ruhl Libre', serif; direction: rtl; text-align: right; font-size: 19px; line-height: 1.95; color: var(--navy); }}
  .compare-table {{ width: 100%; border-collapse: collapse; background: var(--white); border: 1px solid var(--border); margin-bottom: 18px; }}
  .compare-table thead {{ background: var(--habad); }}
  .compare-table thead th {{ padding: 12px 16px; font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); text-align: left; }}
  .compare-table tbody tr {{ border-bottom: 1px solid var(--border); }}
  .compare-table tbody tr:hover {{ background: var(--cream); }}
  .compare-table td {{ padding: 14px 16px; font-size: 15px; color: var(--text-mid); vertical-align: top; }}
  .compare-table td:first-child {{ font-family: 'Frank Ruhl Libre', serif; font-size: 18px; color: var(--navy); white-space: nowrap; }}
  .compare-table tr.harav td {{ background: var(--habad-tint); }}
  .compare-table tr.harav td:last-child {{ font-weight: 600; color: var(--habad-deep); }}
  .quote-block {{ background: var(--cream); border: 1px solid var(--border); border-left: 4px solid var(--gold); padding: 22px 26px; margin-bottom: 18px; position: relative; }}
  .quote-block .quote-fr {{ color: var(--text-mid); line-height: 1.75; }}
  .quote-source {{ margin-top: 12px; font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text-muted); padding-top: 12px; border-top: 1px dashed var(--border); }}
  .lemaaseh-block {{ background: linear-gradient(180deg, var(--habad-tint) 0%, var(--white) 50%); border: 2px solid var(--habad); padding: 28px 32px; margin-bottom: 18px; }}
  .lemaaseh-block h3 {{ font-family: 'Cormorant Garamond', serif; font-size: 24px; font-weight: 600; color: var(--habad-deep); margin-bottom: 14px; }}
  .lemaaseh-block ul {{ margin-left: 20px; color: var(--text-mid); }}
  .lemaaseh-block li {{ margin-bottom: 8px; line-height: 1.7; }}
  .lemaaseh-block li strong {{ color: var(--navy); }}
  footer {{ background: var(--navy); border-top: 2px solid var(--gold); padding: 28px 40px; text-align: center; margin-top: 60px; }}
  footer p {{ font-family: 'Inter', sans-serif; font-size: 12px; color: rgba(255,255,255,0.4); }}
  footer a {{ color: var(--gold); text-decoration: none; }}
  @media (max-width: 768px) {{
    header, .breadcrumb, .page-hero, main, footer {{ padding-left: 20px; padding-right: 20px; }}
    .hero-title-he {{ font-size: 34px; }}
    .hero-title {{ font-size: 24px; }}
  }}
</style>
</head>
<body>

<header>
  <a href="../../../index.html" class="logo">
    <span class="logo-he">דעת</span>
    <span class="logo-en">DAAT</span>
  </a>
  <nav>
    <a href="../../../index.html">Accueil</a>
    <a href="../index.html">Hilkhot Shabbat</a>
    <a href="index.html">Siman {n}</a>
    <a href="../../../chitah-admour-hazaken.html">📜 Chitah de l'Admour</a>
  </nav>
</header>

<div class="breadcrumb">
  <div class="breadcrumb-inner">
    <a href="../../../index.html">Accueil</a>
    <span class="sep">›</span>
    <a href="../index.html">Hilkhot Shabbat</a>
    <span class="sep">›</span>
    <a href="index.html">Siman {n}</a>
    <span class="sep">›</span>
    <span class="current">Niveau 4 — Daat HaRav</span>
  </div>
</div>

<div class="page-hero">
  <div class="hero-inner">
    <div class="hero-meta">Orah Haïm {n} · Niveau 4 · שיטת אדמו״ר הזקן</div>
    <p class="hero-title-he">דעת הרב</p>
    <h1 class="hero-title" style="margin: 0;">Daat HaRav — Le Choulhan Aroukh HaRav sur le Siman {n}</h1>
    <p class="hero-subtitle">{spec["subtitle_fr"]}</p>
  </div>
</div>

<main>

  <div class="intro-block">
    <p><strong>Pourquoi un niveau 4 dédié à l'Admour HaZaken ?</strong> Le <strong>Choulhan Aroukh HaRav</strong> n'est pas un commentaire sur le Mehaber — c'est un <strong>Choulhan Aroukh autonome et complet</strong>, écrit par l'Admour HaZaken. Sa singularité : il combine <em>halakha + טעמי המצוות + dimension intérieure</em> dans un seul ouvrage, et il tranche avec une rigueur talmudique unique.</p>
    <p>Pour le Habad, l'Admour HaZaken est <strong>הפוסק האחרון</strong>. Cette page rassemble, pour le siman {n}, le texte intégral du Rav, son originalité, et les דברי הרבי qui éclairent le sujet.</p>
    <p style="margin-top:14px;"><a href="../../../chitah-admour-hazaken.html" style="color:var(--habad);font-weight:600;">→ Lire la préface générale sur la chitah de l'Admour HaZaken</a></p>
  </div>

  <!-- 1. TEXTE DU CHOULHAN AROUKH HARAV -->
  <section class="section-block">
    <span class="section-num">1 · טקסט אדמו״ר הזקן</span>
    <h2 class="section-title-he">שלחן ערוך הרב — סימן {siman_he}</h2>
    <h2 class="section-title-fr">Le texte intégral du Choulhan Aroukh HaRav (שולחן ערוך הרב)</h2>
    <div class="section-divider"></div>

    <p style="margin-bottom: 24px; color: var(--text-mid); font-size: 15px;">
      <strong>סימן {siman_he} — {spec["title_he"]} — וּבוֹ {HEB_LETTERS[spec["siman_count"]]} סְעִיפִים</strong><br>
      <em>Source : édition Kehot, telle que reproduite sur Sefaria. {spec["siman_count"]} seifim + {spec["ka_count"]} entrée(s) de Kountress Aharon (קונטרס אחרון).</em>
    </p>

{seifim_html}

    <details style="margin-top: 32px; background: var(--white); border: 1px solid var(--border); border-left: 4px solid var(--habad); padding: 18px 24px;">
      <summary style="font-family: 'Cormorant Garamond', serif; font-size: 22px; font-weight: 600; color: var(--habad-deep); cursor: pointer;">
        קונטרס אחרון — {spec["ka_count"]} entrée(s) (cliquer pour déplier)
      </summary>
      <p style="margin-top: 12px; color: var(--text-muted); font-style: italic; font-size: 13px;">
        Le Kountress Aharon est l'annexe pilpoulique de l'Admour HaZaken — son laboratoire halakhique en bas de page.
      </p>

{ka_html}
    </details>

    <details style="margin-top: 18px; background: rgba(245, 200, 100, 0.10); border: 1px dashed var(--gold); border-left: 4px solid var(--gold); padding: 18px 24px;">
      <summary style="font-family: 'Cormorant Garamond', serif; font-size: 22px; font-weight: 600; color: var(--gold-dark); cursor: pointer;">
        📷 הגהות וציונים — À transcrire depuis l'édition imprimée Kehot (en attente photos)
      </summary>
      <p style="margin-top: 12px; color: var(--text-mid); line-height: 1.7;">
        L'édition Kehot du Choulhan Aroukh HaRav comporte au bas de chaque page une section dense de <strong>הגהות וציונים</strong> (cross-références marginales) qui n'est <strong>pas reproduite sur Sefaria</strong>. Outil essentiel pour la recherche pilpoulique.
      </p>
      <p style="margin-top: 14px; font-size: 13px; color: var(--text-muted); font-style: italic; padding-top: 12px; border-top: 1px dashed var(--border);">
        ⚠ <strong>Placeholder à remplir dès réception des photos.</strong>
      </p>
    </details>

    <p style="margin-top: 20px; font-size: 13px; color: var(--text-muted); font-style: italic;">
      Source : <a href="https://www.sefaria.org/Shulchan_Arukh_HaRav%2C_Orach_Chayim.{n}" target="_blank" style="color: var(--habad);">Sefaria — Shulchan Arukh HaRav, Orach Chayim {n}</a>.
    </p>
  </section>

  <!-- 2. LA FORCE DU PSAK -->
  <section class="section-block">
    <span class="section-num">2 · כח הפסק</span>
    <h2 class="section-title-he">כחו של אדמו״ר הזקן בפסק</h2>
    <h2 class="section-title-fr">La force du psak (פסק) de l'Admour HaZaken</h2>
    <div class="section-divider"></div>

    <p style="margin-bottom: 18px; color: var(--text-mid);">Comparaison de la position de l'Admour HaZaken avec celles du Mehaber (מחבר), du Rama (רמ״א) et de la Mishna Berurah (משנה ברורה) sur les points-clés du siman {n}.</p>

    <table class="compare-table">
      <thead>
        <tr><th style="width: 18%;">Sujet</th><th>Mehaber</th><th>Rama</th><th>Mishna Berurah</th><th>Choulhan Aroukh HaRav</th></tr>
      </thead>
      <tbody>
{compare_table_html}
      </tbody>
    </table>

    <p style="margin-top: 18px; font-size: 13px; color: var(--text-muted); font-style: italic;">
      Comparaison établie à partir du texte hébraïque intégral du Choulhan Aroukh HaRav {n}.
    </p>
  </section>

  <!-- 3. CHIDOUSH -->
  <section class="section-block">
    <span class="section-num">3 · חידוש אדמו״ר הזקן</span>
    <h2 class="section-title-he">חידושים מיוחדים של הרב</h2>
    <h2 class="section-title-fr">Les חידושים propres au Rav sur ce siman</h2>
    <div class="section-divider"></div>

    <p style="margin-bottom: 24px; color: var(--text-mid);">
      Originalités qui distinguent l'Admour HaZaken sur le siman {n}. Chaque hidoush (חידוש) suit la structure : <em>position classique → hidoush du Rav → conséquence pratique</em>.
    </p>

{hidushim_html}
  </section>

  <!-- 4. DIVREI HAREBBE -->
  <section class="section-block">
    <span class="section-num">4 · דברי הרבי</span>
    <h2 class="section-title-he">סיכות, מאמרים ואגרות הרבי</h2>
    <h2 class="section-title-fr">Les paroles du Rabbi sur les thèmes du siman {n}</h2>
    <div class="section-divider"></div>

    <div style="background: rgba(245, 200, 100, 0.15); border-left: 3px solid var(--gold); padding: 14px 20px; margin-bottom: 24px; font-size: 14px; color: var(--text-mid);">
      <strong>⚠ Note honnête sur ce siman :</strong> {spec["rebbe_refs_intro"]}
    </div>

    <table class="compare-table">
      <thead>
        <tr><th>Référence</th><th>Sujet</th><th>Lien avec le siman {n}</th></tr>
      </thead>
      <tbody>
{refs_table_html}
      </tbody>
    </table>

    <p style="margin-top: 24px; font-size: 13px; color: var(--text-muted); font-style: italic; padding: 14px 18px; background: var(--cream-dark); border-left: 3px solid var(--habad);">
      <strong>⚠ Validation :</strong> les références ci-dessus sont des <em>indices de recherche</em> à valider contre les volumes physiques de l'édition Kehot. La source la plus directe pour les pesakim du Rabbi par siman reste <strong>שערי הלכה ומנהג</strong>.
    </p>
  </section>

  <!-- 5. LEMAASEH -->
  <section class="section-block">
    <span class="section-num">5 · למעשה</span>
    <h2 class="section-title-he">הלכה למעשה — מנהג חב״ד</h2>
    <h2 class="section-title-fr">La conduite Habad pratique</h2>
    <div class="section-divider"></div>

    <p style="margin-bottom: 22px; color: var(--text-mid);">
      Points de conduite halakhique qui découlent directement du Choulhan Aroukh HaRav siman {n}, dans la sensibilité Habad.
    </p>

    <div class="lemaaseh-block">
      <h3>Pour le Hassid (חסיד) Habad — Siman {n}</h3>
      <ul>
        {lemaaseh_html}
      </ul>

      <p style="margin-top: 22px; font-size: 13px; color: var(--text-muted); font-style: italic; padding-top: 14px; border-top: 1px dashed var(--border);">
        ⚠ Cette section présente la conduite halakhique Habad. Pour toute question concrète : <strong>consulter ton Rav</strong>.
      </p>
    </div>
  </section>

</main>

<footer>
  <p>DAAT דעת — © 5786 / 2026 · <a href="../../../index.html">Retour à l'accueil</a> · Initié par le Rav Yossef Haim Samama</p>
</footer>

<link rel="stylesheet" href="../../../assets/css/chat-widget.css">
<script>window.DAAT_CHAT_API_URL = 'https://daatai.vercel.app/api/chat';</script>
<script src="../../../assets/js/chat-widget.js" defer></script>
</body>
</html>
'''

    # Apply Hebrew gloss + cleanup SA HaRav residuals + modern convention
    html = apply_hebrew_glosses(html)
    html = cleanup_residual_sa_harav(html)
    html = apply_modern_convention(html, spec['siman'], spec['siman_he'])
    return html

def generate_index(spec):
    """Generate the index.html for a siman with only niveau 4 available."""
    n = spec['siman']
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="../../../favicon.svg">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Siman {n} — {spec["title_fr"]} · Choulhan Aroukh · Étude en français | DAAT</title>
  <meta name="description" content="Étude du Siman {n} (Choulhan Aroukh, Orah Haïm) — {spec["title_fr"]}. Niveau 4 Daat HaRav (chitah de l'Admour HaZaken) disponible. Niveaux 1-3 à venir.">
  <meta name="author" content="Rav Yossef Haim Samama">
  <link rel="canonical" href="https://daattorah.com/sources/shabbat/siman-{n}/">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="DAAT דעת">
  <meta property="og:title" content="Siman {n} — {spec["title_fr"]}">
  <meta property="og:description" content="{spec["description"]}">
  <meta property="og:url" content="https://daattorah.com/sources/shabbat/siman-{n}/">
  <meta property="og:image" content="https://daattorah.com/assets/img/og/og-default.svg">
  <meta property="og:locale" content="fr_FR">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,600&family=Frank+Ruhl+Libre:wght@300;400;500;700;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy: #1A1F3A; --gold: #C5A55A; --gold-light: #D4B97A;
      --cream: #FAF6EE; --cream-dark: #F0EAD8;
      --text-dark: #1A1F3A; --text-mid: #3D4266; --text-muted: #7A7F9A;
      --white: #FFFFFF; --border: #E4DDD0;
      --green: #2E7D52; --purple: #6B3FA0;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Cormorant Garamond', Georgia, serif; background: var(--cream); color: var(--text-dark); line-height: 1.7; }}
    header {{ background: var(--navy); padding: 0 40px; display: flex; align-items: center; justify-content: space-between; height: 70px; border-bottom: 2px solid var(--gold); }}
    .logo {{ display: flex; align-items: baseline; gap: 12px; text-decoration: none; }}
    .logo-he {{ font-family: 'Frank Ruhl Libre', serif; font-size: 26px; font-weight: 700; color: var(--gold); }}
    .logo-en {{ font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #fff; letter-spacing: 3px; }}
    nav {{ display: flex; gap: 24px; align-items: center; }}
    nav a {{ font-family: 'Inter', sans-serif; font-size: 13px; color: rgba(255,255,255,0.7); text-decoration: none; letter-spacing: 1px; }}
    nav a:hover {{ color: var(--gold); }}
    .breadcrumb {{ background: var(--navy); padding: 12px 40px; border-bottom: 1px solid rgba(197,165,90,0.15); }}
    .breadcrumb-inner {{ max-width: 1100px; margin: 0 auto; }}
    .breadcrumb a, .breadcrumb span {{ font-family: 'Inter', sans-serif; font-size: 12px; color: rgba(255,255,255,0.4); text-decoration: none; letter-spacing: 0.5px; }}
    .breadcrumb a:hover {{ color: var(--gold); }}
    .breadcrumb .sep {{ margin: 0 8px; color: rgba(255,255,255,0.2); }}
    .breadcrumb .current {{ color: var(--gold); }}
    .siman-hero {{ background: var(--navy); padding: 60px 40px 48px; border-bottom: 3px solid var(--gold); }}
    .siman-hero-inner {{ max-width: 1100px; margin: 0 auto; }}
    .siman-meta {{ font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 4px; text-transform: uppercase; color: var(--gold); margin-bottom: 16px; }}
    .siman-title-he {{ font-family: 'Frank Ruhl Libre', serif; font-size: 48px; font-weight: 900; color: var(--gold); direction: rtl; margin-bottom: 8px; }}
    .siman-title-fr {{ font-family: 'Cormorant Garamond', serif; font-size: 32px; font-weight: 300; color: var(--white); margin-bottom: 12px; }}
    .siman-subtitle {{ font-size: 17px; color: rgba(255,255,255,0.6); font-style: italic; max-width: 800px; }}
    .content {{ max-width: 1100px; margin: 0 auto; padding: 50px 40px 60px; }}
    .levels-header {{ font-family: 'Cormorant Garamond', serif; font-size: 26px; color: var(--navy); margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }}
    .levels-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 60px; }}
    .level-card {{ background: var(--white); border: 1px solid var(--border); padding: 28px; position: relative; transition: transform 0.2s, box-shadow 0.2s; }}
    .level-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 30px rgba(26,31,58,0.1); }}
    .level-card.available {{ cursor: pointer; }}
    .level-card.coming-soon {{ opacity: 0.55; }}
    .level-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }}
    .level-num {{ font-size: 48px; font-weight: 300; color: var(--cream-dark); line-height: 1; }}
    .level-status-badge {{ font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 4px 10px; border-radius: 2px; }}
    .badge-ready {{ background: #E8F5EE; color: #2E7D52; }}
    .badge-soon {{ background: #F0F0F0; color: #999; }}
    .level-bar {{ height: 3px; margin-bottom: 16px; }}
    .bar-1 {{ background: var(--green); }}
    .bar-2 {{ background: var(--navy); }}
    .bar-3 {{ background: var(--purple); }}
    .bar-habad {{ background: #3851A3; }}
    .level-name-he {{ font-family: 'Frank Ruhl Libre', serif; font-size: 15px; color: var(--text-muted); direction: rtl; margin-bottom: 4px; }}
    .level-name-fr {{ font-family: 'Cormorant Garamond', serif; font-size: 24px; font-weight: 600; color: var(--navy); margin-bottom: 12px; }}
    .level-desc {{ font-size: 15px; color: var(--text-mid); line-height: 1.6; margin-bottom: 20px; }}
    .level-actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .btn-level {{ font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; letter-spacing: 1px; padding: 10px 18px; text-decoration: none; border-radius: 2px; transition: all 0.15s; }}
    .seif-info {{ background: var(--white); border: 1px solid var(--border); border-left: 4px solid var(--gold); padding: 28px 32px; margin-bottom: 40px; }}
    .seif-info-label {{ font-family: 'Inter', sans-serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); margin-bottom: 14px; }}
    .seif-text-he {{ font-family: 'Frank Ruhl Libre', serif; direction: rtl; text-align: right; font-size: 19px; line-height: 1.95; color: var(--navy); margin-bottom: 16px; }}
    footer {{ background: var(--navy); border-top: 2px solid var(--gold); padding: 32px 40px; text-align: center; }}
    footer p {{ font-family: 'Inter', sans-serif; font-size: 12px; color: rgba(255,255,255,0.3); }}
    footer a {{ color: var(--gold); text-decoration: none; }}
    @media (max-width: 768px) {{
      header, .breadcrumb, .siman-hero, .content, footer {{ padding-left: 20px; padding-right: 20px; }}
      .siman-title-he {{ font-size: 38px; }}
      .siman-title-fr {{ font-size: 24px; }}
      .levels-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

  <header>
    <a href="../../../index.html" class="logo">
      <span class="logo-he">דעת</span>
      <span class="logo-en">DAAT</span>
    </a>
    <nav>
      <a href="../../../index.html">Accueil</a>
      <a href="../index.html">Hilkhot Shabbat</a>
      <a href="../../../chat.html">💬 IA Daat</a>
      <a href="../../../chitah-admour-hazaken.html">📜 Chitah de l'Admour</a>
    </nav>
  </header>

  <div class="breadcrumb">
    <div class="breadcrumb-inner">
      <a href="../../../index.html">Accueil</a>
      <span class="sep">›</span>
      <a href="../index.html">Hilkhot Shabbat</a>
      <span class="sep">›</span>
      <span class="current">Siman {n}</span>
    </div>
  </div>

  <div class="siman-hero">
    <div class="siman-hero-inner">
      <div class="siman-meta">Orah Haïm · Hilkhot Shabbat · Siman {spec["siman_he"]}</div>
      <div class="siman-title-he" aria-hidden="true">{spec["title_he"]}</div>
      <h1 class="siman-title-fr" style="margin: 0;">Siman {n} — {spec["title_fr"]}</h1>
      <div class="siman-subtitle">{spec["subtitle_fr"]}</div>
    </div>
  </div>

  <div class="content">

    <div class="seif-info">
      <div class="seif-info-label">Texte hébreu — שולחן ערוך עם הגהות הרמ״א</div>
      <div class="seif-text-he">
        {spec["mehaber_seif1_preview"]}
      </div>
    </div>

    <div class="levels-header">Niveaux d'étude — Siman {n}</div>
    <div class="levels-grid">

      <div class="level-card coming-soon">
        <div class="level-bar bar-1"></div>
        <div class="level-top">
          <div class="level-num">01</div>
          <span class="level-status-badge badge-soon">Bientôt</span>
        </div>
        <div class="level-name-he">רמת המתחילים</div>
        <div class="level-name-fr">Base — Initiation</div>
        <div class="level-desc">Texte hébreu avec traduction française complète, explication pédagogique des concepts-clés, cas pratiques modernes. <em>En préparation.</em></div>
      </div>

      <div class="level-card coming-soon">
        <div class="level-bar bar-2"></div>
        <div class="level-top">
          <div class="level-num">02</div>
          <span class="level-status-badge badge-soon">Bientôt</span>
        </div>
        <div class="level-name-he">רמת הלמדן</div>
        <div class="level-name-fr">Lamdan — Pilpoul avancé</div>
        <div class="level-desc">חקירת היסוד, sources Rishonim et Acharonim, מחלוקות classiques, נפקא מינות pour les cas modernes. <em>En préparation.</em></div>
      </div>

      <div class="level-card coming-soon">
        <div class="level-bar bar-3"></div>
        <div class="level-top">
          <div class="level-num">03</div>
          <span class="level-status-badge badge-soon">Bientôt</span>
        </div>
        <div class="level-name-he">חזרה וסיכום</div>
        <div class="level-name-fr">Synthèse Magistrale</div>
        <div class="level-desc">Récapitulatif structuré pour révision et mémorisation : axiomes, arbres de décision, mnémoniques, pièges à éviter. <em>En préparation.</em></div>
      </div>

      <div class="level-card available">
        <div class="level-bar bar-habad"></div>
        <div class="level-top">
          <div class="level-num">04</div>
          <span class="level-status-badge badge-ready">Disponible</span>
        </div>
        <div class="level-name-he">דעת הרב</div>
        <div class="level-name-fr">Daat HaRav — Chitah de l'Admour HaZaken</div>
        <div class="level-desc">Le Choulhan Aroukh HaRav sur ce siman : {spec["siman_count"]} seifim complets et {spec["ka_count"]} entrée(s) de Kountress Aharon. Force et originalité du psak de l'Admour HaZaken, חידוש propre au Rav, sikhot et igrot du Rabbi qui éclairent le sujet, conduite למעשה.</div>
        <div class="level-actions">
          <a href="niveau-4-daat-harav.html" class="btn-level" style="background:#3851A3;color:#fff;">📜 Étudier ce niveau</a>
        </div>
      </div>

    </div>

  </div>

  <footer>
    <p>DAAT דעת — © 5786 / 2026 · <a href="../../../index.html">Retour à l'accueil</a> · Initié par le Rav Yossef Haim Samama</p>
  </footer>

  <link rel="stylesheet" href="../../../assets/css/chat-widget.css">
  <script>window.DAAT_CHAT_API_URL = 'https://daatai.vercel.app/api/chat';</script>
  <script src="../../../assets/js/chat-widget.js" defer></script>
</body>
</html>
'''
    # Apply modern convention (gematria + Admour HaZaken) on the index too
    return apply_modern_convention(html, spec['siman'], spec['siman_he'])

if __name__ == '__main__':
    print('Module — to be called with a spec dict via the wrapper script.')
