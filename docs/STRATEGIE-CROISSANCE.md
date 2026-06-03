# 🚀 Stratégie de croissance DAAT — SEO · Réseaux sociaux · Newsletter · Blog

> Document de synthèse + plan d'action. Objectif : faire connaître `daattorah.com`,
> publier en permanence **sans effort manuel**, et installer DAAT comme la
> référence francophone de l'étude halakhique en ligne.
>
> Rédigé le 2026-06-03. Branche : `claude/date-ai-promotion-strategy-WCqE1`.

---

## 1. État des lieux — ce qui existe déjà (audit du dépôt)

DAAT est **déjà très bien armé techniquement**. Avant d'ajouter quoi que ce soit,
voici l'actif réel détecté dans le code :

| Brique | Statut | Détail |
|--------|--------|--------|
| **Contenu** | 🟢 Énorme | 124 simanim (Orah Haïm 242–365) × 4 niveaux × 3 langues (FR/HE/EN) = corpus de réutilisation gigantesque |
| **SEO technique** | 🟢 Excellent | `sitemap.xml` (123 KB), `robots.txt` qui **accueille explicitement** GPTBot, ClaudeBot, PerplexityBot, Google-Extended ; canonical URLs ; schémas FAQPage/AboutPage/Person ; corrections Lighthouse (CLS + contraste WCAG AA) |
| **AEO / LLM** | 🟢 Rare et précieux | `llms.txt` (42 KB) — fichier dédié aux moteurs de réponse IA. **Très peu de sites l'ont.** Avantage compétitif. |
| **Newsletter** | 🟢 En production | `api/newsletter.js` + `api/_email-sequence.js` : inscription publique + **séquence automatique J0→J14** (welcome + 5 emails) via **Resend** + **Vercel KV**. Cron quotidien `0 9 * * *`. Promesse : « un siman chaque dimanche ». |
| **Visuels sociaux** | 🟡 Embryon | `scripts/generate-og-image.js` génère une image Open Graph SVG 1200×630 par siman (charte DAAT navy/or). Note dans le code : « pour Facebook on pourra brancher `@vercel/og` plus tard ». |
| **Partage** | 🟡 Manuel | Bouton « 📤 Partager » sur les réponses du chat (PR #103). |
| **Page LinkedIn** | 🟢 Créée | Page entreprise « DAAT דעת » existe (Guillaume Samama t'a nommé Super-administrateur le 01/06/2026). **Aucune publication automatisée dessus pour l'instant.** |
| **Communauté** | 🟢 Active | Groupe WhatsApp + formulaire Khavroutha (`communaute.html`). |
| **Blog / articles** | 🔴 Absent | **Aucune section blog/actualités** sur le site. C'est le grand manque pour le SEO/AEO. |
| **Publication réseaux** | 🔴 Absent | **Aucun système d'auto-publication** Instagram/Facebook/LinkedIn/X. Tout est manuel. |
| **« Skill » de publication** | 🔴 Introuvable | Recherché dans `.claude/skills`, skills globaux et Google Drive : **n'existe pas en tant que fichier**. C'était un concept discuté, jamais matérialisé. Seul skill présent : `session-start-hook`. |
| **« Omniprésence sociale »** | 🔴 Concept | Pas de fichier ni d'outil connecté. C'est le terme marketing « social omnipresence » (être partout à la fois) — voir §4, c'est exactement ce que la solution ci-dessous met en place. |

### Verdict
La **fondation est là** (contenu + SEO + newsletter + Vercel/Node + Anthropic SDK).
Il manque **2 choses** pour décoller : **(A)** un moteur d'auto-publication réseaux
sociaux, et **(B)** un **blog** pour capter le trafic de recherche et nourrir l'IA.

---

## 2. Synthèse des conversations / traces passées

Recherche menée dans Gmail + Google Drive (compte `yossefhs@gmail.com`) :

- **Newsletter déjà lancée et fonctionnelle** : email de bienvenue Resend reçu
  (« Barukh haba dans la communauté Daat », 06/05/2026) — promesse d'« un siman
  du Choulhan Aroukh chaque dimanche ».
- **Page LinkedIn DAAT créée** le 01/06/2026 (tu en es Super-administrateur).
- **Modèles de référence dans ta boîte** : tu reçois depuis des années les
  newsletters **Torah-Box** (feuillet hebdo paracha), **Chiourim**, **Mercaz
  Daat (daat.org.il)**. Ce sont les formats qui marchent dans le monde Torah
  francophone → à imiter (régularité hebdo + dédicace d'étude + visuel fort).
- **Aucune trace d'un « skill » d'auto-publication** ni de doc « omniprésence
  sociale » sauvegardé. → On part donc d'une feuille blanche **propre**, ce qui
  est une bonne nouvelle : on construit directement la bonne architecture.

---

## 3. Recherche web — meilleures pratiques 2026

### 3.1 SEO → AEO (Answer Engine Optimization)
Le jeu a changé : on n'optimise plus seulement pour Google, mais pour **être cité
par ChatGPT, Perplexity, Claude et les Google AI Overviews**.

- **55 %** des citations d'AI Overview viennent des **30 premiers %** de la page →
  mettre la **réponse directe en tête** de chaque page.
- **38 %** des citations viennent du **top 10 Google** → AEO ≠ remplace le SEO,
  c'est une extension.
- Formats gagnants : **définition concise en intro**, **listes ordonnées /
  checklists**, **tableaux comparatifs**, **Q/R structurées** (schema FAQ).
- DAAT a déjà `llms.txt` + schémas → **on est en avance**. Le manque = du
  **contenu « réponse à une question »** indexable = **un blog**.

### 3.2 Outils d'auto-publication réseaux (comparatif 2026)

| Outil | Modèle | Prix d'entrée | Plateformes | Pour DAAT |
|-------|--------|---------------|-------------|-----------|
| **Postiz** | Open-source, **auto-hébergeable**, API | **Gratuit** (self-host) / cloud 29 $/mo | 30+ (X, LinkedIn, IG, FB, TikTok, YouTube, Threads, Bluesky, Mastodon…) | ⭐ **Recommandé** — gratuit, API, agentic, contrôle total |
| **Ayrshare** | API-first, clé en main | 149 $/mo (limité) | 13 | Le plus simple à coder, mais **cher** pour une asso |
| **Buffer** | SaaS simple | **Tier gratuit** + API | IG, FB, LinkedIn, X, TikTok, Pinterest | Bon démarrage gratuit, API correcte |
| **n8n** | Orchestrateur open-source | **Gratuit** (self-host) / cloud | Via Postiz/Ayrshare/Buffer | ⭐ **La « colle »** qui automatise tout le pipeline |
| Publer / Vista / SocialPilot | SaaS | 30–79 $/mo | 10–15 | Manuel, moins « code-first » |

**Insight clé 2026** : 83 % des équipes marketing automatisent leurs publications,
mais celles qui **adaptent le message par plateforme** (vs copier-coller identique)
ont un engagement nettement meilleur → la génération de contenu doit produire
**une variante par réseau**, pas un texte unique.

### 3.3 Pipeline IA « 1 contenu → 10 formats »
Le pattern qui marche pour un créateur solo en 2026 :
**source unique → IA génère N variantes → publication multi-plateforme → newsletter**,
avec **une étape de validation humaine** avant mise en ligne (au début).
Un blog post peut devenir 10+ assets (thread X, carrousel IG, post LinkedIn,
post FB, story, email) **sans réécriture manuelle**.

---

## 4. ⭐ La solution recommandée — « Moteur de contenu DAAT »

> **Principe : DAAT produit déjà LE contenu le plus dur à produire (la Torah de
> qualité). On ne crée rien de neuf — on REDISTRIBUE automatiquement le corpus
> existant partout, en permanence.** C'est ça, l'« omniprésence sociale ».

### 4.1 Architecture (s'appuie sur l'existant, zéro réécriture du site)

```
┌─────────────────────────────────────────────────────────────────────┐
│  SOURCE  : corpus existant (124 simanim × 4 niveaux × 3 langues)      │
│            + calendrier juif (paracha / fête de la semaine)           │
└───────────────────────────────┬─────────────────────────────────────┘
                                 │  Cron Vercel hebdo (déjà en place)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GÉNÉRATION  : Claude (Anthropic SDK, déjà installé)                  │
│   1 siman  →  • post LinkedIn (ton pro, 1 enseignement)              │
│              • thread X (3-5 tweets, la sougya en fil)               │
│              • caption Instagram + texte carrousel                   │
│              • post Facebook (groupe communautaire)                  │
│              • story / hook « halakha pratique du jour »             │
│              • brouillon d'article de BLOG (SEO/AEO long)            │
│              • objet + corps de l'email newsletter                   │
└───────────────────────────────┬─────────────────────────────────────┘
                                 ▼
┌──────────────────────────────┐   ┌──────────────────────────────────┐
│  VISUEL : generate-og-image  │   │  VALIDATION (option, au début)   │
│  → carte SVG/PNG par siman   │   │  Brouillon → ton email/Notion    │
└──────────────┬───────────────┘   └───────────────┬──────────────────┘
               │                                    │ « OK » en 1 clic
               ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PUBLICATION : Postiz (API)  →  LinkedIn · Instagram · Facebook · X  │
│  NEWSLETTER  : Resend (déjà en place)  →  email hebdo                 │
│  BLOG        : nouvelle section /blog/ du site (SEO/AEO)              │
└─────────────────────────────────────────────────────────────────────┘
```

**Pourquoi c'est la meilleure option pour DAAT :**
1. **Réutilise 90 % de l'infra déjà payée/codée** (Vercel cron, Anthropic SDK,
   Resend, KV, générateur OG). Coût marginal ≈ 0.
2. **Le contenu existe déjà** — Claude ne « hallucine » pas de la halakha, il
   **reformate** un siman validé. Sécurité halakhique préservée (+ le disclaimer
   « pour la pratique, demande à ton Rav » est déjà dans l'ADN du site).
3. **Une variante par plateforme** (best practice 2026), pas du copier-coller.
4. **Le blog nourrit le SEO ET l'IA** (AEO) ET les réseaux ET la newsletter :
   un seul effort, 5 canaux.
5. **Validation humaine optionnelle** au début (tu valides en 1 clic), puis
   **100 % autonome** une fois la qualité éprouvée.

### 4.2 Le composant central : `/blog/` (le chaînon manquant)
Un blog est le **multiplicateur** : c'est la seule brique qui sert SEO + AEO +
réseaux + newsletter en même temps. Idées de rubriques, toutes tirées du corpus :
- **« La halakha de la semaine »** (liée à la paracha / fête à venir).
- **« 3 minutes pour comprendre… »** (vulgarisation d'un siman, intent définitionnel).
- **« Mehaber vs Rama vs Admour HaZaken sur… »** (intent comparatif → adoré par l'IA).
- **« Cas pratique »** (intent process : checklist + Q/R → schema FAQ).
Chaque article = réponse directe en intro (AEO) + sources citées (déjà le standard DAAT).

### 4.3 Recommandation d'outil de publication
- **Démarrage gratuit / contrôle total** → **Postiz auto-hébergé** (open-source,
  API, 30+ réseaux). Idéal pour une asso financée par les dons.
- **Si tu veux zéro maintenance serveur** → **Buffer (tier gratuit)** pour
  commencer, puis **Ayrshare** si le budget le permet plus tard.
- **Orchestration** → soit directement dans le code Vercel (cron → génération →
  appel API Postiz), soit via **n8n** si tu préfères un canvas visuel modifiable
  sans code.

---

## 5. Plan d'action par phases

### Phase 0 — Quick wins (cette semaine, 0 € )
- [ ] Publier **manuellement** 2-3 posts sur la page LinkedIn (l'amorcer).
- [ ] Ajouter les **liens réseaux + lien newsletter** dans le footer de toutes les pages.
- [ ] Vérifier que les **OG images** s'affichent bien au partage (LinkedIn/WhatsApp).
- [ ] Soumettre `sitemap.xml` à Google Search Console + Bing Webmaster.

### Phase 1 — Le blog (fondation SEO/AEO) — *le plus gros levier*
- [ ] Créer la section `/blog/` (réutilise le template/charte existants).
- [ ] Script `generate-blog-post.js` : 1 siman → 1 article AEO (Claude).
- [ ] Publier 4–8 articles de départ (1 par grande rubrique).
- [ ] Ajouter le blog au `sitemap.xml` + flux **RSS** (= source pour l'automation).

### Phase 2 — Moteur d'auto-publication réseaux
- [ ] Choisir l'outil (Postiz self-host recommandé) + connecter les comptes.
- [ ] `api/social-cron.js` (ou workflow n8n) : cron hebdo → Claude génère le
      « content kit » multi-plateforme → publication via API.
- [ ] Étape validation : brouillon envoyé par email, publication sur « OK ».
- [ ] Passer en **100 % autonome** une fois la qualité validée sur ~4 semaines.

### Phase 3 — Boucle de croissance
- [ ] Newsletter : ajouter un **CTA de parrainage** (« invite un ami à étudier »).
- [ ] Réseaux → site : chaque post renvoie vers le siman/blog correspondant.
- [ ] Mesurer (voir §6) et doubler ce qui marche.

---

## 6. KPIs à suivre
- **SEO/AEO** : impressions Search Console ; nombre de pages indexées ;
  **citations dans ChatGPT/Perplexity** (tester des prompts cibles à la main).
- **Réseaux** : abonnés, portée, taux d'engagement par plateforme, clics vers le site.
- **Newsletter** : inscrits, taux d'ouverture, taux de clic, parrainages.
- **Site** : visiteurs uniques, sessions de chat IA, dons (`/soutenir`).
- **Nord** : nombre de personnes qui **étudient réellement** un siman / semaine.

---

## 7. Décisions à prendre (avant de coder la Phase 2)
1. **Budget mensuel** réseaux : 0 € (Postiz self-host / Buffer free) ou ~30–150 $/mo (cloud) ?
2. **Plateformes prioritaires** : LinkedIn + Instagram + Facebook + X ? (WhatsApp/Telegram en plus ?)
3. **Validation humaine** au début, ou **full-auto** direct ?
4. **Langue des posts** : FR d'abord, ou FR + HE + EN dès le départ ?

> Une fois ces 4 points tranchés, l'implémentation de la Phase 1 (blog) et de la
> Phase 2 (auto-publication) peut démarrer immédiatement — toute l'infra de base
> est déjà là.

---

### Sources (recherche web, 2026)
- [Zapier — Best social media management tools 2026](https://zapier.com/blog/best-social-media-management-tools/)
- [Zernio — Apps to post to all social media 2026](https://zernio.com/blog/apps-to-post-to-all-social-media)
- [WoopSocial — Ayrshare alternatives](https://woopsocial.com/blog/ayrshare-alternatives)
- [Postiz vs Ayrshare](https://postiz.com/compare/postiz/ayrshare)
- [Ayrshare — Social Media APIs](https://www.ayrshare.com/)
- [ALM Corp — AEO 2026 playbook](https://almcorp.com/blog/answer-engine-optimization-2026/)
- [Frase — Complete AEO guide 2026](https://www.frase.io/blog/what-is-answer-engine-optimization-the-complete-guide-to-getting-cited-by-ai)
- [n8n — Automate multi-platform social content with AI](https://n8n.io/workflows/3066-automate-multi-platform-social-media-content-creation-with-ai/)
- [DEV — Turn blog posts into social with n8n + AI](https://dev.to/flowyantradev/how-to-automatically-turn-blog-posts-into-social-media-content-with-n8n-and-openai-free-template-1hcl)
