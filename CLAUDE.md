# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

DAAT (דעת / daattorah.com) is a trilingual halakhic study platform: hand-authored static HTML pages for the Choulhan Aroukh (Orah Haïm, Hilkhot Shabbat) plus Vercel serverless functions powering an AI study assistant. No front-end framework — pages are standalone HTML with inline `<style>`; the API is ESM Node functions under `api/`.

## ⚠️ Clause de vérification obligatoire avant publication (RÈGLE ABSOLUE)

**Avant toute mise en ligne en production (`main`), et à la fin du travail de chaque lot / chaque semaine, il faut RE-VÉRIFIER la totalité du contenu produit et le confronter aux sources originales pour être certain qu'il n'y a aucune erreur.** Cette vérification n'est pas optionnelle : c'est la dernière porte avant publication.

Elle comporte, au minimum :
1. **Contrôle structurel** de tous les fichiers produits : 15 fichiers/siman ; parité trilingue (FR/HE/EN) ; 0 jeton interdit ; `canonical == og:url` ; geresh/gershayim corrects (jamais d'apostrophe/guillemet ASCII à l'intérieur d'un mot hébreu) ; chaque fichier finit par `</html>` ; nombre de `<details class="seif-details">` = nombre réel de seifim du Choul'han Aroukh HaRav.
2. **Confrontation aux sources (Sefaria)** : re-télécharger le Mehaber (`Shulchan_Arukh,_Orach_Chayim.N`) et le Choul'han Aroukh HaRav (`Shulchan_Arukh_HaRav,_Orach_Chayim.N`) et **comparer le texte hébreu source du niveau-4** (`.sa-he` dans les blocs `seif-details`) au texte réel — verbatim, consonnes identiques — pour garantir qu'aucun seif n'a été inventé, tronqué, ni altéré, et que le nombre de seifim est exact. En cas de doute halakhique sur un contenu (traduction, explication, psak), **retourner voir la source** avant de publier.
3. **Ne publier qu'une fois cette vérification entièrement verte**, et n'annoncer « c'est en ligne » qu'après confirmation. Toute divergence détectée doit être corrigée (et re-vérifiée) avant le déploiement.

Le script `scripts/verify-oh-source.py N [N...]` automatise la confrontation aux sources pour le compartiment `oh-quotidien` ; le lancer sur chaque lot avant de proposer la mise en ligne.

### ⚠️ Lacune du Choul'han Aroukh HaRav dans `oh-quotidien` (niveau-4 = page-pont 🌉)

Le Choul'han Aroukh HaRav (Admour HaZaken) **ne couvre pas tout Orah Haïm** : il y a des blocs entiers qu'il n'a pas rédigés. Dans le compartiment `oh-quotidien`, la première lacune connue est **les simanim 132 à 154** (il s'arrête au 131 et reprend au 155) ; d'autres trous suivent (ex. 157, 170-179, 210, 220, 240, 420…). **AVANT de produire un niveau-4, toujours vérifier le nombre de seifim SA HaRav** : `curl -s "https://www.sefaria.org/api/texts/Shulchan_Arukh_HaRav,_Orach_Chayim.N?context=0&pad=0"` → si `he` est vide (0 seif), l'Admour HaZaken **n'a pas écrit ce siman**.

Dans ce cas, **NE JAMAIS fabriquer de texte SA HaRav** (règle anti-fabrication ABSOLUE). Le niveau-4 devient une **page-passerelle sobre** (🌉), générée par `scripts/gen-bridge.py` (ou `/tmp/gen-bridge.py`) : elle explique honnêtement l'absence, renvoie aux niveaux 1-3 (Mehaber/Rama) et au **Siddour de l'Admour HaZaken** (où sa pratique sur la tefila est consignée), **sans aucune citation reconstruite ni le mot « n'existe pas sur Sefaria »**. Les niveaux 1-3 + index restent des pages normales (contenu Mehaber/Rama). `verify-oh-source.py` passe alors avec 0 seif attendu = 0 bloc `seif-details`. Décision utilisateur (2026) : **page-pont sobre**, pas de reconstruction façon 304/322.

## ⚠️ Le Choul'han Aroukh est le repère — ordre compris (RÈGLE ABSOLUE)

**Toute référence doit être exactement celle du Choul'han Aroukh** : le numéro du séif,
la découpe entre séifim, l'ordre des propositions à l'intérieur d'un séif, et l'ordre dans
lequel la page les présente. Une page ne réarrange pas la source pour les besoins de son
exposé ; si un enchaînement pédagogique semble l'exiger, c'est l'exposé qui plie.

Décision de l'utilisateur, août 2026, après le siman 243 : *« Il faut toujours que ce soit
exactement comme dans le Choul'han Aroukh. Le Choul'han Aroukh est le repère pour toute
référence. »*

Ce que le 243 a montré, et qu'aucun des garde-fous de contenu ne pouvait voir — les
citations y étaient réelles, la langue juste, la structure conforme :

- le champ, le four, le moulin et la glose du Rama, tous dans le **séif א**, étaient publiés
  sous « סעיף ב », et le vrai séif ב n'était cité nulle part ;
- une clause déplacée d'un raisonnement à l'autre donnait comme raison de **permettre** le
  champ ce que le Choul'han Aroukh donne comme raison d'**interdire** le bain ;
- et la page présentait la fin du séif א **après** le séif ב.

`scripts/verifier-alignement.py` est le contrôle qui répond de cette règle. Il lit
l'étiquette de séif dans le titre **et dans le paragraphe** (`<p><strong>סעיף א.</strong> …`,
`<strong>א.</strong>` entre `<br>`), sur `niveau-1-base.html` en entier et sur `index.html`,
`niveau-2-lamdan.html`, `niveau-3-synthese.html` pour les seules étiquettes inline. Il pose
deux questions : *le bloc annoncé séif N est-il le séif N ?* et *les blocs se suivent-ils
dans l'ordre de la source ?* Le lancer avant de publier une page de séif.

## ⚠️ Avant tout push sur `main` : fusionner puis vérifier (RÈGLE ABSOLUE)

Plusieurs sessions travaillent sur ce dépôt depuis des copies distinctes. **Par deux fois**, une
session a poussé sur `main` un commit construit sur une copie périmée : les commits `7ed67012`
(« journal S3 ») et `a1311630` (« journal S5 ») ont chacun **supprimé silencieusement des dizaines
de simanim déjà publiés** et annulé des correctifs appliqués à plus de 1 300 fichiers, sans que le
message de commit n'en dise un mot. Le site a perdu douze simanim en ligne, deux fois.

Donc, **avant tout push sur `main`, sans exception** :

```bash
git fetch origin main && git merge origin/main   # jamais publier sur une base périmée
python3 scripts/verifier-integrite.py            # doit sortir 0
```

`scripts/verifier-integrite.py` compare l'état local à `origin/main` et **refuse** un état qui
supprimerait un siman publié, désynchroniserait le catalogue du disque, ou annulerait l'un des deux
correctifs mécaniques (`scripts/fix-jsonld-lang.py`, `scripts/heb-nums.py` — tous deux idempotents et
rejouables). Si une suppression est réellement voulue, `--autoriser-suppressions` et **le dire dans le
message de commit**. Le workflow `.github/workflows/anti-regression.yml` fait le même contrôle après
coup sur `main` et échoue en rouge si des simanim disparaissent.

Ce contrôle est structurel et ne remplace pas la clause de vérification de contenu ci-dessous.

## Commands

```bash
# Full build (run by Vercel as vercel-build, and locally before commit if you touched content or chat-widget.js)
npm run build
#   → generate-simanim-index.js : régénère data/simanim-disponibles.json (titres) — FUSION,
#                                 ne supprime jamais une entrée, couvre les 4 sections
#   → extract-corpus.js         : régénère data/corpus-shabbat.json (le corpus BM25 du chat)
#   → build:js                  : terser sur assets/js/chat-widget.js → chat-widget.min.js

# Content state guard — MUST stay green (124/124 conformes). Exits non-zero on boilerplate / missing files / desynced TOC.
python3 scripts/audit-simanim.py            # full report
python3 scripts/audit-simanim.py --quiet    # summary only (what the SessionStart hook prints)
python3 scripts/audit-simanim.py --write-progress   # regenerates PROGRESS.md (never hand-edit PROGRESS.md)

# Content-truth guard — checks every Hebrew "verbatim" quote against its real source on Sefaria.
# audit-simanim.py is structural only and passes on pages full of invented citations; this is the
# complementary gate. Exits non-zero while any quote is ABSENT from the source it cites.
python3 scripts/verifier-citations.py                       # whole site, FR (Hebrew quotes are shared across the 3 languages)
python3 scripts/verifier-citations.py --only-absent          # just the list to fix
python3 scripts/verifier-citations.py --path sources/shabbat/siman-297

# Garde-fou de langue — chaque page est-elle écrite dans la langue qu'elle annonce ?
# Trois échelles : la page entière, le bloc isolé, et l'entête (title/og/twitter/JSON-LD),
# cette dernière étant invisible à la lecture mais lue par Google et les aperçus de partage.
# Complémentaire des deux autres : une page peut être 174/174 conforme, sans citation
# fausse, et avoir un corps entièrement français sous un lang="en".
python3 scripts/verifier-langues.py            # tout le site
python3 scripts/verifier-langues.py --lignes   # + la liste des blocs à traduire

# Generate a siman's index page from data/simanim/siman-XXX.json (does NOT generate study levels — those are written by hand)
node scripts/generate-siman.js --siman XXX [--force] [--no-sitemap]
```

There is no test suite and no linter. Three complementary gates stand in for one: `scripts/audit-simanim.py` checks **structure** (boilerplate, missing files, desynced TOC), `scripts/verifier-citations.py` checks **content** (does each Hebrew quote actually exist at the reference it claims?), and `scripts/verifier-langues.py` checks **language** (is the body of `X-en.html` actually English — and is its `<title>`/`og:title`/`description`?). None subsumes the others — a page can be 174/174 conforme, carry no false citation, and still be a French page served under `lang="en"`, which is what four pages of simanim 304 and 322 were; 212 further pages had a correct body under a French head, which only the third scale of `verifier-langues.py` can see. Run all three before declaring content work done; the SessionStart hook (`.claude/hooks/session-start.sh`, remote-only) runs `npm install` then this audit at the start of every web session.

A fourth gate watches what those three structurally cannot see. The four halakhic errors found in the rabbinic audit of August 2026 (simanim 318, 253, 308, 320) passed all three without a single alert, because **no citation was false** — the Hebrew was verbatim, the structure was sound, the language was right; it was the French reasoning built on top that was wrong. Proof: `verifier-citations.py --path sources/shabbat/siman-320` returned 0 anomalies on a page whose séif 320:6 (ש״כ:ו — `מותר לסחוט לימוני״ש`, the decisive permission on lemon) was never mentioned at all. `scripts/veilleur.py` looks for the shared signature of those four: **A** a séif of the Choulhan Aroukh that no page of the siman ever mentions; **B** an absolute formulation (« une seule crainte », « n'est pas … en soi », a crossed Mehaber/Rama attribution), weighted by observed yield; **C** a concept present in level 1 or level 4 but absent from the level-3 synthesis — the site then holds its own correction without knowing it.

The recurring pattern is worth stating plainly, because it dictates where to look: in every case **levels 1 and 4 were correct** (they translate the primary text) and the error was born in the **pedagogical synthesis**, from where it spread to the derived `/questions/` pages and to the index metadata. The veilleur produces **candidates, never verdicts**, and never writes into a page: `--signalements` files them in the reader-report registry as `NEEDS_RABBINIC_VALIDATION`, deduplicated server-side, so the Rav triages machine findings and reader reports in one place. `.github/workflows/veilleur.yml` runs it every Sunday (needs the `ADMIN_PASSWORD` repo secret to file; without it, it reports only).

## Ce que le corpus indexe — à lire avant d'écrire du contenu

Deux chantiers avancent en parallèle sur ce dépôt : l'un **écrit le contenu**
(encadrés « Ce que dit ce séif », vérification des citations, audit), l'autre
**maintient la chaîne d'indexation** (extraction, recherche, API du chat). Ce qui
suit est le contrat entre les deux : où écrire pour que le chat vous voie.

**Un encadré n'est indexé que s'il est d'un type connu ET dans une section lue.**
- Types indexés : `definition`, `remember`, `key-point`, plus les tableaux
  « Cas pratiques modernes » (une ligne = un chunk).
- Les encadrés du niveau Lamdan (`hakira-box`, `rishon-card`, `pilpul-box`,
  `machloket-box`, `nafka-mina-box`, `yesod-box`, `teruts-box`, `kashya-box`)
  ne sont **volontairement pas** indexés à part : mesuré sur un banc de 47
  questions de niveau lamdan, les indexer n'apporte **aucun gain** et coûte
  2 à 4 points sur les questions pratiques — leur texte est déjà présent, capté
  par les chunks narratifs de la même page. Les indexer le fragmenterait en deux
  chunks concurrents.
- Les sections « Le texte du Choul'han Aroukh », « Mishnah Berurah — premières
  entrées », « Plan de l'étude » et « Questions de compréhension » ne sont pas
  indexées **en tant que texte** — c'est du source recopié. Mais les encadrés
  RÉDIGÉS qu'on y place le sont : c'est là que vivent les « Ce que dit ce séif ».
  (Ils ne l'étaient pas avant août 2026 : 158 encadrés des lots 7 à 9 étaient
  écrits, publiés, et invisibles au chat.)

**Le build vous avertit — lisez sa sortie.** `npm run build` signale désormais :
un siman indexé sans titre, un fichier de niveau qui ne produit aucun chunk, un
fichier dont l'extraction capte moins de la moitié du texte, et un répertoire de
`sources/` non déclaré dans `SECTIONS` (dont le contenu n'entre dans rien).

**`data/corpus-shabbat.json` n'est plus versionné** — c'est une sortie de build de
34 Mio que GitHub refuserait au-delà de 100 Mio. Il est régénéré par
`vercel-build` et déclaré dans `vercel.json` (`includeFiles`). Après un clone
frais : `npm run build`. Cela supprime aussi le conflit récurrent entre branches
sur ce fichier.

**Le périmètre du corpus n'est plus écrit en dur** dans le prompt système : il est
calculé depuis le corpus (`corpusPerimeter()`). Inutile de le mettre à jour à la
main en ajoutant des simanim.

## Content model — the core of the repo

`sources/shabbat/siman-242/` … `siman-365/` = **124 simanim** of Hilkhot Shabbat. Each siman directory holds an `index.html` plus up to **4 study levels**, and **every page exists in 3 languages**:

| Level | File stem | Audience |
|-------|-----------|----------|
| 1 — Base | `niveau-1-base` | Hebrew text + fluent French translation + explanation |
| 2 — Lamdan | `niveau-2-lamdan` | In-depth pilpoul (Rishonim/Acharonim, hakira, machloket) — body is largely Hebrew |
| 3 — Synthèse | `niveau-3-synthese` | Structured recap for revision |
| 4 — Daat HaRav | `niveau-4-daat-harav` | Shitah of the Admour HaZaken (Choulhan Aroukh HaRav + Kountress Aharon) |

Language convention (applies site-wide, not just simanim): **`X.html` = French (default, `lang="fr"`)**, **`X-he.html` = Hebrew (`dir`/RTL)**, **`X-en.html` = English**. When you change content in one language you must keep the other two in sync — this is the single most common source of inconsistency. Many `scripts/*.py` exist to propagate edits across the trilingual set (translate, add buttons, fix canonicals, audit Rama gloses); prefer adapting one of those to mass-edits by hand.

Levels 1–3 exist for all 124 simanim; Level 4 exists for **122** of them. **Simanim 304 and 322 have no Level 4** — the Admour HaZaken did not write them in the Choulhan Aroukh HaRav, so they carry a "bridge page" (🌉 in `PROGRESS.md`) instead. Treat "124 simanim" (corpus / Mehaber) and "122 simanim" (Level 4 / Daat HaRav) as distinct counts; do not collapse them.

Study-level pages are **artisanal**: `generate-siman.js` only builds the repetitive `index.html` (SEO head, JSON-LD, breadcrumb, hero, FAQ). Do not try to industrialize the level pages — generic generated pilpoul has no value, and the audit flags boilerplate as an error.

`PROGRESS.md` is the generated manifest of per-siman/per-level state (✅ written · 🔴 boilerplate · ❌ absent · 🌉 bridge). Other top-level HTML (homepage `index.html`, `chat.html`, `soutenir.html`, `about/faq/communaute`, `blog/`) follows the same trilingual triple.

## URL scheme (vercel.json)

Public URLs are short and canonical; the physical paths are rewritten:
- `/oh/` → catalogue · `/oh/:n` → siman index · `/oh/:n/base|lamdan|synthese|daat-harav` → the 4 levels
- `/oh/:n/he` · `/oh/:n/en` → language variants
- Old `/sources/shabbat/...` paths **301-redirect** to `/oh/...`, so always link via `/oh/`.

When adding pages/levels, add matching `rewrites` in `vercel.json`. The repo deploys as a static site (`outputDirectory: "."`) on Vercel; `main` → daattorah.com (auto-deploy on merge). Security headers and `/api/*` CORS are also set here; `crons` triggers `/api/newsletter` daily.

## API architecture (`api/`, ESM serverless on Vercel, Node 22)

Shared modules are prefixed `_` (e.g. `_kv.js`, `_auth.js`, `_corpus.js`, `_system-prompt.js`, `_sefaria.js`, `_deepseek.js`). State lives in **Upstash Redis** (`_kv.js`) — there is no SQL database. Everything (rate limits, usage/cost tracking, plans, dedications, meta-response cache) is KV keys.

**`api/chat.js`** is the heart and the most complex file — the AI study assistant ("Daat"):
- Agentic loop with **tool use** (Sefaria API, the DAAT corpus, mareh mekomot), **SSE streaming**, and **1h prompt caching** on the long system prompt.
- **Cost-optimized model routing** (`pickModel`): meta/greeting questions → DeepSeek or Haiku (or a KV-cached canned answer, $0); halakhic-depth questions → Opus; otherwise Sonnet. New users get a lifetime "Aperçu Premium" of 3 Opus answers (with per-IP and global daily anti-abuse caps).
- **Corpus-first**: a strong BM25 match in the Rav's own corpus (`data/corpus-shabbat.json`, built by `extract-corpus.js`) is reformulated by Haiku instead of calling Opus/Sonnet. Several behaviors are env-gated (`CORPUS_FIRST_ENABLED`, `CORPUS_MIN_SCORE`, `CORPUS_QUOTA_FREE`).
- Time-budget aware: forces a final synthesis (`tool_choice: none`) past ~50s and hard-aborts at 80s, because Vercel kills the lambda ~90s. Usage/cost **must be written to KV before `res.end()`** (no fire-and-forget in serverless Node).
- Note model IDs are pinned in-file (`claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5`) — update here when bumping models.

**Auth** (`_auth.js`, `auth.js`): passwordless **email OTP** (6-digit code via Resend) → **JWT** session in the `daat_session` cookie. Cookies are `SameSite=None; Secure` on purpose: the chat API is served from `daatai.vercel.app` but consumed from `daattorah.com` (cross-site), so `Lax` would drop them. Pages set `window.DAAT_CHAT_API_URL` to the API origin. Anonymous users get a `daat_guest_id` cookie.

**Monetization / plans**: HelloAsso donations hit `helloasso-webhook.js` (verified via `HELLOASSO_WEBHOOK_SECRET`), which sets the user's plan in KV. Plans: `anonymous`, `free`, `khavroutha`, `beit_midrash`, `beit_midrash_plus`, `yeshiva`, `lifetime` — each with daily + monthly question caps defined in `chat.js`. `dedicaces.js` / `dedicace/[siman].js` drive the dedication banners.

**Admin** (`api/admin/*`, pages under `admin/`): gated by `ADMIN_PASSWORD` / `SOUTIEN_ADMIN_SECRET` via the `X-Admin-Secret` header.

### Environment variables

Set in Vercel (never committed; `.env` is git-ignored). Core: `ANTHROPIC_API_KEY`, `UPSTASH_REDIS_REST_URL`/`_TOKEN` (and `KV_REST_API_*`), `JWT_SECRET`, `RESEND_API_KEY` (+ `RESEND_FROM_EMAIL`), `DEEPSEEK_API_KEY`, `HELLOASSO_WEBHOOK_SECRET` (+ `HELLOASSO_FORM_*` URLs), `ADMIN_PASSWORD`/`ADMIN_EMAIL`/`SOUTIEN_ADMIN_SECRET`, `CRON_SECRET`. Behavior flags: `CORPUS_FIRST_ENABLED`, `CORPUS_MIN_SCORE`, `CORPUS_QUOTA_FREE`, `SOUTIEN_MONTHLY_TARGET`.

## Conventions & gotchas

- **Citation convention**: quotation marks are reserved for **verbatim** text. A condensation of a seif is introduced by `<em>résumé</em> :` (`תמצית` / `summary`) and is not judged by `verifier-citations.py`. Anything inside quotes must exist word-for-word in the cited source or the gate fails. This is what makes the gate meaningful — before it, every Level 4 table cell wore quotation marks whether it quoted or paraphrased, and a fabricated citation looked exactly like its forty legitimate neighbours. An ellipsis inside quotes is still fine (`« A… B »` means A and B are each verbatim); each segment is checked separately.
- **Trilingual parity**: a change is not done until FR, HE, and EN are updated consistently.
- **Corpus is derived**: after editing siman HTML that should be searchable by the chat, rerun `npm run build` so `data/corpus-shabbat.json` and `data/simanim-disponibles.json` reflect it.
- **`data/corpus-shabbat.json` n'est plus versionné** (34 Mio réécrits à chaque build, et GitHub refuse un fichier >100 Mio). Il est régénéré par `vercel-build` avant le bundling des fonctions et déclaré dans `vercel.json` (`includeFiles`). **Après un clone frais : lancer `npm run build` avant tout script local qui lit le corpus.**
- **Don't hand-edit generated files**: `PROGRESS.md`, `data/simanim-disponibles*.json`, `data/corpus-shabbat.json`, `assets/js/chat-widget.min.js`, `sitemap.xml` are build outputs.
- **Visual identity** (used throughout the inline CSS): Navy `#1A1F3A`, Or `#C5A55A`, Crème `#FAF6EE`; fonts Frank Ruhl Libre (Hebrew) + Cormorant Garamond.
- **README.md is stale** (describes an old single-siman layout with different level names) — trust this file, `vercel.json`, and `scripts/README.md` instead.
