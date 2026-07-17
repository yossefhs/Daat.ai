#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DAAT — Répare le numéro de siman TRONQUÉ au gershayim dans le champ JSON-LD
"description" des pages de niveau (« ...du Siman רס » -> « ...du Siman רס״ט »).
Cause : le gabarit des pages de niveau a coupé le numéral hébreu au ״.
Ne touche QUE le champ "description" du JSON-LD. DRY-RUN par défaut ; --apply pour écrire."""
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
APPLY='--apply' in sys.argv
GERSH='״'
def to_heb(n):
    ones=['','א','ב','ג','ד','ה','ו','ז','ח','ט']
    tens=['','י','כ','ל','מ','נ','ס','ע','פ','צ']
    huns=['','ק','ר','ש','ת','תק','תר','תש','תת','תתק']
    low=n%100
    if low==15: body=huns[n//100]+'טו'
    elif low==16: body=huns[n//100]+'טז'
    else:
        body=huns[n//100]+tens[low//10]+ones[n%10]
    return (body+GERSH) if len(body)==1 else body[:-1]+GERSH+body[-1]

desc_rx=re.compile(r'("description":\s*")([^"]*?)((?:Siman|סימן)\s+)([א-ת]+)(")')
fixed_files=0; fixed_occ=0; sample=[]
for n in range(242,366):
    full=to_heb(n); full_letters=full.replace(GERSH,'')
    for stem in ['index','niveau-1-base','niveau-2-lamdan','niveau-3-synthese','niveau-4-daat-harav']:
        for suf in ['','-he','-en']:
            fp=ROOT/f'sources/shabbat/siman-{n}/{stem}{suf}.html'
            if not fp.exists(): continue
            t=fp.read_text(encoding='utf-8'); orig=t; cnt=0
            def repl(m):
                global cnt
                run=m.group(4)
                if run==full_letters: return m.group(0)  # already full, leave
                cnt+=1
                return m.group(1)+m.group(2)+m.group(3)+full+m.group(5)
            t=desc_rx.sub(repl,t)
            if t!=orig:
                fixed_files+=1; fixed_occ+=cnt
                if len(sample)<10: sample.append((fp.relative_to(ROOT),n,'->',full))
                if APPLY: fp.write_text(t,encoding='utf-8')
print('APPLIQUÉ' if APPLY else 'DRY-RUN')
print('Fichiers modifiés:',fixed_files,'| occurrences corrigées:',fixed_occ)
for s in sample: print('   ',str(s[0]),'  Siman',s[1],'->',s[3])
