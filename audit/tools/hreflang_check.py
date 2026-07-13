#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vérifie que les hreflang fr/he/en d'une page pointent vers le MÊME siman+niveau,
et que la cible résout vers un fichier existant. Lecture seule."""
import os, re, json, csv
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/"audit"
vj=json.load(open(ROOT/"vercel.json",encoding="utf-8"))
def src_rx(src):
    out=[];i=0;tok=re.compile(r':(\w+)(\([^)]*\))?(\*)?')
    while i<len(src):
        m=tok.match(src,i)
        if m:
            n,rx,st=m.group(1),m.group(2),m.group(3)
            out.append(f'(?P<{n}>{rx[1:-1]})' if rx else (f'(?P<{n}>.+)' if st else f'(?P<{n}>[^/]+)')); i=m.end()
        else: out.append(re.escape(src[i]));i+=1
    return re.compile('^'+''.join(out)+'$')
REW=[(src_rx(r['source']),r['destination']) for r in vj['rewrites'] if r.get('source') and r.get('destination')]
def resolve(path):
    p=path.split('?')[0].split('#')[0]
    if p in('','/'):return ROOT/'index.html'
    for rx,d in REW:
        m=rx.match(p)
        if m:
            for k,v in (m.groupdict() or {}).items(): d=d.replace(f':{k}*',v).replace(f':{k}',v)
            fp=ROOT/d.lstrip('/');
            return (fp/'index.html') if fp.is_dir() else fp
    fp=ROOT/p.lstrip('/'); return (fp/'index.html') if fp.is_dir() else fp

def siman_level_of(fp):
    s=str(fp); m=re.search(r'siman-(\d+)',s); sim=m.group(1) if m else ''
    lvl=''
    for k,v in [('niveau-1-base','base'),('niveau-2-lamdan','lamdan'),('niveau-3-synthese','synthese'),('niveau-4-daat-harav','daat'),('index','index')]:
        if os.path.basename(s).startswith(k): lvl=v;break
    return sim,lvl

SKIP={'.git','node_modules','.claude'}
issues=[]
for dp,dirs,fs in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in SKIP]
    for fn in fs:
        if not fn.endswith('.html'):continue
        fp=Path(dp)/fn; rel=str(fp.relative_to(ROOT))
        if not rel.startswith('sources/'):continue
        txt=fp.read_text(encoding='utf-8',errors='replace')
        hl=dict(re.findall(r'rel="alternate"[^>]+hreflang="([^"]+)"[^>]+href="([^"]+)"',txt,re.I))
        my_sim,my_lvl=siman_level_of(fp)
        for lang,href in hl.items():
            if lang=='x-default':continue
            path=urlparse(href).path or '/'
            tgt=resolve(path)
            if not tgt.exists():
                issues.append((rel,lang,href,'CIBLE-INEXISTANTE',f'{my_sim}/{my_lvl}','')); continue
            ts,tl=siman_level_of(tgt)
            if my_sim and ts and my_sim!=ts:
                issues.append((rel,lang,href,'SIMAN-DIFFERENT',f'{my_sim}/{my_lvl}',f'{ts}/{tl}'))
            elif my_lvl and tl and my_lvl!=tl:
                issues.append((rel,lang,href,'NIVEAU-DIFFERENT',f'{my_sim}/{my_lvl}',f'{ts}/{tl}'))
with open(AUDIT/'hreflang-incoherences.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['Fichier','Lang_cible','Href','Probleme','Source_siman_niveau','Cible_siman_niveau'])
    for r in issues:w.writerow(r)
from collections import Counter
print("Incohérences hreflang (cible ≠ même siman/niveau ou inexistante):",len(issues))
print(" ",dict(Counter(i[3] for i in issues)))
for i in issues[:15]:print("  ",i)
