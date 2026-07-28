# -*- coding: utf-8 -*-
"""Contrôles techniques et éditoriaux (§10, §20).

Chaque contrôle est éprouvé dans les deux sens : il doit **se taire** sur une
vraie page saine, et **parler** dès qu'on y injecte le défaut visé. Un
contrôle qui ne fait que se taire n'est pas un contrôle.
"""
import pathlib

import pytest

from daat_audit.blocks import split_blocks
from daat_audit.checks import REGISTRY, CheckContext, run_all
from daat_audit.models import Risk, Severity

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "siman-242-base.html"


@pytest.fixture(scope="module")
def page() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def contexte(html: str) -> CheckContext:
    return CheckContext(
        blocks=split_blocks(html, section="OH", siman=242,
                            niveau="base", langue="fr"),
        html=html, url="https://daattorah.com/oh/242/base",
    )


def codes(findings) -> set[str]:
    return {f.rule_code for f in findings}


# ── Silence sur une page saine ───────────────────────────────────────────

def test_page_reelle_saine_ne_produit_aucun_signalement(page):
    """Le siman 242 niveau 1 est conforme aux deux gates du dépôt : les
    contrôles techniques ne doivent rien y trouver. Toute régression vers du
    bruit se verra ici."""
    assert run_all(contexte(page)) == []


# ── Chaque contrôle détecte bien le défaut qu'il vise ────────────────────

def test_tech_001_espaces_multiples(page):
    abime = page.replace("Le devoir d'", "Le  devoir  d'", 1)
    assert "TECH-001" in codes(run_all(contexte(abime)))


def test_tech_002_caractere_invisible(page):
    abime = page.replace("Le devoir d'", "Le​devoir d'", 1)
    assert "TECH-002" in codes(run_all(contexte(abime)))


def test_tech_003_parentheses_desequilibrees():
    html = "<main><p>Une phrase avec une parenthèse ouverte (et jamais refermée.</p></main>"
    assert "TECH-003" in codes(run_all(contexte(html)))


def test_tech_004_guillemets_desequilibres():
    html = "<main><p>Il a dit « une chose importante et longue, sans jamais refermer.</p></main>"
    assert "TECH-004" in codes(run_all(contexte(html)))


def test_tech_004_ignore_le_gershayim_hebreu():
    """Le gershayim marque une abréviation, pas une citation : le compter
    produirait un signalement sur chaque page hébraïque."""
    html = '<main><p>Le siman רמ״ב traite de l\'honneur du Shabbat, dit le מ״ב.</p></main>'
    assert "TECH-004" not in codes(run_all(contexte(html)))


def test_tech_005_page_vide():
    assert "TECH-005" in codes(run_all(contexte("<main></main>")))


def test_tech_006_paragraphe_duplique():
    texte = ("Ce paragraphe est assez long pour dépasser le seuil des quatre-vingts "
             "caractères retenu par le contrôle des doublons exacts.")
    html = f"<main><h1>T</h1><p>{texte}</p><p>{texte}</p></main>"
    assert "TECH-006" in codes(run_all(contexte(html)))


def test_tech_006_ignore_les_libelles_courts_repetes():
    html = "<main><h1>T</h1><p>Voir plus</p><p>Voir plus</p></main>"
    assert "TECH-006" not in codes(run_all(contexte(html)))


def test_tech_007_lien_casse():
    ctx = contexte("<main><h1>T</h1><p>Texte.</p></main>")
    ctx.broken_links = {"https://daattorah.com/oh/999/base": 404}
    assert "TECH-007" in codes(run_all(ctx))


def test_tech_008_hebreu_sans_direction():
    """Hébreu long, page en ltr, aucune classe orientée : défaut réel."""
    html = ('<html dir="ltr"><main><h1>T</h1><p>'
            'אמר רבי יוחנן משום רבי יוסי כל המענג את השבת נותנין לו נחלה בלי מצרים'
            "</p></main></html>")
    assert "TECH-008" in codes(run_all(contexte(html)))


def test_tech_008_muet_quand_une_classe_de_la_page_oriente_le_texte():
    """La classe est reconnue parce que la feuille de style de la PAGE la
    déclare rtl — c'est ainsi que le site oriente ses citations."""
    html = ('<html dir="ltr"><head><style>.he { direction: rtl; }</style></head>'
            '<main><h1>T</h1><p class="he">'
            'אמר רבי יוחנן משום רבי יוסי כל המענג את השבת נותנין לו נחלה בלי מצרים'
            "</p></main></html>")
    assert "TECH-008" not in codes(run_all(contexte(html)))


def test_tech_008_muet_quand_un_ancetre_porte_dir_rtl():
    """La direction s'hérite : un conteneur rtl suffit."""
    html = ('<html dir="ltr"><main><h1>T</h1><div dir="rtl"><p>'
            'אמר רבי יוחנן משום רבי יוסי כל המענג את השבת נותנין לו נחלה בלי מצרים'
            "</p></div></main></html>")
    assert "TECH-008" not in codes(run_all(contexte(html)))


def test_edit_002_phrase_inachevee():
    html = ("<main><h1>T</h1><p>Cette phrase est suffisamment longue pour être "
            "examinée par le contrôle et se termine brusquement sans</p></main>")
    assert "EDIT-002" in codes(run_all(contexte(html)))


def test_edit_002_muet_sur_une_enumeration():
    """Un plan « 1. … 2. … » n'est pas une phrase inachevée."""
    html = ("<main><h1>T</h1><p>1. Le texte du Choul'han Aroukh 2. La question "
            "de la source 3. Les catégories de personnes 4. La conclusion</p></main>")
    assert "EDIT-002" not in codes(run_all(contexte(html)))


def test_edit_003_repetition_de_mot():
    html = ("<main><h1>T</h1><p>Il faut honorer le le Shabbat selon ses moyens, "
            "dit le Choul'han Aroukh.</p></main>")
    assert "EDIT-003" in codes(run_all(contexte(html)))


# ── EDIT-001 : constate, ne tranche pas ──────────────────────────────────

def test_edit_001_signale_le_melange_de_deux_graphies():
    html = ("<main><h1>T</h1><p>On honore le Shabbat selon ses moyens.</p>"
            "<p>Celui qui délecte le Chabbat reçoit une part sans limites.</p></main>")
    findings = [f for f in run_all(contexte(html)) if f.rule_code == "EDIT-001"]
    assert len(findings) == 1


def test_edit_001_ne_propose_aucune_correction():
    """Trancher entre deux translittérations attestées est une décision
    éditoriale qui revient au Rav (§4) : l'outil constate l'hésitation et
    donne les comptes du site, rien de plus."""
    html = ("<main><h1>T</h1><p>On honore le Shabbat selon ses moyens.</p>"
            "<p>Celui qui délecte le Chabbat reçoit une part sans limites.</p></main>")
    finding = next(f for f in run_all(contexte(html)) if f.rule_code == "EDIT-001")
    assert finding.proposed_correction is None
    assert finding.severity is Severity.P4_SUGGESTION
    assert finding.risk is Risk.MEDIUM
    assert "Shabbat" in finding.explanation and "Chabbat" in finding.explanation


def test_edit_001_muet_quand_la_page_est_coherente():
    html = ("<main><h1>T</h1><p>On honore le Shabbat selon ses moyens.</p>"
            "<p>Celui qui délecte le Shabbat reçoit une part sans limites.</p></main>")
    assert "EDIT-001" not in codes(run_all(contexte(html)))


def test_edit_001_ne_juge_pas_lhebreu_au_dictionnaire_francais():
    html = ("<main><h1>T</h1><p>On honore le Shabbat selon ses moyens.</p>"
            '<p class="he">Chabbat שבת</p></main>')
    assert "EDIT-001" not in codes(run_all(contexte(html)))


# ── Contrat commun à tous les contrôles ──────────────────────────────────

def test_aucun_controle_ne_modifie_les_blocs(page):
    """§4 : la phase d'audit propose, elle ne touche à rien."""
    ctx = contexte(page)
    avant = [(b.stable_id, b.sha256, b.raw_content) for b in ctx.blocks]
    run_all(ctx)
    assert [(b.stable_id, b.sha256, b.raw_content) for b in ctx.blocks] == avant


def test_tout_signalement_est_qualifie(page):
    abime = page.replace("Le devoir d'", "Le  devoir​ d'", 1)
    findings = run_all(contexte(abime))
    assert findings
    for f in findings:
        assert isinstance(f.severity, Severity)
        assert isinstance(f.risk, Risk)
        assert 0.0 < f.confidence <= 1.0
        assert f.explanation
        assert f.rule_code in REGISTRY
