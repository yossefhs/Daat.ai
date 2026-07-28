# -*- coding: utf-8 -*-
"""Découpage en blocs et stabilité des identifiants (§6, §20).

Les assertions portent sur une vraie page du site
(``tests/fixtures/siman-242-base.html``), pas sur du HTML de laboratoire :
c'est le balisage réel qui doit être supporté.
"""
import pathlib

import pytest

from daat_audit.blocks import split_blocks
from daat_audit.models import BlockType

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "siman-242-base.html"


@pytest.fixture(scope="module")
def blocks():
    html = FIXTURE.read_text(encoding="utf-8")
    return split_blocks(html, section="OH", siman=242, niveau="base", langue="fr")


# ── Découpage ────────────────────────────────────────────────────────────

def test_la_page_produit_des_blocs_de_plusieurs_types(blocks):
    assert len(blocks) > 20
    types = {b.block_type for b in blocks}
    assert BlockType.TITRE in types
    assert BlockType.CITATION_HEBRAIQUE in types
    assert BlockType.SOUS_TITRE in types


def test_le_texte_du_choulhan_aroukh_est_capture_en_citation_hebraique(blocks):
    hebreu = " ".join(b.normalized_content
                      for b in blocks if b.block_type is BlockType.CITATION_HEBRAIQUE)
    assert "כבוד השבת" in hebreu


def test_navigation_et_pied_de_page_exclus(blocks):
    contenus = " ".join(b.normalized_content for b in blocks)
    assert "lang-switcher" not in contenus
    for b in blocks:
        assert b.block_type is not None


def test_aucun_bloc_vide(blocks):
    assert all(b.normalized_content.strip() for b in blocks)


def test_ordre_sequentiel_et_sans_trou(blocks):
    assert [b.order_index for b in blocks] == list(range(1, len(blocks) + 1))


# ── Identifiants stables ─────────────────────────────────────────────────

def test_identifiants_uniques_et_bien_formes(blocks):
    ids = [b.stable_id for b in blocks]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("OH-242-BASE-FR-") for i in ids)


def test_meme_page_memes_identifiants(blocks):
    """Le découpage est déterministe : rejouer la page donne les mêmes ID."""
    again = split_blocks(FIXTURE.read_text(encoding="utf-8"),
                         section="OH", siman=242, niveau="base", langue="fr")
    assert [b.stable_id for b in again] == [b.stable_id for b in blocks]
    assert [b.sha256 for b in again] == [b.sha256 for b in blocks]


def test_inserer_un_paragraphe_ne_renumerote_pas_les_citations(blocks):
    """Le point de la conception du §6 : le rang est calculé PAR TYPE.

    Un index global décalerait tous les blocs suivants dès qu'on insère quoi
    que ce soit ; ici, insérer un paragraphe ne touche pas les identifiants
    des citations hébraïques — et les décisions déjà rendues sur ces blocs
    restent rattachées au bon contenu.
    """
    html = FIXTURE.read_text(encoding="utf-8")
    modifie = html.replace("<main", "<main><p>Paragraphe inséré en tête.</p>", 1)
    apres = split_blocks(modifie, section="OH", siman=242,
                         niveau="base", langue="fr")

    def citations(bs):
        return {b.stable_id: b.sha256
                for b in bs if b.block_type is BlockType.CITATION_HEBRAIQUE}

    assert citations(apres) == citations(blocks)


def test_un_changement_de_contenu_change_le_sha256():
    base = "<main><p>Texte d'origine, suffisamment long pour être un bloc.</p></main>"
    autre = "<main><p>Texte modifié, suffisamment long pour être un bloc.</p></main>"
    a = split_blocks(base, siman=242)[0]
    b = split_blocks(autre, siman=242)[0]
    assert a.stable_id == b.stable_id       # même place, même identifiant
    assert a.sha256 != b.sha256             # mais contenu différent


def test_le_prefixe_suit_la_langue_et_le_niveau():
    html = "<main><p>Un paragraphe de longueur raisonnable pour le test.</p></main>"
    bloc = split_blocks(html, section="OH", siman=268,
                        niveau="lamdan", langue="he")[0]
    assert bloc.stable_id.startswith("OH-268-LAMDAN-HE-")
