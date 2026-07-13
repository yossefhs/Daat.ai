#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DAAT audit — scan chronologie/zmanim/mesures. Lecture seule.
Extrait les occurrences des termes horaires + heuristiques de risque. Ne conclut pas."""
import os, re, csv, html
from pathlib import Path
from collections import Counter, defaultdict

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/"audit"

TERMS = {
 'shkia': r'שקיע|chkia|shkia|shkiah|coucher du soleil|coucher',
 'netz': r'הנץ|lever du soleil|netz',
 'tzeit': r'צאת הכוכבים|צאת|tzeit|tzeis|sortie des étoiles|sortie des .toiles',
 'bein_hashmashot': r'בין השמשות|bein hashmashot|bein hashemashot|bein ha[- ]?shmashot|entre[- ]?les[- ]?soleils',
 'plag': r'פלג המנחה|plag hamin|plag hamincha|plag ha[- ]?minha',
 'tosefet': r'תוספת שבת|tosefet shabbat|tossefet|rajout.{0,6}shabbat',
 'mil': r'\bmil\b|מיל',
 'zmaniot': r'zmaniot|zemaniot|זמניות|proportionnelle',
 'degres': r'\bdegr[ée]s?\b|°',
 'rt': r"Rabb[ée]nou Tam|Rabbeinu Tam|רבנו תם|ר\"?ת",
 'gueonim': r"Gu[ée]onim|Geonim|גאונים",
 'admour': r"Admour Hazaken|Alter Rebbe|אדמו\"?ר הזקן|Admour Ha[- ]?Zaken",
 'siddour': r"Siddour|Siddur|סידור",
}
NUMS = ['13.5','13,5','58.5','58,5','22.5','22,5','96','90','72','18','16.1','16,1','8.5','8,5']

def read(p):
    try: return p.read_text(encoding='utf-8',errors='replace')
    except: return ''

SKIP={'.git','node_modules','.claude'}
files=[]
for dp,dirs,fs in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in SKIP]
    for fn in fs:
        if fn.endswith('.html'): files.append(Path(dp)/fn)

def strip_tags(s): return re.sub(r'\s+',' ', re.sub(r'<[^>]+>',' ', s)).strip()

rows=[]     # occurrences
flags=[]    # heuristic risk
num_counter=Counter()
term_files=defaultdict(set)

sent_split=re.compile(r'(?<=[.!?׃])\s+')
for fp in files:
    rel=str(fp.relative_to(ROOT))
    if rel.startswith(('node_modules','admin/','mockup/','emails/')): continue
    raw=read(fp)
    # only scan body text; approximate by stripping script/style
    body=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ', raw, flags=re.S|re.I)
    text=html.unescape(strip_tags(body))
    low=text.lower()
    present={k:bool(re.search(rx, text, re.I)) for k,rx in TERMS.items()}
    for k,v in present.items():
        if v: term_files[k].add(rel)
    for n in NUMS:
        c=text.count(n)
        if c: num_counter[n]+=c
    # heuristic risk lines: sentence mixing >=2 shitot OR a zmanim number with 'toujours/universel/partout'
    for sent in sent_split.split(text):
        s=sent.strip()
        if len(s)<8: continue
        sl=s.lower()
        shitot=sum(1 for k in ('rt','gueonim','admour') if re.search(TERMS[k],s,re.I))
        has_zman_num=any(n in s for n in ['13.5','13,5','58.5','58,5','72','90','96','18'])
        has_bhs=re.search(TERMS['bein_hashmashot'],s,re.I)
        has_tos=re.search(TERMS['tosefet'],s,re.I)
        universal=re.search(r'toujours|universel|partout|dans tous les cas|en tout lieu|dans le monde entier',sl)
        # Flag 1: two+ shitot in same sentence with a number (possible mixing)
        if shitot>=2 and has_zman_num:
            flags.append((rel,'melange-shitot-chiffre','MOYENNE',s[:280]))
        # Flag 2: bein hashmashot AND tosefet shabbat in same sentence (possible conflation)
        if has_bhs and has_tos:
            flags.append((rel,'bein-hashmashot+tosefet-meme-phrase','MOYENNE',s[:280]))
        # Flag 3: zmanim number presented as universal/fixed
        if has_zman_num and universal:
            flags.append((rel,'duree-presentee-universelle','IMPORTANTE',s[:280]))
        # collect occurrence rows for the key terms (limit noise: only zmanim-bearing sentences)
        if (has_zman_num or has_bhs or has_tos or re.search(TERMS['plag'],s,re.I) or re.search(TERMS['shkia'],s,re.I) or re.search(TERMS['tzeit'],s,re.I)):
            hit=[k for k in TERMS if re.search(TERMS[k],s,re.I)]
            rows.append((rel,'|'.join(hit),s[:280]))

with open(AUDIT/'chronologie-occurrences.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Fichier','Termes','Phrase'])
    for r in rows: w.writerow(r)
with open(AUDIT/'chronologie-risques.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Fichier','Type_risque','Gravite','Phrase'])
    for r in flags: w.writerow(r)

print("Fichiers scannés (contenu):", sum(1 for fp in files if not str(fp.relative_to(ROOT)).startswith(('admin/','mockup/','emails/'))))
print("Occurrences zmanim (phrases):", len(rows))
print("Phrases à risque heuristique:", len(flags))
print("  par type:", dict(Counter(f[1] for f in flags)))
print()
print("Nombres-clés (occurrences totales):")
for n,c in num_counter.most_common():
    print(f"   {c:6d}  '{n}'")
print()
print("Fichiers contenant chaque terme:")
for k in TERMS:
    print(f"   {len(term_files[k]):5d}  {k}")
