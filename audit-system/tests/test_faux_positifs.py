# -*- coding: utf-8 -*-
"""Non-régression sur les mécanismes qui ont produit les faux positifs (§8).

Cent vingt-trois signalements ont été relus un à un par le Rav. Un seul était
une erreur réelle ; soixante-huit étaient des faux positifs et quarante-six des
variantes légitimes. Ce fichier fixe, cas par cas, ce qui les produisait, pour
que le moteur ne puisse pas y revenir sans qu'un test le dise.

Chaque test porte le mécanisme, pas le symptôme : corriger un symptôme sans
nommer sa cause laisse la cause libre de reparaître ailleurs.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from daat_audit.citations import (            # noqa: E402
    NEEDS_SOURCE_VERIFICATION,
    CitationResult,
    finding_de,
)
from daat_audit.decisions import (            # noqa: E402
    Decision,
    Registre,
    empreinte,
)
from daat_audit.hebrew import (               # noqa: E402
    MIN_MOTS_SUIVIS,
    Verdict,
    compare,
    mots_suivis_en_commun,
)
from daat_audit.models import Severity        # noqa: E402
from daat_audit.quotes import est_etiquette   # noqa: E402
from daat_audit.references import ParsedRef   # noqa: E402
from daat_audit.quotes import Quote           # noqa: E402


# Deux passages hébreux authentiques et sans le moindre rapport l'un avec
# l'autre. Ils sont la matière du principal mécanisme : le taux de similarité
# calculé sur la suite des consonnes les rapprochait à 79 %.
CITATION_ETRANGERE = "חמורים דברי סופרים יותר מדברי תורה"
FOLIO_SANS_RAPPORT = (
    "תנו רבנן אין מדליקין בטבל טמא בחול ואין צריך לומר בשבת כיוצא בו אין מדליקין "
    "בנפט לבן בחול ואין צריך לומר בשבת בשלמא נפט לבן מפני שהוא עף אבל טבל טמא "
    "מאי טעמא אמר קרא ואני הנה נתתי לך את משמרת תרומתי"
)


# ── A. Le taux sur les consonnes n'est pas une preuve ────────────────────

def test_deux_textes_sans_rapport_ne_sont_pas_une_variante_possible():
    """« Variante possible » affirme que deux textes sont deux états du même
    passage. Un taux calculé sur la suite des consonnes ne l'établit pas :
    l'hébreu n'a que vingt-deux lettres, et deux textes étrangers l'un à
    l'autre y atteignent couramment 0,75 — la bande même du verdict."""
    verdict, _, detail = compare(CITATION_ETRANGERE, FOLIO_SANS_RAPPORT)
    assert verdict is not Verdict.VARIANTE_POSSIBLE
    assert verdict is Verdict.DIFFERENCE_SUBSTANTIELLE


def test_la_similarite_rendue_est_mesuree_et_non_bornee():
    """``quick_ratio`` compare des multi-ensembles de caractères : il ignore
    l'ordre. S'en servir comme mesure finale faisait ressortir 0,91 là où la
    similarité vraie est 0,875 — et la position retenue avait, elle, un ratio
    réel de 0,54. Une borne supérieure n'est pas une mesure."""
    from daat_audit.hebrew import _best_window, letters_only
    import difflib

    aiguille = letters_only(CITATION_ETRANGERE)
    meule = letters_only(FOLIO_SANS_RAPPORT)
    rendu, fenetre = _best_window(aiguille, meule)
    reel = difflib.SequenceMatcher(None, aiguille, fenetre).ratio()
    assert abs(rendu - reel) < 1e-9, "la valeur rendue doit être le ratio de la fenêtre rendue"


def test_un_mot_remplace_reste_detecte():
    """Le garde-fou ne doit pas éteindre le contrôle : ici, « הקדוש ברוך הוא »
    est devenu « הבורא » — un vrai mot remplacé, à retrouver. Cas réel du
    siman 242."""
    source = (
        "מאי כי חדות ה' היא מעוזכם אמר רבי יוחנן משום רבי אליעזר ברבי שמעון "
        "אמר להם הקדוש ברוך הוא לישראל בני לוו עלי וקדשו קדושת היום והאמינו בי ואני פורע"
    )
    verdict, _, detail = compare(
        "אמר להם הבורא לישראל בני לוו עלי וקדשו קדשת היום והאמינו בי ואני פורע", source
    )
    assert verdict is Verdict.MOT_REMPLACE
    assert "הבורא" in detail


def test_les_mots_suivis_separent_le_bruit_du_signal():
    """Mesure de calibrage : les variantes reconnues par le Rav partagent une
    suite de mots avec leur source, les faux positifs n'en partagent aucune."""
    assert mots_suivis_en_commun(CITATION_ETRANGERE, FOLIO_SANS_RAPPORT) < MIN_MOTS_SUIVIS
    assert mots_suivis_en_commun(
        "כל המענג את השבת נותנין לו נחלה בלי מצרים",
        "אמר רבי יוחנן כל המענג את השבת נותנין לו נחלה בלי מצרים ומשביעין אותו",
    ) >= MIN_MOTS_SUIVIS


# ── B. Un titre rédactionnel n'est pas une citation ──────────────────────

def test_un_intertitre_numerote_nest_pas_une_citation():
    """« חידוש ד — … » est l'auteur qui numérote son propre exposé. Comparé à
    une source, il en est évidemment absent : sept faux positifs venaient de
    là."""
    for titre in (
        "חידוש ד — הבחנה בין כלים, בהמה, ושדה (246:6-7)",
        "חידוש ד — מהדורא בתרא: כנות אינטלקטואלית (édition Kehot)",
        "חידוש ג — הצגה מבנית של מחלוקת בית שמאי-בית הלל על שביתת כלים (246:1)",
    ):
        assert est_etiquette(titre), titre


def test_une_vraie_phrase_commencant_par_le_meme_mot_reste_jugee():
    """Le motif est étroit à dessein : un mot d'appareil suivi d'une lettre
    d'ordre isolée et d'un tiret. Une phrase qui commence par le même mot
    n'est pas un titre."""
    assert not est_etiquette(
        "חידוש גדול יש בדברי הרמב״ם בהלכות שבת שאין כמותו בשאר הפוסקים כלל"
    )
    assert not est_etiquette(
        "יסוד הדבר שאין ישראל צריכין שמירה בשבת שהשבת מגנה עלינו מכל פגע רע"
    )


# ── C. Provenance de la référence ────────────────────────────────────────

def _resultat(mots_communs: int) -> CitationResult:
    return CitationResult(
        quote=Quote(text=CITATION_ETRANGERE, line=1, context=""),
        ref=ParsedRef(raw_text="שבת ל׳:", work="Shabbat", daf="30", amud="b",
                      confidence=0.9),
        verdict=Verdict.DIFFERENCE_SUBSTANTIELLE, ratio=0.79,
        detail="aucune correspondance nette", source_text=FOLIO_SANS_RAPPORT,
        found_elsewhere=None, mots_communs=mots_communs,
    )


def test_une_reference_inferee_sans_trace_met_en_cause_le_rattachement():
    """Le cas le plus fréquent du lot : la prose voisine mentionnait un folio,
    le moteur l'a rattaché à une citation qui n'en vient pas, et le signalement
    reprochait au texte l'erreur du rattachement."""
    finding = finding_de(_resultat(0), "B1", par_voisinage=True)
    assert finding is not None, "le signalement subsiste — rien n'est masqué"
    assert finding.subcategory == NEEDS_SOURCE_VERIFICATION
    assert finding.severity is not Severity.P0_CRITICAL
    assert "rattachement" in finding.explanation
    # Rien n'est affirmé du texte de la page.
    assert "fabriqu" not in finding.explanation.lower()


def test_une_reference_lue_dans_le_bloc_garde_toute_sa_force():
    """L'abstention porte sur l'inférence, pas sur le contrôle. Une référence
    lue dans le bloc cité fonde toujours un signalement critique."""
    finding = finding_de(_resultat(0), "B1", par_voisinage=False)
    assert finding.severity is Severity.P0_CRITICAL


def test_une_reference_inferee_avec_trace_reste_jugee_normalement():
    """S'il existe des mots suivis en commun, le rattachement tient : l'écart
    porte alors sur le texte, et le signalement doit le dire."""
    finding = finding_de(_resultat(MIN_MOTS_SUIVIS + 3), "B1", par_voisinage=True)
    assert finding.subcategory != NEEDS_SOURCE_VERIFICATION


# ── D. Le registre des décisions ─────────────────────────────────────────

def _decision(code: str, resolved: bool) -> tuple[Registre, str]:
    emp = empreinte(siman=263, niveau="lamdan", regle="CIT-001",
                    citation="הרגיל בנר הויין ליה בנים תלמידי חכמים", ref="Shabbat.23b")
    reg = Registre()
    reg.ajouter(Decision(id=495, decision=code, reviewer_role="rav",
                         source="DAAT-TRIAGE v1", resolved=resolved, empreinte=emp))
    return reg, emp


def test_une_variante_acceptee_ne_revient_pas():
    reg, emp = _decision("accepted_variant", True)
    assert reg.est_close(emp)


def test_un_faux_positif_ne_revient_pas():
    reg, emp = _decision("false_positive", True)
    assert reg.est_close(emp)


def test_un_cas_laisse_au_rav_reste_ouvert():
    """Une question laissée au Rav n'est pas une question réglée : le registre
    ne peut pas la clore, et le signalement continue d'être produit."""
    reg, emp = _decision("needs_rav_review", False)
    assert not reg.est_close(emp)
    assert [d.id for d in reg.ouverts()] == [495]


def test_la_decision_ne_vaut_que_pour_ce_passage():
    """Le cœur du dispositif. Au siman 263, « חביות » contre « גרבי » a été jugé
    variante d'édition. Inscrire ce couple dans les variantes connues aurait
    valu partout — or ailleurs la substitution peut porter un sens. La décision
    est donc attachée à une empreinte : le même texte à un autre endroit, ou
    confronté à une autre source, reste examiné."""
    reg, emp = _decision("accepted_variant", True)
    assert reg.est_close(emp)
    ailleurs = empreinte(siman=264, niveau="lamdan", regle="CIT-001",
                         citation="הרגיל בנר הויין ליה בנים תלמידי חכמים",
                         ref="Shabbat.23b")
    autre_source = empreinte(siman=263, niveau="lamdan", regle="CIT-001",
                             citation="הרגיל בנר הויין ליה בנים תלמידי חכמים",
                             ref="Shabbat.25b")
    assert not reg.est_close(ailleurs)
    assert not reg.est_close(autre_source)


def test_lhistorique_est_cumulatif():
    """Aucune décision n'est effacée ; la dernière fait foi."""
    reg, emp = _decision("false_positive", True)
    reg.ajouter(Decision(id=495, decision="needs_rav_review", reviewer_role="rav",
                         source="revue ultérieure", resolved=False, empreinte=emp))
    assert len(reg) == 2
    assert not reg.est_close(emp)
    assert reg.derniere(emp).decision == "needs_rav_review"


# ── E. Le registre livré ─────────────────────────────────────────────────

def test_le_registre_livre_porte_les_123_decisions():
    reg = Registre.charger()
    toutes = [d for suite in reg.par_empreinte.values() for d in suite]
    comptes: dict[str, int] = {}
    for d in toutes:
        comptes[d.decision] = comptes.get(d.decision, 0) + 1
    assert len(toutes) == 123
    assert comptes == {"false_positive": 68, "accepted_variant": 46,
                       "needs_rav_review": 8, "error": 1}
    assert [d.id for d in reg.ouverts()] == [395, 396, 431, 434, 447, 487, 491, 496]
    assert [d.id for d in toutes if d.decision == "error"] == [504]


def test_les_cas_rav_ne_sont_pas_resolus():
    reg = Registre.charger()
    for d in reg.ouverts():
        assert d.resolved is False
        assert d.reviewer_role == "rav"
