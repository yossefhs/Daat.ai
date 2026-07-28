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


# ── Idempotence ──────────────────────────────────────────────────────────

def test_relancer_lanalyse_ne_duplique_pas_les_signalements(session, settings):
    """Sans cela, chaque passe recrée les signalements — et un signalement déjà
    jugé réapparaîtrait à l'état NEW, à rejuger indéfiniment."""
    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    run_crawl(session, settings, transport=_transport(_page(faux)))

    premiers = run_analyse(session, settings, provider=_provider())
    assert premiers
    total = len(session.execute(select(AuditFinding)).scalars().all())

    seconds = run_analyse(session, settings, provider=_provider())
    assert seconds == [], "la seconde passe ne doit rien signaler de nouveau"
    assert len(session.execute(select(AuditFinding)).scalars().all()) == total


def test_une_decision_survit_a_une_nouvelle_analyse(session, settings):
    """Le point qui compte vraiment : le travail du relecteur est préservé."""
    from daat_audit.workflow import Role, appliquer

    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    run_crawl(session, settings, transport=_transport(_page(faux)))
    run_analyse(session, settings, provider=_provider())

    # Le périmètre de test couvre trois simanim et le mock sert la même page
    # pour chacun : il y a donc un signalement par page, tous légitimes.
    ligne = session.execute(select(AuditFinding)).scalars().first()
    appliquer(session, ligne, "escalate", Role.EDITOR, "yossef")

    run_analyse(session, settings, provider=_provider())
    apres = session.get(AuditFinding, ligne.id)
    assert apres.status.value == "RABBINIC_REVIEW_REQUIRED"


def test_une_page_modifiee_produit_bien_un_nouveau_signalement(session, settings):
    """La déduplication ne doit pas rendre le système aveugle à un changement."""
    run_crawl(session, settings, transport=_transport(_page(VRAI_TEXTE)))
    assert run_analyse(session, settings, provider=_provider()) == []

    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    run_crawl(session, settings, transport=_transport(_page(faux)))
    assert run_analyse(session, settings, provider=_provider())


# ── Référence implicite au siman de la page ──────────────────────────────

def _page_mehaber(citation: str, annonce: str = "Le texte du Choul'han Aroukh") -> str:
    """La page EST le siman : le bloc n'énonce aucune référence, il est
    seulement annoncé comme le texte du Mehaber. Motif le plus fréquent."""
    return (
        "<html><head><title>Siman 242</title></head><body><main>"
        f"<h1>Siman 242</h1><h3>{annonce}</h3>"
        f'<blockquote class="text-source" dir="rtl">"{citation}"</blockquote>'
        "</main></body></html>"
    )


def _siman_entier() -> LocalProvider:
    return LocalProvider({"Shulchan_Arukh,_Orach_Chayim.242": VRAI_TEXTE})


def test_reference_deduite_de_la_page_sur_indice_de_mehaber(session, settings):
    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    run_crawl(session, settings, transport=_transport(_page_mehaber(faux)))
    findings = run_analyse(session, settings, provider=_siman_entier())
    assert findings, "le texte du Mehaber doit être rattaché au siman de la page"
    assert findings[0].confidence < 0.6      # inférence : confiance abaissée


def test_sans_indice_aucune_reference_nest_supposee(session, settings):
    """Sans mention du Mehaber, supposer le siman comparerait toute citation
    de Guemara au Choulhan Aroukh et la déclarerait absente."""
    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    html = _page_mehaber(faux, annonce="Une histoire rapportée par la Guemara")
    run_crawl(session, settings, transport=_transport(html))
    assert run_analyse(session, settings, provider=_siman_entier()) == []


def test_un_indice_de_rama_fait_renoncer(session, settings):
    """Le Rama est une couche distincte que Sefaria ne sert pas sous un nom
    vérifié : mieux vaut se taire que d'inventer une référence."""
    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    html = _page_mehaber(faux, annonce="Le texte du Rama (הגה) sur le Choul'han Aroukh")
    run_crawl(session, settings, transport=_transport(html))
    assert run_analyse(session, settings, provider=_siman_entier()) == []


# ── Frontière de section : rang du titre ─────────────────────────────────

def _page_intertitre(balise: str) -> str:
    faux = VRAI_TEXTE.replace("מכבסים", "אוכלים")
    return (
        "<html><head><title>Siman 242</title></head><body><main><h1>S</h1>"
        "<p>La Guemara (Shabbat 119a) rapporte deux enseignements :</p>"
        f"<{balise}>Enseignement A</{balise}>"
        f'<blockquote class="text-source" dir="rtl">"{faux}"</blockquote>'
        "</main></body></html>"
    )


def test_un_intertitre_h3_ne_coupe_pas_le_lien_avec_lannonce(session, settings):
    """Le site emploie h3 pour les intertitres d'une même sougya
    (« Enseignement A », « Enseignement B ») : les traiter comme des frontières
    faisait perdre l'essentiel des citations de Guemara."""
    run_crawl(session, settings, transport=_transport(_page_intertitre("h3")))
    assert run_analyse(session, settings, provider=_provider())


def test_un_titre_de_section_h2_coupe_bien_le_lien(session, settings):
    """h2 marque une section numérotée : un vrai changement de sujet."""
    run_crawl(session, settings, transport=_transport(_page_intertitre("h2")))
    assert run_analyse(session, settings, provider=_provider()) == []


def test_une_reference_absente_nest_demandee_quune_fois(session):
    """Un séif qui n'existe pas ne se met pas à exister : sans ce garde, la
    même requête 404 repartait des dizaines de fois vers Sefaria."""
    appels = []

    class Comptant(LocalProvider):
        def fetch(self, ref):
            appels.append(ref)
            return super().fetch(ref)

    source = CachedProvider(Comptant({}), session)
    assert source.fetch("Shulchan_Arukh,_Orach_Chayim.253.8") is None
    assert source.fetch("Shulchan_Arukh,_Orach_Chayim.253.8") is None
    assert len(appels) == 1


# ── Seul un conteneur de source annonce une citation ─────────────────────

def _bloc(selecteur: str):
    from daat_audit.models import ContentBlock
    return ContentBlock(stable_id="X", order_index=1,
                        block_type=None, raw_content="", normalized_content="",
                        css_selector=selecteur, sha256="x")


def test_conteneur_de_source_reconnu():
    from daat_audit.analyze import est_conteneur_source
    for sel in ("body > main > blockquote.text-source",
                "body > main > div.sacred-text.he",
                "body > main > p.sa-he"):
        assert est_conteneur_source(_bloc(sel)), sel


def test_prose_hebraique_de_lauteur_nest_pas_un_conteneur_de_source():
    """Au niveau lamdan la page est largement rédigée en hébreu par l'auteur
    (« שורש הסוגיא : … », « חקירה : … ») : la traiter comme une citation
    littérale produisait l'essentiel du bruit — 231 des 352 signalements
    venaient de ce seul niveau, dont 25 seulement d'un vrai conteneur."""
    from daat_audit.analyze import est_conteneur_source
    for sel in ("body > main > p.he", "body > main > div.rishon-card",
                "body > main > p", "body > main > table.compare-table"):
        assert not est_conteneur_source(_bloc(sel)), sel


def test_la_prose_hebraique_reste_verifiee_si_elle_cite_entre_guillemets():
    """Écarter le conteneur ne rend pas aveugle : une citation dûment marquée
    dans cette prose est toujours extraite."""
    from daat_audit.quotes import extract_quotes
    html = ('רש״י (שמות כ ח): " תנו לב לזכור תמיד את יום השבת שאם נזדמן לך חפץ יפה "')
    assert len(extract_quotes(html, marked=False)) == 1


def test_le_niveau_4_est_rapporte_au_choulhan_aroukh_harav(session, settings):
    """Le niveau 4 expose la shita de l'Admour HaZaken : le comparer au texte
    du Mehaber rendait « variante » sur des pages entières."""
    from daat_audit.analyze import reference_implicite_du_siman
    from daat_audit.models import ContentBlock, Page

    bloc = _bloc("p.sa-he")
    bloc.normalized_content = "Le texte du Choul'han Aroukh, siman 242"
    for niveau, attendu in (("daat-harav", "Shulchan_Arukh_HaRav,_Orach_Chayim.242"),
                            ("base", "Shulchan_Arukh,_Orach_Chayim.242")):
        page = Page(url="u", siman=242, langue="fr", niveau=niveau)
        ref = reference_implicite_du_siman(page, bloc, [])
        assert ref is not None and ref.sefaria_ref() == attendu
