# Système d'audit DaatTorah — Phases 1 à 4

Audit automatique du site public [daattorah.com](https://daattorah.com), en **lecture seule**.

Ce système explore le périmètre défini (simanim 242 à 269, français, niveau *base*),
archive chaque page et chaque version, détecte les changements, découpe les pages en
blocs identifiés, et **confronte chaque citation hébraïque au texte réel de la source
qu'elle invoque**. Il ne propose jamais de correction sur du contenu, et
**ne modifie jamais le site public.**

## Place dans l'écosystème existant

Ce dépôt est la *source* de daattorah.com (déploiement statique Vercel). Deux gates
y existent déjà et restent la référence pour l'audit des fichiers sources :

| Outil | Ce qu'il vérifie |
|---|---|
| `scripts/audit-simanim.py` | Structure (fichiers manquants, boilerplate, TOC) |
| `scripts/verifier-citations.py` | Contenu (chaque citation hébraïque confrontée à Sefaria) |
| **`audit-system/` (ce système)** | **Ce que les visiteurs voient réellement en production** : rendu, redirections, liens, dérive entre déploiements, historique versionné |

La couche de comparaison de citations **reprend** la logique éprouvée de
`verifier-citations.py` (résolution de références, normalisation hébraïque,
multi-éditions Sefaria) plutôt que de la réimplémenter — chacun de ses détails vient
d'un faux positif constaté sur le site.

## Garanties de sécurité (§4 du cahier des charges)

- **Trois modes** : `audit_readonly` (défaut, seul implémenté), `staging_review`,
  `production_publish`. Voir `daat_audit/config.py`.
- **Aucune écriture vers le site.** L'unique point de passage prévu pour une future
  publication (`daat_audit/safety.py::ensure_site_write_allowed`) échoue
  systématiquement — y compris en mode `production_publish`, car la publication
  n'est pas implémentée. Un test le verrouille pour les trois modes.
- **Aucune autocorrection.** Le modèle `AuditRule.autocorrect_allowed` vaut `False`
  par défaut et rien ne l'active — pas même une précision mesurée à 100 %. Le champ
  `SuggestedCorrection.applied` reste `False`.
- **Aucune correction proposée sur une citation.** Le contrôle `CIT-001` porte la
  citation, le texte source et le verdict ; il laisse `proposed_correction` à `null`.
  Réécrire une citation, c'est trancher une question de contenu — cela revient au Rav.
- **Journal inaltérable** : aucun endpoint de suppression sur `audit_logs`, et le
  durcissement côté base est outillé — `deploy/postgres-harden.sql` crée le rôle
  applicatif sans `UPDATE/DELETE/TRUNCATE` sur cette table (à exécuter après les
  migrations, puis faire pointer `AUDIT_DATABASE_URL` de l'API sur ce rôle).
- **Crawler respectueux** : User-Agent identifiable (`DaatTorah-AuditBot/0.1`),
  délai de 1,5 s appliqué à chaque requête sortante — y compris chaque saut de
  redirection et la vérification de liens —, timeout borné, redirections tracées.
- **Un seul crawl à la fois** : `POST /crawl` répond 409 si un job est déjà actif
  (la politesse est garantie globalement, pas seulement par job), et le périmètre
  d'un job est borné (simanim 1–999, 200 max par job — rejet en 422 sinon).
- **API sans authentification** = outil interne : le docker-compose lie le port
  sur `127.0.0.1` uniquement. Ne pas exposer publiquement en l'état.

## Architecture

```
audit-system/
├── daat_audit/
│   ├── config.py            # pydantic-settings, préfixe AUDIT_, 3 modes
│   ├── safety.py            # garde-fous : jamais d'écriture vers le site
│   ├── models.py            # les 14 tables du cahier des charges (§17)
│   ├── db.py                # moteur SQLAlchemy 2 (SQLite dev / PostgreSQL prod)
│   ├── hashing.py           # SHA-256 html + texte normalisé (détection de changement)
│   ├── extract.py           # titre, texte visible, liens internes (BeautifulSoup/lxml)
│   ├── blocks.py            # découpage en blocs typés + identifiants stables (§6)
│   ├── hebrew.py            # normalisation hébraïque + comparaison graduée (§9)
│   ├── references.py        # moteur de références, gematria validée (§7)
│   ├── checks.py            # contrôles TECH-001..008 et EDIT-001..003 (§10)
│   ├── quotes.py            # fragments donnés pour littéraux (convention §8)
│   ├── citations.py         # confrontation citation ↔ source, verdicts (§8-§9)
│   ├── analyze.py           # passe de vérification + CLI (python -m daat_audit.analyze)
│   ├── metrics.py           # fiabilité par règle (§21)
│   ├── workflow.py          # machine à états des décisions (§13, §14)
│   ├── sources/             # fournisseurs de textes (§15)
│   │   ├── base.py          #   contrat TextSourceProvider
│   │   ├── sefaria.py       #   Sefaria, multi-éditions, débit limité
│   │   ├── local.py         #   fournisseur local (tests, hors-ligne)
│   │   └── cache.py         #   mémorisation en base (table source_texts)
│   ├── crawler/
│   │   ├── urls.py          # périmètre : /oh/{242..269}/base
│   │   ├── fetch.py         # httpx, débit limité, redirections tracées, transport injectable
│   │   └── crawl.py         # orchestration + CLI (python -m daat_audit.crawler.crawl)
│   ├── api/
│   │   ├── main.py          # FastAPI (+ OpenAPI /docs, interface /admin)
│   │   ├── auth.py          # le rôle découle du secret présenté (§14)
│   │   ├── schemas.py
│   │   └── static/admin.html    # interface de validation, autonome (§16)
│   └── data/
│       ├── works_aliases.json   # table d'alias des ouvrages (§7)
│       └── terminologie.json    # graphies attestées — GÉNÉRÉ, ne pas éditer
├── scripts/build-terminologie.py  # régénère terminologie.json depuis sources/
├── alembic/                 # migrations (schéma initial : 14 tables)
├── tests/                   # 182 tests, réseau entièrement simulé
├── docker-compose.yml       # PostgreSQL 16 + API (+ service crawler ponctuel)
└── var/                     # base SQLite locale et artefacts (git-ignoré)
```

### Choix d'architecture, et écarts assumés avec le cahier des charges

| Sujet | Choix | Pourquoi |
|---|---|---|
| Base de données | **SQLite par défaut, PostgreSQL via `AUDIT_DATABASE_URL`** | Les tests et le développement ne demandent aucun service ; le schéma est identique (SQLAlchemy 2 + Alembic, `render_as_batch` pour SQLite). Docker Compose fournit PostgreSQL 16. |
| Célery / Redis | **Absents en Phase 1** | Le seul travail asynchrone est un crawl de 28 pages (~45 s), porté par les `BackgroundTasks` FastAPI. Une file de tâches n'apporterait que de la surface d'infrastructure ; elle deviendra pertinente en Phase 4 (comparaison de citations en masse). |
| Scrapy / Playwright | **httpx + BeautifulSoup** | Le périmètre est fermé (28 URL construites, pas découvertes) et les pages sont statiques — pas de JavaScript à rendre. Scrapy est dimensionné pour la découverte de sites ; Playwright pour le rendu. Le transport httpx est injectable, donc testable sans réseau. |
| Sync plutôt qu'async | **Client httpx synchrone** | Le débit est volontairement limité à ~1 requête/1,5 s : l'asynchrone n'accélérerait rien et compliquerait tout. |
| Python | **Code compatible 3.11+, image Docker 3.12** | L'environnement de développement fournit 3.11 ; le déploiement conteneurisé utilise 3.12 comme demandé. |

## Installation

```bash
cd audit-system
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # ajuster si besoin
```

### Initialiser la base et lancer un crawl

```bash
.venv/bin/alembic upgrade head                     # crée les 14 tables
.venv/bin/python -m daat_audit.crawler.crawl       # crawl du périmètre 242-269
# Variantes :
#   --simanim 242-245      périmètre restreint
#   --check-links          vérifier aussi les liens internes
#   --verbose              journal détaillé
```

### Lancer l'API

```bash
.venv/bin/uvicorn daat_audit.api.main:app --reload
# → http://localhost:8000/docs (OpenAPI)
```

Endpoints : `GET /health`, `POST /crawl` (202, tâche de fond), `GET /crawl`,
`GET /crawl/{id}`, `GET /pages[?siman=&audit_status=]`,
`GET /pages/{id}[?include_html=&include_text=]`, `GET /stats`,
`GET /findings[?siman=&rule_code=&severity=&risk=&status=]`,
`GET /findings/{id}`, `GET /findings/{id}/history`, `GET /stats/rules`,
`POST /findings/{id}/decision`, `POST /findings/{id}/rabbinic-answer`,
`GET /workflow/actions`, et l'interface `GET /admin`.

### Avec Docker (PostgreSQL)

```bash
docker compose up --build            # API sur 127.0.0.1:8000, migrations au démarrage
docker compose run --rm crawler      # crawl ponctuel
# Durcissement du journal d'audit (après les migrations) :
#   psql -U daat_audit -d daat_audit -v app_password="'…'" -f deploy/postgres-harden.sql
```

Le mot de passe PostgreSQL de développement se surcharge par `AUDIT_DB_PASSWORD`.

### Tests

```bash
.venv/bin/python -m pytest tests/ -q          # 182 tests, aucun accès réseau
```

Les handlers HTTP simulés assertent la méthode de chaque requête : toute
requête non-GET/HEAD vers le site fait échouer la suite — l'invariant
« lecture seule » est vérifié au niveau HTTP, pas seulement déclaré.

### Derrière un proxy TLS d'entreprise

```bash
AUDIT_CA_BUNDLE=/chemin/vers/ca-bundle.crt .venv/bin/python -m daat_audit.crawler.crawl
```

## Ce qui est vérifié — et ce qui ne l'est pas

**Vérifié dans cet environnement :**
- les 182 tests (SQLite en mémoire, réseau simulé par `httpx.MockTransport`) ;
- la migration Alembic sur SQLite (14 tables + `alembic_version`) ;
- un crawl réel complet du périmètre : 28/28 pages archivées (HTML brut, texte
  nettoyé, double empreinte SHA-256), déduplication confirmée en conditions
  réelles (re-crawl d'une page inchangée → aucune version en doublon).

**Non vérifié dans cet environnement (à valider au premier déploiement) :**
- `docker compose up` (pas de démon Docker ici) — le fichier est fourni et
  standard, mais n'a pas tourné ;
- la migration sur PostgreSQL (testée sur SQLite uniquement) ;
- le service `crawler` du compose.

## Phase 2 — ce qui a été ajouté

Le crawl ne fait plus qu'archiver : chaque nouvelle version de page est
**découpée, analysée et signalée**. L'analyse ne tourne que lorsqu'une version
est créée (première collecte ou changement de contenu) ; une page inchangée
n'est pas réanalysée, sinon chaque passage dupliquerait blocs et signalements.

| Module | Rôle | §  |
|---|---|---|
| `blocks.py` | découpage en blocs typés, identifiants stables `OH-268-BASE-FR-P014` | §6 |
| `references.py` | références FR/HE/translittérées, gematria **validée** | §7 |
| `hebrew.py` | normalisation + comparaison à verdict gradué | §9 |
| `checks.py` | 8 contrôles techniques, 3 éditoriaux | §10 |

**Identifiant stable : rang par type, pas index global.** Un index global se
décale dès qu'un paragraphe est inséré n'importe où dans la page, et toutes les
décisions déjà rendues se retrouvent rattachées au mauvais bloc. Le rang par
type ne bouge que si un bloc du *même* type est inséré avant — un test le
vérifie en insérant un paragraphe et en constatant que les identifiants des
citations hébraïques ne bougent pas. L'identifiant ne survit pas à une
réorganisation profonde ; le `sha256` du bloc permet alors de retrouver un
contenu déplacé.

### Trois faux positifs corrigés, et ce qu'ils apprennent

Ces trois défauts ont la même forme : **une règle écrite d'après une idée du
site plutôt que d'après le site**. C'est la même erreur que celle traquée dans
le contenu, commise dans l'instrument.

1. **Le dictionnaire de terminologie était inventé.** Sept de ses dix entrées
   désignaient comme forme canonique une graphie que le site n'emploie nulle
   part, et pour מוקצה la forme donnée comme fautive (*Muktzeh*, 75) était plus
   fréquente que la forme dite correcte (*Mouktsé*, 37). Il est désormais
   **dérivé** du site par `scripts/build-terminologie.py`, et EDIT-001 ne
   tranche plus : il signale qu'une page hésite entre deux graphies, donne les
   comptes du site, et ne propose aucune correction — choisir entre deux
   translittérations attestées est une décision éditoriale qui revient au Rav.
2. **TECH-008 et TECH-001 lisaient un champ qui ne pouvait pas contenir le
   défaut cherché.** TECH-008 cherchait la classe RTL dans `raw_content`, qui
   est le HTML *intérieur* de la balise et ne contient donc jamais ses propres
   attributs : 7 signalements sur 7 étaient faux. TECH-001 cherchait des
   espaces doubles dans `normalized_content`, qui les a déjà réduits : il ne
   pouvait rien trouver. Les classes qui orientent le texte sont maintenant
   lues **dans le CSS de la page** (le site oriente par `.he`, `.text-source`
   et `.he-q` — trois noms qu'aucune liste écrite d'avance n'aurait devinés).
3. **La graphie pleine passait pour une falsification.** Sefaria vocalise en
   graphie défective (עֹנֶג, מְכֻבָּד), le site écrit en graphie pleine (עונג,
   מכובד) : Isaïe 58:13 cité **mot pour mot** ressortait en « mot remplacé ».
   D'où le verdict `DIFF_ORTHOGRAPHE`. Seul le *vav médian* est neutralisé —
   le vav initial est la conjonction, le vav final un suffixe, et le yod n'est
   jamais touché pour que בית ne se confonde pas avec בת : mieux vaut un faux
   positif qu'une citation fautive déclarée conforme.

Sur la page réelle servant de fixture (siman 242, niveau 1, FR), les onze
contrôles ne produisent **aucun signalement** — ce qui est le résultat correct
pour une page conforme aux deux gates du dépôt. Les tests vérifient donc les
deux sens : silence sur la page saine, **et** détection dès qu'on y injecte le
défaut visé. Un contrôle qui ne fait que se taire n'est pas un contrôle.

## Phase 4 — vérification des citations

Le crawl reste hors ligne : il collecte, découpe et applique les contrôles
techniques. La vérification des citations est une **passe séparée**, parce
qu'elle interroge un service tiers et peut échouer pour des raisons qui n'ont
rien à voir avec le site — les mêler ferait dépendre l'archivage de la
disponibilité de Sefaria.

```bash
.venv/bin/python -m daat_audit.analyze                  # tout le périmètre
.venv/bin/python -m daat_audit.analyze --simanim 242-245 --dry-run
```

### Ce que le contrôle CIT-001 fait, et ce qu'il refuse de faire

| | |
|---|---|
| Compare | chaque fragment **donné pour littéral** au texte réel de la source citée |
| Ignore | nikoud, ponctuation, graphie pleine/défective, abréviations, tronçons littéraux |
| Signale | mot ajouté, supprimé, remplacé, ordre différent, absence |
| Ne fait **jamais** | proposer une réécriture, corriger, qualifier une intention |

Une absence est qualifiée, pas accusée : le fragment est recherché ailleurs
dans le corpus, ce qui distingue une **citation fabriquée** d'une **citation
exacte mal référencée** — deux défauts qui n'appellent pas la même correction.
Quand rien n'est trouvé, le signalement dit « introuvable ailleurs dans le
corpus interrogé — à vérifier par le Rav », et s'arrête là.

### Ce que le premier essai réel a appris

Le pipeline a d'abord rendu **zéro** citation examinée sur une vraie page :
79 blocs, 5 références, 8 citations, aucune paire. La cause n'était pas un
bogue mais une hypothèse fausse sur le site — j'appariais citation et
référence **dans le même bloc**, alors que le site annonce la source depuis la
prose qui précède :

> `<p>La Guemara (Beitsa 15b) raconte :</p>` puis `<blockquote>` hébreu.

Le rattachement remonte donc les blocs précédents, avec deux garde-fous : un
**titre de section arrête la remontée** (nouvelle section, nouveau sujet), et
la fenêtre est bornée. Une référence rattachée par voisinage est une
inférence, pas une lecture : le signalement le dit et sa confiance baisse.

### Résultat sur une page réelle

Une fois corrigé, le système a trouvé seul, sur le siman 242 niveau 1 — page
conforme aux deux gates existants (174/174) :

> `אָמַר לָהֶם **הַבּוֹרֵא** לְיִשְׂרָאֵל בָּנַי, לְווּ עָלַי…`
> alors que Beitsa 15b porte, dans **les deux** éditions hébraïques de Sefaria :
> `אמר להם **הקדוש ברוך הוא** לישראל בני לוו עלי…`

Une appellation divine substituée dans un passage présenté comme littéral.
Vérifié à la main contre la source avant d'être rapporté ; **non corrigé** —
la décision revient au Rav.

### Fiabilité par règle (§21)

`GET /stats/rules` et `daat_audit.metrics` calculent la précision de chaque
règle à partir des décisions humaines rendues. Deux précautions : une règle
sans décision affiche `null` et non 100 % — une règle non éprouvée n'a pas de
précision ; et un signalement classé `SOURCE_UNAVAILABLE` n'est pas compté en
faux positif, car il ne dit rien sur la règle.

## Phase 3 — validation, rôles et interface

### La règle qui gouverne le workflow

> **Un signalement à risque halakhique ne peut jamais être approuvé par un
> éditeur seul.** Il doit passer par le Rav.

Ce n'est pas une précaution d'usage : c'est la raison d'être du système. Le
contrôle n'est donc **pas dans l'interface** — où un appel direct à l'API le
contournerait — mais dans la transition d'état elle-même, et deux tests le
verrouillent : un sur le module, un sur l'API.

Le rôle découle **du secret présenté**, jamais d'un champ de la requête :

```bash
AUDIT_ADMIN_SECRET=…   # → rôle « editor »
AUDIT_RAV_SECRET=…     # → rôle « rav »
```

Sans secret configuré, toute décision est refusée (503, *fail closed*) : un
outil qui laisse décider sans savoir qui décide ne trace rien d'utile.

### Transitions

| Action | Cible | Rôle |
|---|---|---|
| `approve` | `EDITOR_APPROVED` | éditeur — **sauf** risque halakhique |
| `escalate` | `RABBINIC_REVIEW_REQUIRED` | éditeur (ouvre une question au Rav) |
| `rabbinic_approve` / `rabbinic_reject` | `RABBINIC_APPROVED` / `REJECTED` | **rav seul** |
| `reject`, `false_positive`, `editorial_variant`, `source_unavailable` | — | éditeur |
| `ready_for_staging` | `READY_FOR_STAGING` | après approbation uniquement |
| `reopen` | `ADMIN_REVIEW_REQUIRED` | retour arrière |

`PUBLISHED` **n'est la cible d'aucune transition** : la publication n'est pas
implémentée, et un test vérifie qu'aucun chemin n'y mène.

### Traçabilité et retour arrière

Chaque décision écrit **deux** traces : une ligne dans `admin_decisions` et une
entrée au journal `audit_logs`. Aucune décision passée n'est jamais modifiée ni
supprimée — un retour arrière *ajoute* une ligne. La source justifiant la
décision est conservée (`source_attached`).

### Interface `/admin`

Page autonome servie par l'API (aucune ressource externe : l'outil doit
fonctionner hors ligne). Elle présente le **texte de la page et la source
côte à côte**, pour que l'humain compare lui-même plutôt que de croire le
verdict, et rappelle explicitement, sur tout signalement halakhique, que la
décision revient au Rav. Le secret vit en `sessionStorage`, jamais au-delà de
l'onglet.

Deux détails d'affichage ont été corrigés après avoir regardé le rendu réel :

- les guillemets `« »` sont **neutres** au sens de l'algorithme bidi ; contre
  de l'hébreu ils basculent, et `« X » → « Y »` s'affichait à l'envers. Dans un
  outil dont tout l'objet est de dire *quel* mot a changé, c'est un contresens.
  Les segments cités sont désormais isolés, guillemets compris (vérifié par les
  positions réelles des éléments dans un navigateur, pas à l'œil) ;
- un couple ne différant que par une mère de lecture n'est plus listé comme un
  mot remplacé — il faisait lire deux défauts là où il n'y en a qu'un.

## Limites actuelles

- **Seul l'hébreu est vérifié.** Les traductions françaises ne sont confrontées
  à rien : une traduction inexacte d'une citation exacte passe inaperçue.
- Le rattachement d'une référence par voisinage est une inférence bornée : une
  citation éloignée de son annonce peut rester non vérifiée (silence), ce qui
  est le bon sens de l'erreur, mais reste une couverture incomplète.
- **Faire évoluer une règle ne rejoue pas les pages inchangées** : il faudra
  une commande de réanalyse explicite (Phase 4).
- La précision des règles n'est pas encore mesurée (`AuditRule.precision`
  existe mais n'est pas alimenté) : **Phase 4**, §21.
- EDIT-002 (« phrase inachevée ») reste la règle la plus fragile : sur la page
  de test, ses deux seuls déclenchements étaient des faux positifs (un sommaire
  et un filigrane), corrigés en amont par le typage des blocs. Elle est à
  surveiller sur un corpus plus large.
- La vérification des liens internes est optionnelle (`--check-links`) et bornée
  (`AUDIT_MAX_LINKS_CHECKED`, 200 par défaut) pour rester respectueuse.
- `GET /pages/{id}?include_html=true` retourne le HTML complet : prévoir une
  pagination des versions quand l'historique grandira.
- Le verrou « un seul crawl » est un contrôle-puis-insertion sans verrou de
  base (fenêtre de course théorique) — suffisant pour un outil interne
  mono-utilisateur, à durcir si l'API devenait partagée.

## Prochaines étapes recommandées

1. **Mesurer la précision sur un vrai passage de revue** : le mécanisme est en
   place, mais aucune règle n'a encore été jugée en nombre. C'est ce qui dira
   lesquelles méritent d'être gardées.
2. **Réanalyse à règle modifiée** : faire évoluer une règle ne rejoue pas les
   pages inchangées ; il faut une commande explicite.
3. **Élargir le périmètre** : les trois langues et les quatre niveaux, une fois
   la précision des règles mesurée sur le périmètre actuel.
4. **Planification** : un crawl quotidien (cron) pour détecter la dérive entre
   déploiements, une fois le système déployé quelque part en continu.

Régénérer le dictionnaire de terminologie après une évolution du contenu :

```bash
.venv/bin/python scripts/build-terminologie.py           # régénère
.venv/bin/python scripts/build-terminologie.py --check   # échoue si désynchronisé
```
