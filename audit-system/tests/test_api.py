# -*- coding: utf-8 -*-
"""API FastAPI (§18, §20) — TestClient, réseau simulé, base SQLite fichier."""
from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

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
