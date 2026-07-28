# -*- coding: utf-8 -*-
"""Passe d'analyse des citations et cache des sources (§8, §15, §20)."""
import httpx
from sqlalchemy import select

from daat_audit.analyze import run_analyse
from daat_audit.crawler.crawl import run_crawl
from daat_audit.models import AuditFinding, AuditLog, Risk, SourceText
from daat_audit.sources import LocalProvider
from daat_audit.sources.cache import CachedProvider

# La page de test cite ce passage en l'attribuant à שבת קי״ט ע״א.
VRAI_TEXTE = "מתקנת עזרא שיהיו מכבסים בגדים בחמישי בשבת מפני כבוד השבת"


def _page(citation: str, ref: str = "שבת קי״ט ע״א") -> str:
    return (
        "<html><head><title>Siman 242</title></head><body><main>"
        "<h1>Siman 242</h1>"
        f'<blockquote class="text-source" dir="rtl">גמ\' {ref} : "{citation}"</blockquote>'
        "</main></body></html>"
    )


def _transport(html: str) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "HEAD")
        return httpx.Response(200, text=html)
    return httpx.MockTransport(handler)


def _provider() -> LocalProvider:
    return LocalProvider({"Shabbat.119a": VRAI_TEXTE})


def test_citation_exacte_ne_produit_aucun_signalement(session, settings):
    run_crawl(session, settings, transport=_transport(_page(VRAI_TEXTE)))
    findings = run_analyse(session, settings, provider=_provider())
    assert findings == []
    assert session.execute(select(AuditFinding)).scalars().all() == []


def test_citation_falsifiee_est_signalee_et_archivee(session, settings):
    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    run_crawl(session, settings, transport=_transport(_page(faux)))
    findings = run_analyse(session, settings, provider=_provider())

    assert findings, "la citation modifiée n'a pas été détectée"
    ligne = session.execute(select(AuditFinding)).scalars().first()
    assert ligne.rule_code == "CIT-001"
    assert ligne.risk is Risk.HALAKHIC
    assert ligne.proposed_correction is None      # §4 : jamais de correction
    assert ligne.source_text and "מכבסים" in ligne.source_text
    assert ligne.sources == "Shabbat.119a"        # source consultée, tracée
    assert ligne.block_id is not None


def test_dry_run_nécrit_rien(session, settings):
    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    run_crawl(session, settings, transport=_transport(_page(faux)))
    findings = run_analyse(session, settings, provider=_provider(), dry_run=True)

    assert findings, "le dry-run doit tout de même rapporter ce qu'il trouve"
    assert session.execute(select(AuditFinding)).scalars().all() == []


def test_lanalyse_est_journalisee(session, settings):
    run_crawl(session, settings, transport=_transport(_page(VRAI_TEXTE)))
    run_analyse(session, settings, provider=_provider())
    actions = [a.action for a in session.execute(select(AuditLog)).scalars().all()]
    assert "analyse.citations" in actions


def test_une_reference_absente_du_fournisseur_ne_produit_rien(session, settings):
    """Source injoignable ≠ citation fausse."""
    run_crawl(session, settings, transport=_transport(_page(VRAI_TEXTE)))
    assert run_analyse(session, settings, provider=LocalProvider({})) == []


# ── Cache des textes sources ─────────────────────────────────────────────

def test_le_cache_evite_de_redemander_le_meme_passage(session):
    source = CachedProvider(_provider(), session)
    assert source.fetch("Shabbat.119a").text == VRAI_TEXTE
    assert (source.hits, source.misses) == (0, 1)

    assert source.fetch("Shabbat.119a").text == VRAI_TEXTE
    assert (source.hits, source.misses) == (1, 1)


def test_le_cache_archive_les_editions_consultees(session):
    CachedProvider(_provider(), session).fetch("Shabbat.119a")
    ligne = session.execute(select(SourceText)).scalars().first()
    assert ligne.ref == "Shabbat.119a"
    assert ligne.version_title == "local"
    assert ligne.sha256 and ligne.fetched_at


def test_une_reference_absente_nest_pas_mise_en_cache(session):
    source = CachedProvider(_provider(), session)
    assert source.fetch("Berakhot.999a") is None
    assert session.execute(select(SourceText)).scalars().all() == []


# ── Rattachement de la référence par voisinage ───────────────────────────

# Sur le site, la référence annonce la citation depuis la prose qui précède ;
# le bloc hébreu lui-même n'en porte pas. Un premier essai sur une page réelle
# l'a montré sans ambiguïté : 79 blocs, 5 références, 8 citations, zéro paire.
def _page_annoncee(citation: str) -> str:
    return (
        "<html><head><title>Siman 242</title></head><body><main>"
        "<h1>Siman 242</h1>"
        "<p>La Guemara (Shabbat 119a) rapporte :</p>"
        f'<blockquote class="text-source" dir="rtl">"{citation}"</blockquote>'
        "</main></body></html>"
    )


def test_reference_annoncee_par_le_bloc_precedent(session, settings):
    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    run_crawl(session, settings, transport=_transport(_page_annoncee(faux)))
    findings = run_analyse(session, settings, provider=_provider())

    assert findings, "la référence du bloc précédent n'a pas été rattachée"
    assert "annonce la citation" in findings[0].explanation
    assert findings[0].confidence < 0.9, \
        "un rattachement par voisinage est une inférence : la confiance baisse"


def test_un_titre_de_section_arrete_le_rattachement(session, settings):
    """Une nouvelle section est un nouveau sujet : la référence d'avant ne la
    concerne plus, et lui rattacher la citation fabriquerait un faux positif."""
    html = (
        "<html><head><title>Siman 242</title></head><body><main>"
        "<h1>Siman 242</h1>"
        "<p>La Guemara (Shabbat 119a) rapporte :</p>"
        "<h2>Autre sujet</h2>"
        '<blockquote class="text-source" dir="rtl">'
        '"דבר אחר לגמרי שאין לו שום קשר עם הקודם כלל"</blockquote>'
        "</main></body></html>"
    )
    run_crawl(session, settings, transport=_transport(html))
    assert run_analyse(session, settings, provider=_provider()) == []
