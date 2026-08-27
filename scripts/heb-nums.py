#!/usr/bin/env python3
"""Pages hébraïques : « סימן 176 » → « סימן קע״ו · 176 ».

Le numéral hébreu est la forme lue ; le chiffre arabe est conservé à côté,
comme dans les tuiles du catalogue (קצ״ז · 197).

Portée : navigation prev/next, renvois internes (.intra-ref), autres liens,
prose visible, et le libellé de fil d'Ariane JSON-LD (« name »).
Laissés intacts : les <span class="siman-num-fr"> (déjà accolés à un numéral
hébreu), les mots-clés (meta keywords / JSON-LD keywords), les « headline »
JSON-LD (déjà structurées avec ·), et tout texte source verbatim
(blockquote.text-source, .sa-he).
"""
import re, sys, glob

ONES = ['', 'א','ב','ג','ד','ה','ו','ז','ח','ט']
TENS = ['', 'י','כ','ל','מ','נ','ס','ע','פ','צ']
HUNS = ['', 'ק','ר','ש','ת','תק','תר','תש','תת','תתק']

def heb(n):
    h = HUNS[n // 100]; r = n % 100
    t = 'טו' if r == 15 else 'טז' if r == 16 else TENS[r // 10] + ONES[r % 10]
    s = h + t
    return s + '׳' if len(s) == 1 else s[:-1] + '״' + s[-1]

def spans(s, pat):
    return [(m.start(), m.end()) for m in re.finditer(pat, s, re.S)]

def convert(path, apply=False):
    s = open(path, encoding='utf-8').read()
    protect = (spans(s, r'<blockquote class="text-source">.*?</blockquote>')
               + spans(s, r'<[^>]*class="[^"]*sa-he[^"]*"[^>]*>.*?</[a-z]+>'))
    scripts = spans(s, r'<script\b.*?</script>')
    out, n = [], 0
    for m in re.finditer(r'סימן(\s+)(\d{1,3})\b', s):
        num = int(m.group(2))
        if not 1 <= num <= 999:
            continue
        pre = s[max(0, m.start() - 200):m.start()]
        if 'siman-num-fr' in pre[-40:]:                       continue   # déjà apparié
        if re.search(r'(title|alt|content|keywords)="[^"]*$', pre): continue
        if any(a <= m.start() < b for a, b in protect):        continue   # texte source
        if any(a <= m.start() < b for a, b in scripts):
            if not re.search(r'"name"\s*:\s*"[^"]*$', pre):     continue   # JSON-LD : fil d'Ariane seul
        out.append((m.start(), m.end(), f'סימן{m.group(1)}{heb(num)} · {num}'))
        n += 1
    if n and apply:
        for st, en, new in reversed(out):
            s = s[:st] + new + s[en:]
        open(path, 'w', encoding='utf-8').write(s)
    return n

if __name__ == '__main__':
    apply = '--apply' in sys.argv
    tot = files = 0
    for f in sorted(glob.glob('sources/**/*-he.html', recursive=True)):
        k = convert(f, apply)
        if k: files += 1; tot += k
    print(('CONVERTI' if apply else 'À CONVERTIR'), f': {files} fichiers, {tot} occurrences')
