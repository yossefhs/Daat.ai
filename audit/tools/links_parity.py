#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DAAT audit — liens internes cassés + parité inter-langues. Lecture seule."""
import os, re, json, csv
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT/"audit"
BASE = "daattorah.com"

vj = json.load(open(ROOT/"vercel.json", encoding="utf-8"))
def src_rx(src):
    # Tokenise vercel source into literals and params (:name, :name*, :name(regex))
    out=[]; i=0; gi=0
    tok=re.compile(r':(\w+)(\([^)]*\))?(\*)?')
    while i < len(src):
        m=tok.match(src,i)
        if m:
            name,rx,star=m.group(1),m.group(2),m.group(3)
            if rx:
                body=rx[1:-1]  # strip parens, keep as-is regex
                out.append(f'(?P<{name}>{body})')
            elif star:
                out.append(f'(?P<{name}>.+)')
            else:
                out.append(f'(?P<{name}>[^/]+)')
            i=m.end()
        else:
            out.append(re.escape(src[i])); i+=1
    return re.compile('^'+''.join(out)+'$')
REW=[(src_rx(r['source']), r['destination']) for r in vj.get('rewrites',[]) if r.get('source') and r.get('destination')]
RED=[(src_rx(r['source']), r['destination']) for r in vj.get('redirects',[]) if r.get('source') and r.get('destination')]

def expand(dest,m):
    o=dest
    for k,v in (m.groupdict() or {}).items():
        o=o.replace(f':{k}*',v).replace(f':{k}',v)
    return o

def target_exists(path, depth=0):
    """path: url-path starting with /. Return (ok, kind)."""
    if depth>5: return True,'loop'
    p = unquote(path.split('?')[0].split('#')[0])
    if p in ('','/'): return (ROOT/'index.html').exists(),'file'
    for rx,dest in RED:
        m=rx.match(p)
        if m:
            nd=expand(dest,m)
            if nd.startswith('http'): return True,'ext-redir'
            return target_exists(nd,depth+1)
    for rx,dest in REW:
        m=rx.match(p)
        if m:
            nd=expand(dest,m)
            if nd.startswith('/api'): return True,'api'
            if nd.startswith('http'): return True,'ext'
            fp=ROOT/nd.lstrip('/')
            if fp.is_dir(): fp=fp/'index.html'
            return fp.exists(),'rewrite'
    fp=ROOT/p.lstrip('/')
    if fp.is_dir():
        return (fp/'index.html').exists(),'dir'
    return fp.exists(),'file'

SKIP={'.git','node_modules','.claude'}
html_files=[]
for dp,dirs,files in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in SKIP]
    for fn in files:
        if fn.endswith('.html'): html_files.append(Path(dp)/fn)

broken=[]      # file, href, resolved, kind
checked=0
href_rx=re.compile(r'(?:href|src)="([^"]+)"', re.I)
for fp in html_files:
    rel=str(fp.relative_to(ROOT))
    txt=fp.read_text(encoding='utf-8',errors='replace')
    for raw in href_rx.findall(txt):
        h=raw.strip()
        if not h or h.startswith('#') or h.startswith('mailto:') or h.startswith('tel:') \
           or h.startswith('data:') or h.startswith('javascript:'): continue
        # external?
        if h.startswith('http://') or h.startswith('https://'):
            u=urlparse(h)
            if BASE not in u.netloc:
                continue  # external — not resolved here
            path=u.path or '/'
        elif h.startswith('//'):
            continue
        elif h.startswith('/'):
            path=h
        else:
            # relative to file dir
            base_dir=fp.parent
            resolved=(base_dir / h.split('?')[0].split('#')[0]).resolve()
            try:
                rp=resolved.relative_to(ROOT)
            except ValueError:
                broken.append((rel,h,'HORS-RACINE','rel')); continue
            path='/'+str(rp).replace('\\','/')
        checked+=1
        ok,kind=target_exists(path)
        if not ok:
            broken.append((rel,h,path,kind))

# ---- parity: each FR strict page should have -he and -en siblings ----
parity=[]
def sib(fp, suffix):
    name=fp.name
    if name.endswith('-en.html'): stem=name[:-8]
    elif name.endswith('-he.html'): stem=name[:-8]
    else: stem=name[:-5]
    return fp.parent/(stem+suffix)
STRICT_PREFIX=('sources/','limoud/','blog/','auteur/')
for fp in html_files:
    rel=str(fp.relative_to(ROOT)).replace('\\','/')
    name=fp.name
    if name.endswith('-en.html') or name.endswith('-he.html'): continue
    if not (rel.startswith(STRICT_PREFIX) or (('/' not in rel) and rel in (
        'index.html','chat.html','about.html','faq.html','communaute.html','soutenir.html','contenu.html'))):
        continue
    he=sib(fp,'-he.html'); en=sib(fp,'-en.html')
    if not he.exists(): parity.append((rel,'HE manquant',str(he.relative_to(ROOT))))
    if not en.exists(): parity.append((rel,'EN manquant',str(en.relative_to(ROOT))))

with open(AUDIT/'liens-casses.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Fichier_source','Lien','Cible_resolue','Type'])
    for r in broken: w.writerow(r)
with open(AUDIT/'parite-langues-manquantes.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Fichier_FR','Probleme','Fichier_attendu'])
    for r in parity: w.writerow(r)

from collections import Counter
print("Liens internes vérifiés:", checked)
print("Liens cassés:", len(broken))
bk=Counter(b[3] for b in broken); print("  par type:", dict(bk))
# group broken by href value
byhref=Counter(b[1] for b in broken)
print("  top hrefs cassés:")
for h,c in byhref.most_common(20):
    print(f"    {c:5d}  {h}")
print()
print("Parité langue manquante (pages FR sans sibling):", len(parity))
pc=Counter(p[1] for p in parity); print("  ",dict(pc))
for p in parity[:20]: print("   ",p)
