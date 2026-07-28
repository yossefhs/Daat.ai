# -*- coding: utf-8 -*-
"""Empreintes et normalisation minimale (§20)."""
from daat_audit.hashing import normalize_whitespace, sha256_hex, text_fingerprint


def test_espaces_multiples_sans_effet_sur_l_empreinte():
    assert text_fingerprint("שבת   קודש") == text_fingerprint("שבת קודש")
    assert text_fingerprint("a\n\n\n\nb") == text_fingerprint("a\n\nb")


def test_changement_de_contenu_change_l_empreinte():
    assert text_fingerprint("מותר") != text_fingerprint("אסור")


def test_le_nikoud_change_l_empreinte():
    """La normalisation d'archivage ne touche PAS au nikoud (§9 : cela
    relève du comparateur de citations, qui distinguera les deux modes)."""
    assert text_fingerprint("שַׁבָּת") != text_fingerprint("שבת")


def test_sha256_stable():
    assert sha256_hex("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_normalisation_conserve_le_texte():
    assert normalize_whitespace("  שלום   עולם  ") == "שלום עולם"
