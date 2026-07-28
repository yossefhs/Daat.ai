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


# ── Workflow de validation (Phase 3) ─────────────────────────────────────

EDITEUR = {"X-Admin-Secret": "secret-editeur", "X-Admin-User": "yossef"}
RAV = {"X-Admin-Secret": "secret-rav", "X-Admin-User": "Rav Samama"}


@pytest.fixture()
def client_admin(tmp_path):
    """Application avec les deux secrets configurés."""
    db_url = f"sqlite:///{tmp_path}/admin_test.db"
    settings = Settings(_env_file=None, database_url=db_url,
                        crawl_delay_seconds=0.0, siman_start=242, siman_end=244,
                        admin_secret="secret-editeur", rav_secret="secret-rav")
    Base.metadata.create_all(create_engine(db_url))
    app = create_app(settings=settings, transport=_mock_transport())
    with TestClient(app) as c:
        c.db_url = db_url
        yield c


def _seed(client, risk_halakhic: bool = False) -> int:
    from daat_audit.models import Risk
    _seed_finding(client, risk=Risk.HALAKHIC if risk_halakhic else Risk.LOW)
    return client.get("/findings").json()[0]["id"]


def test_decision_sans_secret_refusee(client_admin):
    fid = _seed(client_admin)
    assert client_admin.post(f"/findings/{fid}/decision",
                             json={"action": "approve"}).status_code == 401


def test_decision_avec_mauvais_secret_refusee(client_admin):
    fid = _seed(client_admin)
    reponse = client_admin.post(f"/findings/{fid}/decision", json={"action": "approve"},
                                headers={"X-Admin-Secret": "faux"})
    assert reponse.status_code == 403


def test_sans_secret_configure_les_decisions_sont_refusees(client):
    """Fail closed : décider sans savoir qui décide ne trace rien d'utile."""
    _seed_finding(client)
    fid = client.get("/findings").json()[0]["id"]
    reponse = client.post(f"/findings/{fid}/decision", json={"action": "approve"},
                          headers={"X-Admin-Secret": "peu importe"})
    assert reponse.status_code == 503
    assert "aucun secret d'administration" in reponse.json()["detail"]


def test_editeur_approuve_un_signalement_technique(client_admin):
    fid = _seed(client_admin)
    reponse = client_admin.post(f"/findings/{fid}/decision",
                                json={"action": "approve", "note": "vérifié"},
                                headers=EDITEUR)
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["previous_status"] == "NEW" and corps["new_status"] == "EDITOR_APPROVED"
    assert corps["user"] == "yossef"


def test_lapi_refuse_lapprobation_editeur_dun_signalement_halakhique(client_admin):
    """La garantie doit tenir par l'API, pas seulement dans le module :
    c'est l'API qu'on pourrait appeler directement."""
    fid = _seed(client_admin, risk_halakhic=True)
    reponse = client_admin.post(f"/findings/{fid}/decision", json={"action": "approve"},
                                headers=EDITEUR)
    assert reponse.status_code == 422
    assert "risque halakhique" in reponse.json()["detail"]
    assert client_admin.get(f"/findings/{fid}").json()["status"] == "NEW"


def test_le_rav_ne_peut_pas_etre_usurpe_par_un_entete(client_admin):
    """Le rôle vient du secret, jamais d'un champ envoyé."""
    fid = _seed(client_admin, risk_halakhic=True)
    reponse = client_admin.post(
        f"/findings/{fid}/decision",
        json={"action": "approve", "note": "je suis le rav"},
        headers={"X-Admin-Secret": "secret-editeur", "X-Admin-User": "rav"},
    )
    assert reponse.status_code == 422


def test_parcours_complet_escalade_puis_avis_du_rav(client_admin):
    fid = _seed(client_admin, risk_halakhic=True)

    assert client_admin.post(f"/findings/{fid}/decision",
                             json={"action": "escalate", "note": "avis ?"},
                             headers=EDITEUR).status_code == 200
    detail = client_admin.get(f"/findings/{fid}", headers=RAV).json()
    assert detail["status"] == "RABBINIC_REVIEW_REQUIRED"
    assert detail["rabbinic_reviews"][0]["status"] == "pending"

    assert client_admin.post(f"/findings/{fid}/rabbinic-answer",
                             json={"answer": "confirmé", "confirme": True},
                             headers=RAV).status_code == 200

    final = client_admin.get(f"/findings/{fid}", headers=RAV).json()
    assert final["status"] == "RABBINIC_APPROVED"
    assert final["rabbinic_reviews"][0]["reviewer"] == "Rav Samama"
    assert [d["action"] for d in final["decisions"]] == ["escalate", "rabbinic_approve"]


def test_seul_le_rav_repond_aux_questions(client_admin):
    fid = _seed(client_admin, risk_halakhic=True)
    client_admin.post(f"/findings/{fid}/decision", json={"action": "escalate"},
                      headers=EDITEUR)
    reponse = client_admin.post(f"/findings/{fid}/rabbinic-answer",
                                json={"answer": "ok", "confirme": True}, headers=EDITEUR)
    assert reponse.status_code == 403


def test_historique_expose_et_ordonne(client_admin):
    fid = _seed(client_admin)
    client_admin.post(f"/findings/{fid}/decision", json={"action": "approve"},
                      headers=EDITEUR)
    client_admin.post(f"/findings/{fid}/decision", json={"action": "reopen"},
                      headers=EDITEUR)
    historique = client_admin.get(f"/findings/{fid}/history").json()
    assert [d["action"] for d in historique] == ["approve", "reopen"]


def test_actions_possibles_selon_le_role(client_admin):
    fid = _seed(client_admin, risk_halakhic=True)
    editeur = client_admin.get(f"/findings/{fid}", headers=EDITEUR).json()
    assert "approve" not in editeur["available_actions"]
    assert "escalate" in editeur["available_actions"]

    rav = client_admin.get(f"/findings/{fid}", headers=RAV).json()
    assert "approve" in rav["available_actions"]

    anonyme = client_admin.get(f"/findings/{fid}").json()
    assert anonyme["available_actions"] == []


def test_catalogue_des_transitions(client_admin):
    actions = client_admin.get("/workflow/actions").json()
    par_action = {a["action"]: a for a in actions}
    assert par_action["rabbinic_approve"]["roles"] == ["rav"]
    assert "PUBLISHED" not in {a["cible"] for a in actions}


def test_la_precision_dune_regle_apparait_apres_decision(client_admin):
    """Le chaînon qui manquait : sans décisions humaines, aucune précision."""
    fid = _seed(client_admin)
    assert client_admin.get("/stats/rules").json()[0]["precision"] is None

    client_admin.post(f"/findings/{fid}/decision", json={"action": "approve"},
                      headers=EDITEUR)
    assert client_admin.get("/stats/rules").json()[0]["precision"] == 1.0


def test_interface_admin_servie_et_autonome(client_admin):
    """Page autonome : aucune ressource externe, pour fonctionner hors ligne."""
    reponse = client_admin.get("/admin")
    assert reponse.status_code == 200
    page = reponse.text
    assert "DAAT" in page and "Audit interne" in page
    assert "http://" not in page.replace("http://www.w3.org", "")
    assert "cdn" not in page.lower()
    # Le secret ne doit pas être persisté au-delà de l'onglet. On vise l'usage
    # réel, pas le mot : il figure dans un commentaire qui explique justement
    # qu'on ne s'en sert pas.
    assert "localStorage.setItem" not in page
    assert "localStorage.getItem" not in page
    assert "sessionStorage.setItem" in page


def test_le_texte_mixte_est_isole_pour_le_bidi(client_admin):
    """Les guillemets « » sont neutres au sens bidi : contre de l'hébreu, ils
    basculent et « X » → « Y » s'affiche à l'envers. Dans un outil dont l'objet
    est de dire QUEL mot a changé, c'est un contresens."""
    page = client_admin.get("/admin").text
    assert "unicode-bidi: isolate" in page
    assert "<bdi dir=\\\"rtl\\\">" in page or '<bdi dir="rtl">' in page
    # L'explication et les notes passent par l'isolation, pas par le simple échappement.
    assert "${mixte(f.explanation)}" in page
