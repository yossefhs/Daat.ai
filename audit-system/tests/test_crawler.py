# -*- coding: utf-8 -*-
"""Crawler (§20) : versionnage, détection de changement, redirections, 404.

Réseau entièrement simulé par httpx.MockTransport.
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy import select

from daat_audit.crawler.crawl import run_crawl
from daat_audit.crawler.urls import parse_simanim_arg, perimeter_urls
from daat_audit.models import (
    AuditFinding,
    ContentBlock,
    CrawlJobStatus,
    Page,
    PageAuditStatus,
    PageVersion,
    ParsedReference,
)


def _page_html(siman: int, body: str = "contenu initial") -> str:
    return (
        f"<html><head><title>Siman {siman} — Niveau 1</title></head>"
        f"<body><h1>Siman {siman}</h1><p>{body}</p>"
        f'<a href="/oh/{siman + 1}/base">suivant</a></body></html>'
    )


def _handler(content_by_siman: dict[int, str], missing: set[int] = frozenset(),
             redirect: dict[str, str] | None = None):
    """Handler simulé. Asserte l'invariant central de la Phase 1 au niveau
    HTTP : le système ne fait QUE lire le site (GET/HEAD). Toute autre
    méthode ferait échouer le test immédiatement."""
    redirect = redirect or {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "HEAD"), \
            f"méthode {request.method} interdite : le crawler est en lecture seule"
        url = str(request.url)
        if url in redirect:
            return httpx.Response(301, headers={"location": redirect[url]})
        for siman, body in content_by_siman.items():
            if url.endswith(f"/oh/{siman}/base"):
                if siman in missing:
                    return httpx.Response(404, text="not found")
                return httpx.Response(200, text=_page_html(siman, body))
        return httpx.Response(404, text="not found")

    return handler


def _transport(content_by_siman: dict[int, str], missing: set[int] = frozenset(),
               redirect: dict[str, str] | None = None) -> httpx.MockTransport:
    return httpx.MockTransport(_handler(content_by_siman, missing, redirect))


def test_perimetre_urls(settings):
    urls = perimeter_urls(settings)
    assert len(urls) == 3  # 242-244 dans la config de test
    assert urls[0] == (242, "https://daattorah.com/oh/242/base")


def test_parse_simanim():
    assert parse_simanim_arg("242-245") == [242, 243, 244, 245]
    assert parse_simanim_arg("250,242,242") == [242, 250]


def test_premier_crawl_cree_pages_et_versions(session, settings):
    transport = _transport({242: "a", 243: "b", 244: "c"})
    job = run_crawl(session, settings, transport=transport)

    assert job.status is CrawlJobStatus.DONE
    assert job.pages_total == 3 and job.pages_ok == 3 and job.pages_failed == 0

    pages = list(session.execute(select(Page).order_by(Page.siman)).scalars())
    assert [p.siman for p in pages] == [242, 243, 244]
    assert all(p.audit_status is PageAuditStatus.CRAWLED for p in pages)
    assert all(p.titre and str(p.siman) in p.titre for p in pages)

    versions = list(session.execute(select(PageVersion)).scalars())
    assert len(versions) == 3
    assert all(v.is_change is False for v in versions)
    assert all(v.html_raw and v.text_clean and v.text_sha256 for v in versions)


def test_contenu_identique_ne_duplique_pas_les_versions(session, settings):
    transport = _transport({242: "stable", 243: "stable", 244: "stable"})
    run_crawl(session, settings, transport=transport)
    job2 = run_crawl(session, settings, transport=transport)

    assert job2.pages_changed == 0
    versions = list(session.execute(select(PageVersion)).scalars())
    assert len(versions) == 3, "aucune version en doublon pour un contenu inchangé"


def test_changement_detecte_et_nouvelle_version(session, settings):
    run_crawl(session, settings, transport=_transport({242: "v1", 243: "x", 244: "x"}))
    job2 = run_crawl(session, settings, transport=_transport({242: "v2 modifié", 243: "x", 244: "x"}))

    assert job2.pages_changed == 1
    page = session.execute(select(Page).where(Page.siman == 242)).scalar_one()
    assert page.audit_status is PageAuditStatus.CHANGED
    assert page.last_modified_at is not None
    versions = list(session.execute(
        select(PageVersion).join(Page).where(Page.siman == 242)
    ).scalars())
    assert len(versions) == 2
    assert versions[-1].is_change is True


def test_page_absente_marquee_missing(session, settings):
    transport = _transport({242: "a", 243: "b", 244: "c"}, missing={243})
    job = run_crawl(session, settings, transport=transport)

    assert job.pages_missing == 1
    page = session.execute(select(Page).where(Page.siman == 243)).scalar_one()
    assert page.audit_status is PageAuditStatus.MISSING
    assert page.http_status == 404


def test_redirection_enregistree(session, settings):
    base = _handler(
        {242: "a", 243: "b", 244: "c"},
        redirect={"https://daattorah.com/oh/242/base": "https://daattorah.com/oh/242bis/base"},
    )

    def handler_final(request: httpx.Request) -> httpx.Response:
        if str(request.url).endswith("/oh/242bis/base"):
            return httpx.Response(200, text=_page_html(242, "redirigé"))
        return base(request)

    job = run_crawl(session, settings, transport=httpx.MockTransport(handler_final))
    page = session.execute(select(Page).where(Page.siman == 242)).scalar_one()
    assert page.redirect_target == "https://daattorah.com/oh/242bis/base"
    assert job.pages_ok == 3


def test_erreur_reseau_journalisee_sans_interrompre_le_crawl(session, settings):
    def handler(request: httpx.Request) -> httpx.Response:
        if "/oh/243/" in str(request.url):
            raise httpx.ConnectError("réseau coupé")
        return httpx.Response(200, text=_page_html(0, "ok"))

    job = run_crawl(session, settings, transport=httpx.MockTransport(handler))
    assert job.pages_failed == 1
    assert job.pages_ok == 2
    assert job.status is CrawlJobStatus.DONE
    page = session.execute(select(Page).where(Page.siman == 243)).scalar_one()
    assert page.audit_status is PageAuditStatus.ERROR


def test_html_change_mais_texte_identique_ne_versionne_pas(session, settings):
    """L'invariant fondateur du double hash (§5) : un re-déploiement qui
    modifie le HTML (script, attribut, style) sans changer le texte visible
    ne doit PAS créer de fausse version."""
    run_crawl(session, settings, transport=_transport({242: "x", 243: "x", 244: "x"}))

    def handler_v2(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "HEAD")
        for siman in (242, 243, 244):
            if str(request.url).endswith(f"/oh/{siman}/base"):
                # même texte visible, HTML différent (script + attribut injectés)
                html = _page_html(siman, "x").replace(
                    "<body>", '<body data-deploy="abc123"><script>var x=1;</script>')
                return httpx.Response(200, text=html)
        return httpx.Response(404)

    job2 = run_crawl(session, settings, transport=httpx.MockTransport(handler_v2))
    assert job2.pages_changed == 0
    versions = list(session.execute(select(PageVersion)).scalars())
    assert len(versions) == 3, "HTML modifié mais texte identique : pas de nouvelle version"


def test_http_500_marque_error(session, settings):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "HEAD")
        if "/oh/243/" in str(request.url):
            return httpx.Response(500, text="oops")
        return httpx.Response(200, text=_page_html(0, "ok"))

    job = run_crawl(session, settings, transport=httpx.MockTransport(handler))
    assert job.pages_failed == 1 and job.pages_ok == 2
    page = session.execute(select(Page).where(Page.siman == 243)).scalar_one()
    assert page.audit_status is PageAuditStatus.ERROR
    assert page.http_status == 500


def test_boucle_de_redirection_detectee(session, settings):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "HEAD")
        url = str(request.url)
        if "/oh/243/" in url or "/boucle" in url:
            return httpx.Response(301, headers={"location": "https://daattorah.com/boucle"})
        return httpx.Response(200, text=_page_html(0, "ok"))

    job = run_crawl(session, settings, transport=httpx.MockTransport(handler))
    assert job.pages_failed == 1
    page = session.execute(select(Page).where(Page.siman == 243)).scalar_one()
    assert page.audit_status is PageAuditStatus.ERROR
    # Le dernier statut reçu (301) est conservé — pas None.
    assert page.http_status == 301
    assert page.redirect_target == "https://daattorah.com/boucle"


def test_page_retablie_redevient_crawled(session, settings):
    """404 puis retour à la normale avec contenu inchangé → CRAWLED,
    pas MISSING à perpétuité."""
    run_crawl(session, settings, transport=_transport({242: "s", 243: "s", 244: "s"}))
    run_crawl(session, settings, transport=_transport({242: "s", 243: "s", 244: "s"}, missing={243}))
    page = session.execute(select(Page).where(Page.siman == 243)).scalar_one()
    assert page.audit_status is PageAuditStatus.MISSING

    run_crawl(session, settings, transport=_transport({242: "s", 243: "s", 244: "s"}))
    session.refresh(page)
    assert page.audit_status is PageAuditStatus.CRAWLED
    versions = list(session.execute(
        select(PageVersion).join(Page).where(Page.siman == 243)).scalars())
    assert len(versions) == 1, "contenu inchangé : pas de nouvelle version au rétablissement"


def test_verification_des_liens_internes(session, settings):
    """Chemin check_links : lien cassé compté et journalisé (§5)."""
    from daat_audit.models import AuditLog

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "HEAD"), "lecture seule, même pour les liens"
        url = str(request.url)
        for siman in (242, 243, 244):
            if url.endswith(f"/oh/{siman}/base"):
                html = _page_html(siman, "x").replace(
                    "</body>", '<a href="/lien-casse">casse</a><a href="/oh/243/base">ok</a></body>')
                return httpx.Response(200, text=html)
        if url.endswith("/lien-casse"):
            return httpx.Response(404)
        if url.endswith("/oh/245/base"):  # lien « suivant » du siman 244
            return httpx.Response(200, text="ok")
        return httpx.Response(404)

    job = run_crawl(session, settings, transport=httpx.MockTransport(handler), check_links=True)
    assert job.broken_links == 1
    logs = [l for l in session.execute(select(AuditLog)).scalars()
            if l.action == "crawl.broken_link"]
    assert len(logs) == 1 and "lien-casse" in logs[0].source


def test_bornes_simanim():
    """§ sécurité : le périmètre d'un job est borné et validé."""
    import pytest as _pytest

    for bad in ("abc", "242-999999", "0", "1-999", "", "242-241"):
        with _pytest.raises(ValueError):
            parse_simanim_arg(bad)


# ── Phase 2 : analyse pendant le crawl ───────────────────────────────────

def _real_page_transport(sample_html: str) -> httpx.MockTransport:
    """Sert la vraie page du site pour les 3 simanim du périmètre de test."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "HEAD")
        return httpx.Response(200, text=sample_html)
    return httpx.MockTransport(handler)


def test_le_crawl_decoupe_la_page_en_blocs(session, settings, sample_html):
    run_crawl(session, settings, transport=_real_page_transport(sample_html))
    blocs = session.execute(select(ContentBlock)).scalars().all()
    assert blocs, "aucun bloc archivé"
    assert all(b.stable_id and b.sha256 for b in blocs)
    # Une PageVersion par page, et des blocs rattachés à chacune.
    versions = session.execute(select(PageVersion)).scalars().all()
    assert {b.page_version_id for b in blocs} == {v.id for v in versions}


def test_le_crawl_extrait_les_references(session, settings, sample_html):
    run_crawl(session, settings, transport=_real_page_transport(sample_html))
    refs = session.execute(select(ParsedReference)).scalars().all()
    assert refs, "aucune référence extraite d'une page qui en contient"
    assert all(r.block_id is not None for r in refs)
    assert all(0.0 < r.confidence <= 1.0 for r in refs)


def test_une_page_inchangee_nest_pas_reanalysee(session, settings, sample_html):
    """Sans cette règle, chaque passage dupliquerait blocs et signalements,
    et les décisions déjà rendues se détacheraient de leur contenu."""
    transport = _real_page_transport(sample_html)
    run_crawl(session, settings, transport=transport)
    apres_premier = len(session.execute(select(ContentBlock)).scalars().all())

    run_crawl(session, settings, transport=transport)
    assert len(session.execute(select(ContentBlock)).scalars().all()) == apres_premier


def test_une_page_modifiee_est_reanalysee(session, settings, sample_html):
    run_crawl(session, settings, transport=_real_page_transport(sample_html))
    avant = len(session.execute(select(ContentBlock)).scalars().all())

    modifie = sample_html.replace("</main>", "<p>Ajout après coup.</p></main>")
    run_crawl(session, settings, transport=_real_page_transport(modifie))
    assert len(session.execute(select(ContentBlock)).scalars().all()) > avant


def test_les_signalements_sont_rattaches_a_leur_bloc(session, settings, sample_html):
    """Un défaut injecté doit produire un signalement relié au bon bloc."""
    abime = sample_html.replace("Le devoir d'", "Le  devoir  d'", 1)
    run_crawl(session, settings, transport=_real_page_transport(abime))

    findings = session.execute(select(AuditFinding)).scalars().all()
    assert findings, "aucun signalement sur une page volontairement abîmée"
    cible = next(f for f in findings if f.rule_code == "TECH-001")
    assert cible.block_id is not None
    bloc = session.get(ContentBlock, cible.block_id)
    assert bloc is not None and bloc.stable_id.startswith("OH-242-BASE-FR-")
    assert cible.status is not None       # statut initial renseigné (§13)


def test_page_saine_naboutit_a_aucun_signalement(session, settings, sample_html):
    run_crawl(session, settings, transport=_real_page_transport(sample_html))
    assert session.execute(select(AuditFinding)).scalars().all() == []


# ── Périmètre multi-niveaux ──────────────────────────────────────────────

def test_perimetre_couvre_les_quatre_niveaux(settings):
    from daat_audit.crawler.urls import NIVEAUX
    settings.niveau = "all"
    urls = perimeter_urls(settings)
    assert len(urls) == 3 * len(NIVEAUX)          # 3 simanim de test × 4 niveaux
    assert {u.rsplit("/", 1)[-1] for _, u in urls} == set(NIVEAUX)


def test_niveau_4_absent_pour_304_et_322(settings):
    """L'Admour HaZaken n'a pas écrit ces simanim : demander la page serait
    provoquer un 404 attendu, qui se lirait comme une anomalie."""
    settings.niveau = "all"
    urls = perimeter_urls(settings, simanim=[304, 322, 305])
    niveaux_304 = [u.rsplit("/", 1)[-1] for n, u in urls if n == 304]
    assert "daat-harav" not in niveaux_304
    assert "daat-harav" in [u.rsplit("/", 1)[-1] for n, u in urls if n == 305]


def test_niveau_inconnu_rejete(settings):
    from daat_audit.crawler.urls import niveaux_demandes
    settings.niveau = "pilpoul"
    with pytest.raises(ValueError, match="niveau inconnu"):
        niveaux_demandes(settings)


def test_le_niveau_enregistre_vient_de_lurl(session, settings):
    """settings.niveau peut valoir « all » : chaque page doit porter SON
    niveau, sans quoi les identifiants de blocs se collisionneraient."""
    settings.niveau = "base,lamdan"
    run_crawl(session, settings, transport=_transport({242: "x", 243: "y", 244: "z"}))
    pages = session.execute(select(Page)).scalars().all()
    assert {p.niveau for p in pages} == {"base", "lamdan"}
