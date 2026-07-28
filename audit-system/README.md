# Système d'audit DaatTorah — Phase 1

Audit automatique du site public [daattorah.com](https://daattorah.com), en **lecture seule**.

Ce système explore le périmètre défini (simanim 242 à 269, français, niveau *base*),
archive chaque page et chaque version, détecte les changements, et posera en phases
suivantes les contrôles de citations, le workflow de validation et l'interface
d'administration. **Il ne modifie jamais le site public.**

## Place dans l'écosystème existant

Ce dépôt est la *source* de daattorah.com (déploiement statique Vercel). Deux gates
y existent déjà et restent la référence pour l'audit des fichiers sources :

| Outil | Ce qu'il vérifie |
|---|---|
| `scripts/audit-simanim.py` | Structure (fichiers manquants, boilerplate, TOC) |
| `scripts/verifier-citations.py` | Contenu (chaque citation hébraïque confrontée à Sefaria) |
| **`audit-system/` (ce système)** | **Ce que les visiteurs voient réellement en production** : rendu, redirections, liens, dérive entre déploiements, historique versionné |

En Phase 4, la couche de comparaison de citations **réutilisera** la logique éprouvée
de `verifier-citations.py` (résolution de références, normalisation hébraïque,
multi-éditions Sefaria) plutôt que de la réimplémenter.

## Garanties de sécurité (§4 du cahier des charges)

- **Trois modes** : `audit_readonly` (défaut, seul implémenté), `staging_review`,
  `production_publish`. Voir `daat_audit/config.py`.
- **Aucune écriture vers le site.** L'unique point de passage prévu pour une future
  publication (`daat_audit/safety.py::ensure_site_write_allowed`) échoue
  systématiquement en Phase 1 — y compris en mode `production_publish`, car la
  publication n'est pas implémentée. Un test le verrouille.
- **Aucune autocorrection.** Le modèle `AuditRule.autocorrect_allowed` vaut `False`
  par défaut et rien ne l'active. Le champ `SuggestedCorrection.applied` reste `False`.
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
│   ├── crawler/
│   │   ├── urls.py          # périmètre : /oh/{242..269}/base
│   │   ├── fetch.py         # httpx, débit limité, redirections tracées, transport injectable
│   │   └── crawl.py         # orchestration + CLI (python -m daat_audit.crawler.crawl)
│   ├── api/
│   │   ├── main.py          # FastAPI : /health /crawl /pages /stats (+ OpenAPI /docs)
│   │   └── schemas.py
│   └── data/works_aliases.json  # amorce de la table d'alias des ouvrages (§7)
├── alembic/                 # migrations (schéma initial : 14 tables)
├── tests/                   # 42 tests, réseau entièrement simulé
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

Endpoints Phase 1 : `GET /health`, `POST /crawl` (202, tâche de fond),
`GET /crawl`, `GET /crawl/{id}`, `GET /pages[?siman=&audit_status=]`,
`GET /pages/{id}[?include_html=&include_text=]`, `GET /stats`.

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
.venv/bin/python -m pytest tests/ -q          # 42 tests, aucun accès réseau
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
- les 42 tests (SQLite en mémoire, réseau simulé par `httpx.MockTransport`) ;
- la migration Alembic sur SQLite (14 tables + `alembic_version`) ;
- un crawl réel complet du périmètre : 28/28 pages archivées (HTML brut, texte
  nettoyé, double empreinte SHA-256), déduplication confirmée en conditions
  réelles (re-crawl d'une page inchangée → aucune version en doublon).

**Non vérifié dans cet environnement (à valider au premier déploiement) :**
- `docker compose up` (pas de démon Docker ici) — le fichier est fourni et
  standard, mais n'a pas tourné ;
- la migration sur PostgreSQL (testée sur SQLite uniquement) ;
- le service `crawler` du compose.

## Limites actuelles (Phase 1)

- Pas de découpage en blocs (§6), pas de détection de références (§7), pas de
  comparaison de citations (§8-§9), pas de contrôles (§10) : **Phase 2**.
- Pas d'interface d'administration ni d'endpoints d'anomalies : **Phase 3**
  (les tables et énumérations existent déjà).
- La vérification des liens internes est optionnelle (`--check-links`) et bornée
  (`AUDIT_MAX_LINKS_CHECKED`, 200 par défaut) pour rester respectueuse.
- `GET /pages/{id}?include_html=true` retourne le HTML complet : prévoir une
  pagination des versions quand l'historique grandira.
- Le verrou « un seul crawl » est un contrôle-puis-insertion sans verrou de
  base (fenêtre de course théorique) — suffisant pour un outil interne
  mono-utilisateur, à durcir si l'API devenait partagée.

## Prochaines étapes recommandées

1. **Phase 2 — découpage & références** : blocs stables (`OH-268-BASE-FR-P014`)
   à partir de la structure réelle des pages (sections numérotées, `blockquote`,
   tableaux) ; moteur de références s'appuyant sur `works_aliases.json` ;
   portage de la normalisation hébraïque de `scripts/verifier-citations.py`
   (deux modes : stricte / normalisée, verdicts gradués du §9).
2. **Phase 3 — validation** : endpoints anomalies + interface d'administration
   (le workflow §14 est déjà modélisé).
3. **Phase 4 — sources** : `TextSourceProvider` avec fournisseur Sefaria
   (multi-éditions — leçon apprise : l'édition Davidson diffère du Vilna) et
   fournisseur local de test ; métriques de fiabilité par règle (§21).
4. **Planification** : un crawl quotidien (cron) pour détecter la dérive entre
   déploiements, une fois le système déployé quelque part en continu.
