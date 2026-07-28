# -*- coding: utf-8 -*-
"""Orchestration d'un crawl (§5) : collecte → extraction → archivage versionné.

Politique de versionnage :
- première collecte d'une URL   → PageVersion (is_change=False) ;
- empreinte texte modifiée      → nouvelle PageVersion (is_change=True) ;
- contenu identique             → pas de nouvelle version (last_crawled_at
  mis à jour, événement consigné dans le journal du job).

Tout est écrit dans la base d'audit UNIQUEMENT. Le site n'est jamais modifié
(voir daat_audit.safety).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import Settings, get_settings
from ..db import make_engine, make_session_factory
from ..extract import extract_page
from ..hashing import sha256_hex, text_fingerprint
from ..models import (
    AuditLog,
    CrawlJob,
    CrawlJobStatus,
    Page,
    PageAuditStatus,
    PageVersion,
    utcnow,
)
from .fetch import Fetcher
from .urls import parse_simanim_arg, perimeter_urls

logger = logging.getLogger("daat_audit.crawler")


def _log_event(session: Session, action: str, **fields) -> None:
    session.add(AuditLog(user=None, action=action, **fields))


def run_crawl(
    session: Session,
    settings: Settings,
    simanim: list[int] | None = None,
    check_links: bool | None = None,
    transport: httpx.BaseTransport | None = None,
    job: CrawlJob | None = None,
) -> CrawlJob:
    """Exécute un crawl complet du périmètre et retourne le job renseigné."""
    do_check_links = settings.check_links if check_links is None else check_links
    targets = perimeter_urls(settings, simanim)

    if job is None:
        job = CrawlJob(mode=settings.mode.value)
        session.add(job)
    job.status = CrawlJobStatus.RUNNING
    job.pages_total = len(targets)
    session.commit()

    _log_event(
        session, "crawl.start",
        justification=f"{len(targets)} URL, délai {settings.crawl_delay_seconds}s, "
                      f"liens={'oui' if do_check_links else 'non'}",
    )
    session.commit()

    entries: list[dict] = []
    all_internal_links: set[str] = set()

    with Fetcher(settings, transport=transport) as fetcher:
        for siman, url in targets:
            entry: dict = {"siman": siman, "url": url}
            result = fetcher.get(url)
            entry["status"] = result.status
            entry["elapsed_ms"] = result.elapsed_ms
            if result.redirect_chain:
                entry["redirects"] = result.redirect_chain

            page = session.execute(select(Page).where(Page.url == url)).scalar_one_or_none()
            if page is None:
                page = Page(url=url, siman=siman, langue=settings.langue, niveau=settings.niveau)
                session.add(page)

            page.last_crawled_at = utcnow()
            page.http_status = result.status
            page.redirect_target = result.redirect_chain[-1] if result.redirect_chain else None

            if result.error:
                page.audit_status = PageAuditStatus.ERROR
                entry["error"] = result.error
                job.pages_failed += 1
                logger.warning("échec %s : %s", url, result.error)
            elif result.status == 404:
                page.audit_status = PageAuditStatus.MISSING
                entry["missing"] = True
                job.pages_missing += 1
                job.pages_failed += 1
                logger.warning("page absente (404) : %s", url)
            elif not result.ok or result.html is None:
                page.audit_status = PageAuditStatus.ERROR
                entry["error"] = f"HTTP {result.status}"
                job.pages_failed += 1
                logger.warning("HTTP %s : %s", result.status, url)
            else:
                extracted = extract_page(result.html, url)
                page.titre = extracted.title
                all_internal_links.update(extracted.internal_links)

                fingerprint = text_fingerprint(extracted.text)
                if page.current_text_sha256 is None:
                    change = False
                    store = True
                    page.audit_status = PageAuditStatus.CRAWLED
                    entry["new"] = True
                elif page.current_text_sha256 != fingerprint:
                    change = True
                    store = True
                    page.audit_status = PageAuditStatus.CHANGED
                    page.last_modified_at = utcnow()
                    job.pages_changed += 1
                    entry["changed"] = True
                else:
                    change = False
                    store = False
                    entry["unchanged"] = True
                    # Une page passée par MISSING/ERROR qui répond à nouveau
                    # avec un contenu inchangé est rétablie — sans quoi le
                    # statut d'incident resterait gravé à jamais.
                    page.audit_status = PageAuditStatus.CRAWLED

                if store:
                    session.add(PageVersion(
                        page=page,
                        http_status=result.status,
                        html_raw=result.html,
                        text_clean=extracted.text,
                        html_sha256=sha256_hex(result.html),
                        text_sha256=fingerprint,
                        is_change=change,
                    ))
                    page.current_text_sha256 = fingerprint
                job.pages_ok += 1

            entries.append(entry)
            session.commit()

        # ── Vérification optionnelle des liens internes (§5) ──────────────
        if do_check_links and all_internal_links:
            known_urls = {u for _, u in targets}
            to_check = sorted(all_internal_links - known_urls)[: settings.max_links_checked]
            broken: list[dict] = []
            for link in to_check:
                status = fetcher.head_status(link)
                if status is None or status >= 400:
                    broken.append({"url": link, "status": status})
                    _log_event(session, "crawl.broken_link", source=link,
                               justification=f"HTTP {status}")
            job.broken_links = len(broken)
            if broken:
                entries.append({"broken_links": broken})
            session.commit()

    job.status = CrawlJobStatus.FAILED if job.pages_ok == 0 and job.pages_total > 0 \
        else CrawlJobStatus.DONE
    job.finished_at = utcnow()
    job.log = json.dumps(entries, ensure_ascii=False)
    _log_event(
        session, "crawl.end",
        justification=f"ok={job.pages_ok} échecs={job.pages_failed} "
                      f"changées={job.pages_changed} absentes={job.pages_missing}",
    )
    session.commit()
    return job


def main(argv: list[str] | None = None) -> int:
    """CLI : ``python -m daat_audit.crawler.crawl [--simanim 242-269] [--check-links]``"""
    parser = argparse.ArgumentParser(description="Crawler d'audit DaatTorah (lecture seule)")
    parser.add_argument("--simanim", help="ex. 242-269 ou 242,243,250 (défaut : périmètre configuré)")
    parser.add_argument("--check-links", action="store_true", help="vérifier les liens internes")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    settings = get_settings()
    engine = make_engine(settings)
    factory = make_session_factory(engine)
    simanim = parse_simanim_arg(args.simanim) if args.simanim else None

    with factory() as session:
        job = run_crawl(session, settings, simanim=simanim,
                        check_links=args.check_links or None)
        print(
            f"Job #{job.id} : {job.status.value} — "
            f"{job.pages_ok}/{job.pages_total} OK, "
            f"{job.pages_changed} changée(s), {job.pages_missing} absente(s), "
            f"{job.pages_failed} échec(s), {job.broken_links} lien(s) cassé(s)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
