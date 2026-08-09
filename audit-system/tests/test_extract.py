# -*- coding: utf-8 -*-
"""Extraction HTML (§20) — sur une page réelle du site."""
from daat_audit.extract import extract_page

URL = "https://daattorah.com/oh/242/base"


def test_titre_extrait(sample_html):
    result = extract_page(sample_html, URL)
    assert result.title
    assert "242" in result.title or "רמ" in result.title


def test_texte_contient_le_contenu_halakhique(sample_html):
    result = extract_page(sample_html, URL)
    # La page du siman 242 contient le texte du Mehaber sur le kavod Shabbat.
    assert "כבוד השבת" in result.text
    assert "Shabbat" in result.text
    # Les scripts/styles ne fuient pas dans le texte.
    assert "function" not in result.text
    assert "font-family" not in result.text


def test_liens_internes_absolus_et_dedoublonnes(sample_html):
    result = extract_page(sample_html, URL)
    assert result.internal_links, "une page du site contient toujours des liens internes"
    assert all(l.startswith("https://daattorah.com") for l in result.internal_links)
    assert len(result.internal_links) == len(set(result.internal_links))
    # Aucune ancre ni lien externe.
    assert not any("#" in l for l in result.internal_links)


def test_hotes_tiers_exclus():
    html = (
        '<html><title>t</title><body>'
        '<a href="/oh/243/base">interne</a>'
        '<a href="https://www.sefaria.org/x">externe</a>'
        '<a href="mailto:a@b.c">mail</a>'
        '<a href="#section">ancre</a>'
        "</body></html>"
    )
    result = extract_page(html, URL)
    assert result.internal_links == ["https://daattorah.com/oh/243/base"]
