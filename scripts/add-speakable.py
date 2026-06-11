#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add-speakable.py — Ajoute le schema Speakable au BlogPosting des 39
articles. Permet à Google Assistant et autres TTS de lire la réponse
directe (le lead-tldr) à voix haute en citant DAAT.

Front de l'art Voice Search 2026.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"

# CSS selectors pointing to the speakable content (lead-tldr is the
# direct answer ≤60 words inserted by action 5)
SPEAKABLE = {
    "@type": "SpeakableSpecification",
    "cssSelector": [".lead-tldr", ".lead-nuance", "h1"],
}


def patch_blogposting(jsonld_str: str) -> tuple:
    """Returns (new_str, changed_bool)."""
    d = json.loads(jsonld_str)
    graph = d.get("@graph") if isinstance(d.get("@graph"), list) else None
    targets = graph if graph is not None else [d]
    changed = False
    for entity in targets:
        t = entity.get("@type", "")
        types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
        if any(x in types for x in ("BlogPosting", "Article")):
            if "speakable" not in entity:
                entity["speakable"] = SPEAKABLE
                changed = True
                break
    return json.dumps(d, ensure_ascii=False, indent=2), changed


def process(p: Path) -> str:
    html = p.read_text(encoding="utf-8")
    # Cible le bloc JSON-LD principal (le premier qui contient BlogPosting)
    pattern = re.compile(
        r'(<script type="application/ld\+json"[^>]*>)\s*(\{.*?\})\s*(</script>)', re.S
    )
    for m in pattern.finditer(html):
        body = m.group(2)
        if "BlogPosting" not in body and "Article" not in body:
            continue
        if '"speakable"' in body:
            return "skip"
        new_body, changed = patch_blogposting(body)
        if not changed:
            continue
        open_tag, _, close_tag = m.groups()
        new_html = html[: m.start()] + open_tag + "\n" + new_body + "\n" + close_tag + html[m.end():]
        p.write_text(new_html, encoding="utf-8")
        return "ok"
    return "no-blogposting"


def main():
    files = sorted(BLOG.glob("*.html"))
    stats = {"ok": 0, "skip": 0, "no-blogposting": 0, "error": 0}
    for f in files:
        if f.stem.startswith("index"):
            continue
        try:
            r = process(f)
        except Exception as e:
            print(f"  ⚠️ {f.name} : {e}")
            stats["error"] += 1
            continue
        stats[r] = stats.get(r, 0) + 1
    print(f"Articles traités       : {sum(stats.values())}")
    print(f"  Speakable ajoutée    : {stats['ok']}")
    print(f"  Déjà présente (skip) : {stats['skip']}")
    print(f"  Pas de BlogPosting   : {stats['no-blogposting']}")
    print(f"  Erreurs              : {stats['error']}")


if __name__ == "__main__":
    main()
