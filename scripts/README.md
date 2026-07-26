# Scripts de build — DAAT

## generate-siman.js

Génère la page d'accueil d'un siman (`sources/shabbat/siman-XXX/index.html`) à partir d'un fichier JSON.

### Usage

```bash
# Générer le siman 247 depuis data/simanim/siman-247.json
node scripts/generate-siman.js --siman 247

# Ou pointer vers un fichier de données précis
node scripts/generate-siman.js --file data/simanim/siman-247.json

# Forcer l'écrasement d'un fichier existant
node scripts/generate-siman.js --siman 247 --force

# Sans mise à jour automatique du sitemap
node scripts/generate-siman.js --siman 247 --no-sitemap
```

### Workflow pour ajouter un nouveau siman

1. Créer `data/simanim/siman-XXX.json` (cf. `siman-247-exemple.json` pour la structure)
2. Lancer `node scripts/generate-siman.js --siman XXX` → produit `sources/shabbat/siman-XXX/index.html` + met à jour `sitemap.xml`
3. Rédiger manuellement les 3 niveaux d'étude :
   - `sources/shabbat/siman-XXX/niveau-1-base.html` (initiation)
   - `sources/shabbat/siman-XXX/niveau-2-lamdan.html` (pilpoul approfondi)
   - `sources/shabbat/siman-XXX/niveau-3-synthese.html` (synthèse magistrale)
4. Référencer le nouveau siman dans `sources/shabbat/index.html` (carte)
5. Mettre à jour `llms.txt` à la racine
6. Commit + push → Vercel/GitHub Pages redéploie automatiquement

### Structure d'un fichier JSON de siman

Tous les champs sont obligatoires sauf `seifText` et `subtitle`. Voir `data/simanim/siman-242.json` pour un exemple complet.

| Champ | Description |
|---|---|
| `number` | Numéro du siman (entier) |
| `numberHe` | Représentation hébraïque (ex : `רמ״ב`) |
| `titleHe` | Titre du siman en hébreu (issu du Choulhan Aroukh) |
| `titleFr` | Titre en français |
| `subtitle` | Sous-titre (optionnel) |
| `description` | Meta description SEO (~155 caractères) |
| `keywords` | Mots-clés SEO séparés par des virgules |
| `teaches` | Tableau des concepts halakhiques enseignés (pour Schema.org) |
| `citations` | Tableau des sources citées (Choulhan Aroukh, Mishna Brura, etc.) |
| `seifText` | Objet `{seif, he, fr}` (optionnel) — texte du seif principal |
| `levels` | Tableau de 3 objets `{num, bar, nameHe, nameFr, desc, href, pdf?}` |
| `faq` | Tableau d'objets `{q, a}` — alimente la FAQPage Schema + section visible |

### Pourquoi le générateur ne produit que la page index ?

Chaque siman a son propre pilpoul, ses propres tableaux de poskim, ses propres concepts. Tenter d'industrialiser les 3 niveaux d'étude ne ferait que produire des pages génériques sans valeur. Le générateur prend en charge ce qui est répétitif (head SEO, JSON-LD, breadcrumb, hero, navigation, FAQ) — la rédaction halakhique reste artisanale.

## audit-simanim.py

Audite l'état réel des niveaux 1-4 de tous les simanim de Hilkhot Shabbat (242-365) : fichiers manquants, contenu générique non réécrit (boilerplate laissé par `generate-niveaux-123.py`), tables des matières du Niveau 2 désynchronisées.

```bash
python3 scripts/audit-simanim.py                  # rapport complet
python3 scripts/audit-simanim.py --quiet          # résumé seul
python3 scripts/audit-simanim.py --write-progress # régénère PROGRESS.md
```

Le script renvoie un **code de sortie non nul** dès qu'une erreur est détectée (boilerplate, fichier absent, TOC désynchronisée). Il peut donc servir de garde-fou — par exemple en hook `SessionStart` ou en pre-commit — pour empêcher de considérer un siman comme « complété » alors qu'il contient encore du contenu générique.

`PROGRESS.md` (racine du dépôt) est le manifeste de progression : il est **généré** par ce script, ne pas l'éditer à la main.

## cout-question.js

Calcule le coût réel d'une question du chat Daat, et la marge de chaque plan payant. Le script **lit les constantes du code** (`api/chat.js` : tarifs des modèles, multiplicateurs de cache, budget d'outils, `MONTHLY_LIMITS` ; `api/_system-prompt.js` : taille du prompt système) — il ne peut donc pas diverger de ce qu'il mesure.

```bash
node scripts/cout-question.js             # tarifs et plafonds actuels
node scripts/cout-question.js --eur 1.08  # taux de change €→$ (défaut 1.08)
```

Il produit deux tableaux : le coût par scénario (corpus-first Haiku, Sonnet standard, Opus typique, Opus cache froid, Opus pire cas) et la marge par plan dans l'hypothèse la plus défavorable.

**À relancer après tout changement** de tarif Anthropic, de modèle dans `MODELS`, de plafond dans `MONTHLY_LIMITS`, ou de taille du prompt système. Les chiffres du commentaire de calibrage dans `api/chat.js` en sont issus — ne pas les recopier à la main.

Deux limites à connaître : la taille du prompt système est une **estimation** (3,5 caractères par token ; pour un compte exact, utiliser l'endpoint `count_tokens` d'Anthropic), et le pire cas suppose que 100 % des questions consomment le budget maximal en repartant d'un cache froid — ce qui n'arrive jamais. Le coût réellement observé est dans `/admin` (champ `cost_usd`).

⚠️ Les coûts sont en **dollars** (les tarifs Anthropic le sont, et le champ KV s'appelle `cost_usd`) ; les recettes des plans sont en **euros**. C'est le seul endroit du projet où les deux unités se rencontrent, d'où le taux de change explicite.
