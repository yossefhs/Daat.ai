# -*- coding: utf-8 -*-
"""API FastAPI (§18, §20) — TestClient, réseau simulé, base SQLite fichier."""
from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select

from daat_audit.api.main import create_app
from daat_audit.config import Settings
from daat_audit.models import Base


def _html(siman: int) -> str:
    return (f"<html><head><title>Siman {siman}</title></head>"
            f"<body><p>Contenu du siman {siman}</p></body></html>")


def _mock_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method in ("GET", "HEAD"), "l'API d'audit ne fait que lire le site"
        url = str(request.url)
        for siman in (242, 243, 244):
            if url.endswith(f"/oh/{siman}/base"):
                return httpx.Response(200, text=_html(siman))
        return httpx.Response(404)

    return httpx.MockTransport(handler)


@pytest.fixture()
def client(tmp_path):
    db_url = f"sqlite:///{tmp_path}/api_test.db"
    settings = Settings(_env_file=None, database_url=db_url,
                        crawl_delay_seconds=0.0, siman_start=242, siman_end=244)
    Base.metadata.create_all(create_engine(db_url))
    app = create_app(settings=settings, transport=_mock_transport())
    with TestClient(app) as c:
        c.db_url = db_url          # pour insérer des données de test en base
        yield c


def test_health_affiche_le_mode(client):
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert data["mode"] == "audit_readonly"


def test_openapi_documente(client):
    spec = client.get("/openapi.json").json()
    assert "/crawl" in spec["paths"]
    assert "/pages/{page_id}" in spec["paths"]


def test_crawl_puis_consultation_des_pages(client):
    # Lancement (202) — le TestClient exécute la tâche de fond avant de rendre la main.
    response = client.post("/crawl", json={})
    assert response.status_code == 202
    job_id = response.json()["id"]

    job = client.get(f"/crawl/{job_id}").json()
    assert job["status"] == "done"
    assert job["pages_ok"] == 3

    pages = client.get("/pages").json()
    assert len(pages) == 3
    assert pages[0]["siman"] == 242
    assert pages[0]["audit_status"] == "crawled"

    # Filtre par siman.
    only = client.get("/pages", params={"siman": 243}).json()
    assert len(only) == 1 and only[0]["siman"] == 243

    # Détail : versions présentes, HTML non inclus par défaut.
    detail = client.get(f"/pages/{pages[0]['id']}").json()
    assert len(detail["versions"]) == 1
    assert detail["versions"][0]["html_raw"] is None
    assert detail["versions"][0]["text_sha256"]

    # HTML inclus sur demande explicite.
    full = client.get(f"/pages/{pages[0]['id']}", params={"include_html": True}).json()
    assert "Contenu du siman 242" in full["versions"][0]["html_raw"]

    stats = client.get("/stats").json()
    assert stats["pages"] == 3 and stats["versions"] == 3


def test_page_inconnue_404(client):
    assert client.get("/pages/9999").status_code == 404
    assert client.get("/crawl/9999").status_code == 404


def test_crawl_simanim_invalides_rejetes_en_422(client):
    """Validation du périmètre : pas de 500, pas de crawl de 42 h."""
    assert client.post("/crawl", json={"simanim": "abc"}).status_code == 422
    assert client.post("/crawl", json={"simanim": "242-999999"}).status_code == 422
    assert client.post("/crawl", json={"simanim": "0"}).status_code == 422
    assert client.post("/crawl", json={"simanim": "242-241"}).status_code == 422


def test_un_seul_crawl_a_la_fois(client):
    """409 si un job est déjà actif : la politesse envers le site est
    garantie globalement, pas seulement par job."""
    from daat_audit.models import CrawlJob, CrawlJobStatus

    factory = client.app.state.session_factory
    with factory() as db:
        db.add(CrawlJob(status=CrawlJobStatus.RUNNING, mode="audit_readonly"))
        db.commit()

    response = client.post("/crawl", json={})
    assert response.status_code == 409


def test_audit_status_invalide_rejete_en_422(client):
    response = client.get("/pages", params={"audit_status": "bogus"})
    assert response.status_code == 422
    assert "audit_status invalide" in response.json()["detail"]


# ── Signalements et métriques (Phase 4) ──────────────────────────────────

def _seed_finding(client, **champs):
    """Insère un signalement directement dans la base de l'application."""
    from sqlalchemy.orm import sessionmaker

    from daat_audit.models import AuditFinding, Page, Risk, Severity

    with sessionmaker(bind=create_engine(client.db_url))() as db:
        page = db.execute(select(Page)).scalars().first()
        if page is None:
            page = Page(url="https://daattorah.com/oh/242/base", siman=242,
                        langue="fr", niveau="base")
            db.add(page)
            db.commit()
        defauts = dict(
            page_id=page.id, category="citation", current_text="טקסט",
            explanation="écart constaté", confidence=0.9,
            severity=Severity.P1_MAJOR, risk=Risk.HALAKHIC, rule_code="CIT-001",
        )
        defauts.update(champs)
        db.add(AuditFinding(**defauts))
        db.commit()


def test_findings_vide_au_depart(client):
    assert client.get("/findings").json() == []


def test_findings_liste_et_detail(client):
    _seed_finding(client)
    findings = client.get("/findings").json()
    assert len(findings) == 1
    assert findings[0]["rule_code"] == "CIT-001"
    assert findings[0]["risk"] == "HALAKHIC"
    # Aucune correction proposée sur du contenu (§4).
    assert findings[0]["proposed_correction"] is None

    detail = client.get(f"/findings/{findings[0]['id']}")
    assert detail.status_code == 200
    assert detail.json()["explanation"] == "écart constaté"


def test_finding_inconnu_renvoie_404(client):
    assert client.get("/findings/9999").status_code == 404


def test_findings_filtrables(client):
    from daat_audit.models import Risk

    _seed_finding(client, rule_code="CIT-001")
    _seed_finding(client, rule_code="TECH-001", risk=Risk.LOW)

    assert len(client.get("/findings?rule_code=CIT-001").json()) == 1
    assert len(client.get("/findings?siman=242").json()) == 2
    assert len(client.get("/findings?siman=999").json()) == 0


def test_filtre_enumere_invalide_renvoie_422(client):
    """Une valeur inconnue doit échouer franchement : une liste vide se
    lirait à tort comme « aucune anomalie »."""
    reponse = client.get("/findings?severity=P9_INEXISTANT")
    assert reponse.status_code == 422
    assert "Valeurs admises" in reponse.json()["detail"]


def test_stats_rules_precision_nulle_sans_decision(client):
    _seed_finding(client)
    stats = client.get("/stats/rules").json()
    assert stats[0]["code"] == "CIT-001"
    assert stats[0]["alerts"] == 1
    assert stats[0]["precision"] is None, \
        "une règle jamais jugée ne doit pas afficher de précision"
