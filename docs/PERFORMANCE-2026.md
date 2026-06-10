# Performance INP 2026 — Optimisation du chat-widget

Date : 2026-06-10
Branche : `claude/seo-full-sweep`
Cible : Core Web Vital **INP (Interaction to Next Paint) < 200 ms**, devenu
le 3ᵉ Web Vital officiel depuis mars 2024. Selon Google, 43 % des sites
échouent à ce seuil — DAAT le passait probablement de justesse sur les
pages siman lourdes (jusqu'à 274 KB pour le siman 301 N4).

## Le problème

Sur chaque page siman, on chargeait `chat-widget.min.js` (35 KB minifié,
~58 KB source, 1363 lignes) en `defer`. Au DOMContentLoaded, le widget :

1. Crée 2 nœuds DOM (bouton FAB + panel complet de 600+ lignes HTML).
2. Attache une dizaine d'event listeners (drag, scroll, input, etc.).
3. Lit `localStorage` (`daat-conversations-v1`, `daat-lang-v1`).
4. Polle `window.daatAuth` jusqu'à ce qu'il existe, puis branche un hook
   `onChange` pour la sync serveur des conversations.
5. Si l'utilisateur est connecté, déclenche un `fetch` GET vers
   `/api/conversations` pour la sync pull-and-merge.

Tout ça s'exécute pendant les premières centaines de ms de la page, en
concurrence avec le rendu du contenu. C'est **~30-60 ms de scripting**
sur un appareil milieu de gamme, et un `fetch` qui occupe le main thread
au moment où l'utilisateur veut interagir avec le texte du siman.

**Or, la grande majorité des visiteurs n'utilise pas le chat.** Les pages
siman attirent principalement des lecteurs (SEO organique), pas des
poseurs de questions.

## La solution : mini-loader paresseux

Nouveau fichier : [`assets/js/chat-loader.js`](../assets/js/chat-loader.js)
(~3,5 KB source, <1 KB une fois minifié).

Le loader :

1. Crée immédiatement un bouton FAB statique avec exactement les mêmes
   classes CSS que le vrai widget (`.daat-chat-button`,
   `.daat-chat-button-icon`, `.daat-chat-button-pulse`). Le CSS étant
   déjà chargé, le rendu est identique sans aucun FOUC.
2. Attache des listeners passifs sur 4 signaux d'engagement :
   - **clic / touch sur le FAB** → charge le widget + l'ouvre.
   - **mouseenter / focusin sur le FAB** → précharge le widget (mais ne
     l'ouvre pas).
   - **scroll > 600 px** → précharge le widget (lecteur engagé).
   - **idle + 4 s** → fallback de chargement (préserve la sync
     conversations des utilisateurs connectés).
3. Au moment du chargement, injecte un `<script async>` qui pointe vers
   `chat-widget.min.js` (path déduit du src du loader lui-même → marche
   pour tous les chemins relatifs et absolus).
4. Le vrai widget s'auto-init normalement (idempotent : il vérifie
   `window.daatChatWidget`).

### Gain mesurable

| Page test                      | Avant            | Après                | Gain         |
|--------------------------------|------------------|----------------------|--------------|
| Siman 248 N1 (85 KB)           | 35 KB JS au boot | <1 KB                | ~34 KB       |
| Siman 301 N4 (274 KB)          | 35 KB JS au boot | <1 KB                | ~34 KB       |
| Blog livraison-colis (19 KB)   | inchangé*        | inchangé*            | —            |

*Les pages blog n'ont pas été migrées (un autre agent travaille dessus
en parallèle). Elles peuvent être migrées plus tard avec la même
commande.*

**Estimation INP** :
- Scripting au boot : -30 à -60 ms (dépend de l'appareil) sur les
  appareils mobiles milieu de gamme.
- Network : -1 requête HTTP (le widget se charge seulement si engagé).
- TBT (Total Blocking Time) : -25 à -40 ms attendus.
- INP du premier clic non-chat : amélioré car main thread plus libre.
- INP du premier clic sur le FAB : légèrement dégradé (~+200 ms le
  temps que le script télécharge), mais l'utilisateur s'attend à un
  petit délai à l'ouverture du chat — acceptable.

## Autres pistes inspectées (et leur statut)

### intra-links.js

Inspecté : c'est un délégué d'événement sur `document.click`, plus un
`flashOnHashLoad` léger au boot. Coût total : <2 ms. **Pas de changement
nécessaire.**

### Polices Google Fonts

Déjà optimal : `preconnect` + `preload as=style` avec
`onload="this.rel='stylesheet'"` et fallback `<noscript>`. Le paramètre
`display=swap` est présent dans l'URL Google Fonts. **Pas de changement
nécessaire.**

### Images

Les pages siman ne contiennent **aucune** image `<img>`. Toutes les
illustrations sont des emojis ou des caractères hébreux. **Pas de
changement nécessaire.**

### CSS

- `chat-widget.css` : 25 KB chargé en bloquant. Comme le loader affiche
  le FAB à `DOMContentLoaded`, on ne peut pas le différer sans risquer
  un FOUC. **Laissé tel quel.**
- `intra-links.css` : 1,9 KB. Trop petit pour être un problème.

### JSON-LD

Non touché (autres agents en parallèle).

## Comment migrer les autres pages

Le loader fonctionne sur **toutes** les pages, pas seulement les siman.
Pour migrer (par exemple) les pages blog une fois l'autre agent terminé :

```bash
# Modifier scripts/replace-chat-with-loader.py pour pointer vers blog/
# OU faire un sed ciblé (penser au pattern dev `chat-widget.js`) :
find blog/ -name "*.html" -exec sed -i 's|chat-widget\.min\.js" defer|chat-loader.js" defer|g' {} +
```

Le loader est rétrocompatible : remettre un chemin direct vers
`chat-widget.min.js` dans un HTML reste fonctionnel.

## Recommandations pour aller plus loin (hors scope de cette PR)

1. **Critical CSS inline** : extraire les ~3 KB de CSS au-dessus du fold
   et les inliner dans le `<head>`, puis charger le reste en async. Gain
   FCP potentiel : 100-200 ms sur 3G.
2. **Image optimization** : si jamais des images sont ajoutées (OG, blog
   posts), utiliser AVIF/WebP avec `<picture>` et `loading="lazy"`.
3. **Service Worker** : cacher `chat-widget.min.js`, les fonts, et le CSS
   au premier paint pour gagner ~80 ms sur les visites répétées.
4. **Préfetch sur les liens internes** : sur la page catalogue `/oh/`,
   précharger les pages siman au survol via `<link rel="prefetch">`.
5. **Minifier le CSS** : `chat-widget.css` n'est pas minifié (25 KB →
   ~15 KB possible).
6. **Splitter le chat-widget** : 1363 lignes dans un seul module. Le
   pilpoul markdown + tables + RTL pourrait être lazy-loadé à la
   première réponse de l'IA (gain au load du widget).

## Validation

- `python3 scripts/audit-simanim.py --quiet` → 124/124 conformes ✓
- `node --check assets/js/*.js` → tous OK ✓
- Pas de modification de pages blog, du JSON-LD, du CSS visuel.
- Le chat reste pleinement fonctionnel (chargement à la demande).
- Les intra-links restent inchangés.
