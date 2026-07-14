#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DAAT — Localise les <title> des pages HE/EN dont le SUJET est resté en français,
en le remplaçant par le sujet de la page index du même siman (langue correspondante).
Gère les balises internes (<bdi>). DRY-RUN par défaut ; --apply pour écrire."""
import os,re,sys,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
APPLY='--apply' in sys.argv

title_rx=re.compile(r'<title[^>]*>(.*?)</title>', re.S|re.I)
og_rx=re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', re.I)
SUFFIX_SRC=re.compile(r'\s*\((?:Choulhan Aroukh|Shulchan Aruch|שולחן ערוך|Choulhan Aroukh HaRav)\)\s*$')
PREFIX_SIMAN=re.compile(r'^(?:Siman|סימן)\s+\S+\s+—\s+')
# marqueurs français (accents ou mots-outils/thèmes récurrents)
# marqueurs FRANÇAIS à haute confiance : accents, apostrophe élidée (l'/d'/qu'), mots-outils
# français qui n'apparaissent ni en hébreu (pas de latin) ni en anglais ('the/of/for'...).
FR=re.compile(r"[éèêàçùâîôûïëœ]|\b(le|la|les|des|une|un|pour|sur|dans|avec|aux|du|par|non-juif|qui)\b|\b[ldsjqn]'", re.I)
def norm(s): return re.sub(r'\s+',' ',s).strip()

TOPIC={}
for n in range(242,366):
    for lang,suf in [('he','-he'),('en','-en')]:
        fp=ROOT/f'sources/shabbat/siman-{n}/index{suf}.html'
        if not fp.exists(): continue
        m=og_rx.search(fp.read_text(encoding='utf-8'))
        if not m: continue
        og=SUFFIX_SRC.sub('', norm(html.unescape(m.group(1))))
        topic=PREFIX_SIMAN.sub('', og).strip()
        if topic and not FR.search(topic):   # le sujet index doit lui-même être propre
            TOPIC[(n,lang)]=topic

report={'fixed':0,'skip_no_topic':0,'skip':0}; manual=[]
for dp,dirs,fs in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in {'.git','node_modules','.claude'}]
    for fn in fs:
        if not (fn.endswith('-he.html') or fn.endswith('-en.html')): continue
        rel=str(Path(dp,fn).relative_to(ROOT))
        m=re.search(r'sources/shabbat/siman-(\d+)/',rel)
        if not m: continue
        n=int(m.group(1)); lang='he' if fn.endswith('-he.html') else 'en'
        fp=Path(dp,fn); t=fp.read_text(encoding='utf-8')
        mt=title_rx.search(t)
        if not mt: continue
        raw=mt.group(1)
        visible=norm(html.unescape(re.sub(r'<[^>]+>','',raw)))
        if ' | ' not in visible or ' — ' not in visible: continue
        core,suffix=visible.rsplit(' | ',1)
        pre,topic=core.rsplit(' — ',1)
        topic=topic.strip()
        if not FR.search(topic):   # sujet déjà propre
            continue
        full=TOPIC.get((n,lang))
        if not full:
            report['skip_no_topic']+=1; manual.append((rel,'pas de sujet index propre')); continue
        # remplacer le segment ' — <topic FR> |' dans le texte visible reconstruit,
        # mais on doit écrire dans raw (qui peut contenir <bdi>). Le topic FR est du texte brut après le dernier '—'.
        # Reconstruire le nouveau <title> en gardant le préfixe (avec bdi) tel quel.
        # raw = "<...bdi...>PRE — TOPIC" (le suffixe | ... est hors <title>? non, il est dans visible)
        # visible = core | suffix ; on remplace dans raw le 'topic' brut par 'full'
        raw_topic = raw.rsplit('—',1)[1]  # texte après le dernier — (contient ' TOPIC | SUFFIX' ? non: | est dans le title)
        # le title complet inclut le suffixe. raw contient donc "... — TOPIC | SUFFIX"
        if '—' not in raw or '|' not in raw:
            report['skip']+=1; manual.append((rel,'structure inattendue')); continue
        head, tail = raw.rsplit('—',1)   # tail = " TOPIC | SUFFIX"
        seg_topic, seg_suffix = tail.split('|',1)
        new_tail = f' {full} |{seg_suffix}'
        new_raw = head + '—' + new_tail
        new_title = f'<title>{new_raw}</title>'
        t2 = title_rx.sub(lambda mm: new_title, t, count=1)
        if t2!=t:
            report['fixed']+=1
            if APPLY: fp.write_text(t2,encoding='utf-8')

print('APPLIQUÉ' if APPLY else 'DRY-RUN')
print('Titres localisés (sujet FR -> sujet index):', report['fixed'])
print('Non traités (pas de sujet index propre / structure):', report['skip_no_topic']+report['skip'])
for mm in manual[:12]: print('   ',mm[0],'|',mm[1])
