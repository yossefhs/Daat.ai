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
| **« Omnisocial »** | 🟢 Identifié | L'outil dont on avait parlé = **OmniSocials** (omnisocials.com) : 10 $/mo, 10 réseaux, **connexion MCP native à Claude**. C'est le pilier de la solution (§4). |
| **Skill `daat-social`** | 🟢 Créé | `.claude/skills/daat-social/` : le moteur réutilisable qui transforme un siman → kit multi-plateforme dans la voix DAAT, puis publie via OmniSocials. C'est le « skill » qu'on voulait. |

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
| **OmniSocials** | SaaS **+ MCP natif Claude** | **10 $/mo** (essai 14 j) | 10 (IG, FB, LinkedIn, X, YouTube, TikTok, Pinterest, Bluesky, Threads, Mastodon) | ⭐⭐ **LE choix** — Claude rédige, **programme et publie** en langage naturel ; MCP+skill open-source MIT ; pas cher |
| **Postiz** | Open-source, auto-hébergeable, API | Gratuit (self-host) / 29 $/mo | 30+ | Alternative si on veut du self-host |
| **Buffer** | SaaS simple | Tier gratuit + API | IG, FB, LinkedIn, X… | Démarrage gratuit basique |
| **Ayrshare** | API-first | 149 $/mo | 13 | Cher pour une asso |
| **n8n** | Orchestrateur open-source | Gratuit (self-host) | Via API | Optionnel, si canvas visuel souhaité |

**→ Choix retenu : OmniSocials.** Il fait exactement ce qu'on cherchait : **connecter
Claude pour faire les envois**. Setup dans `.claude/skills/daat-social/references/omnisocials-setup.md`.

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

## 4. ⭐ La solution recommandée — Skill `daat-social` + OmniSocials

> **Principe : DAAT produit déjà LE contenu le plus dur (la Torah de qualité). On ne
> crée rien de neuf — on REDISTRIBUE automatiquement le corpus existant partout.**
> C'est ça, l'omniprésence — et **OmniSocials** en est le bras armé.

La meilleure option n'est **pas** de coder un cron Vercel + choisir un outil d'API :
c'est plus simple et plus puissant. **Claude devient lui-même le community manager** via
le skill `daat-social` (créé dans ce dépôt) et publie via le **MCP OmniSocials**.

### 4.1 Architecture (réutilise l'existant, zéro réécriture du site)

```
┌─────────────────────────────────────────────────────────────────────┐
│  SOURCE  : corpus existant (data/simanim/*.json + sources/shabbat/)   │
│            + calendrier juif (paracha / fête de la semaine)           │
└───────────────────────────────┬─────────────────────────────────────┘
                                 │  Skill .claude/skills/daat-social
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GÉNÉRATION  : Claude (reformate, n'invente pas de psak)              │
│   1 siman  →  • post LinkedIn   • thread X   • caption+carrousel IG   │
│              • post Facebook    • rappel communauté WhatsApp          │
│              • (option) article BLOG long SEO/AEO + email newsletter  │
│  VISUEL : node scripts/generate-og-image.js --siman {N}              │
└───────────────────────────────┬─────────────────────────────────────┘
                                 ▼  VALIDATION HUMAINE (au début)
                                 │  tu relis → « OK »
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PUBLICATION : OmniSocials (MCP)  → programme LinkedIn·IG·FB·X… aux   │
│                                     heures optimales, étalé/semaine   │
│  NEWSLETTER  : Resend (déjà en place)  →  email hebdo                 │
│  BLOG        : section /blog/ à créer (SEO/AEO) — le multiplicateur   │
└─────────────────────────────────────────────────────────────────────┘
```

**Utilisation concrète (rituel hebdo ~15 min, validé par toi) :**
> « Publie le siman 247 » → Claude lit la source, génère le kit FR multi-plateforme +
> le visuel, te le présente, tu dis « OK », Claude **programme** la semaine sur
> OmniSocials (LinkedIn mar, IG mer, X jeu, FB ven). Puis ça tourne tout seul.

**Pourquoi c'est la meilleure option pour DAAT :**
1. **OmniSocials = exactement « connecter Claude pour faire les envois »** — 10 $/mo,
   MCP natif, 10 réseaux, OAuth. Rien à coder côté publication.
2. **Le skill est réutilisable et versionné** — la voix, la charte, les formats par
   plateforme et les **garde-fous halakhiques** sont encapsulés une fois pour toutes.
3. **Le contenu existe déjà** — Claude **reformate** un siman validé, ne hallucine pas
   de halakha (+ disclaimer « pour la pratique, demande à ton Rav » intégré au skill).
4. **Une variante par plateforme** (best practice 2026), pas du copier-coller.
5. **Validation humaine au début**, puis bascule full-auto possible une fois la qualité
   éprouvée — sans changer d'outil.
6. **Le même kit nourrit blog + newsletter** : un seul effort, plusieurs canaux.

### 4.2 Le composant central : `/blog/` (le chaînon manquant)
Un blog est le **multiplicateur** : c'est la seule brique qui sert SEO + AEO +
réseaux + newsletter en même temps. Idées de rubriques, toutes tirées du corpus :
- **« La halakha de la semaine »** (liée à la paracha / fête à venir).
- **« 3 minutes pour comprendre… »** (vulgarisation d'un siman, intent définitionnel).
- **« Mehaber vs Rama vs Admour HaZaken sur… »** (intent comparatif → adoré par l'IA).
- **« Cas pratique »** (intent process : checklist + Q/R → schema FAQ).
Chaque article = réponse directe en intro (AEO) + sources citées (déjà le standard DAAT).

### 4.3 Outil de publication — décision : **OmniSocials**
- **10 $/mo**, essai 14 j sans CB. 10 réseaux. OAuth (rien à copier-coller).
- **MCP natif Claude** : `claude mcp add omnisocials …` ou remote `mcp.omnisocials.com`
  (Settings → Integrations → Claude). Détails : `references/omnisocials-setup.md`.
- Claude **rédige, programme et publie** en langage naturel + analytics + audits.
- Alternatives gardées en réserve : Postiz (self-host gratuit), Buffer (free).

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

### Phase 2 — Moteur d'auto-publication réseaux ✅ *(outillage prêt)*
- [x] Skill `daat-social` créé (`.claude/skills/daat-social/`) : génère le kit
      multi-plateforme dans la voix DAAT, avec garde-fous halakhiques.
- [ ] Créer le compte **OmniSocials** (essai 14 j) + connecter LinkedIn/IG/FB/X.
- [ ] Connecter OmniSocials à Claude (MCP) — voir `omnisocials-setup.md`.
- [ ] Rituel hebdo : « Publie le siman {N} » → kit FR → validation → programmation.
- [ ] Passer en **full-auto** une fois la qualité validée sur ~4 semaines.

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

## 7. Décisions (tranchées le 2026-06-03)
1. **Outil / budget** : ✅ **OmniSocials, 10 $/mo** (connexion MCP à Claude).
2. **Validation** : ✅ **humaine au début**, full-auto une fois la qualité éprouvée.
3. **Langue** : ✅ **français d'abord**, HE/EN ensuite.
4. **Plateformes prioritaires** : LinkedIn (page déjà créée) → Instagram → Facebook → X.

> Reste à faire côté toi : créer le compte OmniSocials et connecter les réseaux + Claude.
> Côté contenu, le skill `daat-social` est prêt à générer dès maintenant. La Phase 1
> (blog) reste le plus gros levier SEO/AEO et peut démarrer en parallèle.

---

### Sources (recherche web, 2026)
- [OmniSocials — Connect Claude to your social media](https://omnisocials.com/integrations/claude)
- [OmniSocials — pricing & features](https://omnisocials.com/)
- [Zapier — Best social media management tools 2026](https://zapier.com/blog/best-social-media-management-tools/)
- [Zernio — Apps to post to all social media 2026](https://zernio.com/blog/apps-to-post-to-all-social-media)
- [WoopSocial — Ayrshare alternatives](https://woopsocial.com/blog/ayrshare-alternatives)
- [Postiz vs Ayrshare](https://postiz.com/compare/postiz/ayrshare)
- [Ayrshare — Social Media APIs](https://www.ayrshare.com/)
- [ALM Corp — AEO 2026 playbook](https://almcorp.com/blog/answer-engine-optimization-2026/)
- [Frase — Complete AEO guide 2026](https://www.frase.io/blog/what-is-answer-engine-optimization-the-complete-guide-to-getting-cited-by-ai)
- [n8n — Automate multi-platform social content with AI](https://n8n.io/workflows/3066-automate-multi-platform-social-media-content-creation-with-ai/)
- [DEV — Turn blog posts into social with n8n + AI](https://dev.to/flowyantradev/how-to-automatically-turn-blog-posts-into-social-media-content-with-n8n-and-openai-free-template-1hcl)
