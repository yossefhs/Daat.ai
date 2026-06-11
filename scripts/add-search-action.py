#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add-search-action.py — Ajoute potentialAction: SearchAction au WebSite
de la homepage trilingue. Active la 'Sitelinks Search Box' dans Google.

Le site n'a pas de search interne classique, mais le chat IA peut
prendre une query en paramètre URL (?q=...). Comme Google a besoin
d'une URL HTTP simple, on pointe le SearchAction vers /chat.html?q={}.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = {
    "fr": ROOT / "index.html",
    "he": ROOT / "index-he.html",
    "en": ROOT / "index-en.html",
}

URL_TEMPLATE = {
    "fr": "https://daattorah.com/chat.html?q={search_term_string}",
    "he": "https://daattorah.com/chat.html?lang=he&q={search_term_string}",
    "en": "https://daattorah.com/chat.html?lang=en&q={search_term_string}",
}


def patch_website(jsonld_str: str, lang: str) -> str:
    """Ajoute potentialAction au WebSite dans le @graph."""
    d = json.loads(jsonld_str)
    graph = d.get("@graph", [d])
    for entity in graph:
        if entity.get("@type") == "WebSite":
            entity["potentialAction"] = {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": URL_TEMPLATE[lang],
                },
                "query-input": "required name=search_term_string",
            }
            break
    return json.dumps(d, ensure_ascii=False, indent=2)


def process(p: Path, lang: str) -> bool:
    html = p.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<script type="application/ld\+json"[^>]*>)\s*(\{.*?\})\s*(</script>)', re.S
    )
    m = pattern.search(html)
    if not m:
        print(f"  ⚠️ {p.name} : pas de JSON-LD trouvé")
        return False
    open_tag, body, close_tag = m.groups()
    if '"SearchAction"' in body:
        print(f"  · {p.name} : SearchAction déjà présente")
        return False
    new_body = patch_website(body, lang)
    new_html = html[: m.start()] + open_tag + "\n" + new_body + "\n" + close_tag + html[m.end():]
    p.write_text(new_html, encoding="utf-8")
    print(f"  ✓ {p.name} : SearchAction ajoutée ({lang})")
    return True


def main():
    for lang, p in PAGES.items():
        if not p.exists():
            print(f"  ⚠️ {p} absent")
            continue
        process(p, lang)


if __name__ == "__main__":
    main()
