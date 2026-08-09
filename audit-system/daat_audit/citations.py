# -*- coding: utf-8 -*-
"""Vérification des citations contre leur source réelle (§8, §9, §12).

C'est le contrôle qui donne son sens au système : il confronte chaque fragment
**présenté comme littéral** au texte que la page dit citer.

Trois principes gouvernent ce module, et ils viennent tous du domaine :

1. **Aucune correction n'est jamais proposée.** Le signalement porte la
   citation, le texte source et le verdict ; il ne réécrit rien. Réécrire une
   citation, c'est trancher une question de contenu — cela revient au Rav
   (§4). ``proposed_correction`` reste donc à ``None``, y compris quand
   l'écart paraît évident.
2. **Une variante d'édition n'est pas une erreur** (§8). Les verdicts bénins
   — nikoud, ponctuation, graphie pleine/défective, citation tronçonnée dont
   tous les tronçons sont littéraux — ne produisent aucun signalement.
3. **Une absence n'est pas une accusation.** Quand un fragment est absent de
   la source citée, on cherche s'il existe *ailleurs* : cela distingue une
   citation fabriquée d'une citation exacte mal référencée. Les deux
   n'appellent pas la même correction, et le système dit laquelle il constate
   sans jamais affirmer l'intention.
"""
from __future__ import annotations

from dataclasses import dataclass

from .checks import Finding
from .hebrew import SEVERITY, Verdict, compare
from .models import Risk, Severity
from .quotes import Quote
from .references import ParsedRef

# Verdicts qui n'ont pas à être signalés : la citation est littérale, aux
# différences d'édition et de typographie près.
BENINS = {
    Verdict.IDENTIQUE,
    Verdict.DIFF_PONCTUATION,
    Verdict.DIFF_NIKOUD,
    Verdict.DIFF_ORTHOGRAPHE,
    Verdict.CITATION_TRONQUEE,
}

# Gravité du signalement selon le verdict. Le risque est HALAKHIC dans tous les
# cas : il s'agit du texte d'une source, quel que soit le degré de l'écart.
GRAVITE = {
    Verdict.ORDRE_DIFFERENT: Severity.P3_MINOR,
    Verdict.MOT_AJOUTE: Severity.P2_SIGNIFICANT,
    Verdict.MOT_SUPPRIME: Severity.P2_SIGNIFICANT,
    Verdict.VARIANTE_POSSIBLE: Severity.P2_SIGNIFICANT,
    Verdict.MOT_REMPLACE: Severity.P1_MAJOR,
    Verdict.DIFFERENCE_SUBSTANTIELLE: Severity.P0_CRITICAL,
}


@dataclass
class CitationResult:
    quote: Quote
    ref: ParsedRef | None
    verdict: Verdict | None
    ratio: float
    detail: str
    source_text: str = ""
    found_elsewhere: list[str] | None = None


def verifier_citation(
    quote: Quote,
    refs: list[ParsedRef],
    provider,
    *,
    chercher_ailleurs: bool = True,
) -> CitationResult | None:
    """Confronte un fragment cité aux références que son bloc annonce.

    Plusieurs références peuvent voisiner une citation ; on retient **la plus
    favorable**. Retenir la première conduirait à déclarer fausse une citation
    exacte au seul motif qu'une autre référence traînait dans le même bloc.
    """
    candidates = [r for r in refs if r.sefaria_ref()]
    if not candidates:
        return None

    meilleur: CitationResult | None = None
    for ref in candidates:
        document = provider.fetch(ref.sefaria_ref())
        if document is None or not document:
            continue
        verdict, ratio, detail, extrait = _comparer_par_segment(quote.text, document)
        resultat = CitationResult(
            quote=quote, ref=ref, verdict=verdict, ratio=ratio,
            detail=detail, source_text=extrait,
        )
        if meilleur is None or _meilleur_que(resultat, meilleur):
            meilleur = resultat
        if verdict in BENINS:
            break      # inutile de chercher mieux qu'une citation littérale

    if meilleur is None:
        return None

    # Chercher dans tout le corpus AVANT de conclure à une absence : une
    # citation exacte mal référencée et une citation fabriquée n'appellent ni
    # le même verdict, ni la même correction, ni la même gravité.
    if (chercher_ailleurs and meilleur.verdict is not None
            and meilleur.verdict not in BENINS
            and SEVERITY[meilleur.verdict] >= SEVERITY[Verdict.MOT_REMPLACE]):
        try:
            hits = provider.search(quote.text)
        except Exception:       # un service tiers indisponible n'invalide rien
            hits = []
        meilleur.found_elsewhere = [h.ref for h in hits][:4]

    return meilleur


def _comparer_par_segment(texte: str, document) -> tuple[Verdict, float, str, str]:
    """Compare la citation à la **bonne sous-section**, pas au folio entier.

    Sefaria sert un folio en segments. Les fondre en un seul bloc a deux
    défauts : le taux de similarité devient une moyenne sans signification sur
    plusieurs milliers de mots, et une correspondance fortuite à cheval sur
    deux passages sans rapport suffit à produire une « variante possible ».

    On compare donc segment par segment, et l'on retient le meilleur. Les
    paires de segments voisins sont également essayées, car une citation
    chevauche souvent une frontière ; le texte entier sert de dernier recours.

    Le quatrième membre du retour est le passage effectivement retenu : c'est
    lui qui est archivé et montré au relecteur, plutôt que tout le folio.
    """
    segments = [s for s in document.segments if s.strip()]
    candidats: list[str] = list(segments)
    candidats += [a + " " + b for a, b in zip(segments, segments[1:])]
    if not candidats:
        candidats = [document.text]

    meilleur: tuple[Verdict, float, str, str] | None = None
    for extrait in candidats:
        verdict, ratio, detail = compare(texte, extrait)
        courant = (verdict, ratio, detail, extrait[:2000])
        if meilleur is None or (SEVERITY[verdict], -ratio) < (SEVERITY[meilleur[0]], -meilleur[1]):
            meilleur = courant
        if verdict in BENINS:
            return courant

    # Dernier recours : la citation enjambe peut-être plus de deux segments.
    verdict, ratio, detail = compare(texte, document.text)
    if meilleur is None or (SEVERITY[verdict], -ratio) < (SEVERITY[meilleur[0]], -meilleur[1]):
        return verdict, ratio, detail, document.text[:2000]
    return meilleur


def _meilleur_que(a: CitationResult, b: CitationResult) -> bool:
    if a.verdict is None or b.verdict is None:
        return b.verdict is None
    if SEVERITY[a.verdict] != SEVERITY[b.verdict]:
        return SEVERITY[a.verdict] < SEVERITY[b.verdict]
    return a.ratio > b.ratio


def finding_de(resultat: CitationResult, block_id: str,
               *, par_voisinage: bool = False) -> Finding | None:
    """Signalement correspondant à un résultat, ou ``None`` s'il est bénin.

    ``par_voisinage`` dit que la référence n'a pas été lue dans le bloc de la
    citation mais dans la prose qui l'annonce. C'est le cas courant sur le
    site, mais cela reste une inférence : le signalement le dit et sa
    confiance en tient compte.
    """
    if resultat.verdict is None or resultat.verdict in BENINS:
        return None

    ref_txt = resultat.ref.sefaria_ref() if resultat.ref else "?"
    explication = (
        f"citation donnée pour littérale, mais {resultat.detail or 'différente'} "
        f"par rapport à {ref_txt} (similarité {resultat.ratio:.0%})"
    )

    severite = GRAVITE.get(resultat.verdict, Severity.P2_SIGNIFICANT)

    if resultat.verdict is Verdict.DIFFERENCE_SUBSTANTIELLE:
        if resultat.found_elsewhere:
            # Le texte existe, mot pour mot, ailleurs : ce n'est pas une
            # falsification mais un défaut de référence. Le classer P0 mettait
            # sur le même plan « la page invente une source » et « la page se
            # trompe de folio » — deux choses qui n'appellent ni la même
            # urgence ni la même correction.
            severite = Severity.P2_SIGNIFICANT
        if resultat.found_elsewhere:
            explication = (
                f"absente de {ref_txt}, mais retrouvée mot pour mot en "
                f"{', '.join(resultat.found_elsewhere)} — la référence semble "
                "être celle qui est erronée, non le texte cité"
            )
        elif resultat.found_elsewhere is not None:
            explication = (
                f"absente de {ref_txt}, et introuvable ailleurs dans le corpus "
                "interrogé — à vérifier par le Rav avant toute conclusion"
            )

    confiance = min(0.95, resultat.ref.confidence if resultat.ref else 0.5)
    if par_voisinage:
        # La référence est une inférence, pas une lecture : elle ne peut pas
        # fonder un signalement critique.
        if severite is Severity.P0_CRITICAL:
            severite = Severity.P1_MAJOR
        explication += (
            " — référence rattachée depuis le texte qui annonce la citation, "
            "non depuis le bloc cité lui-même"
        )
        confiance *= 0.8

    # Le texte existe ailleurs mot pour mot : le défaut porte sur la
    # référence, non sur le texte. Le dire dans la catégorie, et pas seulement
    # dans la phrase, permet de trier les deux séparément.
    sous_categorie = ("reference_erronee" if resultat.found_elsewhere
                      else resultat.verdict.value)

    return Finding(
        rule_code="CIT-001",
        category="citation",
        subcategory=sous_categorie,
        block_id=block_id,
        current_text=resultat.quote.text[:600],
        explanation=explication,
        # Jamais de correction proposée sur une citation : voir §1 du module.
        proposed_correction=None,
        severity=severite,
        risk=Risk.HALAKHIC,
        confidence=round(confiance, 3),
    )
