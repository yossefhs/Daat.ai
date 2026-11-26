# Protocole allégé — scripts de travail (copies de référence)

Rangés ici le 26 novembre 2026 parce que les originaux, tenus dans l'espace temporaire de la session, ont été effacés par un
redémarrage (voir `audit/oh-394-397/LISEZMOI.md`). Ce sont des copies : les chemins (`SP`, `wt-eN`, `memoire-eN`), les numéros de
simanim et les chaînes du catalogue sont ceux du dernier lot qui les a employés ; les adapter avant de relancer.

- `lot-leger.js` — workflow de production et de vérification allégée (un rédacteur par niveau : N1 ∥ N4 → N2 → N3 + index ;
  puis deux vérificateurs par passe, un arbitre sur les objections graves, trois passes au plus). Args : `{simanim, tours}`.
- `confirmation.js` — passe de confirmation unique (deux vérificateurs par siman, sans arbitre). Args : `{simanim, passe, contexte}`.
- `liens-suivant.py` — pose le lien « suivant » N → N+1 dans les 15 pages de N.
- `integrer-e8.py` — données `data/simanim/siman-N.json`, cartes et entêtes du catalogue, introduction, bouton de section
  (version du lot 394-397, qui a ouvert la section Te'houmin).
- `portes.sh` — toutes les portes de publication, une à la fois (rendu Chromium compris : modules Python playwright, pillow, numpy).
- `enligne.sh` — attend le déploiement (empreinte du sitemap) puis compare chaque fichier publié à son équivalent en ligne.
