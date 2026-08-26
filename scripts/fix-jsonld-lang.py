#!/usr/bin/env python3
"""Aligne le JSON-LD des pages -he/-en sur leur propre URL canonique.

Défaut corrigé : sur les pages index-he.html / index-en.html, les champs
JSON-LD @id, url et le dernier item du fil d'Ariane pointaient vers la
version FRANÇAISE de la page (.../242/) au lieu de la page elle-même
(.../242/he) — Google reçoit alors trois pages qui se déclarent être
la même entité.

Règle appliquée : @id / url / item doivent valoir l'URL canonique de la page.
N'agit qu'à l'intérieur des blocs <script type="application/ld+json">.
"""
import re, sys, glob

def canon(s):
    m = re.search(r'rel="canonical" href="([^"]+)"', s)
    return m.group(1) if m else None

def fix(path, apply=False):
    s = open(path, encoding='utf-8').read()
    c = canon(s)
    if not c or not re.search(r'/(he|en)$', c):
        return 0
    base = re.sub(r'/(he|en)$', '', c)          # .../oh/242
    out, n = [], 0
    pos = 0
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        blk = m.group(1)
        new = blk
        # "@id": "BASE/#article"  →  "@id": "CANON#article"
        new, k1 = re.subn(r'("@id"\s*:\s*")' + re.escape(base) + r'/(#[A-Za-z-]*")', r'\1' + c + r'\2', new)
        # "url"|"item": "BASE/"   →  "CANON"
        new, k2 = re.subn(r'("(?:url|item)"\s*:\s*")' + re.escape(base) + r'/(")', r'\1' + c + r'\2', new)
        n += k1 + k2
        out.append((m.start(1), m.end(1), new))
    if n and apply:
        for st, en, new in reversed(out):
            s = s[:st] + new + s[en:]
        open(path, 'w', encoding='utf-8').write(s)
    return n

if __name__ == '__main__':
    apply = '--apply' in sys.argv
    skip = [a.split('=')[1] for a in sys.argv if a.startswith('--skip=')]
    skip = skip[0].split(',') if skip else []
    files = []
    for sec in ('shabbat', 'orah-haim', 'yoreh-deah', 'nida'):
        for sfx in ('he', 'en'):
            files += glob.glob(f'sources/{sec}/siman-*/*-{sfx}.html')
    tot = touched = 0
    for f in sorted(files):
        if any(f'siman-{n}/' in f for n in skip):
            continue
        n = fix(f, apply)
        if n:
            touched += 1
            tot += n
    print(('CORRIGÉ' if apply else 'À CORRIGER'), f': {touched} fichiers, {tot} champs JSON-LD')
