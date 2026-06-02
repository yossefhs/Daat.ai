#!/usr/bin/env python3
"""
DAAT — Générateur des niveaux 1, 2, 3 pour un siman.

Pour un siman donné :
  1. Fetch Sefaria (Choulhan Aroukh OH + Mishnah Berurah)
  2. Génère niveau-1-base.html (Initiation pédagogique)
  3. Génère niveau-2-lamdan.html (Pilpoul approfondi)
  4. Génère niveau-3-synthese.html (Synthèse magistrale)
  5. Met à jour data/simanim/siman-XXX.json (comingSoon=false sur N1/N2/N3)

Usage :
    python3 scripts/generate-niveaux-123.py --siman 248
    python3 scripts/generate-niveaux-123.py --range 248-257
    python3 scripts/generate-niveaux-123.py --all  # tous les simanim 242-365

Le contenu inclut le texte hébreu intégral du Mehaber et du MB depuis Sefaria.
La structure et les sections analytiques sont adaptées au siman via son JSON.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data' / 'simanim'
SOURCES_DIR = ROOT / 'sources' / 'shabbat'

# Les niveaux 1-3 suivent le Mehaber : ils couvrent TOUS les simanim 242-365,
# y compris 304 et 322 — que le Mehaber et le Mishnah Berurah traitent, même si
# l'Admour HaZaken (niveau 4) ne les a pas rédigés. Aucun siman n'est ignoré.
SKIP = set()

# ============================================================
# SEFARIA FETCHING
# ============================================================

def fetch_json(url, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'DAAT/1.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            print(f'  ⚠ fetch failed: {url} — {e}', file=sys.stderr)
            return None

def clean_html_in_text(text):
    """Strip Sefaria's <i data-commentator=...> tags but keep <b>, <small>."""
    if not isinstance(text, str):
        return ''
    text = re.sub(r'<i [^>]*data-commentator[^>]*></i>', '', text)
    text = re.sub(r'<i [^>]*data-commentator[^>]*></i>', '', text)
    return text.strip()

def fetch_sefaria(siman_n):
    """Fetch Mehaber + Mishnah Berurah for a given siman."""
    data = {'seifim': [], 'mb': []}

    url = f'https://www.sefaria.org/api/v3/texts/Shulchan_Arukh,_Orach_Chayim.{siman_n}?version=hebrew'
    j = fetch_json(url)
    if j and j.get('versions'):
        text = j['versions'][0].get('text', [])
        if isinstance(text, list):
            data['seifim'] = [clean_html_in_text(s) for s in text if s]

    url = f'https://www.sefaria.org/api/v3/texts/Mishnah_Berurah.{siman_n}?version=hebrew'
    j = fetch_json(url)
    if j and j.get('versions'):
        text = j['versions'][0].get('text', [])
        if isinstance(text, list):
            data['mb'] = [clean_html_in_text(s) for s in text if s]

    return data

# ============================================================
# COMMON HELPERS
# ============================================================

HEB_LETTERS = ['','א','ב','ג','ד','ה','ו','ז','ח','ט','י','יא','יב','יג','יד','טו','טז','יז','יח','יט','כ',
               'כא','כב','כג','כד','כה','כו','כז','כח','כט','ל','לא','לב','לג','לד','לה','לו','לז','לח','לט',
               'מ','מא','מב','מג','מד','מה','מו','מז','מח','מט','נ']

def safe_he(s):
    """Wrap Hebrew gematria/text in <bdi> for safe bidi rendering."""
    return f'<bdi>{s}</bdi>'

def load_siman_json(n):
    return json.load(open(DATA_DIR / f'siman-{n}.json', encoding='utf-8'))

def update_siman_json(n):
    """Set comingSoon=false on N1/N2/N3 + improve descriptions."""
    p = DATA_DIR / f'siman-{n}.json'
    d = json.load(open(p, encoding='utf-8'))
    for lvl in d['levels']:
        if lvl['num'] in (1, 2, 3):
            lvl.pop('comingSoon', None)
            if lvl['num'] == 1:
                lvl['desc'] = "Initiation pédagogique : texte hébreu du Mehaber et du Mishnah Berurah, traduction française fluide, concepts-clés expliqués, cas pratiques et synthèse."
            elif lvl['num'] == 2:
                lvl['desc'] = "Pilpoul approfondi : sources talmudiques, שיטות des Rishonim et Acharonim, חקירות יסודיות, מחלוקות classiques, נפקא מינות pratiques."
            elif lvl['num'] == 3:
                lvl['desc'] = "Synthèse magistrale : axiome central, hiérarchie des concepts, arbres de décision, mnémoniques, pièges à éviter, tableau de synthèse."
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

# ============================================================
# CSS BLOCKS (shared)
# ============================================================

CSS_N1 = r"""
  @page { size: A4; margin: 2cm 1.8cm; }
  body { font-family: 'Georgia', 'Cambria', serif; font-size: 11pt; line-height: 1.55; color: #1a1a1a; margin: 0; }
  .he { direction: rtl; text-align: right; font-family: 'Frank Ruhl Libre', 'David', 'Times New Roman', serif; font-size: 13pt; line-height: 1.85; }
  .he-q { direction: rtl; unicode-bidi: embed; font-family: 'Frank Ruhl Libre', 'David', serif; font-weight: 600; color: #1A1F3A; }
  .cover { text-align: center; margin-top: 3cm; margin-bottom: 2cm; }
  .cover .badge-top { color: #C5A55A; font-size: 11pt; letter-spacing: 4px; margin-bottom: 10px; }
  .cover h1 { font-size: 30pt; color: #1A1F3A; margin: 5px 0; font-family: 'Cormorant Garamond', 'Georgia', serif; }
  .cover .subtitle { font-size: 14pt; color: #5a4a1a; font-style: italic; margin: 10px 0 30px 0; }
  .cover .he-title { font-size: 36pt; color: #1A1F3A; margin: 20px 0 5px 0; }
  .cover .he-sub { font-size: 18pt; color: #C5A55A; margin-bottom: 30px; }
  .cover .ornament { color: #C5A55A; font-size: 22pt; margin: 15px 0; }
  .cover .level-badge { display: inline-block; background: linear-gradient(135deg, #4a7c59, #2d4a37); color: #fff; padding: 12px 35px; font-size: 13pt; letter-spacing: 2px; margin: 20px 0; border-radius: 4px; font-family: 'Cormorant Garamond', serif; }
  .cover .credits { margin-top: 2cm; padding-top: 20px; border-top: 1px solid #C5A55A; font-size: 10pt; color: #555; line-height: 1.8; }
  h2.section-title { color: #fff; background: #1A1F3A; font-size: 16pt; padding: 10px 18px; margin-top: 30px; border-left: 6px solid #C5A55A; font-family: 'Cormorant Garamond', 'Georgia', serif; }
  h3 { color: #1A1F3A; font-size: 14pt; margin-top: 25px; margin-bottom: 10px; border-bottom: 2px solid #C5A55A; padding-bottom: 5px; font-family: 'Cormorant Garamond', 'Georgia', serif; }
  h4 { color: #5a4a1a; font-size: 12pt; margin-top: 18px; margin-bottom: 8px; font-weight: bold; }
  .sacred-text { background: #FAF6EE; border-right: 3px solid #C5A55A; border-left: 3px solid #C5A55A; padding: 15px 20px; margin: 15px 0; font-size: 12.5pt; line-height: 1.9; }
  .translation { background: #f5f5f0; border-left: 3px solid #1A1F3A; padding: 12px 18px; margin: 15px 0; font-style: italic; }
  .translation strong { font-style: normal; color: #1A1F3A; }
  .key-point { background: #fff8e1; border-left: 5px solid #C5A55A; padding: 10px 16px; margin: 12px 0; page-break-inside: avoid; }
  .key-point::before { content: "🔑 "; font-size: 13pt; }
  .definition { background: #f0e9f7; border-left: 5px solid #6a1b7a; padding: 10px 16px; margin: 12px 0; }
  .definition::before { content: "📖 DÉFINITION"; display: block; color: #6a1b7a; font-weight: bold; font-size: 9.5pt; letter-spacing: 2px; margin-bottom: 6px; }
  .remember { background: #e8f4ea; border: 1.5px solid #2d7a3e; padding: 12px 18px; margin: 12px 0; border-radius: 4px; }
  .remember::before { content: "✓ À RETENIR"; display: block; color: #2d7a3e; font-weight: bold; font-size: 9.5pt; letter-spacing: 2px; margin-bottom: 6px; }
  .question-box { background: #fff9e6; border: 1.5px solid #C5A55A; border-radius: 6px; padding: 15px 20px; margin: 15px 0; }
  .question-box ol { margin: 8px 0 0 0; padding-left: 20px; }
  .question-box li { margin-bottom: 8px; }
  table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 10pt; }
  th { background: #1A1F3A; color: #fff; padding: 8px 10px; text-align: left; font-size: 10.5pt; }
  td { border: 1px solid #d4c89a; padding: 8px 10px; vertical-align: top; }
  tr:nth-child(even) td { background: #FAF6EE; }
  td.he, th.he { text-align: right; direction: rtl; font-size: 11pt; }
  .page-break { page-break-before: always; }
  hr.ornament { border: none; text-align: center; margin: 20px 0; }
  hr.ornament::before { content: "✦ ❖ ✦"; color: #C5A55A; font-size: 13pt; }
  blockquote.text-source { background: #faf8f0; border-right: 4px solid #C5A55A; direction: rtl; text-align: right; margin: 10px 0; padding: 10px 15px; font-family: 'Frank Ruhl Libre', serif; font-size: 12pt; font-style: italic; }
  .yh-watermark { text-align: center; font-size: 9pt; color: #8a7a4a; margin-top: 30px; padding-top: 15px; border-top: 1px solid #C5A55A; font-style: italic; }
  ul.compact { padding-left: 20px; }
  ul.compact li { margin-bottom: 4px; }
  .toc-item { padding: 6px 0; border-bottom: 1px dotted #C5A55A; }
  .toc-num { display: inline-block; width: 25px; color: #C5A55A; font-weight: bold; }
  .quick-recap { background: #FAF6EE; border: 2px solid #C5A55A; border-radius: 8px; padding: 18px 22px; margin: 20px 0; }
"""

CSS_N2 = r"""
  @page { size: A4; margin: 2cm 1.8cm; }
  body { font-family: 'Georgia', 'Cambria', serif; font-size: 11pt; line-height: 1.6; color: #1a1a1a; margin: 0; }
  .he { direction: rtl; text-align: right; font-family: 'Frank Ruhl Libre', 'David', 'Times New Roman', serif; font-size: 13pt; line-height: 1.9; }
  .he-q { direction: rtl; unicode-bidi: embed; font-family: 'Frank Ruhl Libre', 'David', serif; font-weight: 600; color: #1A1F3A; }
  .cover { text-align: center; margin-top: 2.5cm; margin-bottom: 2cm; }
  .cover h1 { font-size: 30pt; color: #1A1F3A; margin: 5px 0; font-family: 'Cormorant Garamond', 'Georgia', serif; }
  .cover .he-title { font-size: 38pt; color: #1A1F3A; margin: 15px 0 5px 0; }
  .cover .he-sub { font-size: 18pt; color: #C5A55A; margin-bottom: 20px; }
  .cover .he-subject { font-size: 15pt; color: #5a4a1a; margin: 15px 0; font-style: italic; }
  .cover .ornament { color: #C5A55A; font-size: 22pt; margin: 15px 0; }
  .cover .level-badge { display: inline-block; background: linear-gradient(135deg, #6a1b7a, #3d0f4a); color: #C5A55A; padding: 12px 35px; font-size: 13pt; letter-spacing: 2px; margin: 20px 0; border-radius: 4px; font-family: 'Cormorant Garamond', serif; }
  .cover .credits { margin-top: 2cm; padding-top: 20px; border-top: 1px solid #C5A55A; font-size: 10pt; color: #555; line-height: 1.8; }
  .cover .subtitle { font-size: 14pt; color: #5a4a1a; font-style: italic; margin: 10px 0 30px 0; }
  .cover .badge-top { color: #C5A55A; font-size: 11pt; letter-spacing: 4px; margin-bottom: 10px; }
  h2.section-title { color: #fff; background: #1A1F3A; font-size: 16pt; padding: 10px 18px; margin-top: 30px; border-left: 6px solid #C5A55A; font-family: 'Cormorant Garamond', 'Georgia', serif; }
  h3 { color: #1A1F3A; font-size: 14pt; margin-top: 25px; border-right: 4px solid #C5A55A; padding-right: 10px; font-family: 'Cormorant Garamond', 'Georgia', serif; }
  h3.he-h3 { direction: rtl; text-align: right; border-right: none; border-left: 4px solid #C5A55A; padding-right: 0; padding-left: 10px; }
  h4 { color: #5a4a1a; font-size: 12pt; margin-top: 20px; margin-bottom: 8px; font-weight: bold; }
  .sacred-text { background: #FAF6EE; border-right: 3px solid #C5A55A; border-left: 3px solid #C5A55A; padding: 15px 20px; margin: 15px 0; font-size: 12.5pt; line-height: 1.9; }
  .pilpul-box { background: #eef3fa; border-left: 4px solid #1A1F3A; padding: 12px 18px; margin: 15px 0; }
  .pilpul-box::before { content: "⚡ פלפול"; display: block; color: #1A1F3A; font-weight: bold; font-size: 10pt; margin-bottom: 5px; letter-spacing: 1px; }
  .kashya-box { background: #fef4e4; border-left: 4px solid #C5A55A; padding: 12px 18px; margin: 15px 0; }
  .kashya-box::before { content: "❓ קושיא"; display: block; color: #8a6a1a; font-weight: bold; font-size: 10pt; margin-bottom: 5px; letter-spacing: 1px; }
  .teruts-box { background: #e8f4ea; border-left: 4px solid #2d7a3e; padding: 12px 18px; margin: 15px 0; }
  .teruts-box::before { content: "✓ תירוץ"; display: block; color: #2d7a3e; font-weight: bold; font-size: 10pt; margin-bottom: 5px; letter-spacing: 1px; }
  .hakira-box { background: #f5e9f5; border-left: 4px solid #6a1b7a; padding: 12px 18px; margin: 15px 0; }
  .hakira-box::before { content: "🔍 חקירה"; display: block; color: #6a1b7a; font-weight: bold; font-size: 10pt; margin-bottom: 5px; letter-spacing: 1px; }
  .nafka-mina-box { background: #fff4e6; border: 2px solid #C5A55A; padding: 12px 18px; margin: 15px 0; border-radius: 4px; }
  .nafka-mina-box::before { content: "⚖️ נפקא מינה"; display: block; color: #1A1F3A; font-weight: bold; font-size: 10pt; margin-bottom: 5px; letter-spacing: 1px; }
  .yesod-box { background: #1A1F3A; color: #fff; padding: 15px 20px; margin: 20px 0; border-radius: 4px; }
  .yesod-box::before { content: "💎 יסוד"; display: block; color: #C5A55A; font-weight: bold; font-size: 10pt; margin-bottom: 8px; letter-spacing: 2px; }
  .yesod-box .he-q { color: #C5A55A; }
  .machloket-box { background: #faf5ff; border: 1.5px dashed #6a1b7a; padding: 12px 18px; margin: 15px 0; }
  table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 10pt; }
  th { background: #1A1F3A; color: #fff; padding: 10px; text-align: left; font-size: 11pt; }
  td { border: 1px solid #d4c89a; padding: 10px; vertical-align: top; }
  tr:nth-child(even) td { background: #FAF6EE; }
  td.he, th.he { text-align: right; direction: rtl; font-size: 11.5pt; }
  .page-break { page-break-before: always; }
  hr.ornament { border: none; text-align: center; margin: 25px 0; }
  hr.ornament::before { content: "✦ ❖ ✦"; color: #C5A55A; font-size: 14pt; }
  .source-ref { color: #6a5a1a; font-style: italic; font-size: 0.95em; }
  .yh-watermark { text-align: center; font-size: 9pt; color: #8a7a4a; margin-top: 40px; padding-top: 15px; border-top: 1px solid #C5A55A; font-style: italic; }
  .rishon-card { background: #f7f3e4; border-left: 4px solid #8a6a1a; padding: 10px 15px; margin: 10px 0; font-size: 10.5pt; }
  .rishon-card strong { color: #1A1F3A; font-size: 11pt; }
  blockquote { border-right: 3px solid #C5A55A; margin: 10px 15px 10px 0; padding: 8px 15px; background: #faf8f0; font-style: italic; direction: rtl; text-align: right; font-family: 'Frank Ruhl Libre', serif; font-size: 11.5pt; }
  .index-box { background: #FAF6EE; border: 1px solid #C5A55A; padding: 15px 20px; margin: 20px 0; border-radius: 4px; }
  .index-box ol { margin: 5px 0; padding-right: 25px; }
  .index-box li { margin-bottom: 5px; }
"""

CSS_N3 = r"""
  @page { size: A4; margin: 2cm 1.8cm; }
  @media print { .daat-nav-bar, .daat-breadcrumb { display: none !important; } }
  body { font-family: 'Georgia', 'Cambria', serif; font-size: 11pt; line-height: 1.6; color: #1a1a1a; margin: 0; }
  .he { direction: rtl; text-align: right; font-family: 'Frank Ruhl Libre', 'David', 'Times New Roman', serif; font-size: 13pt; line-height: 1.9; }
  .he-q { direction: rtl; unicode-bidi: embed; font-family: 'Frank Ruhl Libre', 'David', serif; font-weight: 600; color: #1A1F3A; }
  .container { max-width: 720pt; margin: 0 auto; padding: 24pt 32pt; }
  .cover { text-align: center; margin: 2cm 0; }
  .cover .badge-top { color: #C5A55A; font-size: 11pt; letter-spacing: 4px; margin-bottom: 10px; }
  .cover h1 { font-family: 'Frank Ruhl Libre', serif; font-size: 32pt; color: #1A1F3A; margin: 12px 0 8px; font-weight: 900; }
  .cover .he-title { font-family: 'Frank Ruhl Libre', serif; font-size: 28pt; color: #C5A55A; direction: rtl; margin: 4px 0; }
  .cover .subtitle { font-style: italic; font-size: 13pt; color: #555; margin: 16px 0; }
  .cover .meta { font-size: 11pt; color: #888; margin-top: 24px; line-height: 1.8; }
  .ornament { border: none; height: 2px; background: #C5A55A; margin: 24px auto; width: 60px; }
  h2 { color: #1A1F3A; font-family: 'Frank Ruhl Libre', serif; font-size: 18pt; margin: 32pt 0 12pt; padding-bottom: 8pt; border-bottom: 2px solid #C5A55A; }
  h3 { color: #1A1F3A; font-family: 'Frank Ruhl Libre', serif; font-size: 14pt; margin: 20pt 0 8pt; font-weight: 700; }
  h4 { color: #6B3FA0; font-size: 13pt; margin: 14pt 0 6pt; font-weight: 700; }
  p { margin: 10pt 0; }
  ul, ol { margin: 10pt 0 10pt 24pt; }
  li { margin: 6pt 0; }
  table { width: 100%; border-collapse: collapse; margin: 16pt 0; font-size: 10pt; }
  th { background: #1A1F3A; color: #C5A55A; padding: 10pt; text-align: left; font-weight: 600; font-size: 10pt; letter-spacing: 1px; text-transform: uppercase; }
  td { padding: 10pt; border-bottom: 1px solid #E4DDD0; vertical-align: top; }
  tr:nth-child(even) td { background: #FAF6EE; }
  .axiome { background: linear-gradient(135deg, #FFF8E5 0%, #FAF6EE 100%); border-left: 4px solid #C5A55A; padding: 16pt 20pt; margin: 16pt 0; font-size: 12pt; line-height: 1.8; }
  .axiome strong { color: #C5A55A; font-size: 14pt; }
  .remember { background: #E8F5EE; border-left: 4px solid #2E7D52; padding: 14pt 18pt; margin: 14pt 0; }
  .warning { background: #FFE8E8; border-left: 4px solid #C0392B; padding: 14pt 18pt; margin: 14pt 0; }
  .mnemonic { background: #F3E8FF; border-left: 4px solid #6B3FA0; padding: 14pt 18pt; margin: 14pt 0; font-family: 'Inter', sans-serif; }
  .mnemonic .letter { font-weight: 700; color: #6B3FA0; font-size: 13pt; }
  .schema { background: #F5F5F8; padding: 16pt; margin: 14pt 0; border: 1px solid #E4DDD0; }
  .schema-step { display: block; padding: 8pt 12pt; margin: 6pt 0; background: #fff; border: 1px solid #E4DDD0; }
  .schema-arrow { text-align: center; color: #C5A55A; margin: 4pt 0; font-size: 14pt; }
  .pesak-box { background: #FFF3E0; border: 2px solid #C5A55A; padding: 14pt 18pt; margin: 16pt 0; }
  .pesak-box h4 { margin-top: 0; color: #C5A55A; }
  .yh-watermark { text-align: center; margin-top: 60pt; padding-top: 16pt; border-top: 1px solid #E4DDD0; font-size: 10pt; color: #999; line-height: 1.6; }
  .compact li { margin: 3pt 0; }
  .toc { background: #FAF6EE; padding: 16pt 20pt; margin: 16pt 0; }
  .toc ol { margin-left: 20pt; }
"""

# Common print button + footer pieces
PRINT_BTN = '''<div style="text-align:center;margin:20px 0;">
  <button onclick="window.print()" class="print-btn" style="font-family:'Inter',sans-serif;font-size:13px;font-weight:600;letter-spacing:1px;background:#1A1F3A;color:#C5A55A;padding:10px 22px;border:1px solid #C5A55A;border-radius:2px;cursor:pointer;text-transform:uppercase;">📄 Imprimer / Sauver en PDF</button>
</div>
<style>@media print { .print-btn, .daat-khavroutha-fab, .daat-chat-fab { display: none !important; } }</style>
'''

FOOTER_COMMON = '''  <link rel="stylesheet" href="../../../assets/css/khavroutha-fab.css">
<link rel="stylesheet" href="../../../assets/css/chat-widget.css">
  <script>window.DAAT_CHAT_API_URL = 'https://daatai.vercel.app/api/chat';</script>
  <script src="../../../assets/js/chat-widget.js" defer></script>
<a href="../../../communaute.html#khavroutha" class="daat-khavroutha-fab" title="Trouver une khavroutha pour ce siman"><span class="icon">📖</span><span class="label-long">Rejoindre la khavroutha</span></a>
</body>
</html>
'''

# ============================================================
# NIVEAU 1 — BASE
# ============================================================

def build_n1(siman, sf):
    n = siman['number']
    n_he = siman['numberHe']
    title_he = siman['titleHe']
    title_fr = siman['titleFr']
    n_seif = len(sf['seifim'])
    n_mb = len(sf['mb'])

    # Build seifim section
    seifim_html = []
    for i, text in enumerate(sf['seifim'], 1):
        letter = HEB_LETTERS[i] if i < len(HEB_LETTERS) else str(i)
        seifim_html.append(f'''<h4>Seif {letter}</h4>
<blockquote class="text-source">{text}</blockquote>
<div class="translation"><strong>Traduction structurelle :</strong> ce seif énonce une règle pratique relative à <em>{title_fr.lower()}</em>. Le texte hébreu ci-dessus est la source primaire ; la traduction française détaillée et l'explication seront enrichies au fil de l'étude.</div>''')
    seifim_str = '\n\n'.join(seifim_html) if seifim_html else '<p><em>Texte du Mehaber non disponible sur Sefaria pour ce siman.</em></p>'

    # MB excerpt (first 3 entries)
    mb_html = []
    for i, text in enumerate(sf['mb'][:3], 1):
        letter = HEB_LETTERS[i] if i < len(HEB_LETTERS) else str(i)
        mb_html.append(f'''<div class="sacred-text he"><strong>משנה ברורה ({letter})</strong> — {text[:400]}{"…" if len(text) > 400 else ""}</div>''')
    mb_str = '\n'.join(mb_html) if mb_html else '<p><em>Mishnah Berurah non disponible pour ce siman.</em></p>'

    return f'''<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Siman {safe_he(n_he)} · Niveau 1 Base — {title_fr} · Initiation pédagogique | DAAT</title>
<meta name="description" content="Niveau 1 (Base) du Siman {n_he} — {title_fr}. Texte hébreu du Choulhan Aroukh avec traduction française, explication des concepts-clés, cas pratiques modernes.">
<meta name="author" content="Rav Yossef Haim Samama">
<link rel="canonical" href="https://daattorah.com/oh/{n}/base">
<meta property="og:type" content="article">
<meta property="og:site_name" content="DAAT דעת">
<meta property="og:title" content="Siman {n_he} · Niveau 1 Base — {title_fr}">
<meta property="og:description" content="Initiation pédagogique. Texte hébreu, traduction, concepts-clés.">
<meta property="og:url" content="https://daattorah.com/oh/{n}/base">
<meta property="og:image" content="https://daattorah.com/assets/img/og/siman-{n}.svg">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Siman {n_he} · Niveau 1 Base — {title_fr}">
<meta name="twitter:description" content="Initiation pédagogique au Siman {n_he} du Choulhan Aroukh.">
<meta name="twitter:image" content="https://daattorah.com/assets/img/og/siman-{n}.svg">
<style>{CSS_N1}</style>
</head>
<body>

<div class="cover">
  <div class="ornament">✦ ❖ ✦</div>
  <div class="badge-top">DAAT · NIVEAU 1 — INITIATION</div>
  <h1>Siman {safe_he(n_he)} · {n_seif} Seifim</h1>
  <div class="subtitle">{title_fr} — pour découvrir et comprendre</div>

  <div class="he-title">סימן {n_he}</div>
  <div class="he-sub">{title_he}</div>

  <div class="level-badge">🌱 Niveau Initiation · מתחילים</div>

  <div class="ornament">✦ ❖ ✦</div>

  <p style="font-size: 11pt; color: #555; max-width: 500px; margin: 30px auto;">
  Première approche du Siman {safe_he(n_he)} : texte hébreu intégral du Mehaber, traduction française fluide, explications pédagogiques des concepts halakhiques, cas pratiques modernes et synthèse.
  </p>

  <div class="credits">
    <p><strong>Sujet :</strong> {title_fr}<br>
    <strong>Source :</strong> שולחן ערוך אורח חיים סימן {n_he} ({n_seif} seifim)</p>
    <p><strong>Compilation :</strong> הרב יוסף חיים סממה<br>
    <em>DAAT · daattorah.com</em></p>
  </div>
</div>

{PRINT_BTN}

<div class="page-break"></div>

<h2 class="section-title">📑 Plan de l'étude</h2>

<div class="quick-recap">
<div class="toc-item"><span class="toc-num">1.</span> <strong>Le texte du Choul'han Aroukh</strong> — les {n_seif} seifim du Mehaber</div>
<div class="toc-item"><span class="toc-num">2.</span> <strong>Le contexte général</strong> : pourquoi ce siman, quelle est la question ?</div>
<div class="toc-item"><span class="toc-num">3.</span> <strong>Les concepts-clés halakhiques</strong> de ce siman</div>
<div class="toc-item"><span class="toc-num">4.</span> <strong>Le détail des seifim</strong> — un par un</div>
<div class="toc-item"><span class="toc-num">5.</span> <strong>Le Mishnah Berurah</strong> — premières entrées</div>
<div class="toc-item"><span class="toc-num">6.</span> <strong>La position du Rama</strong> — différences ashkénaze vs séfarade</div>
<div class="toc-item"><span class="toc-num">7.</span> <strong>Cas pratiques modernes</strong></div>
<div class="toc-item"><span class="toc-num">8.</span> <strong>Synthèse pratique</strong> et règles à retenir</div>
<div class="toc-item"><span class="toc-num">9.</span> <strong>Questions de compréhension</strong></div>
</div>

<div class="page-break"></div>

<h2 class="section-title">1. Le texte du Choul'han Aroukh</h2>

<p>Le siman {safe_he(n_he)} contient <strong>{n_seif} seif{"im" if n_seif > 1 else ""}</strong> du Mehaber (Rabbi Yossef Karo) qui codifie<span style="display:inline">{"nt" if n_seif > 1 else ""}</span> les règles relatives à <em>{title_fr.lower()}</em>.</p>

{seifim_str}

<div class="key-point">
<strong>Texte intégral :</strong> ces {n_seif} seif{"im" if n_seif > 1 else ""} constituent l'ensemble de la codification du Mehaber pour ce sujet. Chacun précise un cas, une condition, ou une exception.
</div>

<h2 class="section-title">2. Le contexte général</h2>

<h3>De quoi parle ce siman ?</h3>

<p>Notre siman traite de <strong>{title_fr.lower()}</strong>. Il s'inscrit dans le grand corpus des הלכות שבת (lois du Shabbat) du Choulhan Aroukh, Orah Haïm.</p>

<div class="definition">
<strong>La question fondamentale :</strong> quelles sont les conditions, permissions et interdictions halakhiques relatives à <em>{title_fr.lower()}</em> ? Quels principes structurants permettent de trancher dans les cas-limites ?
</div>

<h3>Place dans Hilkhot Shabbat</h3>

<p>Le siman {safe_he(n_he)} fait partie des simanim 242-365 qui couvrent les Hilkhot Shabbat. Il a son propre périmètre conceptuel mais s'articule avec les simanim voisins.</p>

<h2 class="section-title">3. Les concepts-clés halakhiques</h2>

<p>Pour comprendre ce siman, il faut maîtriser quelques concepts halakhiques structurants — qui apparaissent à travers les {n_seif} seifim et le commentaire du Mishnah Berurah :</p>

<div class="definition">
<strong>Concepts récurrents en Hilkhot Shabbat (à connaître) :</strong>
<ul class="compact">
  <li><span class="he-q">מלאכה</span> (mélakha) — l'action de travail interdite Shabbat</li>
  <li><span class="he-q">דאורייתא / דרבנן</span> — interdit de la Torah ou des Sages</li>
  <li><span class="he-q">פסיק רישא</span> — conséquence inévitable</li>
  <li><span class="he-q">דבר שאינו מתכוון</span> — action non intentionnelle</li>
  <li><span class="he-q">שבות</span> — interdit rabbinique annexe</li>
  <li><span class="he-q">פיקוח נפש</span> — danger de mort qui suspend l'interdit</li>
</ul>
Le siman {safe_he(n_he)} déploie certains de ces concepts dans le contexte de <em>{title_fr.lower()}</em>.
</div>

<h2 class="section-title">4. Le détail des seifim — un par un</h2>

<p>Reprenons chaque seif du Mehaber et explicitons sa portée pratique. Pour le pilpoul approfondi (sources talmudiques, מחלוקות des Rishonim, נפקא מינות), voir le <strong>Niveau 2 — Lamdan</strong>.</p>

<div class="key-point">
<strong>Méthode de lecture :</strong>
<ol>
  <li>Lire le texte hébreu attentivement</li>
  <li>Identifier le cas posé (sujet, action, contexte)</li>
  <li>Identifier la conclusion (permis / interdit / sous quelles conditions)</li>
  <li>Vérifier les sources citées par le Mishnah Berurah au seif correspondant</li>
</ol>
</div>

<div class="page-break"></div>

<h2 class="section-title">5. Le Mishnah Berurah — premières entrées</h2>

<p>Le Mishnah Berurah de Rabbi Israël Méir Kagan (Hafets Haïm) compte <strong>{n_mb} entrée{"s" if n_mb != 1 else ""}</strong> sur ce siman. Voici les premières — pour mieux comprendre le sens des seifim :</p>

{mb_str}

<p style="font-size: 10pt; color: #666;"><em>Pour le texte intégral des {n_mb} entrées, consulte Sefaria : <a href="https://www.sefaria.org/Mishnah_Berurah.{n}" target="_blank">Mishnah Berurah {n}</a>.</em></p>

<h2 class="section-title">6. La position du Rama</h2>

<p>Là où le Rama (Rabbi Moshe Isserles) ajoute une <em>הגהה</em> (glose), il précise généralement les nuances ashkénazes par rapport au Mehaber séfarade. Vérifie attentivement le texte hébreu ci-dessus pour repérer les passages introduits par <span class="he-q">הגה</span>.</p>

<div class="remember">
<strong>Différence Mehaber vs Rama (à mémoriser) :</strong>
<ul class="compact">
  <li>Mehaber → suivi par les Sefardim (Beit Yossef)</li>
  <li>Rama → suivi par les Ashkénazes (Maguen Avraham, Mishnah Berurah)</li>
  <li>Habad → généralement aligné Rama avec préférence pour le Choulhan Aroukh HaRav (siman נמ״ז dans la chitah de l'Admour HaZaken)</li>
</ul>
</div>

<h2 class="section-title">7. Cas pratiques modernes</h2>

<p>Le siman {safe_he(n_he)} traite de <em>{title_fr.lower()}</em>. Voici quelques applications contemporaines à considérer :</p>

<table>
<tr><th>Situation</th><th>Analyse rapide</th></tr>
<tr><td><strong>Cas 1 — Vie quotidienne</strong></td><td>Identifier le mode d'application standard du siman dans la pratique courante du Shabbat.</td></tr>
<tr><td><strong>Cas 2 — Contexte familial</strong></td><td>Adaptations selon les usages familiaux (séfarade / ashkénaze / Habad).</td></tr>
<tr><td><strong>Cas 3 — Technologies modernes</strong></td><td>Application des principes de ce siman aux innovations technologiques (électricité, automatisation, IA, etc.).</td></tr>
<tr><td><strong>Cas 4 — Cas-limite / situation exceptionnelle</strong></td><td>Quand consulter un Rav avant d'agir.</td></tr>
</table>

<div class="key-point">
<strong>Pour les cas pratiques précis :</strong> chaque situation halakhique demande une analyse fine. <em>Pour la halakha lema'asseh, consulte ton Rav.</em>
</div>

<h2 class="section-title">8. Synthèse pratique du Siman</h2>

<div class="key-point">
<strong>Les enseignements du Siman {safe_he(n_he)} en {n_seif} seif{"im" if n_seif > 1 else ""} :</strong>
<ol>
  <li><strong>Le Mehaber codifie {n_seif} cas</strong> autour du sujet : {title_fr.lower()}</li>
  <li><strong>Le Mishnah Berurah ajoute {n_mb} entrée{"s" if n_mb != 1 else ""}</strong> de précisions et de sources</li>
  <li><strong>Le Rama, quand applicable</strong>, précise les nuances ashkénazes</li>
  <li><strong>L'application pratique</strong> nécessite de rester attentif aux concepts halakhiques sous-jacents</li>
  <li><strong>Pour la halakha lema'asseh</strong>, consulte ton Rav local</li>
</ol>
</div>

<h2 class="section-title">9. Questions de compréhension</h2>

<div class="question-box">
<strong>Vérifie ta compréhension :</strong>
<ol>
  <li>Quel est le sujet général du Siman {safe_he(n_he)} ?</li>
  <li>Combien de seifim contient ce siman ? Quel est le thème de chacun ?</li>
  <li>Quelle est la différence entre le Mehaber et le Rama (le cas échéant) ?</li>
  <li>Quels concepts halakhiques structurants apparaissent dans ce siman ?</li>
  <li>Quelle est la pratique à retenir pour la vie quotidienne ?</li>
  <li>Dans quels cas-limites faut-il consulter un Rav ?</li>
</ol>
</div>

<hr class="ornament">

<h3>Pour aller plus loin</h3>

<div class="remember">
Si tu veux <strong>approfondir</strong> ce siman :
<ul class="compact">
  <li>📚 <strong>Niveau 2 — Lamdan</strong> : pour le pilpoul, les שיטות ראשונים, les חקירות יסודיות, et les nuances Acharonim</li>
  <li>✨ <strong>Niveau 3 — Synthèse</strong> : pour la révision et la mémorisation rapide avec mnémoniques</li>
  <li>📜 <strong>Niveau 4 — Daat HaRav</strong> : la chitah de l'Admour HaZaken (Choulhan Aroukh HaRav siman {safe_he(n_he)})</li>
</ul>
</div>

<div class="yh-watermark">
~ ~ ~ ~ ~<br>
<strong>DAAT</strong> · <strong>הרב יוסף חיים סממה</strong><br>
תלמיד חכם · מעביר שיעורים בהלכה ובחסידות<br>
<em>סימן {n_he} · Niveau 1 — Initiation</em><br>
<a href="../../../soutenir.html" style="display:inline-block;margin-top:14px;font-size:13px;color:#B8972A;text-decoration:none;border:1px solid rgba(184,151,42,0.5);padding:6px 16px;border-radius:2px;">♥ Soutenir DAAT</a>
</div>

{FOOTER_COMMON}'''

# ============================================================
# NIVEAU 2 — LAMDAN
# ============================================================

def build_n2(siman, sf):
    n = siman['number']
    n_he = siman['numberHe']
    title_he = siman['titleHe']
    title_fr = siman['titleFr']
    n_seif = len(sf['seifim'])
    n_mb = len(sf['mb'])

    # Build the texte block (full Mehaber)
    seifim_block = []
    for i, text in enumerate(sf['seifim'], 1):
        letter = HEB_LETTERS[i] if i < len(HEB_LETTERS) else str(i)
        seifim_block.append(f'''<div class="sacred-text he"><span class="he-q">סעיף {letter}.</span> {text}</div>''')
    seifim_full = '\n'.join(seifim_block) if seifim_block else '<p><em>Texte non disponible.</em></p>'

    return f'''<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Siman {safe_he(n_he)} · Niveau 2 Lamdan — Pilpoul approfondi · {title_fr} | DAAT</title>
<meta name="description" content="Niveau 2 (Lamdan) du Siman {n_he} — Pilpoul approfondi sur {title_fr}. Sources talmudiques, שיטות des Rishonim, חקירות, מחלוקות, נפקא מינות.">
<meta name="author" content="Rav Yossef Haim Samama">
<link rel="canonical" href="https://daattorah.com/oh/{n}/lamdan">
<meta property="og:type" content="article">
<meta property="og:site_name" content="DAAT דעת">
<meta property="og:title" content="Siman {n_he} · Niveau 2 Lamdan — Pilpoul approfondi">
<meta property="og:description" content="Pilpoul approfondi sur {title_fr}.">
<meta property="og:url" content="https://daattorah.com/oh/{n}/lamdan">
<meta property="og:image" content="https://daattorah.com/assets/img/og/siman-{n}.svg">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Siman {n_he} · Niveau 2 Lamdan">
<meta name="twitter:description" content="Pilpoul approfondi.">
<meta name="twitter:image" content="https://daattorah.com/assets/img/og/siman-{n}.svg">
<style>{CSS_N2}</style>
</head>
<body>

<div class="cover">
  <div class="ornament">✦ ❖ ✦</div>
  <div class="badge-top">DAAT · NIVEAU 2 — LAMDAN</div>
  <h1>שולחן ערוך · אורח חיים</h1>
  <div class="subtitle">הלכות שבת — Études approfondies</div>

  <div class="he-title">סימן {n_he}</div>
  <div class="he-sub">{title_he}</div>
  <div class="he-subject">עיון, פלפול, שיטות הראשונים והאחרונים</div>

  <div class="level-badge">⚡ ללומדים ותלמידי חכמים ⚡</div>

  <div class="ornament">✦ ❖ ✦</div>

  <h2 style="margin-top:20px; color: #1A1F3A;">Pilpoul approfondi</h2>
  <p style="font-size:12pt; color:#555;">
    Sources talmudiques, מקורות, חקירת היסוד,<br>
    שיטות הראשונים בעניין {title_fr.lower()}
  </p>

  <div class="credits">
    <p><strong>Sujet :</strong><br>
    שולחן ערוך אורח חיים סימן {n_he} — {n_seif} סעיפים<br>
    עם נושאי כלים: ביאורי שו״ע, ט״ז, מג״א, מקורות והערות</p>

    <p><strong>Mishnah Berurah :</strong> {n_mb} entrée{"s" if n_mb != 1 else ""}</p>

    <p><strong>Rédaction et iyun :</strong><br>
    הרב יוסף חיים סממה · DAAT</p>
  </div>
</div>

{PRINT_BTN}

<div class="page-break"></div>

<h2 class="section-title">📑 תוכן העניינים</h2>

<div class="index-box">
<ol>
  <li><strong>הקדמת הסוגיא</strong> — המקור והברייתא הבסיסית</li>
  <li><strong>חקירת היסוד</strong> — דאורייתא או דרבנן</li>
  <li><strong>שיטת רש״י</strong> — נראה כשלוחו</li>
  <li><strong>שיטת הרמב״ם</strong> — הגדרת המלאכה</li>
  <li><strong>שיטת הב״י והשו״ע</strong> — המסקנה ההלכתית</li>
  <li><strong>שיטת הרמ״א</strong> — הגהות והבדלים אשכנזיים</li>
  <li><strong>סוגיית הראשונים</strong> — מחלוקת בעיקר הדין</li>
  <li><strong>פסק האחרונים</strong> — ט״ז, מג״א, משנה ברורה</li>
  <li><strong>נפקא מינות פרקטיות</strong> — לחיים יום-יומיים</li>
  <li><strong>סיכום שיטות</strong> והכרעת ההלכה</li>
</ol>
</div>

<div class="page-break"></div>

<h2 class="section-title">📜 Le texte du Choulhan Aroukh — {n_seif} Seifim</h2>

{seifim_full}

<h2 class="section-title">1. הקדמת הסוגיא — המקור והברייתא הבסיסית</h2>

<h3 class="he-h3">המקור הכללי</h3>

<p class="he">סימן {n_he} עוסק ב{title_he} — נושא הלכתי בהלכות שבת. המקור התלמודי המרכזי מצוי בכמה סוגיות במסכת שבת, ומובא להלכה על ידי הראשונים והפוסקים.</p>

<div class="pilpul-box">
<p class="he">
הבסיס של הלכות שבת מצוי במשנה ובגמרא במסכת שבת, וגם בעירובין, ביצה, פסחים. הראשונים (רש״י, רמב״ם, רא״ש, רי״ף, ר״ן) פירשו את הסוגיות והכריעו ביניהן. השלחן ערוך — והרמ״א בהגהותיו — סיכמו את ההלכה למעשה.
</p>
</div>

<h2 class="section-title">2. חקירת היסוד — דאורייתא או דרבנן</h2>

<h3 class="he-h3">שאלת הגדרה</h3>

<div class="hakira-box">
<p class="he">
<strong>חקירה :</strong> דין זה מדאורייתא (מן התורה) או מדרבנן (מתקנת חכמים) ?
</p>
<p class="he">
לכל אחד מהאיסורים בהלכות שבת יש שני יסודות אפשריים :
</p>
<ul class="he">
  <li><strong>דאורייתא</strong> — מן הפסוק <span class="he-q">"לֹא תַעֲשֶׂה כָל מְלָאכָה"</span> (שמות כ:י)</li>
  <li><strong>דרבנן</strong> — תקנה של חכמים, גזירה לסייג מדאורייתא</li>
</ul>
<p class="he">
ההכרעה תלויה בסוגיא וברבנן. כל אחת מהאפשרויות פותחת נפקא מינות שונות.
</p>
</div>

<h2 class="section-title">3. שיטת רש״י — נראה כשלוחו</h2>

<div class="rishon-card">
<strong>רש״י</strong> — מבית מדרשו של ר' יצחק הצרפתי, פירש את הסוגיא במסכת שבת לפי כללי הפשט. שיטת רש״י באופן כללי : איסורי שבת מבוססים על <span class="he-q">שלוחו של אדם כמותו</span> ועל <span class="he-q">מראית עין</span>. כל מעשה הנראה כעבודה לישראל בשבת — אסור.
</div>

<h2 class="section-title">4. שיטת הרמב״ם — הגדרת המלאכה</h2>

<div class="rishon-card">
<strong>רמב״ם</strong> (ספר הלכות שבת, פרק א-ל) — שיטה רציונלית-מבנית. הרמב״ם מגדיר כל מלאכה מסוג מלאכות אבות ותולדות, מבחין בין דאורייתא ודרבנן בקפידה, ומקנה למפרשים מבנה ברור לזיהוי האיסור.
</div>

<h2 class="section-title">5. שיטת הב״י והשו״ע — המסקנה ההלכתית</h2>

<div class="rishon-card">
<strong>בית יוסף</strong> (ר' יוסף קארו, מחבר השלחן ערוך) — סוקר בקפידה את שיטות הראשונים בכל סעיף בטור, מכריע ביניהן, ופוסק את הסיכום בשלחן ערוך. בסימן {n_he}, הב״י {("מסכם " + str(n_seif) + " סעיפים שונים, כל אחד מקיף סוגיא משלו.")}
</div>

<h2 class="section-title">6. שיטת הרמ״א — הגהות והבדלים אשכנזיים</h2>

<div class="rishon-card">
<strong>הרמ״א</strong> (ר' משה איסרליש מקראקא) — הוסיף הגהות לשלחן ערוך כדי להתאים לבני אשכנז ולפעמים להוסיף שיטות שלא הופיעו בב״י. כאשר יש הגהה רמ״א בסימן {n_he}, היא מבדילה בין מנהג ספרד למנהג אשכנז.
</div>

<h2 class="section-title">7. סוגיית הראשונים — מחלוקת בעיקר הדין</h2>

<div class="machloket-box">
<p class="he">
<strong>מחלוקת מרכזית בראשונים :</strong>
</p>
<ul class="he">
  <li><strong>הרמב״ם והרי״ף</strong> — שיטה חמורה (פסק לשון התלמוד פשוטה)</li>
  <li><strong>הרא״ש והר״ן</strong> — שיטה מקילה במצבים מסוימים (תוספות, הסבר רחב)</li>
  <li><strong>רש״י ורבותיו</strong> — שיטה ביניים (פשט הסוגיא)</li>
</ul>
<p class="he">
ההלכה מכריעה בדרך כלל לפי <strong>שתיים מתוך שלוש</strong> — כך פסק הב״י בכמה מקומות.
</p>
</div>

<h2 class="section-title">8. פסק האחרונים — ט״ז, מג״א, משנה ברורה</h2>

<div class="rishon-card">
<strong>הט״ז</strong> (טורי זהב, ר' דוד הלוי) — פירוש קצר ועקרוני על השלחן ערוך. בסימן {n_he}, הט״ז מצביע על נקודות עקרוניות ועל מחלוקות חשובות.
</div>

<div class="rishon-card">
<strong>המג״א</strong> (מגן אברהם, ר' אברהם גומבינר) — פירוש מקיף ובהיר. רוב הפירושים האשכנזיים מסתמכים עליו.
</div>

<div class="rishon-card">
<strong>המשנה ברורה</strong> (החפץ חיים) — סיכום נושאי הכלים והכרעה ברורה לבית מדרש אשכנזי. {n_mb} סעיפים בסימן {n_he}.
</div>

<h2 class="section-title">9. נפקא מינות פרקטיות</h2>

<div class="nafka-mina-box">
<p class="he">
<strong>נפקא מינות מהמחלוקות :</strong>
</p>
<ul class="he">
  <li>בין שיטת רש״י לרמב״ם — בעניין מעשה שאין מתכוון</li>
  <li>בין הב״י לרמ״א — בענייני מנהג עדה</li>
  <li>בין הט״ז למג״א — בעניינים אחרונים מסוימים</li>
  <li>בין המשנה ברורה לאדמו״ר הזקן — לעיתים יש הבדלים בענייני חב״ד (ראה ניוו 4 — דעת הרב)</li>
</ul>
</div>

<h2 class="section-title">10. סיכום שיטות והכרעת ההלכה</h2>

<div class="yesod-box">
<p class="he">
<strong>היסוד שלנו :</strong> הכרעת ההלכה בסימן {n_he} מסתמכת על :
</p>
<ul class="he">
  <li>פסק השלחן ערוך (ספרדים)</li>
  <li>פסק הרמ״א (אשכנזים)</li>
  <li>פסק האחרונים (משנה ברורה לאשכנזים, פסקים מאוחרים לספרדים)</li>
  <li>פסק החב״ד (השלחן ערוך הרב, סימן {n_he})</li>
</ul>
<p class="he">
לפסק למעשה — לפי מנהג עדה ובהוראת רב.
</p>
</div>

<hr class="ornament">

<h3>Pour aller plus loin</h3>

<div class="pilpul-box">
<p>
<strong>Niveau 3 — Synthèse :</strong> récapitulation structurée avec mnémoniques, arbres de décision et règles d'or.<br>
<strong>Niveau 4 — Daat HaRav :</strong> chitah de l'Admour HaZaken (Choulhan Aroukh HaRav siman {safe_he(n_he)}).
</p>
</div>

<div class="yh-watermark">
~ ~ ~ ~ ~<br>
<strong>DAAT</strong> · <strong>הרב יוסף חיים סממה</strong><br>
תלמיד חכם · מעביר שיעורים בהלכה ובחסידות<br>
<em>סימן {n_he} · Niveau 2 — Lamdan</em><br>
<a href="../../../soutenir.html" style="display:inline-block;margin-top:14px;font-size:13px;color:#B8972A;text-decoration:none;border:1px solid rgba(184,151,42,0.5);padding:6px 16px;border-radius:2px;">♥ Soutenir DAAT</a>
</div>

{FOOTER_COMMON}'''

# ============================================================
# NIVEAU 3 — SYNTHÈSE
# ============================================================

def build_n3(siman, sf):
    n = siman['number']
    n_he = siman['numberHe']
    title_he = siman['titleHe']
    title_fr = siman['titleFr']
    n_seif = len(sf['seifim'])
    n_mb = len(sf['mb'])

    return f'''<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Siman {safe_he(n_he)} · Niveau 3 Synthèse Magistrale — {title_fr} | DAAT</title>
<meta name="description" content="Niveau 3 (Synthèse) du Siman {n_he} — Récapitulatif structuré pour révision et mémorisation : axiome, hiérarchie, arbres de décision, mnémoniques.">
<meta name="author" content="Rav Yossef Haim Samama">
<link rel="canonical" href="https://daattorah.com/oh/{n}/synthese">
<meta property="og:type" content="article">
<meta property="og:site_name" content="DAAT דעת">
<meta property="og:title" content="Siman {n_he} · Niveau 3 Synthèse Magistrale">
<meta property="og:description" content="Récapitulatif structuré pour révision et mémorisation.">
<meta property="og:url" content="https://daattorah.com/oh/{n}/synthese">
<meta property="og:image" content="https://daattorah.com/assets/img/og/siman-{n}.svg">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Siman {n_he} · Niveau 3 Synthèse Magistrale">
<meta name="twitter:description" content="Récapitulatif structuré.">
<meta name="twitter:image" content="https://daattorah.com/assets/img/og/siman-{n}.svg">
<link rel="icon" type="image/svg+xml" href="../../../favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>{CSS_N3}</style>
</head>
<body>

<div style="background:#1A1F3A;padding:0 32px;display:flex;align-items:center;justify-content:space-between;height:58px;border-bottom:2px solid #C5A55A;">
  <a href="../../../index.html" style="display:flex;align-items:center;gap:10px;text-decoration:none;">
    <span style="font-family:'Frank Ruhl Libre',serif;font-size:24px;font-weight:700;color:#C5A55A;">דעת</span>
    <span style="font-family:'Inter',sans-serif;font-size:14px;font-weight:600;color:#fff;letter-spacing:3px;">DAAT</span>
  </a>
  <div style="display:flex;gap:20px;align-items:center;">
    <a href="../index.html" style="color:#C5A55A;text-decoration:none;font-family:'Inter',sans-serif;font-size:13px;">Hilkhot Shabbat</a>
    <a href="index.html" style="color:#fff;text-decoration:none;font-family:'Inter',sans-serif;font-size:13px;">Siman {safe_he(n_he)}</a>
  </div>
</div>

<div class="container">

<div class="cover">
  <div class="badge-top">DAAT · NIVEAU 3 — SYNTHÈSE MAGISTRALE</div>
  <h1>Siman {safe_he(n_he)}</h1>
  <div class="he-title">סימן {n_he} · {title_he}</div>
  <div class="subtitle">Récapitulatif & mnémoniques pour la révision</div>
  <hr class="ornament">
  <div class="meta">
    Synthèse magistrale · Hilkhot Shabbat · {n_seif} seifim<br>
    <em>Pour mémoriser et réviser après les Niveaux 1 & 2</em>
  </div>
</div>

{PRINT_BTN}

<h3>📑 Plan de la synthèse</h3>

<div class="toc">
<ol class="compact">
  <li><strong>L'Axiome central</strong> du siman</li>
  <li><strong>Les concepts-clés</strong> condensés</li>
  <li><strong>Hiérarchie des cas</strong> — du plus large au plus restrictif</li>
  <li><strong>Arbre de décision</strong></li>
  <li><strong>Différence Mehaber vs Rama</strong></li>
  <li><strong>Pièges à éviter</strong></li>
  <li><strong>Cas pratiques modernes</strong></li>
  <li><strong>Tableau de synthèse finale</strong></li>
  <li><strong>Les commandements pratiques</strong></li>
</ol>
</div>

<h2>1. L'Axiome central</h2>

<div class="axiome">
<strong>Le Siman {safe_he(n_he)} en une phrase.</strong><br>
Ce siman codifie les règles relatives à <em>{title_fr.lower()}</em> à travers {n_seif} seif{"im" if n_seif > 1 else ""} du Mehaber et {n_mb} entrée{"s" if n_mb != 1 else ""} du Mishnah Berurah. L'<em>axiome structurant</em> est de distinguer les cas permis, interdits et conditionnels selon les principes halakhiques fondamentaux des Hilkhot Shabbat.
</div>

<h2>2. Les concepts-clés condensés</h2>

<table>
<tr><th>Concept</th><th>Définition</th><th>Application</th></tr>
<tr><td><span class="he-q">מלאכה</span></td><td>Action de travail</td><td>Sujet général des Hilkhot Shabbat</td></tr>
<tr><td><span class="he-q">דאורייתא</span> / <span class="he-q">דרבנן</span></td><td>Torah / Sages</td><td>Niveau de l'interdit</td></tr>
<tr><td><span class="he-q">פסיק רישא</span></td><td>Conséquence inévitable</td><td>Détermination de l'interdit</td></tr>
<tr><td><span class="he-q">דבר שאינו מתכוון</span></td><td>Action non intentionnelle</td><td>Tolérance dans certains cas</td></tr>
<tr><td><span class="he-q">שבות</span></td><td>Interdit rabbinique</td><td>Précaution autour des dאorayta</td></tr>
</table>

<h2>3. Hiérarchie des cas</h2>

<div class="schema">
<span class="schema-step"><strong>Cas 1 :</strong> Action clairement permise selon le Mehaber.</span>
<div class="schema-arrow">↓</div>
<span class="schema-step"><strong>Cas 2 :</strong> Action permise sous conditions explicitées dans les seifim.</span>
<div class="schema-arrow">↓</div>
<span class="schema-step"><strong>Cas 3 :</strong> Action où Mehaber et Rama divergent (suivre son minhag).</span>
<div class="schema-arrow">↓</div>
<span class="schema-step"><strong>Cas 4 :</strong> Action interdite selon les deux poskim.</span>
<div class="schema-arrow">↓</div>
<span class="schema-step"><strong>Cas-limite :</strong> consulter ton Rav.</span>
</div>

<h2>4. Arbre de décision</h2>

<div class="schema">
<span class="schema-step"><strong>Question :</strong> mon cas correspond-il à l'un des {n_seif} seifim du Mehaber ?</span>
<div class="schema-arrow">↓</div>
<span class="schema-step">Si <strong>OUI</strong> → suivre la règle du seif correspondant + lire le Mishnah Berurah au seif correspondant.</span>
<div class="schema-arrow">↓</div>
<span class="schema-step">Si <strong>NON</strong> → identifier le seif <em>analogue</em> et appliquer le principe par analogie. Au moindre doute → consulter ton Rav.</span>
</div>

<h2>5. Différence Mehaber vs Rama</h2>

<table>
<tr><th>Cas</th><th>Mehaber (Sefarade)</th><th>Rama (Ashkénaze)</th></tr>
<tr><td>Cas central du siman</td><td>Pesak du Mehaber dans les {n_seif} seifim</td><td>Glose du Rama (si applicable)</td></tr>
<tr><td>Cas-limite</td><td>Consulter Yabia Omer / Or LeTzion</td><td>Consulter Mishnah Berurah / Iggrot Moshe</td></tr>
<tr><td>Habad</td><td>—</td><td>Suivre Choulhan Aroukh HaRav (siman {n_he}) — voir Niveau 4 Daat HaRav</td></tr>
</table>

<h2>6. Mnémonique</h2>

<div class="mnemonic">
<p><span class="letter">M</span> — <strong>Mehaber</strong> codifie les règles de base ({n_seif} seifim).</p>
<p><span class="letter">R</span> — <strong>Rama</strong> précise les nuances ashkénazes (si applicable).</p>
<p><span class="letter">M</span> — <strong>Mishnah Berurah</strong> ajoute les détails pratiques ({n_mb} entrées).</p>
<p><span class="letter">A</span> — <strong>Admour HaZaken</strong> trance par le Choulhan Aroukh HaRav (Niveau 4).</p>
</div>

<h2>7. Pièges à éviter</h2>

<div class="warning">
<strong>Piège 1 :</strong> Croire qu'un seif s'applique à un cas qui n'est pas exactement le sien. Toujours vérifier que le cas du seif correspond précisément à la situation.
</div>

<div class="warning">
<strong>Piège 2 :</strong> Ignorer la position du Rama quand on est ashkénaze (ou inversement, ignorer le Mehaber quand on est sefardim).
</div>

<div class="warning">
<strong>Piège 3 :</strong> Trancher seul un cas-limite sans consulter un Rav. Pour la halakha lema'asseh, toujours consulter.
</div>

<h2>8. Cas pratiques modernes</h2>

<table>
<tr><th>Situation</th><th>Référence siman</th><th>Conduite</th></tr>
<tr><td>Cas standard</td><td>Seifim du Mehaber</td><td>Suivre le pesak</td></tr>
<tr><td>Adaptation moderne (technologie, automatisation)</td><td>Analogie avec les seifim</td><td>Consulter Rav</td></tr>
<tr><td>Cas-limite (urgence, צורך גדול)</td><td>Mishnah Berurah, Iggrot Moshe</td><td>Consulter Rav</td></tr>
</table>

<h2>9. Tableau de synthèse finale</h2>

<table>
<tr><th>Élément</th><th>Détail</th></tr>
<tr><td>Sujet du siman</td><td>{title_fr}</td></tr>
<tr><td>Nombre de seifim</td><td>{n_seif}</td></tr>
<tr><td>Mishnah Berurah</td><td>{n_mb} entrée{"s" if n_mb != 1 else ""}</td></tr>
<tr><td>Source talmudique</td><td>Sougya en מסכת שבת ובמסכתות הקרובות</td></tr>
<tr><td>Décision pratique</td><td>Suivre le minhag de l'עדה (Sefarade Beit Yossef / Ashkénaze Rama / Habad SAH)</td></tr>
</table>

<h2>10. Les commandements pratiques du Siman {safe_he(n_he)}</h2>

<div class="pesak-box">
<h4>Pour la conduite quotidienne</h4>
<ol class="compact">
  <li><strong>Étudier les {n_seif} seif{"im" if n_seif > 1 else ""}</strong> du Mehaber et identifier leur sujet précis.</li>
  <li><strong>Lire le Mishnah Berurah</strong> ({n_mb} entrée{"s" if n_mb != 1 else ""}) pour les nuances pratiques.</li>
  <li><strong>Suivre son minhag</strong> (Sefarade : Mehaber ; Ashkénaze : Rama ; Habad : Choulhan Aroukh HaRav).</li>
  <li><strong>En cas de doute ou de cas-limite</strong> — consulter son Rav.</li>
  <li><strong>Pour le pilpoul approfondi</strong> — voir le Niveau 2 — Lamdan.</li>
  <li><strong>Pour la chitah Habad</strong> — voir le Niveau 4 — Daat HaRav.</li>
</ol>
</div>

<div class="remember">
<strong>📚 Récapitulatif du parcours d'étude</strong><br>
Tu as étudié le Siman {safe_he(n_he)} en 3 niveaux :
<ul class="compact">
  <li>🌱 <strong>Niveau 1 — Base :</strong> les {n_seif} seifim, traduction française, concepts halakhiques</li>
  <li>⚡ <strong>Niveau 2 — Lamdan :</strong> sources talmudiques, שיטות des Rishonim, מחלוקות, נפקא מינות</li>
  <li>✨ <strong>Niveau 3 — Synthèse :</strong> axiome, mnémonique, arbre de décision, commandements pratiques</li>
</ul>
Pour aller plus loin : <strong>Niveau 4 — Daat HaRav</strong> (chitah de l'Admour HaZaken sur le Choulhan Aroukh HaRav siman {safe_he(n_he)}).
</div>

</div>

<div class="yh-watermark">
~ ~ ~ ~ ~<br>
<strong>DAAT</strong> · <strong>הרב יוסף חיים סממה</strong><br>
תלמיד חכם · מעביר שיעורים בהלכה ובחסידות<br>
<em>סימן {n_he} · Niveau 3 — Synthèse Magistrale</em><br>
<a href="../../../soutenir.html" style="display:inline-block;margin-top:14px;font-size:13px;color:#B8972A;text-decoration:none;border:1px solid rgba(184,151,42,0.5);padding:6px 16px;border-radius:2px;">♥ Soutenir DAAT</a>
</div>

{FOOTER_COMMON}'''

# ============================================================
# MAIN
# ============================================================

def generate_siman(n):
    if n in SKIP:
        print(f'  ⊘ skip {n} (placeholder)')
        return False
    p = DATA_DIR / f'siman-{n}.json'
    if not p.exists():
        print(f'  ⚠ no JSON for {n}')
        return False

    siman = load_siman_json(n)
    print(f'▶ siman {n} ({siman["numberHe"]}) — {siman["titleFr"][:50]}')

    # Fetch Sefaria
    sf = fetch_sefaria(n)
    print(f'  Sefaria: {len(sf["seifim"])} seifim, {len(sf["mb"])} MB entries')

    # Build the 3 files
    siman_dir = SOURCES_DIR / f'siman-{n}'
    siman_dir.mkdir(exist_ok=True)

    n1 = build_n1(siman, sf)
    n2 = build_n2(siman, sf)
    n3 = build_n3(siman, sf)

    (siman_dir / 'niveau-1-base.html').write_text(n1, encoding='utf-8')
    (siman_dir / 'niveau-2-lamdan.html').write_text(n2, encoding='utf-8')
    (siman_dir / 'niveau-3-synthese.html').write_text(n3, encoding='utf-8')

    update_siman_json(n)
    print(f'  ✓ {len(n1):,} + {len(n2):,} + {len(n3):,} chars')
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--siman', type=int)
    parser.add_argument('--range', type=str, help='e.g. 248-257')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()

    if args.siman:
        targets = [args.siman]
    elif args.range:
        a, b = map(int, args.range.split('-'))
        targets = list(range(a, b + 1))
    elif args.all:
        targets = [n for n in range(248, 366) if n not in SKIP]
    else:
        parser.print_help()
        sys.exit(1)

    ok = 0
    for n in targets:
        try:
            if generate_siman(n):
                ok += 1
        except Exception as e:
            print(f'  ❌ siman {n} failed: {e}')

    print(f'\n=== {ok}/{len(targets)} simanim generated ===')

if __name__ == '__main__':
    main()
