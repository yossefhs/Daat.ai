# -*- coding: utf-8 -*-
"""Modèles SQLAlchemy 2 — les quatorze tables du cahier des charges (§17).

Phase 1 n'alimente que ``pages``, ``page_versions``, ``crawl_jobs`` et
``audit_logs`` ; les autres tables sont créées dès maintenant pour que le
schéma, les énumérations (gravité §11, risque §12, statuts §14) et les
migrations soient posés une fois pour toutes.

Convention : les énumérations sont stockées par VALEUR (chaîne), pas par nom,
pour que la base reste lisible sans le code Python.
"""
from __future__ import annotations

import datetime as dt
import enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _enum(e: type[enum.Enum], name: str) -> Enum:
    return Enum(e, name=name, values_callable=lambda x: [m.value for m in x])


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Base(DeclarativeBase):
    pass


# ─────────────────────────── Énumérations métier ───────────────────────────

class Severity(str, enum.Enum):
    """Gravité (§11)."""

    P0_CRITICAL = "P0_CRITICAL"
    P1_MAJOR = "P1_MAJOR"
    P2_SIGNIFICANT = "P2_SIGNIFICANT"
    P3_MINOR = "P3_MINOR"
    P4_SUGGESTION = "P4_SUGGESTION"


class Risk(str, enum.Enum):
    """Risque, indépendant de la confiance (§12).

    Une anomalie à 99 % de confiance mais de risque HALAKHIC reste interdite
    à l'autocorrection : validation humaine obligatoire.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    HALAKHIC = "HALAKHIC"


class FindingStatus(str, enum.Enum):
    """Workflow de validation (§14)."""

    NEW = "NEW"
    AUTOMATICALLY_ANALYZED = "AUTOMATICALLY_ANALYZED"
    ADMIN_REVIEW_REQUIRED = "ADMIN_REVIEW_REQUIRED"
    EDITOR_APPROVED = "EDITOR_APPROVED"
    RABBINIC_REVIEW_REQUIRED = "RABBINIC_REVIEW_REQUIRED"
    RABBINIC_APPROVED = "RABBINIC_APPROVED"
    REJECTED = "REJECTED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    EDITORIAL_VARIANT = "EDITORIAL_VARIANT"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    READY_FOR_STAGING = "READY_FOR_STAGING"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"


class PageAuditStatus(str, enum.Enum):
    NEW = "new"
    CRAWLED = "crawled"
    CHANGED = "changed"
    MISSING = "missing"
    ERROR = "error"


class BlockType(str, enum.Enum):
    """Types de blocs (§6)."""

    TITRE = "titre"
    SOUS_TITRE = "sous_titre"
    PARAGRAPHE = "paragraphe"
    CITATION_HEBRAIQUE = "citation_hebraique"
    TRADUCTION = "traduction"
    SOURCE = "source"
    LISTE = "liste"
    TABLEAU = "tableau"
    CAS_PRATIQUE = "cas_pratique"
    RESUME = "resume"
    CONCLUSION = "conclusion"
    QUIZ = "quiz"
    NOTE = "note"


class CrawlJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


# ─────────────────────────────── Pages ───────────────────────────────

class Page(Base):
    """Une URL du périmètre (§5)."""

    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    siman: Mapped[int | None] = mapped_column(Integer, index=True)
    langue: Mapped[str] = mapped_column(String(8), default="fr")
    niveau: Mapped[str] = mapped_column(String(32), default="base")
    titre: Mapped[str | None] = mapped_column(String(500))

    http_status: Mapped[int | None] = mapped_column(Integer)
    redirect_target: Mapped[str | None] = mapped_column(String(500))

    first_seen_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_crawled_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    last_modified_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), comment="Dernière date où un changement de contenu a été détecté"
    )

    current_text_sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    audit_status: Mapped[PageAuditStatus] = mapped_column(
        _enum(PageAuditStatus, "page_audit_status"), default=PageAuditStatus.NEW
    )

    versions: Mapped[list["PageVersion"]] = relationship(
        back_populates="page", order_by="PageVersion.fetched_at", cascade="all, delete-orphan"
    )


class PageVersion(Base):
    """Copie datée d'une page : HTML brut + texte nettoyé + empreintes (§5).

    Une version n'est insérée qu'à la première collecte, puis à chaque
    changement d'empreinte du texte — jamais en doublon à contenu identique.
    """

    __tablename__ = "page_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id"), index=True)

    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    http_status: Mapped[int | None] = mapped_column(Integer)
    html_raw: Mapped[str | None] = mapped_column(Text)
    text_clean: Mapped[str | None] = mapped_column(Text)
    html_sha256: Mapped[str | None] = mapped_column(String(64))
    text_sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    is_change: Mapped[bool] = mapped_column(
        Boolean, default=False,
        comment="False pour la première collecte, True pour un changement détecté ensuite",
    )
    notes: Mapped[str | None] = mapped_column(Text)

    page: Mapped[Page] = relationship(back_populates="versions")
    blocks: Mapped[list["ContentBlock"]] = relationship(
        back_populates="page_version", cascade="all, delete-orphan"
    )


class ContentBlock(Base):
    """Bloc de contenu identifiable (§6). Alimenté en Phase 2."""

    __tablename__ = "content_blocks"
    __table_args__ = (UniqueConstraint("page_version_id", "stable_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    page_version_id: Mapped[int] = mapped_column(ForeignKey("page_versions.id"), index=True)

    stable_id: Mapped[str] = mapped_column(
        String(64), index=True, comment="Ex. OH-268-BASE-FR-P014 — stable entre versions proches"
    )
    order_index: Mapped[int] = mapped_column(Integer)
    block_type: Mapped[BlockType] = mapped_column(_enum(BlockType, "block_type"))
    raw_content: Mapped[str | None] = mapped_column(Text)
    normalized_content: Mapped[str | None] = mapped_column(Text)
    css_selector: Mapped[str | None] = mapped_column(String(500))
    sha256: Mapped[str | None] = mapped_column(String(64))

    page_version: Mapped[PageVersion] = relationship(back_populates="blocks")
    references: Mapped[list["ParsedReference"]] = relationship(back_populates="block")


class ParsedReference(Base):
    """Référence de Torah extraite d'un bloc (§7). Alimentée en Phase 2."""

    __tablename__ = "parsed_references"

    id: Mapped[int] = mapped_column(primary_key=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("content_blocks.id"), index=True)

    raw_text: Mapped[str] = mapped_column(Text)
    work: Mapped[str | None] = mapped_column(String(120), comment="Ouvrage/auteur normalisé")
    section: Mapped[str | None] = mapped_column(String(120))
    siman: Mapped[str | None] = mapped_column(String(16))
    seif: Mapped[str | None] = mapped_column(String(16))
    seif_katan: Mapped[str | None] = mapped_column(String(16))
    daf: Mapped[str | None] = mapped_column(String(16))
    amud: Mapped[str | None] = mapped_column(String(4))
    confidence: Mapped[float | None] = mapped_column(Float)
    span_start: Mapped[int | None] = mapped_column(Integer)
    span_end: Mapped[int | None] = mapped_column(Integer)
    validation_status: Mapped[str | None] = mapped_column(String(32))

    block: Mapped[ContentBlock] = relationship(back_populates="references")


class SourceText(Base):
    """Texte de référence récupéré chez un fournisseur (§8). Phase 4."""

    __tablename__ = "source_texts"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    ref: Mapped[str] = mapped_column(String(300), index=True)
    lang: Mapped[str | None] = mapped_column(String(8))
    version_title: Mapped[str | None] = mapped_column(String(300))
    content: Mapped[str | None] = mapped_column(Text)
    sha256: Mapped[str | None] = mapped_column(String(64))
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ─────────────────────────── Anomalies & décisions ───────────────────────────

class AuditFinding(Base):
    """Anomalie détectée (§11)."""

    __tablename__ = "audit_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int | None] = mapped_column(ForeignKey("pages.id"), index=True)
    block_id: Mapped[int | None] = mapped_column(ForeignKey("content_blocks.id"), index=True)

    category: Mapped[str] = mapped_column(String(64), index=True)
    subcategory: Mapped[str | None] = mapped_column(String(64))
    current_text: Mapped[str | None] = mapped_column(Text)
    source_text: Mapped[str | None] = mapped_column(Text)
    proposed_correction: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    sources: Mapped[str | None] = mapped_column(Text, comment="Références des sources, JSON ou texte")

    confidence: Mapped[float | None] = mapped_column(Float, comment="0.0 – 1.0")
    severity: Mapped[Severity] = mapped_column(_enum(Severity, "severity"), index=True)
    risk: Mapped[Risk] = mapped_column(_enum(Risk, "risk"), index=True)
    status: Mapped[FindingStatus] = mapped_column(
        _enum(FindingStatus, "finding_status"), default=FindingStatus.NEW, index=True
    )

    rule_code: Mapped[str | None] = mapped_column(String(64), index=True)
    rule_version: Mapped[str | None] = mapped_column(String(32))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    corrections: Mapped[list["SuggestedCorrection"]] = relationship(back_populates="finding")
    decisions: Mapped[list["AdminDecision"]] = relationship(back_populates="finding")


class SuggestedCorrection(Base):
    """Correction proposée — jamais appliquée automatiquement en Phase 1 (§13)."""

    __tablename__ = "suggested_corrections"

    id: Mapped[int] = mapped_column(primary_key=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey("audit_findings.id"), index=True)
    text_before: Mapped[str | None] = mapped_column(Text)
    text_after: Mapped[str | None] = mapped_column(Text)
    rationale: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    applied: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Toujours False en Phase 1 : aucune application automatique"
    )

    finding: Mapped[AuditFinding] = relationship(back_populates="corrections")


class AdminDecision(Base):
    """Décision d'un administrateur sur une anomalie (§14)."""

    __tablename__ = "admin_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey("audit_findings.id"), index=True)
    user: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(64))
    note: Mapped[str | None] = mapped_column(Text)
    source_attached: Mapped[str | None] = mapped_column(Text)
    previous_status: Mapped[str | None] = mapped_column(String(40))
    new_status: Mapped[str | None] = mapped_column(String(40))
    decided_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    finding: Mapped[AuditFinding] = relationship(back_populates="decisions")


class RabbinicReview(Base):
    """Question soumise au Rav et sa réponse (§14)."""

    __tablename__ = "rabbinic_reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey("audit_findings.id"), index=True)
    reviewer: Mapped[str | None] = mapped_column(String(120))
    question: Mapped[str | None] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(40))
    asked_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    answered_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(Base):
    """Journal d'audit inaltérable depuis l'interface standard (§16).

    Aucun endpoint de suppression n'existe. Côté base, le durcissement est
    OUTILLÉ, pas seulement documenté : deploy/postgres-harden.sql crée le
    rôle applicatif sans UPDATE/DELETE/TRUNCATE sur cette table (à exécuter
    après les migrations — voir README, section déploiement).
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str | None] = mapped_column(String(120), comment="NULL = action système")
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(64))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    text_before: Mapped[str | None] = mapped_column(Text)
    text_after: Mapped[str | None] = mapped_column(Text)
    justification: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(Text)
    page_version_id: Mapped[int | None] = mapped_column(ForeignKey("page_versions.id"))
    rule_version: Mapped[str | None] = mapped_column(String(32))
    previous_status: Mapped[str | None] = mapped_column(String(40))
    new_status: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


# ─────────────────────────── Référentiels & jobs ───────────────────────────

class TerminologyEntry(Base):
    """Dictionnaire métier configurable (§10)."""

    __tablename__ = "terminology_dictionary"

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical: Mapped[str] = mapped_column(String(120), unique=True)
    variants: Mapped[str | None] = mapped_column(Text, comment="Variantes acceptées, JSON")
    forbidden_variants: Mapped[str | None] = mapped_column(Text, comment="Variantes interdites, JSON")
    lang: Mapped[str | None] = mapped_column(String(8))
    notes: Mapped[str | None] = mapped_column(Text)


class SourceProvider(Base):
    """Fournisseur de textes de référence (§8)."""

    __tablename__ = "source_providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    base_url: Mapped[str | None] = mapped_column(String(300))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit_seconds: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)


class AuditRule(Base):
    """Règle de contrôle et ses métriques de fiabilité (§21).

    Une règle ne peut passer en autocorrection qu'avec une précision
    > 99,5 %, un risque faible ET une validation humaine explicite —
    et en Phase 1, jamais (``autocorrect_allowed`` reste False).
    """

    __tablename__ = "audit_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str | None] = mapped_column(String(64))
    version: Mapped[str] = mapped_column(String(32), default="1.0")

    alerts_total: Mapped[int] = mapped_column(Integer, default=0)
    validated_total: Mapped[int] = mapped_column(Integer, default=0)
    rejected_total: Mapped[int] = mapped_column(Integer, default=0)
    false_positives_total: Mapped[int] = mapped_column(Integer, default=0)

    autocorrect_allowed: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def precision(self) -> float | None:
        # Les défauts Python ne s'appliquent qu'au flush : sur un objet
        # jamais persisté, les compteurs valent encore None.
        validated = self.validated_total or 0
        judged = validated + (self.rejected_total or 0) + (self.false_positives_total or 0)
        if not judged:
            return None
        return validated / judged


class CrawlJob(Base):
    """Une exécution du crawler (§5)."""

    __tablename__ = "crawl_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[CrawlJobStatus] = mapped_column(
        _enum(CrawlJobStatus, "crawl_job_status"), default=CrawlJobStatus.PENDING
    )
    mode: Mapped[str | None] = mapped_column(String(32))

    pages_total: Mapped[int] = mapped_column(Integer, default=0)
    pages_ok: Mapped[int] = mapped_column(Integer, default=0)
    pages_failed: Mapped[int] = mapped_column(Integer, default=0)
    pages_changed: Mapped[int] = mapped_column(Integer, default=0)
    pages_missing: Mapped[int] = mapped_column(Integer, default=0)
    broken_links: Mapped[int] = mapped_column(Integer, default=0)

    log: Mapped[str | None] = mapped_column(Text, comment="Journal détaillé par page, JSON")
