# 🎯 SEO/AEO 2026 — Plan d'action pour faire un BOND en avant

> Suite de [`STRATEGIE-CROISSANCE.md`](./STRATEGIE-CROISSANCE.md) (rédigé en juin 2026).
> Recherche faite le 2026-06-10 avec le skill `deep-research` (8 angles, 18+ sources 2025-2026).
> Objectif : faire de daattorah.com le **#1 cité par les AI Overviews** et le **leader long-tail** sur la halakha francophone.

---

## 🎯 Verdict d'entrée

DAAT est **déjà dans le top 5 % mondial** pour la qualité technique d'un site éducatif religieux :
sitemap canonique trilingue, llms.txt 42 KB, robots.txt qui accueille les bots LLM, schémas JSON-LD,
hreflang + x-default, 42 articles blog AEO, 9072 liens d'ancrage intra-page, sources halakhiques
citées mot à mot contre Sefaria.

**Pour passer du top 5 % au top 0,1 %**, il faut désormais jouer un autre jeu : **autorité topique**,
**signaux d'expertise (E-E-A-T)**, **citabilité par les AI Overviews**, et **présence Knowledge Graph**.

---

## 📊 Les 6 chiffres 2026 à retenir

| Métrique | Valeur 2026 | Source |
|---|---|---|
| Citations AI Overview venant du **top 10** Google | **38 %** (vs 76 % en 2024) | Ahrefs, ALM Corp |
| CTR organique sur requêtes avec AI Overview | **−61 %** | ALM Corp |
| Clics gagnés si **cité DANS** l'AI Overview | **+35 % organic, +91 % paid** | ALM Corp |
| Citations venant des **30 premiers %** d'une page | **55 %** | Heroic Rankings |
| Sites qui **échouent** au seuil INP <200 ms | **43 %** | corewebvitals.io |
| Trust (T de E-E-A-T) = élément le **plus important** | Confirmé QRG 2025 | Google Quality Rater Guidelines |

**Ce que ça dit pour DAAT :** être dans le top 10 ne suffit plus ; l'AI Overview prend 62 % de
clics avant même que l'utilisateur scroll. La seule façon de gagner est d'**être cité dans
l'AI Overview lui-même** — ce qui se joue sur la qualité structurelle de la page, pas le rank.

---

## 🧭 Plan d'action priorisé — TOP 15

Trié par **ROI = Impact / Effort**. Quick wins en premier.

### 🟢 Quick wins (cette semaine, < 4 h)

#### **1. Page « bio Rav Yossef Haïm Samama » avec credentials complets** — *Impact 5/5, Effort 1/5*
Aujourd'hui, l'auteur est mentionné par `<meta name="author">` mais il n'y a pas de page
auteur dédiée. **C'est le levier E-E-A-T n°1.** À mettre sur le site :

```
/auteur/rav-yossef-haim-samama (FR, HE, EN)
```
Contenu minimal :
- Bio complète : parcours rabbinique, smikha, beit midrash de formation
- Liste des smikhot reçues + photos des documents
- Liens vers profils académiques externes (Yeshiva, livres, articles publiés)
- Schema `Person` complet avec `sameAs` vers Wikipedia/Wikidata/LinkedIn/Academia.edu
- Une `<a href>` vers cette page dans chaque siman (où apparaît déjà `meta author`)

#### **2. Entrée Wikidata pour Rav Yossef Haïm Samama** — *Impact 5/5, Effort 2/5*
Wikidata est **lue directement par le Knowledge Graph Google**. 30 minutes de création,
15-20 propriétés citées suffisent à activer un **knowledge panel potentiel**.
Propriétés à renseigner : `instance of: human`, `occupation: rabbi`, `religion: Judaism`,
`movement: Chabad-Lubavitch` (?), `language of work: French`, `notable work: daattorah.com`,
`official website`, `LinkedIn`, etc.

#### **3. Ajouter schema `Person` + `sameAs` dans le JSON-LD de CHAQUE page siman** — *Impact 4/5, Effort 1/5*
Aujourd'hui les pages siman ont `Article` + `BreadcrumbList`. Ajouter `author` sous forme
de `Person` complet avec `sameAs` vers Wikidata, LinkedIn, et la page bio :

```json
"author": {
  "@type": "Person",
  "name": "Rav Yossef Haïm Samama",
  "url": "https://daattorah.com/auteur/rav-yossef-haim-samama",
  "sameAs": [
    "https://www.wikidata.org/wiki/Qxxxxx",
    "https://www.linkedin.com/in/...",
    "https://www.academia.edu/..."
  ],
  "jobTitle": "Rabbin, auteur halakhique",
  "alumniOf": {"@type":"EducationalOrganization","name":"..."}
}
```

#### **4. Schema `LearningResource` + `Course` sur les hubs Daat Yomi et Hilkhot Shabbat** — *Impact 4/5, Effort 1/5*
Le Daat Yomi (programme d'étude) est exactement ce que `Course` modélise. Et chaque siman
est un `LearningResource`. Permet l'affichage en **rich result « Cours »** dans Google.

```json
{
  "@type": "Course",
  "name": "Daat Yomi — Hilkhot Shabbat",
  "description": "Programme d'étude quotidien...",
  "provider": {"@type":"Organization","name":"DAAT","url":"https://daattorah.com"},
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "online",
    "startDate": "2026-06-08",
    "endDate": "2027-03-04"
  },
  "teaches": ["Hilkhot Shabbat", "Choulhan Aroukh OH 242-365"]
}
```

#### **5. Réorganiser le H1 + 1er paragraphe de TOUS les blog posts en mode « réponse directe »** — *Impact 5/5, Effort 2/5*
**55 % des citations AI Overview viennent des 30 premiers % de la page.** Pour chaque
article du blog :
- **H1** = la question telle qu'un utilisateur la pose
- **1er paragraphe (≤ 60 mots)** = la réponse halakhique directe, complète, autonome
- Sources et nuances ensuite

Exemple **avant** : `<h1>La livraison de colis pendant Shabbat</h1>`
**Après** : `<h1>Peut-on se faire livrer un colis le Shabbat ?</h1>` + paragraphe TL;DR.

---

### 🟡 Court terme (ce mois, 1-2 jours de travail)

#### **6. Page « À propos / Notre méthode » avec signaux de confiance** — *Impact 4/5, Effort 2/5*
Trust = #1 critère E-E-A-T. La page doit afficher :
- Mission éditoriale, méthode (4 niveaux d'étude, sources citées mot à mot)
- Comité éditorial / rabbins relecteurs
- Politique de correction (ce qu'on a justement fait avec les hagahot manquantes !)
- Mentions de presse (à venir, voir #10)
- Coordonnées physiques (adresse Beit Midrash, téléphone, email)
- Schema `Organization` + `EducationalOrganization` + `foundingDate`

#### **7. Créer 20 articles blog ciblés long-tail FR à partir des concepts halakhiques existants** — *Impact 5/5, Effort 4/5*
Le site a 42 articles déjà. Liste de requêtes français à viser :
- "Peut-on [X] le Shabbat ?" (intent transactionnel + AEO)
- "Différence entre Mehaber et Rama"
- "Choulhan Aroukh HaRav qu'est-ce que c'est"
- "Comment étudier le Choulhan Aroukh en français"
- "Hilkhot Shabbat siman par siman"
- "Mouktsé qu'est-ce que c'est"
- Spécifiques par siman tendance : "voyage en bateau Shabbat halakha" (siman 248), etc.

Skill `daat-social` peut générer chacun à partir du siman correspondant. Cible : **+1 article/semaine pendant 6 mois → 26 articles**.

#### **8. Optimiser INP <200 ms sur les pages siman lourdes** — *Impact 4/5, Effort 3/5*
43 % des sites échouent INP en 2026. Mesure avec PageSpeed Insights sur :
- `/oh/301/daat-harav` (lourde : 63 séifim, JS chat, JS intra-links)
- `/oh/263/base` (14 séifim, 365 longs)
- Pages blog les plus consultées

Optimisations probables : defer du JS chat-widget jusqu'au scroll, lazy-init du JS intra-links,
réduire le DOM des `<details>` collapsés (server-side render minimal).

#### **9. Schema `QAPage` + `Quotation` sur tous les blog posts** — *Impact 3/5, Effort 2/5*
Les blog posts sont déjà `BlogPosting` + `FAQPage`. Ajouter :
- `mainEntity: QAPage` autour de la question-réponse principale
- `Quotation` pour chaque citation du Choulhan Aroukh, avec `spokenByCharacter` pour
  l'auteur (Mehaber, Rama, HaRav…)

Permet l'affichage **enrichi en AI Overview** ET en rich snippet Google.

#### **10. Soumission active aux médias juifs francophones (digital PR)** — *Impact 5/5, Effort 4/5*
DAAT n'a pas encore de backlinks d'autorité dans son domaine. Cible :
- **Akadem** (radio CNRS) : proposer une chronique halakha hebdo basée sur le Daat Yomi
- **Actualité Juive** : article d'invitation sur le lancement
- **Times of Israel French** : éditorial sur la démocratisation de l'étude halakhique
- **Kountrass / Hamodia / Yom Shabbat** : présentation du projet
- **Podcasts juifs FR** : RCJ, JBox, RadioJ — pitch d'interview

Outil : **Source of Sources (SoS)** (gratuit, ex-HARO) pour répondre aux journalistes qui
cherchent un expert halakha. **Featured** (turnaround 18 jours) pour citations académiques.

---

### 🔴 Long terme (3-6 mois)

#### **11. Page Wikipédia pour Rav Yossef Haïm Samama** — *Impact 5/5, Effort 5/5*
Le sommet de l'autorité. **Wikipédia est lu par Google ET par tous les LLM**. Conditions :
- Notabilité (référencé par ≥ 2 sources de presse indépendantes — d'où #10)
- Bibliographie publiée
- Mentionner sans s'auto-promouvoir

**Stratégie réaliste** : créer Wikidata d'abord (#2) ; après ~6 mois de presse couverture
via #10, demander à un wikipédien aguerri de monter la page (Wikipedia francophone refuse
les auto-créations).

#### **12. Knowledge graph / Wikidata pour les CONCEPTS halakhiques traités** — *Impact 4/5, Effort 4/5*
Pas que le rabbin : créer/enrichir les entités Wikidata pour :
- Choulhan Aroukh HaRav (Admour HaZaken) — entité Q123…
- Chaque siman majeur (ex. Mouktza Q...)
- Concepts (קנה שביתה, פוסק עמו שישבות, etc.)

Avec `described at URL: daattorah.com/oh/...` → Google associe DAAT à ces entités.

#### **13. Programme de podcasts / vidéos YouTube** — *Impact 5/5, Effort 5/5*
**Les mentions YouTube sont le facteur #1 de corrélation pour la visibilité en AI Overview**
(Wellows, 2026). Multi-modal : +156 % de taux de citation.

Format minimum viable :
- 1 vidéo YouTube/semaine, 5-10 min : « La halakha de la semaine »
- Voix off + texte hébreu à l'écran + traductions
- Description bourrée de mots-clés long-tail
- Lien vers la page DAAT correspondante

#### **14. Pousser llms.txt vers la version « v2 » : sitemap markdown** — *Impact 3/5, Effort 3/5*
Au-delà du llms.txt actuel, certaines pages mériteraient une **version `.md`** propre
(ex. `/oh/248/base.md`), publiée alongside le HTML. C'est ce que Anthropic et Stripe
font sur leur doc et c'est de plus en plus la pratique 2026.

Implémentation : générer un `.md` par siman lors du build, lister dans `/sitemap-llm.xml`,
référencer dans `llms.txt`.

#### **15. Partenariats croisés avec les écoles & yeshivot francophones** — *Impact 4/5, Effort 4/5*
DAAT n'est pas un concurrent des écoles mais leur outil. Démarcher :
- Yeshiva Heikhal Menahem (Paris), Yeshiva Or Yossef, etc.
- Écoles juives FR : proposer DAAT comme outil de révision + accord backlink réciproque
- Universités juives (Aix, Lille…) : citation académique

Demander mention dans leur « ressources » + backlink officiel.

---

## 📈 Estimation d'impact cumulé

Si tu fais les **5 quick wins (1-5)** dans la semaine :
→ **+30-50 %** de chances d'être cité dans les AI Overviews sur les requêtes que tu vises déjà
→ Knowledge panel potentiel sous 4-8 semaines après #2
→ Aucun changement de design, juste structure

Si tu ajoutes les **5 court-terme (6-10)** ce mois :
→ Cible le **top 3 français** sur les requêtes long-tail halakha sous 6 mois
→ Indexation YouTube + presse = signaux d'autorité forts pour Google

Si tu fais les **5 long-terme (11-15)** sur 6 mois :
→ Cible le **#1 francophone sur la halakha en ligne** (Torah-Box reste leader sur
le quotidien généraliste, mais DAAT sera #1 sur la halakha de précision)
→ Mentions stables dans ChatGPT/Claude/Perplexity sur les concepts traités

---

## 🎓 Sur l'ambition « être trouvé sur « Torah » »

Honnête : **non, daattorah.com ne sera jamais #1 sur le mot « Torah »** seul (concurrence
massive avec Wikipedia, Sefaria, Chabad qui ont 15+ ans d'autorité). Mais ce n'est pas
le bon objectif. Le bon objectif :

✅ **#1 sur « halakha en français »**, « Choulhan Aroukh français », « Hilkhot Shabbat français »
✅ **Cité par défaut dans les AI Overviews** sur les questions halakhiques pratiques en FR
✅ **Knowledge panel actif** pour « Rav Yossef Haïm Samama » et « daattorah.com »
✅ **Source citée** par ChatGPT/Claude/Perplexity quand on leur demande une halakha pratique en FR

Ces 4 objectifs sont atteignables avec le plan ci-dessus en **6-12 mois**. C'est ça, le bond
en avant.

---

## 📚 Sources (2025-2026)

### AI Overviews / AEO
- [Google AI Overviews Ranking Factors 2026 — Wellows](https://wellows.com/blog/google-ai-overviews-ranking-factors/)
- [38% of AI Overview Citations from Top 10 — Ahrefs](https://ahrefs.com/blog/ai-overview-citations-top-10/)
- [AI Overview Citations Drop from 76% to 38% — ALM Corp](https://almcorp.com/blog/google-ai-overview-citations-drop-top-ranking-pages-2026/)
- [Where Google AI Overviews Cite From: 100-Page Study — CXL](https://cxl.com/blog/google-ai-overview-citation-sources/)
- [Google AI Overview Statistics 2026 — Heroic Rankings](https://heroicrankings.com/seo/managed/google-ai-overview-statistics-2026/)

### schema.org & Structured Data
- [Schema.org Course](https://schema.org/Course)
- [Schema.org LearningResource](https://schema.org/LearningResource)
- [Schema.org Quotation](https://schema.org/Quotation)

### Topical Authority
- [How to Rank a New Domain — Topical Authority 2026](https://blog.mean.ceo/how-to-rank-a-new-domain-with-topical-authority/)
- [Topical Authority SEO — SEOspace](https://www.seospace.co/blog/topical-authority-seo)
- [Topical Authority Small Sites — Memorable.design](https://memorable.design/topical-authority-seo-small-site/)

### E-E-A-T & YMYL
- [E-E-A-T Guide 2026 — SEO Kreativ](https://www.seo-kreativ.de/en/blog/e-e-a-t-guide-for-more-trust-and-top-rankings/)
- [Google Quality Rater Guidelines 2026 — HM Digital](https://hmdigitalsolution.com/google-quality-rater-guidelines/)
- [Google E-E-A-T Guide 2026 — Linkbuilder](https://linkbuilder.com/blog/google-eeat-guide)

### Knowledge Graph & Wikidata
- [Guide to Using Wikidata for Google Knowledge Panel](https://www.googleknowledgepanel.net/wikidata-for-google-knowledge-panel-creation/)
- [Wikidata for SEO 2026 — Reputation X](https://www.reputationx.com/blog/wikidata)
- [How Google's Knowledge Graph works — Google Support](https://support.google.com/knowledgepanel/answer/9787176)

### llms.txt & LLM Indexing
- [State of llms.txt 2026 — Presenc AI](https://presenc.ai/research/state-of-llms-txt-2026)
- [llms.txt Explained 2026 — C# Corner](https://www.c-sharpcorner.com/article/llms-txt-explained-the-ultimate-2026-guide-to-ai-search-geo-ai-crawlers-and/)
- [Making Sites Visible to LLMs — Evil Martians](https://evilmartians.com/chronicles/how-to-make-your-website-visible-to-llms)
- [LLMs.txt proposed standard — Search Engine Land](https://searchengineland.com/llms-txt-proposed-standard-453676)

### Backlinks 2026
- [Best HARO Alternatives 2026 — PressWhizz](https://presswhizz.com/blog/best-haro-alternatives/)
- [Best HARO Alternatives 2026 — Backlinko](https://backlinko.com/haro-alternatives)
- [Link Building 2026 — Outpace SEO](https://outpaceseo.com/article/link-building/)

### Core Web Vitals 2026
- [Core Web Vitals 2026 — corewebvitals.io](https://www.corewebvitals.io/core-web-vitals)
- [Core Web Vitals 2026 Technical SEO — ALM Corp](https://almcorp.com/blog/core-web-vitals-2026-technical-seo-guide/)
- [Core Web Vitals Guide 2026 — w3era](https://www.w3era.com/blog/seo/core-web-vitals-guide/)
