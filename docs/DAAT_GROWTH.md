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

## KPIs (à activer — bloqué par Web Analytics OFF)

Acquisition : visiteurs, organique, impressions/clics GSC. Engagement : questions chat, pages/visite. Daat Yomi : J+1, J+7, complétions. Communauté : clics WhatsApp. Soutien : dons.

## Backlog priorisé

### P0
- [x] Tuiles index YD/OH-quotidien/Nida pointaient vers `/sources/...` physiques → routes propres `/yd/N/`, `/oh-quotidien/N/` (S1)
- [ ] **Activer Vercel Web Analytics dans le dashboard** (action humaine, 2 clics) — tout le pipeline mesure est prêt et inerte.

### P1
- [x] Redirects 301 `/sources/yoreh-deah|orah-haim/siman-N` → routes (S1)
- [x] CTA hero « Tester l'IA Daat » → « Poser une question de Halakha » ×3 langues (S1)
- [x] Metas/JSON-LD homepage : « 124 simanim / 3 niveaux » → périmètre réel 4 sections / 4 niveaux ×3 langues (S1)
- [x] `/aujourdhui` → redirect vers `/limoud/` (S1 ; page dédiée = P2)
- [x] Listings `/yd`, `/oh-quotidien`, `/nida` : 247 tuiles statiques injectées au build (generate-section-listings.js) ; générateur JSON v2.1 section-aware réintégré au build, zéro perte de titres (S1)
- [x] Teaser « 64 simanim » → compteur généré au build (197) + 197 tuiles statiques sur /oh/ (S1)
- [x] Events custom v1 : chat_open, chat_question_sent(+section), daat_yomi_started, whatsapp_clicked, chat_cta_hero — vérifiés en prod (POST /event 200) (S2)
- [ ] Chat : transmettre `siman` + URL d'origine dans le payload ; CTA « Poser une question sur ce siman » sur les pages siman.

### P2
- [ ] Page `/aujourdhui` réelle (Daat Yomi du jour + question du jour + partage WhatsApp).
- [ ] Boutons partage WhatsApp sur jour-NNN, simanim, réponses chat.
- [ ] FAQPage JSON-LD homepage sans FAQ visible correspondante → conformité Google à vérifier.
- [ ] `/nida/:n` routes propres (Nida pointe vers /yd/N en attendant).
- [ ] Signaler-une-erreur (formulaire + pipeline NEEDS_RABBINIC_VALIDATION).
- [ ] Sortir les artefacts de transcription (~60 fichiers chiour*/build_subs*) de la racine du repo public.

### P3
- Communautés partenaires (kit hebdo), dashboard croissance, veille concurrentielle.

## Expérimentations

| ID | HYPOTHESIS | CHANGE | METRIC | BASELINE | START | RESULT | DECISION |
|----|-----------|--------|--------|----------|-------|--------|----------|
| E1 | Un CTA orienté bénéfice augmente l'usage du chat vs « Tester l'IA » | Hero ×3 langues | chat_cta_hero + chat_open / sessions | en cours de collecte | S1 | — | — |

## Journal des sessions

### S2
Mode quotidien : santé prod OK (tuiles /yd 32, insights 200). Web Analytics activé par le Rav (S1→S2) — première pageview + 2 events custom validés bout en bout via navigateur (POST /view et /event → 200). Livré commit 849496883 : vaTrack() dans chat-widget.js (chat_open, chat_question_sent+section) + listener délégué sur index×3 et communaute×3 (daat_yomi_started, whatsapp_clicked, chat_cta_hero). JS inline validé node --check partout. Reste API MCP get_web_analytics en 404 (propagation) — le dashboard Vercel fait foi.

### S1 (suite)
SSG livré : commits f1a696f58 + 31a77da2f — 247 tuiles statiques crawlables sur /yd /oh-quotidien /nida, 197 sur /oh/, JSON régénéré (371 simanim, sections exactes), build re-câblé, pluriel « simanim » corrigé. Vérifié en prod.

### S1
Audit complet (agent + prod). 9 fichiers index corrigés (hrefs), 9 redirects, CTAs ×3, metas ×3, journal créé. Détails : DAAT_DECISIONS.md.
