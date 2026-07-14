#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DAAT audit — détecteur des patterns récurrents (mécaniques) sur tout le corpus. Lecture seule.
Patterns: compteur '3 niveaux', coquille סיכות/שיחות, meta cassée par gershayim ASCII,
titres tronqués, commentaires <!-- à vérifier -->, 'Siman 242' hors-244, duplication 'סימן (סימן)'."""
import os,re,csv
from pathlib import Path
from collections import defaultdict, Counter
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/"audit"
SKIP={'.git','node_modules','.claude'}

def read(p):
    try: return p.read_text(encoding='utf-8',errors='replace')
    except: return ''

files=[]
for dp,dirs,fs in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in SKIP]
    for fn in fs:
        if fn.endswith('.html'):
            rel=str(Path(dp,fn).relative_to(ROOT))
            if rel.startswith('sources/'): files.append(Path(dp,fn))

rows=[]  # Pattern, Fichier, Detail
def add(pat,rel,detail): rows.append((pat,rel,detail))

# per pattern, track set of simanim & files
pat_files=defaultdict(set)

sikhot_rx=re.compile(r'סיכות')  # should be שיחות (only flag inside the Divrei HaRebbe heading context: id or h2 with מאמרים ואגרות)
counter3_rx=re.compile(r'(Les\s*3\s*niveaux|3\s*levels\s*of\s*(study|learning|limud)|שלוש\s*רמות)', re.I)
gershayim_meta_rx=re.compile(r'content="[^"]*[א-ת]"[א-ת]')
title_rx=re.compile(r'<title[^>]*>(.*?)</title>', re.S|re.I)
siman_siman_rx=re.compile(r'סימן\s*\(סימן\)')
averifier_rx=re.compile(r'<!--[^>]*?(à vérifier|to verify|nuance à vérifier|nuance to verify|à compléter|à confirmer)[^>]*?-->', re.I)

for fp in files:
    rel=str(fp.relative_to(ROOT))
    t=read(fp)
    sim=(re.search(r'siman-(\d+)',rel) or [None,''])[1]
    # 1. compteur 3 niveaux (only on index pages where 4 cards exist -> heuristic: page has niveau-4 card link)
    if os.path.basename(rel).startswith('index'):
        if counter3_rx.search(t) and ('daat-harav' in t or 'Daat HaRav' in t or 'דעת הרב' in t):
            m=counter3_rx.search(t); add('compteur-3-niveaux',rel,m.group(0)); pat_files['compteur-3-niveaux'].add(rel)
    # 2. coquille סיכות (dans un titre/section Divrei HaRebbe)
    for m in re.finditer(r'(id="[^"]*סיכות[^"]*"|>[^<]*סיכות[^<]{0,40}מאמרים)', t):
        add('coquille-sikhot',rel,'סיכות (→שיחות)'); pat_files['coquille-sikhot'].add(rel); break
    # 3. meta cassée par gershayim ASCII
    if gershayim_meta_rx.search(t):
        # count how many meta lines affected
        n=len(re.findall(r'<meta[^>]*content="[^"]*[א-ת]"[א-ת]', t))
        if n: add('meta-gershayim',rel,f'{n} meta'); pat_files['meta-gershayim'].add(rel)
    # 4. titre tronqué (title ends right before " | " with a dangling word, or is cut). Heuristic: title core ends with a lowercase preposition/word and no closing paren balance
    mt=title_rx.search(t)
    if mt:
        title=re.sub(r'\s+',' ',mt.group(1)).strip()
        core=title.rsplit('|',1)[0].strip()
        # dangling: ends with a short french/english connector word
        if re.search(r'\b(de|à|pour|sur|un|une|les|the|to|from|a|of|on|and|du|des|en|dans)$', core, re.I):
            add('titre-tronque',rel,title[:90]); pat_files['titre-tronque'].add(rel)
    # 5. commentaires à vérifier
    na=len(averifier_rx.findall(t))
    if na: add('commentaire-a-verifier',rel,f'{na}'); pat_files['commentaire-a-verifier'].add(rel)
    # 6. duplication סימן (סימן)
    if siman_siman_rx.search(t):
        add('siman-siman-duplique',rel,'סימן (סימן)'); pat_files['siman-siman-duplique'].add(rel)
    # 7. 'Siman 242' dans un title d'un autre siman
    if mt and sim.isdigit() and sim!='242':
        if re.search(r'Siman 242\b', mt.group(1)):
            add('titre-siman-242',rel,mt.group(1)[:80]); pat_files['titre-siman-242'].add(rel)

with open(AUDIT/'patterns-recurrents-scan.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Pattern','Fichier','Detail'])
    for r in rows: w.writerow(r)

def simset(pat):
    s=set()
    for rel in pat_files[pat]:
        m=re.search(r'siman-(\d+)',rel)
        if m: s.add(int(m.group(1)))
    return s

print("Fichiers sources scannés:",len(files))
print()
for pat in ['compteur-3-niveaux','coquille-sikhot','meta-gershayim','titre-tronque','commentaire-a-verifier','siman-siman-duplique','titre-siman-242']:
    sims=simset(pat)
    # split by section
    sec=Counter()
    for rel in pat_files[pat]:
        parts=rel.split('/'); sec[parts[1]]+=1
    print(f"{pat:26s}: {len(pat_files[pat]):4d} fichiers | {len(sims)} simanim | sections {dict(sec)}")
