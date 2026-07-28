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

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import __version__
from ..config import Settings, get_settings
from ..crawler.crawl import run_crawl
from ..crawler.urls import parse_simanim_arg
from ..db import make_engine, make_session_factory
from ..models import CrawlJob, CrawlJobStatus, Page, PageAuditStatus, PageVersion, utcnow
from . import schemas

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
