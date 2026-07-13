#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAAT — Audit ÉTAPE 1 (inventaire) + contrôles techniques/SEO/numérotation.
NE MODIFIE AUCUN FICHIER DU SITE. Écrit uniquement dans audit/.
"""
import os, re, csv, json, html, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
BASE_URL = "https://daattorah.com"

# ---------- Gematria (Hebrew numeral -> int) ----------
GEM = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,
       'י':10,'כ':20,'ך':20,'ל':30,'מ':40,'ם':40,'נ':50,'ן':50,
       'ס':60,'ע':70,'פ':80,'ף':80,'צ':90,'ץ':90,'ק':100,'ר':200,'ש':300,'ת':400}
def gematria(s):
    # strip gershayim/geresh and spaces
    s = s.replace('״','').replace('"','').replace('׳','').replace("'",'').strip()
    if not s: return None
    tot=0
    for ch in s:
        if ch in GEM: tot+=GEM[ch]
        else: return None
    return tot if tot>0 else None

# ---------- vercel routing ----------
vj = json.load(open(ROOT/"vercel.json", encoding="utf-8"))
REWRITES = [(r.get("source"), r.get("destination")) for r in vj.get("rewrites",[])]
REDIRECTS = [(r.get("source"), r.get("destination"), r.get("permanent")) for r in vj.get("redirects",[])]

def rewrite_source_to_regex(src):
    out=[]; i=0
    tok=re.compile(r':(\w+)(\([^)]*\))?(\*)?')
    while i < len(src):
        m=tok.match(src,i)
        if m:
            name,rx,star=m.group(1),m.group(2),m.group(3)
            if rx: out.append(f'(?P<{name}>{rx[1:-1]})')
            elif star: out.append(f'(?P<{name}>.+)')
            else: out.append(f'(?P<{name}>[^/]+)')
            i=m.end()
        else:
            out.append(re.escape(src[i])); i+=1
    return re.compile('^'+''.join(out)+'$')
REWRITE_RX = [(rewrite_source_to_regex(s), d) for s,d in REWRITES if s and d]
REDIRECT_RX = [(rewrite_source_to_regex(s), d) for s,d,_ in REDIRECTS if s and d]

def resolve_url_path(urlpath):
    """Return a filesystem Path the URL maps to, or None if unresolved. urlpath starts with /."""
    # try direct file
    up = urlpath.split('?')[0].split('#')[0]
    if up == '' or up == '/':
        return ROOT/"index.html"
    # redirects first (they take precedence at edge)
    for rx,dest in REDIRECT_RX:
        if rx.match(up):
            # follow one hop
            newp = expand_dest(dest, rx.match(up))
            if newp.startswith('http'): return 'EXTERNAL_REDIRECT'
            return resolve_url_path(newp)
    # rewrites
    for rx,dest in REWRITE_RX:
        m = rx.match(up)
        if m:
            newp = expand_dest(dest, m)
            if newp.startswith('/api'): return 'API'
            fp = ROOT / newp.lstrip('/')
            return fp
    # static file directly
    cand = ROOT / up.lstrip('/')
    if cand.is_dir():
        idx = cand/"index.html"
        return idx
    return cand

def expand_dest(dest, m):
    out = dest
    if m and m.groupdict():
        for k,v in m.groupdict().items():
            out = out.replace(f':{k}*', v).replace(f':{k}', v)
    return out

# ---------- HTML parsing helpers ----------
def read(fp):
    try:
        return fp.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def first(rx, s, grp=1, flags=re.I|re.S):
    m = re.search(rx, s, flags)
    return m.group(grp).strip() if m else ""

def all_matches(rx, s, flags=re.I|re.S):
    return re.findall(rx, s, flags)

# ---------- sitemap membership ----------
smap = read(ROOT/"sitemap.xml")
SITEMAP_URLS = set(re.findall(r'<loc>\s*([^<]+?)\s*</loc>', smap))
smap_llm = read(ROOT/"sitemap-llm.xml")
SITEMAP_LLM_URLS = set(re.findall(r'<loc>\s*([^<]+?)\s*</loc>', smap_llm))

# ---------- classify page ----------
def lang_from_name(name):
    if name.endswith('-en.html'): return 'en'
    if name.endswith('-he.html'): return 'he'
    return 'fr'

NIVEAU_MAP = {
    'niveau-1-base':'1-Base','niveau-2-lamdan':'2-Lamdan',
    'niveau-3-synthese':'3-Synthese','niveau-4-daat-harav':'4-DaatHaRav',
    'index':'Index',
}
def classify(relpath):
    p = relpath.replace('\\','/')
    section='autre'; siman=''; niveau=''
    if p.startswith('sources/shabbat/'): section='shabbat'
    elif p.startswith('sources/orah-haim/'): section='orah-haim'
    elif p.startswith('sources/yoreh-deah/'): section='yoreh-deah'
    elif p.startswith('sources/nida/'): section='nida'
    elif p.startswith('limoud/'): section='limoud'
    elif p.startswith('blog/'): section='blog'
    elif p.startswith('admin/'): section='admin'
    elif p.startswith('auteur/'): section='auteur'
    elif p.startswith('mockup/'): section='mockup'
    elif p.startswith('emails/'): section='emails'
    elif '/' not in p: section='racine'
    m = re.search(r'siman-(\d+)', p)
    if m: siman = m.group(1)
    m = re.search(r'jour-(\d+)', p)
    if m: siman = 'jour-'+m.group(1)
    stem = os.path.basename(p)
    for k,v in NIVEAU_MAP.items():
        if stem.startswith(k):
            niveau=v; break
    return section, siman, niveau

# ---------- build URL for a file (reverse of rewrite, best-effort canonical) ----------
def public_url(relpath, canonical):
    if canonical: return canonical
    return BASE_URL + '/' + relpath

# ---------- MAIN WALK ----------
SKIP_DIRS = {'.git','node_modules','.claude'}
rows=[]
tech_issues=[]   # (id,url,file,line,lang,siman,niveau,type,gravite,texte,probleme,correction)
titles_seen={}
descs_seen={}
canon_seen={}
issue_id=0
def add_issue(url,file,line,lang,siman,niveau,typ,grav,texte,prob,corr,certitude="haute",rav="non"):
    global issue_id
    issue_id+=1
    tech_issues.append({
        'ID':f'T{issue_id:04d}','URL':url,'Fichier':file,'Ligne':line,'Langue':lang,
        'Siman':siman,'Niveau':niveau,'Type':typ,'Gravite':grav,
        'Texte_actuel':texte[:300],'Probleme':prob,'Correction_proposee':corr,
        'Certitude':certitude,'Validation_Rav':rav})

html_files=[]
for dirpath,dirs,files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        if fn.endswith('.html'):
            html_files.append(Path(dirpath)/fn)

for fp in sorted(html_files):
    rel = str(fp.relative_to(ROOT))
    txt = read(fp)
    name = fp.name
    lang = lang_from_name(name)
    section, siman, niveau = classify(rel)
    # extract head
    html_lang = first(r'<html[^>]*\blang="([^"]+)"', txt)
    html_dir  = first(r'<html[^>]*\bdir="([^"]+)"', txt)
    title = html.unescape(first(r'<title[^>]*>(.*?)</title>', txt))
    desc = html.unescape(first(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', txt) or
                         first(r'<meta[^>]+content="([^"]*)"[^>]+name="description"', txt))
    canonical = first(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', txt)
    robots = first(r'<meta[^>]+name="robots"[^>]+content="([^"]*)"', txt)
    h1 = html.unescape(re.sub(r'<[^>]+>','', first(r'<h1[^>]*>(.*?)</h1>', txt))).strip()
    hreflangs = dict(re.findall(r'<link[^>]+rel="alternate"[^>]+hreflang="([^"]+)"[^>]+href="([^"]+)"', txt, re.I))
    # indexable?
    indexable = 'oui'
    if robots and 'noindex' in robots.lower(): indexable='non (noindex)'
    url = public_url(rel, canonical)
    in_sitemap = 'oui' if (canonical in SITEMAP_URLS or (BASE_URL+'/'+rel) in SITEMAP_URLS) else 'non'
    # seif: not represented at page level
    seif=''
    comments=[]

    # ---- Technical checks (skip admin/mockup/emails from strict SEO) ----
    strict = section in ('shabbat','orah-haim','yoreh-deah','nida','limoud','blog','auteur','racine')
    if strict:
        if not title: add_issue(url,rel,'',lang,siman,niveau,'SEO-title-manquant','MOYENNE','','Balise <title> absente','Ajouter un <title>')
        if not desc: add_issue(url,rel,'',lang,siman,niveau,'SEO-desc-manquante','MOYENNE','','meta description absente','Ajouter meta description')
        if not canonical: add_issue(url,rel,'',lang,siman,niveau,'SEO-canonical-manquant','MOYENNE','','canonical absent','Ajouter canonical')
        if not h1: add_issue(url,rel,'',lang,siman,niveau,'A11y-h1-manquant','MOYENNE','','<h1> absent','Ajouter un H1 unique')
        # lang attr consistency
        if html_lang:
            if lang=='fr' and not html_lang.startswith('fr'):
                add_issue(url,rel,'',lang,siman,niveau,'lang-incoherent','IMPORTANTE',html_lang,f'html lang="{html_lang}" mais fichier FR','lang="fr"')
            if lang=='en' and not html_lang.startswith('en'):
                add_issue(url,rel,'',lang,siman,niveau,'lang-incoherent','IMPORTANTE',html_lang,f'html lang="{html_lang}" mais fichier EN','lang="en"')
            if lang=='he' and not html_lang.startswith('he'):
                add_issue(url,rel,'',lang,siman,niveau,'lang-incoherent','IMPORTANTE',html_lang,f'html lang="{html_lang}" mais fichier HE','lang="he"')
        else:
            add_issue(url,rel,'',lang,siman,niveau,'lang-manquant','MOYENNE','','attribut lang absent sur <html>','Ajouter lang')
        # RTL for hebrew
        if lang=='he' and 'rtl' not in (html_dir or '').lower():
            # some pages may set dir on body; check body
            if not re.search(r'dir="rtl"', txt, re.I):
                add_issue(url,rel,'',lang,siman,niveau,'RTL-manquant','IMPORTANTE',html_dir,'Page hébraïque sans dir="rtl"','Ajouter dir="rtl"')
        # hreflang trio
        if section in ('shabbat','orah-haim','yoreh-deah'):
            for hl in ('fr','en','he'):
                if hl not in hreflangs:
                    add_issue(url,rel,'',lang,siman,niveau,'hreflang-manquant','MOYENNE',str(list(hreflangs)),f'hreflang {hl} absent','Compléter les 3 hreflang')
        # dup title / desc / canonical (only within strict, per language grouping key = title text)
        if title:
            titles_seen.setdefault(title,[]).append(rel)
        if desc:
            descs_seen.setdefault(desc,[]).append(rel)
        if canonical:
            canon_seen.setdefault(canonical,[]).append(rel)

        # ---- Numbering check: numeral that FOLLOWS "סימן"/"Siman" in title vs siman number ----
        if siman.isdigit() and section in ('shabbat','orah-haim','yoreh-deah'):
            n=int(siman)
            # Hebrew: token right after סימן  (may be numeral like רמ״ב / ס׳ / א׳)
            mh = re.search(r'סימן\s+([א-ת]{1,4}[״\'׳"]?[א-ת]?)', title)
            if mh:
                tok=mh.group(1); val=gematria(tok)
                if val is not None and val!=n:
                    add_issue(url,rel,'',lang,siman,niveau,'numerotation-titre-he','CRITIQUE',title,
                              f'Titre: après "סימן" -> {tok} (={val}) mais siman URL = {n}',
                              f'Corriger le numéral hébraïque en {n}','haute','oui')
            # Latin: "Siman <num>" arabic
            ml = re.search(r'\bSiman\s+(\d+)', title)
            if ml and int(ml.group(1))!=n:
                add_issue(url,rel,'',lang,siman,niveau,'numerotation-titre','CRITIQUE',title,
                          f'Titre "Siman {ml.group(1)}" mais siman URL = {n}',
                          f'Corriger en Siman {n}','haute','oui')
            # Latin title with hebrew numeral after "Siman"
            mlh = re.search(r'\bSiman\s+([א-ת]{1,4}[״\'׳"]?[א-ת]?)', title)
            if mlh:
                tok=mlh.group(1); val=gematria(tok)
                if val is not None and val!=n:
                    add_issue(url,rel,'',lang,siman,niveau,'numerotation-titre','CRITIQUE',title,
                              f'Titre: après "Siman" -> {tok} (={val}) mais siman URL = {n}',
                              f'Corriger le numéral en {n}','haute','oui')
            # canonical must contain the siman number
            if canonical and f'/{n}/' not in canonical and not re.search(rf'/{n}(/|$|\b)', canonical):
                add_issue(url,rel,'',lang,siman,niveau,'canonical-siman-incoherent','IMPORTANTE',canonical,
                          f'canonical ne contient pas le numéro {n}','Vérifier canonical')

    rows.append({
        'URL':url,'Langue':lang,'Section':section,'Siman':siman,'Seif':seif,
        'Niveau':niveau,'Fichier_source':rel,'Titre':title,'Statut_HTTP':'200 (fichier présent)',
        'Indexable':indexable,'Present_dans_sitemap':in_sitemap,
        'Commentaires':'; '.join(comments)})

# duplicate detection
for t,files in titles_seen.items():
    if len(files)>1:
        add_issue(BASE_URL,';'.join(files[:5]),'','multi','','', 'SEO-title-duplique','MOYENNE',t,
                  f'Titre identique sur {len(files)} pages','Rendre chaque <title> unique','haute','non')
for c,files in canon_seen.items():
    if len(files)>1:
        add_issue(c,';'.join(files[:5]),'','multi','','', 'canonical-duplique','IMPORTANTE',c,
                  f'canonical identique sur {len(files)} pages (contenu dupliqué ?)','1 canonical unique par contenu','haute','non')

# ---------- write inventory ----------
AUDIT.mkdir(exist_ok=True)
inv_cols=['URL','Langue','Section','Siman','Seif','Niveau','Fichier_source','Titre',
          'Statut_HTTP','Indexable','Present_dans_sitemap','Commentaires']
with open(AUDIT/'inventaire-pages.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=inv_cols); w.writeheader()
    for r in rows: w.writerow(r)

# ---------- write technical issues ----------
tech_cols=['ID','URL','Fichier','Ligne','Langue','Siman','Niveau','Type','Gravite',
           'Texte_actuel','Probleme','Correction_proposee','Certitude','Validation_Rav']
with open(AUDIT/'erreurs-techniques.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=tech_cols); w.writeheader()
    for r in tech_issues: w.writerow(r)

# ---------- summary ----------
from collections import Counter
by_section=Counter(r['Section'] for r in rows)
by_lang=Counter(r['Langue'] for r in rows)
by_niveau=Counter(r['Niveau'] for r in rows if r['Niveau'])
by_grav=Counter(i['Gravite'] for i in tech_issues)
by_type=Counter(i['Type'] for i in tech_issues)
not_in_sitemap=[r for r in rows if r['Present_dans_sitemap']=='non']

print("=== INVENTAIRE ===")
print("Total pages HTML:", len(rows))
print("Par langue:", dict(by_lang))
print("Par section:", dict(by_section))
print("Par niveau:", dict(by_niveau))
print()
print("=== CONTROLES TECHNIQUES/SEO ===")
print("Total problèmes détectés:", len(tech_issues))
print("Par gravité:", dict(by_grav))
print("Par type:")
for t,c in by_type.most_common():
    print(f"   {c:5d}  {t}")
print()
print("Pages hors sitemap:", len(not_in_sitemap))
# categorize not-in-sitemap by section
nis=Counter(r['Section'] for r in not_in_sitemap)
print("   hors-sitemap par section:", dict(nis))
