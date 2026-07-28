# -*- coding: utf-8 -*-
"""Passe de vérification des citations (§8) — séparée du crawl, et à dessein.

Le crawl est hors ligne, rapide et sans dépendance : il collecte, découpe et
applique les contrôles techniques. La vérification des citations, elle,
interroge un service tiers, prend du temps et peut échouer pour des raisons
qui n'ont rien à voir avec le site. Les mêler ferait dépendre l'archivage de
la disponibilité de Sefaria.

    python -m daat_audit.analyze [--simanim 242-245] [--limit 50] [--dry-run]

Le mode ``--dry-run`` affiche sans rien écrire en base. Dans tous les cas,
**rien n'est jamais écrit vers le site** (``daat_audit.safety``).
"""
from __future__ import annotations

import argparse
import logging
import re
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from .checks import Finding
from .citations import finding_de, verifier_citation
from .config import Settings, get_settings
from .db import make_engine, make_session_factory
from .models import (
    AuditFinding,
    AuditLog,
    BlockType,
    ContentBlock,
    Page,
    PageVersion,
    ParsedReference,
)
from .quotes import extract_quotes
from .references import ParsedRef
from .sources import SefariaProvider
from .sources.cache import CachedProvider

logger = logging.getLogger("daat_audit.analyze")


# Nombre de blocs qu'on remonte pour retrouver la référence d'une citation.
# Sur le site, une même annonce introduit couramment cinq citations d'affilée.
FENETRE_BLOCS = 12


def _refs_du_bloc(session: Session, bloc: ContentBlock) -> list[ParsedRef]:
    """Références déjà extraites de ce bloc, converties pour la comparaison."""
    lignes = session.execute(
        select(ParsedReference).where(ParsedReference.block_id == bloc.id)
    ).scalars().all()
    return [
        ParsedRef(
            raw_text=l.raw_text, work=l.work, section=l.section,
            siman=l.siman, seif=l.seif, seif_katan=l.seif_katan,
            daf=l.daf, amud=l.amud, confidence=l.confidence or 0.5,
        )
        for l in lignes
    ]


_RE_BALISE_FINALE = re.compile(r"(?:^|>\s*)([a-z][a-z0-9]*)[.#:]?[^>]*$")


def niveau_de_titre(bloc: ContentBlock) -> int:
    """Rang du titre porté par ce bloc (2 pour h2…), 0 s'il n'en est pas un.

    Déduit du sélecteur CSS, dont le dernier segment est toujours l'élément
    lui-même — plutôt que d'ajouter une colonne et une migration pour une
    information déjà présente.
    """
    m = _RE_BALISE_FINALE.search(bloc.css_selector or "")
    balise = m.group(1) if m else ""
    return int(balise[1]) if len(balise) == 2 and balise[0] == "h" and balise[1].isdigit() else 0


# Le bloc cité est-il annoncé comme le texte du Mehaber pour CE siman ?
# « Le texte du Choul\'han Aroukh », « Texte original (Mehaber) », « שולחן ערוך ».
_CUE_MEHABER = re.compile(
    r"m[ée]haber|choul'?han\s+aroukh|shulchan|שולחן ערוך|texte original", re.I
)
# Le Rama est une couche distincte, que Sefaria ne sert pas sous un nom vérifié
# à ce jour : sur un indice de Rama, on s'abstient plutôt que d'inventer une
# référence. Le silence est le bon mode d'échec.
_CUE_RAMA = re.compile(r"\brama\b|\brema\b|רמ[\"'״׳]א|hagaha|הגה", re.I)


def reference_implicite_du_siman(
    page: Page, bloc: ContentBlock, precedents: list[ContentBlock]
) -> ParsedRef | None:
    """Référence déduite de l'identité de la page (§7).

    Sur le site, la plupart des citations du Mehaber ne portent aucune
    référence : la page **est** le siman, et le bloc est simplement annoncé
    par « Le texte du Choul'han Aroukh » ou « Texte original (Mehaber) ».
    C'est le motif non rattaché le plus fréquent du périmètre.

    L'inférence est **conditionnée à un indice explicite** : sans mention du
    Mehaber dans le voisinage immédiat, on ne suppose rien — sinon toute
    citation de Guemara de la page serait comparée au Choulhan Aroukh et
    déclarée absente, ce qui fabriquerait des faux positifs en masse.

    Faute de séif, la référence vise le **siman entier** : Sefaria le sert
    complet, et une citation qui en provient doit s'y trouver.
    """
    if page.siman is None:
        return None
    voisinage = " ".join(
        [bloc.normalized_content] + [p.normalized_content for p in precedents[-3:]]
    )
    if _CUE_RAMA.search(voisinage) or not _CUE_MEHABER.search(voisinage):
        return None
    return ParsedRef(
        raw_text=f"siman {page.siman} (déduit de la page)",
        work="Choulhan Aroukh", section="Orach Chayim",
        siman=str(page.siman), confidence=0.6,
    )


def refs_pour_citation(
    session: Session, bloc: ContentBlock, precedents: list[ContentBlock],
    page: Page | None = None,
) -> tuple[list[ParsedRef], bool]:
    """Références applicables à une citation, et si elles viennent d'un voisin.

    Sur le site, un bloc de citation ne porte presque jamais sa propre
    référence : c'est la prose qui précède qui l'annonce — « La Guemara
    (Beitsa 15b) raconte : » suivi du bloc hébreu. Apparier strictement par
    bloc ne trouve donc jamais rien, ce qu'un premier essai sur une page
    réelle a montré : 79 blocs, 5 références, 8 citations, **zéro** paire.

    On remonte donc les blocs précédents jusqu'à en trouver un qui porte une
    référence, avec deux garde-fous contre le rattachement abusif :

    - un **titre de section** arrête la remontée — une nouvelle section est un
      nouveau sujet, et la référence d'avant ne la concerne plus ;
    - la fenêtre est bornée à ``FENETRE_BLOCS``.

    Le second membre du retour dit si la référence vient d'un voisin ; le
    signalement le mentionne et abaisse sa confiance en conséquence, car un
    rattachement de voisinage est une inférence, pas une lecture.
    """
    propres = _refs_du_bloc(session, bloc)
    if propres:
        return propres, False

    for precedent in reversed(precedents[-FENETRE_BLOCS:]):
        # Seul un titre de RANG MAJEUR (h1/h2) arrête la remontée. Le site
        # emploie h2 pour ses sections numérotées — « 3. Le dilemme central »,
        # un vrai changement de sujet — et h3 pour les intertitres à
        # l'intérieur d'une même sougya : « Enseignement A », « Enseignement
        # B »… Les traiter pareil coupait le lien entre une citation et la
        # source annoncée juste avant les intertitres, et faisait perdre
        # l'essentiel des citations de Guemara.
        if 0 < niveau_de_titre(precedent) <= 2:
            break
        voisines = _refs_du_bloc(session, precedent)
        if voisines:
            return voisines, True

    if page is not None:
        implicite = reference_implicite_du_siman(page, bloc, precedents)
        if implicite is not None:
            return [implicite], True
    return [], False


def _deja_signale(session: Session, page_id: int, finding: Finding) -> bool:
    """Ce signalement existe-t-il déjà pour cette page ?

    Sans ce contrôle, chaque passe d'analyse recrée les signalements : un
    signalement **déjà jugé** — écarté, classé faux positif, tranché par le Rav —
    réapparaîtrait à l'état ``NEW`` à chaque exécution, et le relecteur
    rejugerait indéfiniment la même chose. Les décisions ne vaudraient plus rien.

    La clé retenue est *(page, règle, texte cité)* et non l'identifiant du bloc :
    un bloc appartient à une version de page, si bien qu'une simple retouche
    ailleurs dans la page créerait un nouveau bloc et donc un nouveau
    signalement. Une décision porte sur **ce texte, à cet endroit** ; tant que ni
    l'un ni l'autre ne change, il n'y a pas lieu de redemander un avis.
    """
    return session.execute(
        select(AuditFinding.id).where(
            AuditFinding.page_id == page_id,
            AuditFinding.rule_code == finding.rule_code,
            AuditFinding.current_text == finding.current_text,
        ).limit(1)
    ).scalar_one_or_none() is not None


def blocs_a_verifier(session: Session, simanim: list[int] | None = None,
                     limit: int | None = None) -> list[ContentBlock]:
    """Blocs de la version courante de chaque page, contenant de l'hébreu."""
    requete = (
        select(ContentBlock)
        .join(PageVersion, ContentBlock.page_version_id == PageVersion.id)
        .join(Page, PageVersion.page_id == Page.id)
        .where(Page.current_text_sha256 == PageVersion.text_sha256)
        .order_by(ContentBlock.id)
    )
    if simanim:
        requete = requete.where(Page.siman.in_(simanim))
    if limit:
        requete = requete.limit(limit)
    return list(session.execute(requete).scalars().all())


def run_analyse(
    session: Session,
    settings: Settings,
    provider=None,
    simanim: list[int] | None = None,
    limit: int | None = None,
    dry_run: bool = False,
) -> list[Finding]:
    """Vérifie les citations des blocs stockés. Retourne les signalements."""
    ferme_apres = provider is None
    brut = provider if provider is not None else SefariaProvider(settings)
    source = CachedProvider(brut, session)

    trouves: list[Finding] = []
    examinees = 0
    deja_connus = 0
    try:
        blocs = blocs_a_verifier(session, simanim, limit)
        # Les blocs précédents servent à retrouver la référence qui annonce une
        # citation ; on les accumule par version de page, jamais d'une page à
        # l'autre.
        precedents: dict[int, list[ContentBlock]] = {}

        for bloc in blocs:
            contexte = precedents.setdefault(bloc.page_version_id, [])
            citations = extract_quotes(
                bloc.raw_content,
                marked=bloc.block_type is BlockType.CITATION_HEBRAIQUE,
            )
            if not citations:
                contexte.append(bloc)
                continue
            page_courante = session.get(PageVersion, bloc.page_version_id).page
            refs, par_voisinage = refs_pour_citation(
                session, bloc, contexte, page=page_courante
            )
            contexte.append(bloc)
            if not refs:
                continue

            for citation in citations:
                examinees += 1
                resultat = verifier_citation(citation, refs, source)
                if resultat is None:
                    continue
                finding = finding_de(resultat, bloc.stable_id,
                                     par_voisinage=par_voisinage)
                if finding is None:
                    continue

                page_id = session.get(PageVersion, bloc.page_version_id).page_id
                if _deja_signale(session, page_id, finding):
                    deja_connus += 1
                    continue

                trouves.append(finding)
                if dry_run:
                    continue
                session.add(AuditFinding(
                    page_id=page_id,
                    block_id=bloc.id,
                    category=finding.category,
                    subcategory=finding.subcategory,
                    current_text=finding.current_text,
                    source_text=resultat.source_text,
                    proposed_correction=None,
                    explanation=finding.explanation,
                    sources=resultat.ref.sefaria_ref() if resultat.ref else None,
                    confidence=finding.confidence,
                    severity=finding.severity,
                    risk=finding.risk,
                    rule_code=finding.rule_code,
                    rule_version=finding.rule_version,
                ))
            if not dry_run:
                session.commit()
    finally:
        if ferme_apres and hasattr(brut, "close"):
            brut.close()

    if not dry_run:
        session.add(AuditLog(
            user=None, action="analyse.citations",
            justification=(
                f"{examinees} citation(s) examinée(s), {len(trouves)} nouveau(x) "
                f"signalement(s), {deja_connus} déjà connu(s), "
                f"cache {source.hits} hit / {source.misses} miss"
            ),
        ))
        session.commit()

    logger.info("%s citations examinées, %s nouveaux signalements, %s déjà connus",
                examinees, len(trouves), deja_connus)
    return trouves


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vérification des citations contre Sefaria (lecture seule)"
    )
    parser.add_argument("--simanim", help="ex. 242-245 ou 242,250")
    parser.add_argument("--limit", type=int, help="nombre maximal de blocs examinés")
    parser.add_argument("--dry-run", action="store_true", help="n'écrit rien en base")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    from .crawler.urls import parse_simanim_arg

    settings = get_settings()
    factory = make_session_factory(make_engine(settings))
    simanim = parse_simanim_arg(args.simanim) if args.simanim else None

    with factory() as session:
        findings = run_analyse(session, settings, simanim=simanim,
                               limit=args.limit, dry_run=args.dry_run)

    if not findings:
        print("Aucun NOUVEL écart de citation. Les signalements déjà connus "
              "conservent leur statut et leurs décisions.")
        return 0

    print(f"{len(findings)} nouveau(x) signalement(s) de citation :\n")
    for f in findings:
        print(f"  [{f.severity.value}] {f.block_id}")
        print(f"      {f.current_text[:90]}")
        print(f"      → {f.explanation}\n")
    print("Aucune correction n'est proposée : toute décision revient au Rav.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
