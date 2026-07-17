#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute le bloc numéral hébreu (gros סימן <héb> + petit « Siman N ») dans le hero
des pages-index Orah Haïm quotidien et Yoreh Deah, à l'identique des pages Shabbat.

Le numéral hébreu est RÉUTILISÉ depuis la ligne meta existante de chaque page
(« · Siman <héb> » / « · סימן <héb> ») — aucune gématria recalculée, aucune source fabriquée.

Idempotent : ne fait rien si le bloc daat-hero-siman est déjà présent.
--apply pour écrire ; sans --apply = dry-run.
"""
import re, sys, glob, os

APPLY = "--apply" in sys.argv

# (glob, classe-meta, balise)
TARGETS = [
    ("sources/orah-haim/siman-*/index.html",    "siman-meta",     "div"),
    ("sources/orah-haim/siman-*/index-he.html", "siman-meta",     "div"),
    ("sources/orah-haim/siman-*/index-en.html", "siman-meta",     "div"),
    ("sources/yoreh-deah/siman-*/index.html",    "daat-hero-meta", "p"),
    ("sources/yoreh-deah/siman-*/index-he.html", "daat-hero-meta", "p"),
    ("sources/yoreh-deah/siman-*/index-en.html", "daat-hero-meta", "p"),
]

HEB = r"[א-ת׳״'\"]+"  # lettres héb. + geresh/gershayim (+ ASCII)

def siman_num_from_path(path):
    m = re.search(r"siman-(\d+)", path)
    return m.group(1) if m else None

def process(path, meta_class, tag):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    if "daat-hero-siman" in src:
        return ("skip-present", None)
    num = siman_num_from_path(path)
    if not num:
        return ("skip-nonum", None)

    # localise la ligne meta : <div class="siman-meta">…</div>  ou  <p class="daat-hero-meta">…</p>
    meta_re = re.compile(
        r'([ \t]*)<' + tag + r'\s+class="' + re.escape(meta_class) + r'"[^>]*>(.*?)</' + tag + r'>',
        re.S,
    )
    m = meta_re.search(src)
    if not m:
        return ("skip-nometa", None)
    indent, inner = m.group(1), m.group(2)

    # extrait le numéral héb. après le DERNIER « Siman » / « סימן »
    hm = re.search(r'(?:Siman|סימן)\s+(' + HEB + r')\s*$', inner.strip())
    if hm:
        heb = hm.group(1)
    else:
        # fallback : lire le numéral depuis la page FR sœur (index.html)
        heb = None
        sib = os.path.join(os.path.dirname(path), "index.html")
        if os.path.exists(sib):
            with open(sib, encoding="utf-8") as f:
                sib_src = f.read()
            sm = re.search(r'(?:Siman|סימן)\s+(' + HEB + r')\s*</', sib_src)
            if sm:
                heb = sm.group(1)
        if not heb:
            return ("skip-noheb", None)

    block = ('<div class="daat-hero-siman">'
             '<span class="daat-hero-siman-he">סימן ' + heb + '</span>'
             '<span class="daat-hero-siman-num">Siman ' + num + '</span></div>')

    # nettoie la meta : retire le dernier segment « · Siman <héb> » / « · סימן <héb> »
    new_inner = re.sub(r'\s*·\s*(?:Siman|סימן)\s+' + HEB + r'\s*$', '', inner.rstrip())
    new_meta = indent + '<' + tag + ' class="' + meta_class + '">' + new_inner + '</' + tag + '>'
    new_block_line = indent + block

    replacement = new_block_line + "\n" + new_meta
    new_src = src[:m.start()] + replacement + src[m.end():]

    if APPLY:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_src)
    return ("done", heb)

def main():
    stats = {}
    samples = []
    for pattern, meta_class, tag in TARGETS:
        for path in sorted(glob.glob(pattern)):
            status, heb = process(path, meta_class, tag)
            stats[status] = stats.get(status, 0) + 1
            if status == "done" and len(samples) < 6:
                samples.append((path, heb))
            if status.startswith("skip-n") and status != "skip-present":
                if len([s for s in samples if s[0]=="ERR"]) < 8:
                    samples.append(("ERR:" + status, path))
    print("APPLY =", APPLY)
    for k in sorted(stats):
        print(f"  {k}: {stats[k]}")
    print("échantillons:")
    for a, b in samples:
        print("   ", a, "->", b)

if __name__ == "__main__":
    main()
