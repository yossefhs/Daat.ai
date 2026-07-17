#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DAAT — Répare les <title> tronqués en complétant UNIQUEMENT le segment sujet,
à partir du sujet complet de la page index du même siman (dans la bonne langue).
Ne remplace que si le sujet tronqué est un préfixe du sujet complet.
DRY-RUN par défaut ; --apply pour écrire."""
import os,re,sys,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
APPLY='--apply' in sys.argv

title_rx=re.compile(r'<title[^>]*>(.*?)</title>', re.S|re.I)
og_rx=re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', re.I)
DANGLE=re.compile(r'\b(de|à|pour|sur|un|une|les|le|la|the|to|from|a|of|on|and|du|des|en|dans|that|with|by|via|au|aux|qui|des|du)$', re.I)
SUFFIX_SRC=re.compile(r'\s*\((?:Choulhan Aroukh|Shulchan Aruch|שולחן ערוך|Choulhan Aroukh HaRav)\)\s*$')
PREFIX_SIMAN=re.compile(r'^(?:Siman|סימן)\s+\S+\s+—\s+')  # "Siman 247 — " / "סימן רמ״ז — "
def norm(s): return re.sub(r'\s+',' ',s).strip()

# 1) Construire le sujet complet par (siman, lang) depuis l'index og:title
TOPIC={}
for n in range(242,366):
    for lang,suf in [('fr',''),('he','-he'),('en','-en')]:
        fp=ROOT/f'sources/shabbat/siman-{n}/index{suf}.html'
        if not fp.exists(): continue
        t=fp.read_text(encoding='utf-8')
        m=og_rx.search(t)
        if not m: continue
        og=SUFFIX_SRC.sub('', norm(html.unescape(m.group(1))))
        topic=PREFIX_SIMAN.sub('', og).strip()
        if topic: TOPIC[(n,lang)]=topic

def lang_of(fn):
    if fn.endswith('-he.html'): return 'he'
    if fn.endswith('-en.html'): return 'en'
    return 'fr'

report={'fixed':0,'skip':0}
manual=[]
for dp,dirs,fs in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in {'.git','node_modules','.claude'}]
    for fn in fs:
        if not fn.endswith('.html'): continue
        rel=str(Path(dp,fn).relative_to(ROOT))
        m=re.search(r'sources/shabbat/siman-(\d+)/',rel)
        if not m: continue
        n=int(m.group(1)); lang=lang_of(fn)
        fp=Path(dp,fn); t=fp.read_text(encoding='utf-8')
        mt=title_rx.search(t)
        if not mt: continue
        raw=mt.group(1); title=norm(html.unescape(re.sub(r'<[^>]+>','',raw)))
        if ' | ' not in title: continue
        core,suffix=title.rsplit(' | ',1)
        if ' — ' not in core: continue
        pre,topic_tr=core.rsplit(' — ',1)
        if not DANGLE.search(topic_tr.strip()): continue   # pas tronqué
        full=TOPIC.get((n,lang))
        if not full: manual.append((rel,'pas de sujet index')); report['skip']+=1; continue
        tt=topic_tr.strip()
        if full.startswith(tt) and len(full)>len(tt):
            # remplacer le segment tronqué (tel qu'il apparaît dans le <title> brut) par le sujet complet
            # topic_tr peut contenir des entités/bdi dans raw : on remplace dans raw le texte tronqué visible
            raw_text=html.unescape(re.sub(r'<[^>]+>','',raw))
            new_text=raw_text.replace(' — '+topic_tr+' | ', ' — '+full+' | ',1)
            if new_text==raw_text:
                manual.append((rel,'segment introuvable dans raw')); report['skip']+=1; continue
            newfull=f'<title>{new_text}</title>'
            t2=title_rx.sub(lambda mm: newfull, t, count=1)
            if t2!=t:
                report['fixed']+=1
                if APPLY: fp.write_text(t2,encoding='utf-8')
        else:
            manual.append((rel,f'non-préfixe: "{tt[:35]}" vs "{full[:45]}"')); report['skip']+=1

print('APPLIQUÉ' if APPLY else 'DRY-RUN')
print('Titres réparés:', report['fixed'], '| non traités:', report['skip'])
for mm in manual[:15]: print('   ',mm[0],'|',mm[1])
