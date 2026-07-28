# -*- coding: utf-8 -*-
"""Tri rapide : export autonome et réinjection tracée (§14, §16, §20)."""
import importlib.util
import pathlib

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"


def _charger(nom: str):
    spec = importlib.util.spec_from_file_location(nom.replace("-", "_"),
                                                  SCRIPTS / f"{nom}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


imp = _charger("import-triage")
exp = _charger("export-triage")


def test_toute_reponse_proposee_a_une_action():
    """Une réponse offerte à l'écran et non traduisible serait un cul-de-sac."""
    proposees = {code for _, code, _, _ in exp.REPONSES}
    assert proposees == set(imp.ACTIONS)


def test_le_role_vient_de_len_tete():
    role, decisions = imp.lire("DAAT-TRIAGE v1 role=rav\n12 erreur\n13 faux")
    assert role is imp.Role.RAV
    assert decisions == [(12, "erreur"), (13, "faux")]


def test_role_editeur_par_defaut():
    role, _ = imp.lire("DAAT-TRIAGE v1\n12 faux")
    assert role is imp.Role.EDITOR


def test_reponse_inconnue_rejetee():
    with pytest.raises(ValueError, match="réponse inconnue"):
        imp.lire("DAAT-TRIAGE v1\n12 peut-etre")


def test_ligne_illisible_rejetee():
    with pytest.raises(ValueError, match="ligne illisible"):
        imp.lire("DAAT-TRIAGE v1\nn'importe quoi du tout")


def test_entree_vide_rejetee():
    with pytest.raises(ValueError, match="aucune décision"):
        imp.lire("DAAT-TRIAGE v1 role=rav")


def test_lexport_ne_precoche_aucune_reponse():
    """Un tri rapide ne doit pas devenir un tri automatique."""
    assert "checked" not in exp.GABARIT
    assert "selected" not in exp.GABARIT.lower().replace("</select>", "")


def test_la_page_de_tri_est_autonome():
    """Elle doit s'ouvrir hors ligne, sans serveur ni ressource distante."""
    for interdit in ("http://", "https://", "cdn", "<script src"):
        assert interdit not in exp.GABARIT, interdit


def test_la_page_montre_la_source_a_cote_de_la_citation():
    """Le lecteur doit trancher sur le texte, pas sur le verdict de l'outil."""
    assert "Texte de la page" in exp.GABARIT and "Source —" in exp.GABARIT
    assert "une indication, pas une preuve" in exp.GABARIT
