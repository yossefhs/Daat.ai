#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DAAT — Déploie le badge « numéral hébreu (gros) + Siman N (petit) » sur les
heros des pages index de Shabbat (FR/HE/EN), et met les numéraux de la liste
d'étude de l'accueil en hébreu. DRY-RUN par défaut ; --apply pour écrire."""
import os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
APPLY='--apply' in sys.argv

def to_heb(n):
    ones=['','א','ב','ג','ד','ה','ו','ז','ח','ט']; tens=['','י','כ','ל','מ','נ','ס','ע','פ','צ']
    huns=['','ק','ר','ש','ת','תק','תר','תש','תת','תתק']
    if n<=0: return ''
    s=huns[n//100]; rem=n%100
    if rem==15: s+='טו'
    elif rem==16: s+='טז'
    else: s+=tens[(n%100)//10]+ones[n%10]
    return (s[:-1]+'״'+s[-1]) if len(s)>1 else s+'׳'

meta_rx=re.compile(r'([ \t]*)<p class="daat-hero-meta">')
meta_clean_rx=re.compile(r'\s*·\s*(?:Siman|סימן)[^<]*(</p>)')
h1_rx=re.compile(r'(<h1 class="daat-hero-title-fr"[^>]*>)(?:Siman|סימן)\s+[^—<]*—\s*')

report={'badge':0,'meta':0,'h1':0,'skip_no_meta':0,'skip_no_h1':0}
skipped=[]
for n in range(242,366):
    for suf in ['','-he','-en']:
        rel=f'sources/shabbat/siman-{n}/index{suf}.html'
        fp=ROOT/rel
        if not fp.exists(): continue
        t=fp.read_text(encoding='utf-8'); orig=t
        heb=to_heb(n)
        badge=f'<div class="daat-hero-siman"><span class="daat-hero-siman-he">סימן {heb}</span><span class="daat-hero-siman-num">Siman {n}</span></div>'
        # 1. insert badge before meta (once)
        if 'daat-hero-siman-he' in t:
            pass  # already done
        else:
            m=meta_rx.search(t)
            if not m:
                report['skip_no_meta']+=1; skipped.append((rel,'no meta')); continue
            indent=m.group(1)
            t=t[:m.start()]+f'{indent}{badge}\n'+t[m.start():]
            report['badge']+=1
        # 2. clean meta (remove '· Siman X')
        t2,c=meta_clean_rx.subn(r'\1',t,count=1)
        if c: report['meta']+=1; t=t2
        # 3. clean h1 (remove 'Siman X — ' prefix)
        t3,c=h1_rx.subn(r'\1',t,count=1)
        if c: report['h1']+=1; t=t3
        else: report['skip_no_h1']+=1; skipped.append((rel,'no h1 pattern'))
        if t!=orig and APPLY: fp.write_text(t,encoding='utf-8')

# ---- homepage ENTRIES numerals -> Hebrew ----
def fix_entries(relpath):
    fp=ROOT/relpath
    if not fp.exists(): return 0
    t=fp.read_text(encoding='utf-8');
    # [day,"date",SIMAN,"NUMERAL",...]  -> replace NUMERAL with to_heb(SIMAN)
    def repl(m):
        num=int(m.group(2)); return f'{m.group(1)}{to_heb(num)}"'
    t2,c=re.subn(r'(\[\d+,"[\d-]+",(\d+),")(?:[^"]*)"', repl, t)
    if c and APPLY: fp.write_text(t2,encoding='utf-8')
    return c

entries_total=0
for hp in ['index.html','index-he.html','index-en.html']:
    entries_total+=fix_entries(hp)

mode='APPLIQUÉ' if APPLY else 'DRY-RUN'
print(f"=== {mode} — badge siman sur index Shabbat ===")
print(f"  Badges insérés : {report['badge']}")
print(f"  Meta nettoyées : {report['meta']}")
print(f"  h1 nettoyés    : {report['h1']}")
print(f"  Sans meta (skip): {report['skip_no_meta']} | sans h1 pattern: {report['skip_no_h1']}")
print(f"  ENTRIES accueil (numéraux → hébreu) : {entries_total} entrées")
if skipped:
    print("  Fichiers à vérifier manuellement:")
    for s in skipped[:20]: print("     ",s[0],'|',s[1])
if not APPLY: print("\n>>> --apply pour écrire.")
