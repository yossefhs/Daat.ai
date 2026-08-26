# DAAT — Journal Growth & Produit

> Journal opérationnel permanent (mode DAATTORAH — Product, SEO, Growth & Execution).
> Complète les docs stratégiques existants : [SEO-AEO-2026-PLAN.md](SEO-AEO-2026-PLAN.md), [STRATEGIE-CROISSANCE.md](STRATEGIE-CROISSANCE.md), [PERFORMANCE-2026.md](PERFORMANCE-2026.md).
> Décisions datées : [DAAT_DECISIONS.md](DAAT_DECISIONS.md). Problèmes éditoriaux/halakhiques : [DAAT_CONTENT_AUDIT.md](DAAT_CONTENT_AUDIT.md).

## Vision

Faire de daattorah.com la référence francophone d'étude structurée du Choulhan Aroukh :
Google → question → réponse → source → siman → approfondissement → Daat Yomi → chat → retour quotidien → communauté → partage → participation → soutien.

## État des lieux (audité, session 1)

- **Corpus disque** : 371 dossiers siman — Chabbat 124 (242–365), Yoreh De'ah 50 (87–200, dont Nida 183–200), Orah Haïm quotidien 197 (1–197). Nida = section d'index (fichiers physiques sous yoreh-deah).
- **Routes** : `/oh/` (Chabbat), `/yd/`, `/oh-quotidien/`, `/nida/` (index seul), `/limoud/` (Daat Yomi, 194 jours ×3 langues).
- **SEO** : sitemap 6259 URLs + sitemap-llm 125 ; robots.txt accueille les bots IA ; canonicals/hreflang par langue ; JSON-LD riche (Course sur limoud, FAQPage sur simanim…).
- **Analytics** : script Vercel Web Analytics présent sur ~100 % des pages, **mais Web Analytics non activé au niveau projet** (API → 404) ⇒ aucune donnée collectée. Aucun event custom.
- **Chat** : widget FAB sur tout le site + chat.html plein écran. Payload = messages + section uniquement (pas de siman ; niveau/minhag en texte). Pas d'auto-open ni teaser.
- **Daat Yomi** : bandeau généré (scripts/generate-limoud-plan.cjs + data/.banner-snippets/), plan 194 jours (2026-06-08 → 2027-03-04), newsletter cron 9h, plan personnalisé KV.
- **Dons** : Qonto (4 montants), HelloAsso (dédicaces + upgrade plan auto via webhook), Tomhei Adaat.
- **Communauté** : 1 lien WhatsApp unique (communaute×3). Aucun lien WhatsApp sur simanim/limoud/blog.

## KPIs — BASELINE (23→26 août 2026, ~3 jours de collecte)

| Métrique | Valeur | Lecture |
|---|---|---|
| Visiteurs / Pages vues | **107 / 346** | 3,2 pages/visiteur · bounce 55 % |
| Top pages | / (40) · /oh (24) · **/oh/281/base (13) · /oh/282/base (10) · /oh/279/base (9)** | Les simanim du Daat Yomi en cours dominent → **les visiteurs suivent le programme quotidien** |
| Référents | **Facebook 13** · Google 9 · Bing 4 · **chatgpt.com 1** | FB mobile = 1er canal externe ; SEO naissant ; 1er référé IA |
| Pays | Israël 46 % · France 24 % · USA 17 % | |
| Appareils | **Mobile 65 %** (iOS 33 + Android 32) | Confirme le mobile-first du brief |
| Events | daat_yomi_started **7/8** · chat_cta_hero 4/4 · chat_open 3/13 · share_clicked 2/2 · correction_submitted 1/1 | Le CTA Daat Yomi convertit ; baseline E1 : chat_cta_hero ≈ 3,7 % des visiteurs |

## Backlog priorisé

### P0
- [x] Tuiles index YD/OH-quotidien/Nida pointaient vers `/sources/...` physiques → routes propres `/yd/N/`, `/oh-quotidien/N/` (S1)
- [x] Web Analytics activé par le Rav (S2) — collecte vérifiée bout en bout.

### P1
- [x] Redirects 301 `/sources/yoreh-deah|orah-haim/siman-N` → routes (S1)
- [x] CTA hero « Tester l'IA Daat » → « Poser une question de Halakha » ×3 langues (S1)
- [x] Metas/JSON-LD homepage : « 124 simanim / 3 niveaux » → périmètre réel 4 sections / 4 niveaux ×3 langues (S1)
- [x] `/aujourdhui` → redirect vers `/limoud/` (S1 ; page dédiée = P2)
- [x] Listings `/yd`, `/oh-quotidien`, `/nida` : 247 tuiles statiques injectées au build (generate-section-listings.js) ; générateur JSON v2.1 section-aware réintégré au build, zéro perte de titres (S1)
- [x] Teaser « 64 simanim » → compteur généré au build (197) + 197 tuiles statiques sur /oh/ (S1)
- [x] Events custom v1 : chat_open, chat_question_sent(+section), daat_yomi_started, whatsapp_clicked, chat_cta_hero — vérifiés en prod (POST /event 200) (S2)
- [x] Chat contextuel : detectSimanContext() (routes + chemins physiques + niveaux, 12 cas testés), contexte injecté dans le 1er message (jamais dans le system prompt caché 1h), FAB « Poser une question sur le Siman N », chat_question_sent enrichi du siman — vérifié en prod sur /oh/318/lamdan (S2)

### P2
- [x] Page `/aujourdhui` réelle ×3 langues : carte Daat Yomi du jour hydratée par api/aujourdhui.js (cache edge minuit Paris), CTA chat/communauté, partage WhatsApp, repli statique crawlable — vérifiée en prod (jour 57/194, siman 282, CTA /limoud/jour-057) (S4)
- [x] Partage WhatsApp : bouton flottant trilingue sur toutes les pages de contenu (simanim OH/YD, limoud, blog) via daat-copy.js — partage natif mobile + wa.me desktop, event share_clicked{type,ref} vérifié en prod (S3). Reste : partage des réponses chat (déjà présent dans la barre feedback).
- [x] FAQPage retiré du JSON-LD homepage ×3 (non conforme sans FAQ visible ; faq.html garde le sien) — round-trip JSON validé, vérifié en prod (S6)
- [x] `/nida/:n(/…)` → 302 vers `/yd/:n(/…)` (contenu physique sous yoreh-deah ; passera en rewrite si pages Nida dédiées) — vérifié en prod (S6)
- [x] Signaler-une-erreur : lien ⚑ + modal trilingue sur toutes les pages de contenu (daat-copy.js), api/signalement.js (rate-limit 5/j/IP, honeypot, zéro donnée perso), back-office admin/signalements.html (stats, filtre, statuts, suppression), pipeline NEW→NEEDS_RABBINIC_VALIDATION→FIXED, event correction_submitted — E2E prod vérifié (S5)
- [x] Artefacts racine gitignorés (~87 doublons untracked — jamais déployés) ; la sauvegarde organisée chiourim/ (57 fichiers) reste versionnée volontairement (S6)

### P3
- [x] Kit communautés partenaires : /partenaires — programme hebdo auto-généré (api/aujourdhui?semaine=1), message WhatsApp copier/transférer, QR statique vers /aujourdhui, events partner_kit_* — E2E prod vérifié (S8)
- [ ] Dashboard croissance consolidé (un écran admin : acquisition, chat, Daat Yomi, partages, signalements, dons)
- [ ] Veille concurrentielle
- [ ] /partenaires en HE/EN si demande

## Expérimentations

| ID | HYPOTHESIS | CHANGE | METRIC | BASELINE | START | RESULT | DECISION |
|----|-----------|--------|--------|----------|-------|--------|----------|
| E1 | Un CTA orienté bénéfice augmente l'usage du chat vs « Tester l'IA » | Hero ×3 langues | chat_cta_hero / visiteurs | **3,7 % (4/107, S7)** | S1 | — | — |

## Journal des sessions

### S8
Kit communautés partenaires livré (commit f80641ad4), suite directe du bilan S7 (Daat Yomi = moteur, FB/WhatsApp = canaux). /partenaires : self-service pour Beth Habad/synagogues/kollelim/groupes — programme de la semaine auto-généré, message WhatsApp prêt à transférer, QR imprimable (statique — URL /aujourdhui stable), zéro maintenance. E2E prod : 5 jours affichés (j55-59, simanim 281-284 avec titres), message construit, wa.me valide, QR chargé. Liens découverte depuis footers /aujourdhui ×3.

### S7
Premier bilan chiffré (dashboard lu via navigateur — l'API de requête MCP reste 404, dashboard = source de vérité). Enseignement majeur : le Daat Yomi est le moteur réel du site (3 des 5 top pages = simanim du programme en cours, event daat_yomi_started en tête) ; Facebook mobile = 1er canal externe ; mobile 65 %. Décision data-driven : prioriser l'amplification communautaire (kit partenaires P3, canaux FB/WhatsApp) qui renforce ce qui marche, long-tail SEO en chantier de fond (Google = 9 visiteurs seulement).

### S6
Reliquat P2 soldé (commit 122635f39) : FAQPage homepage retiré ×3 (JSON-LD re-validé), redirects /nida/:n → /yd/:n (307 vérifiés en prod), .gitignore des artefacts racine (chiourim/ versionné conservé). Backlog P2 : VIDE — restent les P3 et le premier bilan analytics.

### S5
Signaler-une-erreur livré (commit cfa19d3b1) : les lecteurs deviennent relecteurs, aucune halakha modifiée sans validation du Rav. E2E prod : modal 4 champs OK sur /oh/318/lamdan, POST public accepté (signalement test sig_mt8zkjie_x1j9i — à supprimer depuis l'admin), GET sans mot de passe → 401, back-office 200. Note cache : assets JS en max-age=0 must-revalidate → propagation immédiate pour les visiteurs.

### S4
Page /aujourdhui livrée (commit 19978c2f3) : api/aujourdhui.js (JSON public du jour, getEntryForDate, cache CDN jusqu'à minuit Paris, fallback prochaine entrée les vendredi/shabbat) + aujourdhui.html ×3 langues + rewrites (remplacent le 302) + partage WhatsApp actif sur la page. E2E prod : date, jour 57/194, siman 282 partie 2/2, séifim 6-7, CTA correct, share FAB + chat FAB présents.

### S3
Partage WhatsApp livré (commit 63a6593e0) : module dans daat-copy.js (porteur déjà chargé sur toutes les pages de contenu — zéro édition des 582 pages limoud générées ni des ~5500 pages simanim). Bouton flottant bas-gauche trilingue, navigator.share natif + repli wa.me, event share_clicked{type,ref}. 11 cas d'URL testés + E2E prod sur /limoud/jour-042 (event 200). Rebase sur 17 commits d'une autre session (oh-quotidien 198-200), zéro conflit.

### S2
Chat contextuel livré (commit 2acd3cbb0) : Daat sait quel siman l'utilisateur consulte. Reste v2 : contexte sur les pages /limoud/jour-NNN (siman non présent dans l'URL — à lire dans le DOM).
Mode quotidien : santé prod OK (tuiles /yd 32, insights 200). Web Analytics activé par le Rav (S1→S2) — première pageview + 2 events custom validés bout en bout via navigateur (POST /view et /event → 200). Livré commit 849496883 : vaTrack() dans chat-widget.js (chat_open, chat_question_sent+section) + listener délégué sur index×3 et communaute×3 (daat_yomi_started, whatsapp_clicked, chat_cta_hero). JS inline validé node --check partout. Reste API MCP get_web_analytics en 404 (propagation) — le dashboard Vercel fait foi.

### S1 (suite)
SSG livré : commits f1a696f58 + 31a77da2f — 247 tuiles statiques crawlables sur /yd /oh-quotidien /nida, 197 sur /oh/, JSON régénéré (371 simanim, sections exactes), build re-câblé, pluriel « simanim » corrigé. Vérifié en prod.

### S1
Audit complet (agent + prod). 9 fichiers index corrigés (hrefs), 9 redirects, CTAs ×3, metas ×3, journal créé. Détails : DAAT_DECISIONS.md.
