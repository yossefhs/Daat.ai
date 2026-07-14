#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DAAT — correction des défauts MÉCANIQUES (sûrs, non-halakhiques).
DRY-RUN par défaut ; n'écrit QUE si --apply est passé.

Corrections :
 A. Gershayim ASCII (") entre deux lettres hébraïques -> gershayim typographique ״ (U+05F4).
    Corrige les meta/JSON-LD cassés et normalise le corps. Site-wide.
 B. Coquille סיכות -> שיחות, uniquement dans les collocations « discours du Rabbi »
    (jamais סיכות = épingles, ex. siman 301).
 C. Compteur « 3 niveaux » -> « 4 niveaux », uniquement sur les index qui ont
    réellement une 4e carte (présence de 'bar-4'). Exclut les simanim-pont 304/322.
"""
import os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
APPLY='--apply' in sys.argv
SKIP={'.git','node_modules','.claude'}

HEB=r'א-ת'
GERSHAYIM='״'  # ״

# --- collocations שיחות (typo סיכות) : sûres ---
SIKHOT_PAIRS=[
 ('סיכות, מאמרים','שיחות, מאמרים'),
 ('סיכות-מאמרים-ואגרות','שיחות-מאמרים-ואגרות'),
 ('סיכות-מאמרים-ואיגרות','שיחות-מאמרים-ואיגרות'),
 ('סיכות-ואגרות-הרבי','שיחות-ואגרות-הרבי'),
 ('סיכות ואגרות','שיחות ואגרות'),
 ('סיכות הרבי','שיחות הרבי'),
 ('סיכות קודש','שיחות קודש'),
]
# --- compteur 3 -> 4 ---
COUNTER_PAIRS=[
 ("Les 3 niveaux d'étude","Les 4 niveaux d'étude"),
 ('id="les-3-niveaux-d-etude"','id="les-4-niveaux-d-etude"'),
 ('The 3 levels of study','The 4 levels of study'),
 ('The 3 Levels of Study','The 4 Levels of Study'),
 ('The 3 levels of limud','The 4 levels of limud'),
 ('The 3 Levels of Limud','The 4 Levels of Limud'),
 ('שלוש רמות הלימוד','ארבע רמות הלימוד'),
 ('en 3 niveaux','en 4 niveaux'),
 ('in 3 levels','in 4 levels'),
 ('ב-3 רמות','ב-4 רמות'),
 ('בשלוש רמות','בארבע רמות'),
]
# gershayim precedes the FINAL letter of an acronym/numeral; the negative lookahead
# excludes opening-quotation cases like ה"שותף" (a quoted word), converting only
# genuine gershayim (quote followed by exactly one final Hebrew letter).
gersh_rx=re.compile(f'([{HEB}])"([{HEB}])(?![{HEB}])')

def is_content_html(rel):
    return rel.startswith(('sources/','blog/','limoud/','auteur/')) or (
        '/' not in rel and rel.endswith('.html'))

stats={'A_files':0,'A_subs':0,'B_files':0,'B_subs':0,'C_files':0,'C_subs':0}
samples={'A':[],'B':[],'C':[]}

for dp,dirs,fs in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in SKIP]
    for fn in fs:
        if not fn.endswith('.html'): continue
        fp=Path(dp)/fn; rel=str(fp.relative_to(ROOT))
        if not is_content_html(rel): continue
        orig=fp.read_text(encoding='utf-8',errors='replace')
        t=orig
        # ---- A: gershayim ----
        # apply repeatedly (overlapping like אדמו"ר handled by single pass; multiple distinct tokens ok)
        newt,nA=gersh_rx.subn(f'\\1{GERSHAYIM}\\2', t)
        if nA:
            # run a 2nd pass in case of adjacent patterns
            newt,nA2=gersh_rx.subn(f'\\1{GERSHAYIM}\\2', newt)
            nA+=nA2
            if len(samples['A'])<6:
                m=gersh_rx.search(t);
                if m: samples['A'].append((rel, m.group(0)+' -> '+m.group(1)+GERSHAYIM+m.group(2)))
            t=newt; stats['A_files']+=1; stats['A_subs']+=nA
        # ---- B: sikhot collocations ----
        nB=0
        for a,b in SIKHOT_PAIRS:
            if a in t:
                c=t.count(a); t=t.replace(a,b); nB+=c
        if nB:
            stats['B_files']+=1; stats['B_subs']+=nB
            if len(samples['B'])<6: samples['B'].append((rel,f'{nB}× סיכות→שיחות'))
        # ---- C: counter (index pages with bar-4 only) ----
        base=os.path.basename(rel)
        if base.startswith('index') and 'bar-4' in t:
            nC=0
            for a,b in COUNTER_PAIRS:
                if a in t:
                    c=t.count(a); t=t.replace(a,b); nC+=c
            if nC:
                stats['C_files']+=1; stats['C_subs']+=nC
                if len(samples['C'])<8: samples['C'].append((rel,f'{nC}× 3→4'))
        # write?
        if t!=orig and APPLY:
            fp.write_text(t,encoding='utf-8')

mode='APPLIQUÉ' if APPLY else 'DRY-RUN (aucune écriture)'
print(f"=== {mode} ===\n")
print(f"A. Gershayim ASCII -> ״ : {stats['A_subs']} substitutions dans {stats['A_files']} fichiers")
for s in samples['A']: print('     ',s[0],'|',s[1])
print(f"\nB. Coquille סיכות -> שיחות : {stats['B_subs']} substitutions dans {stats['B_files']} fichiers")
for s in samples['B']: print('     ',s[0],'|',s[1])
print(f"\nC. Compteur 3 -> 4 niveaux (index avec bar-4) : {stats['C_subs']} substitutions dans {stats['C_files']} fichiers")
for s in samples['C']: print('     ',s[0],'|',s[1])
print(f"\nTotal fichiers touchés (unique approx): A={stats['A_files']} B={stats['B_files']} C={stats['C_files']}")
if not APPLY: print("\n>>> Relancer avec --apply pour écrire les changements.")
