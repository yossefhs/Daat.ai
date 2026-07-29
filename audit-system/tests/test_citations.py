# -*- coding: utf-8 -*-
"""Vérification des citations contre leur source (§8, §9, §20).

Réseau entièrement simulé : le fournisseur Sefaria est exercé par
``httpx.MockTransport``, le reste par le fournisseur local.
"""
import httpx
import pytest

from daat_audit.citations import BENINS, finding_de, verifier_citation
from daat_audit.hebrew import Verdict
from daat_audit.models import Risk, Severity
from daat_audit.quotes import Quote, extract_quotes
from daat_audit.references import ParsedRef
from daat_audit.sources import LocalProvider, SefariaProvider

# Texte réel de ברכות ל״ד ע״א sur le point litigieux du siman 68.
BERAKHOT_34A = (
    "ואם בא לשוח בסוף כל ברכה וברכה ובתחלת כל ברכה וברכה "
    "מלמדין אותו שלא ישחה"
)
ISAIE_58 = "וְקָרָאתָ לַשַּׁבָּת עֹנֶג לִקְדוֹשׁ ה׳ מְכֻבָּד וְכִבַּדְתּוֹ מֵעֲשׂוֹת דְּרָכֶיךָ"


def ref_berakhot() -> ParsedRef:
    return ParsedRef(raw_text="ברכות ל״ד ע״א", work="Berakhot",
                     daf="34", amud="a", confidence=0.9)


def quote(text: str) -> Quote:
    return Quote(text=text, line=1, context="")


# ── Le cas réel du siman 68 ──────────────────────────────────────────────

def test_verbe_change_est_signale():
    """La page citait « ואם בא לומר » là où la Guemara porte « ואם בא לשוח ».
    Un verbe changé transforme une interdiction de s'incliner en permission
    de parler — c'est le signalement le plus grave que l'outil doit produire."""
    provider = LocalProvider({"Berakhot.34a": BERAKHOT_34A})
    resultat = verifier_citation(
        quote("ואם בא לומר בסוף כל ברכה וברכה"), [ref_berakhot()], provider
    )
    assert resultat is not None
    assert resultat.verdict not in BENINS

    finding = finding_de(resultat, "OH-68-LAMDAN-FR-H001")
    assert finding is not None
    assert finding.rule_code == "CIT-001"
    assert finding.risk is Risk.HALAKHIC
    assert finding.severity in (Severity.P0_CRITICAL, Severity.P1_MAJOR,
                                Severity.P2_SIGNIFICANT)


def test_aucune_correction_nest_jamais_proposee():
    """§4 : réécrire une citation, c'est trancher une question de contenu."""
    provider = LocalProvider({"Berakhot.34a": BERAKHOT_34A})
    resultat = verifier_citation(
        quote("ואם בא לומר בסוף כל ברכה וברכה"), [ref_berakhot()], provider
    )
    finding = finding_de(resultat, "B1")
    assert finding.proposed_correction is None


def test_citation_litterale_ne_produit_aucun_signalement():
    provider = LocalProvider({"Berakhot.34a": BERAKHOT_34A})
    resultat = verifier_citation(
        quote("ואם בא לשוח בסוף כל ברכה וברכה"), [ref_berakhot()], provider
    )
    assert resultat.verdict in BENINS
    assert finding_de(resultat, "B1") is None


def test_graphie_pleine_ne_produit_aucun_signalement():
    """Isaïe 58:13 cité mot pour mot, graphie pleine contre défective."""
    provider = LocalProvider({"Isaiah.58.13": ISAIE_58})
    ref = ParsedRef(raw_text="ישעיה נח", work="Isaiah", siman="58",
                    seif="13", confidence=0.8)
    ref.sefaria_ref = lambda: "Isaiah.58.13"        # type: ignore[method-assign]
    resultat = verifier_citation(
        quote("וקראת לשבת עונג לקדוש ה׳ מכובד"), [ref], provider
    )
    assert resultat.verdict is Verdict.DIFF_ORTHOGRAPHE
    assert finding_de(resultat, "B1") is None


# ── Absence : fabriquée ou mal référencée ? ──────────────────────────────

def test_citation_absente_mais_retrouvee_ailleurs():
    """Distinction essentielle : le texte existe, c'est la référence qui est
    fausse. La correction à faire n'est pas la même que pour une fabrication."""
    provider = LocalProvider({
        "Berakhot.34a": BERAKHOT_34A,
        "Shabbat.118b": "כל המענג את השבת נותנין לו נחלה בלי מצרים ומשביעין אותו",
    })
    resultat = verifier_citation(
        quote("כל המענג את השבת נותנין לו נחלה בלי מצרים"),
        [ref_berakhot()], provider,
    )
    assert resultat.verdict is Verdict.DIFFERENCE_SUBSTANTIELLE
    assert resultat.found_elsewhere == ["Shabbat.118b"]

    finding = finding_de(resultat, "B1")
    assert "Shabbat.118b" in finding.explanation
    assert "la référence semble être celle qui est erronée" in finding.explanation


def test_citation_introuvable_partout_reste_prudente():
    """Introuvable n'est pas « fabriquée » : le système décrit ce qu'il
    constate et renvoie au Rav, sans qualifier l'intention."""
    provider = LocalProvider({"Berakhot.34a": BERAKHOT_34A})
    resultat = verifier_citation(
        quote("דבר שלא נאמר מעולם בשום מקום ואין לו שום מקור כלל"),
        [ref_berakhot()], provider,
    )
    finding = finding_de(resultat, "B1")
    assert "introuvable ailleurs" in finding.explanation
    assert "à vérifier par le Rav" in finding.explanation
    assert finding.severity is Severity.P0_CRITICAL


# ── Plusieurs références voisines ────────────────────────────────────────

def test_la_reference_la_plus_favorable_est_retenue():
    """Retenir la première référence venue déclarerait fausse une citation
    exacte au seul motif qu'une autre référence traîne dans le même bloc."""
    provider = LocalProvider({
        "Berakhot.34a": BERAKHOT_34A,
        "Shabbat.118b": "כל המענג את השבת נותנין לו נחלה בלי מצרים",
    })
    autre = ParsedRef(raw_text="שבת קי״ח:", work="Shabbat",
                      daf="118", amud="b", confidence=0.9)
    resultat = verifier_citation(
        quote("כל המענג את השבת נותנין לו נחלה בלי מצרים"),
        [ref_berakhot(), autre], provider,
    )
    assert resultat.verdict in BENINS
    assert finding_de(resultat, "B1") is None


def test_sans_reference_exploitable_aucun_verdict():
    """Pas de référence = pas de jugement. Le système ne devine pas la source."""
    provider = LocalProvider({"Berakhot.34a": BERAKHOT_34A})
    sans_ref = ParsedRef(raw_text="la Guemara", work=None, confidence=0.3)
    assert verifier_citation(quote("טקסט כלשהו ארוך מספיק"), [sans_ref], provider) is None
    assert verifier_citation(quote("טקסט כלשהו ארוך מספיק"), [], provider) is None


def test_source_injoignable_ne_produit_aucun_verdict():
    """Un service tiers indisponible ne doit pas se traduire en accusation."""
    resultat = verifier_citation(
        quote("ואם בא לשוח בסוף כל ברכה וברכה"), [ref_berakhot()], LocalProvider({})
    )
    assert resultat is None


# ── Convention typographique ─────────────────────────────────────────────

def test_un_resume_annonce_nest_pas_juge():
    """C'est la convention qui rend un verdict possible : les guillemets sont
    réservés au littéral, une condensation est annoncée et n'est pas jugée."""
    html = ('<p>Le Mehaber enseigne — <em>résumé</em> : '
            '"כל המענג את השבת נותנין לו נחלה בלי מצרים ומשביעין אותו"</p>')
    assert extract_quotes(html) == []


def test_une_citation_annoncee_est_bien_extraite():
    html = ('<p>וז״ל הגמרא : "כל המענג את השבת נותנין לו נחלה בלי מצרים"</p>')
    citations = extract_quotes(html)
    assert len(citations) == 1
    assert citations[0].text.startswith("כל המענג")


def test_un_terme_technique_entre_guillemets_nest_pas_une_citation():
    html = '<p>La notion de "תשמישי קדושה" est centrale ici.</p>'
    assert extract_quotes(html) == []


def test_le_json_ld_nest_pas_du_contenu():
    """Métadonnée SEO : elle cite souvent un fragment, mais n'est pas affichée."""
    html = ('<script type="application/ld+json">{"description": '
            '"כל המענג את השבת נותנין לו נחלה בלי מצרים ומשביעין"}</script>')
    assert extract_quotes(html) == []


# ── Fournisseur Sefaria (réseau simulé) ──────────────────────────────────

def _sefaria_transport(segments, versions=("Vilna", "William Davidson")):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "POST")
        chemin = request.url.path
        if chemin.startswith("/api/texts/versions/"):
            return httpx.Response(200, json=[
                {"language": "he", "versionTitle": v} for v in versions
            ])
        if chemin.startswith("/api/v3/texts/"):
            return httpx.Response(200, json={"versions": [
                {"language": "he", "versionTitle": versions[0], "text": segments}
            ]})
        if chemin.startswith("/api/search-wrapper"):
            return httpx.Response(200, json={"hits": {"hits": [
                {"_source": {"ref": "Shabbat 118b"}}
            ]}})
        return httpx.Response(404)
    return httpx.MockTransport(handler)


def test_sefaria_demande_toutes_les_editions_hebraiques(settings):
    """L'édition Davidson diffère du Vilna : comparer à une seule fabrique
    des faux positifs. L'URL doit donc porter plusieurs « version= »."""
    vues = []

    def handler(request: httpx.Request) -> httpx.Response:
        vues.append(str(request.url))
        if request.url.path.startswith("/api/texts/versions/"):
            return httpx.Response(200, json=[
                {"language": "he", "versionTitle": "Vilna"},
                {"language": "he", "versionTitle": "William Davidson"},
            ])
        return httpx.Response(200, json={"versions": [
            {"language": "he", "versionTitle": "Vilna", "text": [BERAKHOT_34A]}
        ]})

    with SefariaProvider(settings, transport=httpx.MockTransport(handler),
                         delay_seconds=0) as provider:
        document = provider.fetch("Berakhot.34a")

    assert document and BERAKHOT_34A in document.text
    url_texte = next(u for u in vues if "/api/v3/texts/" in u)
    assert url_texte.count("version=") >= 3      # défaut + les deux éditions


def test_sefaria_segments_imbriques_sont_aplatis(settings):
    with SefariaProvider(settings, delay_seconds=0,
                         transport=_sefaria_transport([["a", ["ב"]], "ג"])) as p:
        document = p.fetch("Berakhot.34a")
    assert document.segments == ["a", "ב", "ג"]


def test_sefaria_reference_inexistante_retourne_none(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/api/texts/versions/"):
            return httpx.Response(200, json=[])
        return httpx.Response(200, json={"error": "Ref does not exist"})

    with SefariaProvider(settings, transport=httpx.MockTransport(handler),
                         delay_seconds=0) as provider:
        assert provider.fetch("Berakhot.999a") is None


def test_sefaria_indisponible_ne_leve_pas(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("réseau coupé")

    with SefariaProvider(settings, transport=httpx.MockTransport(handler),
                         delay_seconds=0) as provider:
        assert provider.fetch("Berakhot.34a") is None
        assert provider.search("כל המענג את השבת נותנין לו") == []


# ── Étiquettes : ni en-tête ni légende ne sont des citations ─────────────

def test_un_entete_de_reference_nest_pas_une_citation():
    """Le juger comme littéral revenait à demander à Sefaria de contenir mot
    pour mot le titre d'un siman."""
    html = ('<blockquote class="text-source" dir="rtl">'
            "שולחן ערוך אורח חיים סימן רמ״ב סעיף א'</blockquote>")
    assert extract_quotes(html, marked=True) == []


def test_une_legende_bibliographique_nest_pas_une_citation():
    html = ('<blockquote class="text-source" dir="rtl">'
            "עם נושאי כלים: ביאורי שו״ע, ט״ז, מג״א, מקורות והערות</blockquote>")
    assert extract_quotes(html, marked=True) == []


def test_une_vraie_citation_survit_au_filtre():
    """Le filtre doit écarter les étiquettes sans rendre l'outil aveugle."""
    html = ('<blockquote class="text-source" dir="rtl">'
            "אָמַר רַבִּי עֲקִיבָא: עֲשֵׂה שַׁבַּתְּךָ חֹל וְאַל תִּצְטָרֵךְ לַבְּרִיּוֹת"
            "</blockquote>")
    assert len(extract_quotes(html, marked=True)) == 1


def test_une_citation_citant_une_source_reste_une_citation():
    """Une vraie citation peut nommer un ouvrage sans devenir une étiquette."""
    html = ('<blockquote class="text-source" dir="rtl">'
            "כתב המג״א דהא דאמרינן דצריך לכבד את השבת היינו במי שידו משגת ולא באחר"
            "</blockquote>")
    assert len(extract_quotes(html, marked=True)) == 1


def test_une_reference_fausse_nest_pas_classee_critique():
    """Le texte existe mot pour mot ailleurs : c'est un défaut de référence,
    pas une falsification. Les mettre au même niveau P0 confondait « la page
    invente une source » et « la page se trompe de folio »."""
    provider = LocalProvider({
        "Berakhot.34a": BERAKHOT_34A,
        "Shabbat.118b": "כל המענג את השבת נותנין לו נחלה בלי מצרים ומשביעין אותו",
    })
    resultat = verifier_citation(
        quote("כל המענג את השבת נותנין לו נחלה בלי מצרים"), [ref_berakhot()], provider
    )
    assert resultat.found_elsewhere == ["Shabbat.118b"]
    assert finding_de(resultat, "B1").severity is Severity.P2_SIGNIFICANT


def test_une_reference_inferee_ne_fonde_pas_un_signalement_critique():
    provider = LocalProvider({"Berakhot.34a": BERAKHOT_34A})
    resultat = verifier_citation(
        quote("דבר שלא נאמר מעולם בשום מקום ואין לו שום מקור כלל"),
        [ref_berakhot()], provider,
    )
    assert finding_de(resultat, "B1").severity is Severity.P0_CRITICAL
    par_voisinage = finding_de(resultat, "B1", par_voisinage=True)
    assert par_voisinage.severity is Severity.P1_MAJOR
