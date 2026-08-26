# DAAT — Audit de contenu éditorial & halakhique

Règle : **aucune décision halakhique n'est réécrite sans validation du Rav.**
Statuts : `NEW` → `TRIAGED` → `NEEDS_RABBINIC_VALIDATION` → `APPROVED` → `FIXED` / `REJECTED`.

| ID | URL / fichier | Siman · Sé'if | Problème | Source contradictoire | Confiance | Statut |
|----|---------------|---------------|----------|----------------------|-----------|--------|
| C1 | data/simanim-disponibles.json | — | Compteurs affichés aux visiteurs périmés : `yoreh-deah: 32` (50 sur disque), `nida: 18` (dossiers physiques sous yoreh-deah), `lastUpdated: 2026-06-28` | constat disque | haute | TRIAGED (technique, pas halakhique — voir D5) |
| C2 | index.html (JSON-LD FAQPage) | — | FAQPage en JSON-LD sur la homepage sans bloc FAQ visible correspondant — risque de non-conformité aux règles Google sur les rich results | Google Search Central | moyenne | NEW |

*(Les incidents halakhiques historiques — ex. borer 2026-07-20 — sont suivis dans la mémoire projet ; les nouveaux cas détectés s'ajoutent ici.)*

| C3 | /questions/* (5 pages pilote : rechauffer-plat, plata, trier-borer, kiddoush-vendredi-soir, lire-bougie) | 318 · 253 · 319 · 271 · 275 | Pilote long-tail SEO : réponses résumées depuis les synthèses N3 publiées du site. **En noindex + bandeau jusqu'à validation du Rav.** À valider : exactitude des résumés, formulation des minhaguim (318), puis retirer noindex + sitemap + liens internes. | synthèses N3 des simanim cités | haute (contenu déjà publié) | NEEDS_RABBINIC_VALIDATION |
