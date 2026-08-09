# -*- coding: utf-8 -*-
"""API FastAPI du système d'audit (§18) — Phase 1.

Endpoints : santé, lancement/suivi de crawl, consultation des pages et de
leurs versions. Les anomalies (§11) et la validation (§14) arrivent en
Phase 3. Documentation OpenAPI générée automatiquement sur /docs.

L'application est construite par ``create_app`` pour que les tests puissent
injecter leur configuration et un transport HTTP simulé.
"""
from __future__ import annotations

import logging
import pathlib

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import __version__
from ..config import Settings, get_settings
from ..crawler.crawl import run_crawl
from ..crawler.urls import parse_simanim_arg
from ..db import make_engine, make_session_factory
from .. import metrics, workflow
from ..models import (
    AdminDecision,
    AuditFinding,
    CrawlJob,
    CrawlJobStatus,
    FindingStatus,
    Page,
    PageAuditStatus,
    PageVersion,
    RabbinicReview,
    Risk,
    Severity,
    utcnow,
)
from . import auth, schemas

logger = logging.getLogger("daat_audit.api")


def create_app(
    settings: Settings | None = None,
    transport: httpx.BaseTransport | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    engine = make_engine(settings)
    session_factory = make_session_factory(engine)

    app = FastAPI(
        title="DaatTorah — API d'audit",
        version=__version__,
        description=(
            "Système d'audit du site public daattorah.com. **Lecture seule** : "
            "cette API n'écrit que dans la base d'audit et ne modifie jamais le site. "
            f"Mode courant : `{settings.mode.value}`."
        ),
    )
    app.state.settings = settings
    app.state.session_factory = session_factory
    app.state.transport = transport

    def get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    # Le rôle décisionnaire découle du secret présenté (voir api/auth.py).
    role_dependency = auth.make_role_dependency(settings)

    # ── Santé ────────────────────────────────────────────────────────────
    @app.get("/health", response_model=schemas.HealthOut, tags=["système"])
    def health() -> schemas.HealthOut:
        return schemas.HealthOut(status="ok", mode=settings.mode.value, version=__version__)

    # ── Crawl ────────────────────────────────────────────────────────────
    @app.post("/crawl", response_model=schemas.CrawlJobOut, status_code=202, tags=["crawl"])
    def launch_crawl(
        payload: schemas.CrawlIn,
        background: BackgroundTasks,
        db: Session = Depends(get_db),
    ) -> CrawlJob:
        """Lance un crawl du périmètre en tâche de fond (202 Accepted).

        Un seul crawl à la fois : 409 si un job est déjà PENDING/RUNNING —
        c'est le garde-fou de politesse envers le site (le délai entre
        requêtes est porté par le job ; des jobs parallèles l'annuleraient).
        NB : contrôle-puis-insertion sans verrou de base — suffisant pour un
        outil interne, à durcir (contrainte partielle ou advisory lock) si
        l'API devenait multi-utilisateurs.
        """
        try:
            simanim = parse_simanim_arg(payload.simanim) if payload.simanim else None
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

        active = db.execute(
            select(CrawlJob).where(CrawlJob.status.in_(
                [CrawlJobStatus.PENDING, CrawlJobStatus.RUNNING]
            ))
        ).first()
        if active:
            raise HTTPException(409, "un crawl est déjà en cours — réessayer plus tard")

        job = CrawlJob(mode=settings.mode.value, status=CrawlJobStatus.PENDING)
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id

        def _task() -> None:
            with session_factory() as task_db:
                try:
                    task_job = task_db.get(CrawlJob, job_id)
                    run_crawl(task_db, settings, simanim=simanim,
                              check_links=payload.check_links,
                              transport=app.state.transport, job=task_job)
                except Exception:  # noqa: BLE001 — le job doit refléter l'échec
                    logger.exception("crawl %s en échec", job_id)
                    task_db.rollback()  # la session peut être en échec : purger avant d'écrire
                    task_job = task_db.get(CrawlJob, job_id)
                    if task_job is not None:
                        task_job.status = CrawlJobStatus.FAILED
                        task_job.finished_at = utcnow()
                        task_db.commit()

        background.add_task(_task)
        return job

    @app.get("/crawl", response_model=list[schemas.CrawlJobOut], tags=["crawl"])
    def list_jobs(db: Session = Depends(get_db)) -> list[CrawlJob]:
        return list(db.execute(
            select(CrawlJob).order_by(CrawlJob.started_at.desc()).limit(50)
        ).scalars())

    @app.get("/crawl/{job_id}", response_model=schemas.CrawlJobOut, tags=["crawl"])
    def get_job(job_id: int, db: Session = Depends(get_db)) -> CrawlJob:
        job = db.get(CrawlJob, job_id)
        if job is None:
            raise HTTPException(404, "job inconnu")
        return job

    # ── Pages ────────────────────────────────────────────────────────────
    @app.get("/pages", response_model=list[schemas.PageOut], tags=["pages"])
    def list_pages(
        siman: int | None = Query(default=None),
        audit_status: str | None = Query(
            default=None, description="new | crawled | changed | missing | error"
        ),
        db: Session = Depends(get_db),
    ) -> list[Page]:
        stmt = select(Page).order_by(Page.siman)
        if siman is not None:
            stmt = stmt.where(Page.siman == siman)
        if audit_status is not None:
            # Validation explicite : une valeur inconnue donnerait un 500 sur
            # PostgreSQL (cast d'enum) et un résultat vide trompeur sur SQLite.
            try:
                status_enum = PageAuditStatus(audit_status)
            except ValueError as exc:
                valid = ", ".join(s.value for s in PageAuditStatus)
                raise HTTPException(422, f"audit_status invalide (attendu : {valid})") from exc
            stmt = stmt.where(Page.audit_status == status_enum)
        return list(db.execute(stmt).scalars())

    @app.get("/pages/{page_id}", response_model=schemas.PageDetailOut, tags=["pages"])
    def get_page(
        page_id: int,
        include_html: bool = Query(default=False, description="Inclure le HTML brut archivé"),
        include_text: bool = Query(default=False, description="Inclure le texte nettoyé"),
        db: Session = Depends(get_db),
    ) -> schemas.PageDetailOut:
        page = db.get(Page, page_id)
        if page is None:
            raise HTTPException(404, "page inconnue")
        out = schemas.PageDetailOut.model_validate(page)
        out.versions = []
        for version in page.versions:
            v = schemas.PageVersionOut.model_validate(version)
            if not include_html:
                v.html_raw = None
            if not include_text:
                v.text_clean = None
            out.versions.append(v)
        return out

    # ── Statistiques minimales (le tableau de bord complet arrive en Phase 3) ──
    @app.get("/findings", response_model=list[schemas.FindingOut], tags=["signalements"])
    def list_findings(
        siman: int | None = None,
        rule_code: str | None = None,
        severity: str | None = None,
        risk: str | None = None,
        status: str | None = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
    ) -> list[AuditFinding]:
        """Signalements, filtrables (§14).

        Les filtres énumérés sont validés contre leur énumération : une valeur
        inconnue renvoie 422 plutôt qu'une liste vide, qui se lirait à tort
        comme « aucune anomalie ».
        """
        query = select(AuditFinding).order_by(AuditFinding.id.desc())

        if siman is not None:
            query = query.join(Page, AuditFinding.page_id == Page.id).where(Page.siman == siman)
        if rule_code:
            query = query.where(AuditFinding.rule_code == rule_code)
        for valeur, colonne, enumeration, nom in (
            (severity, AuditFinding.severity, Severity, "severity"),
            (risk, AuditFinding.risk, Risk, "risk"),
            (status, AuditFinding.status, FindingStatus, "status"),
        ):
            if not valeur:
                continue
            try:
                query = query.where(colonne == enumeration(valeur))
            except ValueError:
                raise HTTPException(
                    422,
                    f"{nom} invalide : {valeur}. Valeurs admises : "
                    + ", ".join(e.value for e in enumeration),
                )

        return list(db.execute(query.offset(offset).limit(limit)).scalars().all())

    def _finding_ou_404(db: Session, finding_id: int) -> AuditFinding:
        finding = db.get(AuditFinding, finding_id)
        if finding is None:
            raise HTTPException(404, "signalement introuvable")
        return finding

    @app.get("/findings/{finding_id}", response_model=schemas.FindingDetailOut,
             tags=["signalements"])
    def get_finding(
        finding_id: int,
        x_admin_secret: str | None = Header(default=None, alias="X-Admin-Secret"),
        db: Session = Depends(get_db),
    ) -> dict:
        """Détail d'un signalement, avec son historique complet.

        ``available_actions`` n'est renseigné que si un secret valide est
        présenté : la liste dépend du rôle, et un lecteur anonyme n'a pas à
        savoir ce qu'un rav pourrait faire.
        """
        finding = _finding_ou_404(db, finding_id)
        try:
            role = auth.resolve_role(settings, x_admin_secret)
            actions = workflow.actions_possibles(finding, role)
        except HTTPException:
            actions = []

        return {
            **{c.name: getattr(finding, c.name)
               for c in AuditFinding.__table__.columns},
            "available_actions": actions,
            "decisions": workflow.historique(db, finding),
            "rabbinic_reviews": list(db.execute(
                select(RabbinicReview)
                .where(RabbinicReview.finding_id == finding.id)
                .order_by(RabbinicReview.id)
            ).scalars().all()),
        }

    @app.post("/findings/{finding_id}/decision", response_model=schemas.DecisionOut,
              tags=["validation"])
    def decide(
        finding_id: int,
        payload: schemas.DecisionIn,
        identite: tuple = Depends(role_dependency),
        db: Session = Depends(get_db),
    ) -> AdminDecision:
        """Applique une décision (§14).

        Le rôle provient du secret présenté. Un signalement à risque halakhique
        ne peut pas être approuvé par un éditeur : la transition elle-même le
        refuse (422), pas seulement l'interface.
        """
        role, user = identite
        finding = _finding_ou_404(db, finding_id)
        try:
            return workflow.appliquer(
                db, finding, payload.action, role, user,
                note=payload.note, source_attached=payload.source_attached,
            )
        except workflow.WorkflowError as exc:
            db.rollback()
            raise HTTPException(422, str(exc)) from exc

    @app.post("/findings/{finding_id}/rabbinic-answer",
              response_model=schemas.RabbinicReviewOut, tags=["validation"])
    def rabbinic_answer(
        finding_id: int,
        payload: schemas.RabbinicAnswerIn,
        identite: tuple = Depends(role_dependency),
        db: Session = Depends(get_db),
    ) -> RabbinicReview:
        """Réponse du Rav à une question ouverte. Réservée au rôle « rav »."""
        role, user = identite
        if role is not workflow.Role.RAV:
            raise HTTPException(403, "réservé au Rav")
        finding = _finding_ou_404(db, finding_id)
        try:
            return workflow.repondre_rav(db, finding, user, payload.answer,
                                         payload.confirme)
        except workflow.WorkflowError as exc:
            db.rollback()
            raise HTTPException(422, str(exc)) from exc

    @app.get("/findings/{finding_id}/history",
             response_model=list[schemas.DecisionOut], tags=["validation"])
    def finding_history(finding_id: int, db: Session = Depends(get_db)
                        ) -> list[AdminDecision]:
        """Historique intégral. Aucune décision n'est jamais retirée : un
        retour arrière ajoute une ligne, il n'en efface pas."""
        return workflow.historique(db, _finding_ou_404(db, finding_id))

    @app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
    def admin_interface() -> str:
        """Interface d'administration (§16), servie par l'API elle-même.

        Page autonome, sans ressource externe : l'outil doit fonctionner hors
        ligne. Elle n'applique aucune règle de sécurité par elle-même — toutes
        les garanties sont côté API, où elles ne se contournent pas.
        """
        return (pathlib.Path(__file__).parent / "static" / "admin.html").read_text(
            encoding="utf-8"
        )

    @app.get("/workflow/actions", tags=["validation"])
    def workflow_actions() -> list[dict]:
        """Catalogue des transitions, pour l'interface et la documentation."""
        return [
            {
                "action": tr.action,
                "libelle": tr.libelle,
                "cible": tr.target.value,
                "roles": sorted(r.value for r in tr.roles),
                "depuis": sorted(s.value for s in tr.depuis) if tr.depuis else None,
            }
            for tr in workflow.TRANSITIONS.values()
        ]

    @app.get("/stats/rules", response_model=list[schemas.RuleStatsOut], tags=["système"])
    def rule_stats(db: Session = Depends(get_db)) -> list[dict]:
        """Fiabilité par règle (§21). ``precision`` est nulle tant qu'aucune
        décision humaine n'a été rendue."""
        return [
            {
                "code": s.code, "alerts": s.alerts, "judged": s.judged,
                "validated": s.validated, "rejected": s.rejected,
                "false_positives": s.false_positives, "pending": s.pending,
                "precision": s.precision,
            }
            for s in metrics.compute(db)
        ]

    @app.get("/stats", tags=["système"])
    def stats(db: Session = Depends(get_db)) -> dict:
        pages_total = db.execute(select(func.count(Page.id))).scalar_one()
        versions_total = db.execute(select(func.count(PageVersion.id))).scalar_one()
        by_status = dict(db.execute(
            select(Page.audit_status, func.count(Page.id)).group_by(Page.audit_status)
        ).all())
        return {
            "pages": pages_total,
            "versions": versions_total,
            "par_statut": {k.value if hasattr(k, "value") else str(k): v
                           for k, v in by_status.items()},
            "mode": settings.mode.value,
        }

    return app


# Point d'entrée uvicorn : `uvicorn daat_audit.api.main:app`
app = create_app()
