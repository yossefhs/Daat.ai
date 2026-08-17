// Vercel Serverless Function — Endpoint chat de Daat (l'IA pédagogique de DAAT.AI)
// - Claude Opus 4.7 avec tool use (Sefaria API) en boucle agentique
// - Prompt caching (TTL 1h) sur le system prompt long
// - Adaptive thinking (effort: high)
// - Streaming SSE pour l'affichage progressif
// - Multi-turn (l'historique est envoyé par le client à chaque appel)

import Anthropic from '@anthropic-ai/sdk';
import { kv } from './_kv.js';
import { getClientIp } from './_http.js';
import { SYSTEM_PROMPT, buildSystemPrompt } from './_system-prompt.js';
import { SEFARIA_TOOLS, executeSefariaTool } from './_sefaria.js';
import { CORPUS_TOOLS, executeCorpusTool, searchCorpus } from './_corpus.js';
import { searchCorpus as searchShabbatCorpus, corpusCacheKey, CORPUS_CACHE_TTL, stripProfileBlock, profileSignature } from './_corpus-search.js';
import { MAREH_MEKOMOT_TOOLS, executeMarehMekomotTool } from './_mareh_mekomot.js';
import { getUserFromRequest, isAllowedOrigin } from './_auth.js';
import { createHash } from 'node:crypto';
import {
  deepSeekAvailable,
  streamMetaQuestion,
  summarizeOlderTurns,
  reformulateForCorpus,
  DEEPSEEK_PRICING,
} from './_deepseek.js';

const client = new Anthropic();

const MAX_TOOL_ITERATIONS = parseInt(process.env.MAX_TOOL_ITERATIONS || '5', 10); // rondes d'outils + synthèse forcée
// Compteur mensuel d'IA générative par ADRESSE IP, pour les visiteurs non
// connectés. Il rend le quota anonyme insensible à l'effacement du cookie.
//
// SEUIL : 100/mois/IP, soit ~3 par jour et 33 fois le quota individuel anonyme.
// Une adresse IP ne désigne pas une personne : derrière une seule il y a une
// famille, une salle d'étude, ou tout un opérateur mobile (CGNAT). Le seuil est
// donc calé pour ne pouvoir être atteint que par de l'usage AUTOMATISÉ — une
// yéchiva de 30 personnes posant 3 questions chacune dans le mois reste dessous.
// Deux amortisseurs le rendent peu risqué :
//   · la dépense réellement coûteuse (Aperçu Opus) est DÉJÀ plafonnée par IP ;
//   · tryCorpusRescue s'exécute AVANT le 429, donc même bloqué l'utilisateur
//     continue de recevoir le corpus du Rav — seule l'IA générative est rationnée.
// Un compte gratuit affranchit complètement de ce plafond (quota par email).
// Réglable sans redéploiement ; 0 = observation seule.
const ANON_IP_MONTHLY_LIMIT = parseInt(process.env.ANON_IP_MONTHLY_LIMIT || '100', 10);
// Seuil d'ALERTE (journal uniquement) même quand le blocage est désactivé.
const ANON_IP_ALERT_AT = parseInt(process.env.ANON_IP_ALERT_AT || '60', 10);
const MAX_TOOL_CALLS = parseInt(process.env.MAX_TOOL_CALLS || '6', 10);           // plafond DUR de tool calls (parallèle compris) ; le budget temps (FORCE_SYNTHESIS_AFTER_MS) reste le gouverneur principal
// Halakha profonde (routée Opus) : budget ÉLARGI. La règle du בד"א impose de
// vérifier les séifim voisins (n+1) avant toute conclusion — ça coûte plusieurs
// sefaria_get_text. Sur la halakha, la CORRECTION prime sur la latence.
const MAX_TOOL_ITERATIONS_HALAKHA = parseInt(process.env.MAX_TOOL_ITERATIONS_HALAKHA || '7', 10);
const MAX_TOOL_CALLS_HALAKHA = parseInt(process.env.MAX_TOOL_CALLS_HALAKHA || '12', 10);
const MAX_TOKENS_OUTPUT = parseInt(process.env.MAX_TOKENS_OUTPUT || '8192', 10); // cap output. Opus 4.7 / Sonnet 4.6 acceptent 128K ; 4096 (~3000 mots) coupait
// les psakim détaillés AVANT leur conclusion (renvoi au Rav, clause limitante).
// Le budget temps (FORCE_SYNTHESIS_AFTER_MS / HARD_ABORT_MS) reste le gouverneur.
// Cap output pour la SYNTHÈSE FORCÉE : doit rester assez haut pour une réponse
// complète (l'ancien 1500 tronquait les réponses halakhiques détaillées).
const FORCED_SYNTHESIS_MAX_TOKENS = parseInt(process.env.FORCED_SYNTHESIS_MAX_TOKENS || String(MAX_TOKENS_OUTPUT), 10);
const HISTORY_TURNS = 16;       // 16 derniers tours (plus de contexte = meilleure réponse)

// La fonction api/chat.js a maxDuration: 300 (Vercel Pro) dans vercel.json.
// On force la synthèse (tool_choice: none) dès qu'on dépasse FORCE_SYNTHESIS_AFTER_MS
// OU à la dernière itération, puis on laisse jusqu'à HARD_ABORT_MS pour streamer la
// réponse EN ENTIER avant le dernier filet de sécurité (bien avant le kill Vercel ~300s).
// Tunables via env sans redéploiement de code.
const FORCE_SYNTHESIS_AFTER_MS = parseInt(process.env.FORCE_SYNTHESIS_AFTER_MS || '60000', 10); // 60s : arrête la recherche, passe à la synthèse
const HARD_ABORT_MS = parseInt(process.env.HARD_ABORT_MS || '250000', 10); // 250s : dernier recours (~50s de marge avant le kill Vercel 300s)
const ALL_TOOLS = [...MAREH_MEKOMOT_TOOLS, ...CORPUS_TOOLS, ...SEFARIA_TOOLS];

// ── Routing modèles — priorité QUALITÉ, économies opportunistes ──
// Prix en $ par MILLIER de tokens (tarifs publics Anthropic / 1M ÷ 1000) :
//   Haiku 4.5   $1 / $5   par million → 0.001 / 0.005
//   Sonnet 4.6  $3 / $15  par million → 0.003 / 0.015
//   Opus 4.7    $5 / $25  par million → 0.005 / 0.025
// ⚠️ Opus était facturé ici 0.015 / 0.06, soit le tarif de l'ancien Opus 4.1
// ($15/$75 par million). Depuis Opus 4.5 le tarif est $5/$25 : le coût Opus
// enregistré dans /admin était donc surévalué de 3× en entrée et 2,4× en sortie.
const MODELS = {
  haiku:  { id: 'claude-haiku-4-5',  thinking: null,                  effort: null,    in: 0.001, out: 0.005 },
  sonnet: { id: 'claude-sonnet-4-6', thinking: { type: 'adaptive' },  effort: null,    in: 0.003, out: 0.015 },
  opus:   { id: 'claude-opus-4-7',   thinking: { type: 'adaptive' },  effort: 'high',  in: 0.005, out: 0.025 },
};

// ── Prompt caching : multiplicateurs appliqués au prix d'ENTRÉE du modèle ──
// Lecture de cache ≈ 0,1× ; écriture ≈ 1,25× en TTL 5 min et 2× en TTL 1 h.
// Le prompt système est mis en cache avec ttl:'1h' (voir cache_control plus bas),
// donc l'écriture se facture 2×.
// Ces tokens ne sont PAS inclus dans `usage.input_tokens` (qui ne compte que le
// résidu non caché) : sans les facturer explicitement, le prompt système —
// l'essentiel de l'entrée — n'apparaissait nulle part dans le coût enregistré.
const CACHE_READ_MULT = 0.1;
const CACHE_WRITE_MULT = 2.0; // TTL 1h

// Heuristique : qualité d'abord. Routage selon plan + Aperçu Premium pour les nouveaux.
// 1. Méta-questions courtes → DeepSeek/Haiku (zéro coût, zéro perte qualité)
// 2. Subscribers (Beit Midrash+) → Opus toujours
// 3. Khavroutha → Opus sur halakhique pointu, Sonnet ailleurs
// 4. Free/anonyme avec previewUsed < 3 → Aperçu Premium Opus (compte à vie)
// 5. Free/anonyme après Aperçu → Sonnet (qualité standard)
// 6. forceOpus = perk admin manuel : Opus sur tout (sauf méta)
// aperçuBlocked = caps IP ou global atteints (anti-abus) → on dégrade vers Sonnet
// Liste blanche des ouvertures purement conversationnelles : salutations,
// remerciements, « tu es qui », « comment ça marche », acquiescements, adieux.
// Le motif est ANCRÉ (^…$) : la chaîne entière doit correspondre. « bonjour, je
// peux réchauffer un plat ? » n'est donc PAS méta et suit le chemin normal —
// c'est le sens de sécurité voulu : un faux négatif coûte quelques centimes,
// un faux positif fait répondre de la halakha sans aucun garde-fou.
const META_PATTERNS = new RegExp('^(?:' + [
  // Salutations
  '(?:re)?bonjour(?: daat)?', 'bonsoir', 'bonne (?:journee|soiree|nuit)',
  'salut(?: daat)?', 'coucou', 'hello', 'hi', 'hey', '(?:shalom|chalom|sholom)(?: aleikhem)?',
  '(?:shabbat|chabbat) (?:shalom|chalom)', 'boker tov', 'erev tov',
  // Remerciements
  'merci(?: beaucoup| bien| infiniment| a toi)?', 'todah?(?: raba)?', 'thanks', 'thank you',
  'yasher koah', 'yaacher koah',
  // Identité / capacités
  'qui (?:es|est)[- ]?tu', '(?:tu es|t es|vous etes) qui', 'tu es quoi',
  "c est quoi (?:daat|daat torah|ce site|ce chat)", 'presente toi', 'tu sers a quoi',
  'que sais[- ]?tu faire', 'qu est[- ]?ce que tu sais faire', 'tu fais quoi',
  'qui te supervise', 'tu es une ia', 'tu es un robot',
  // Fonctionnement
  'comment (?:ca|cela) (?:marche|fonctionne)', '(?:ca|cela) (?:marche|fonctionne) comment',
  'comment (?:t|tu) utilise[rs]?', 'comment utiliser', 'comment ca se passe',
  // Politesse / acquiescement
  'comment (?:ca va|vas[- ]?tu|allez[- ]?vous)', 'ca va(?: bien)?', 'ca roule',
  'ok(?:ay)?', 'd ?accord', 'super', 'parfait', 'genial', 'bravo', 'top', 'nickel',
  'oui', 'non', 'tres bien', 'compris',
  // Fin de conversation / tests
  'au revoir', 'a bientot', 'bonne continuation', 'bye', 'test', 'essai',
].join('|') + ')$');

function isConversationalMeta(text) {
  const n = String(text || '')
    .toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9 -]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  if (!n) return false;
  return META_PATTERNS.test(n);
}

function pickModel(messages, hint, plan, previewUsed, aperçuBlocked, forceOpus) {
  // Hint explicite du client (ex: depuis une page Lamdan/Synthèse) — gagne toujours
  if (hint === 'opus' || hint === 'sonnet' || hint === 'haiku') return MODELS[hint];

  const lastUser = [...messages].reverse().find(m => m.role === 'user');
  const text = (lastUser?.content || '').toString().trim();
  const lower = text.toLowerCase();

  // 1. Méta-questions très courtes — toujours DeepSeek/Haiku (toutes catégories d'users)
  const isFirstQuestion = messages.length <= 1;
  // Élargi : ajout des termes de minhag, fêtes, rituels et concepts Habad/hassidiques
  // qui auparavant tombaient sous le seuil de 40 chars → routés vers Haiku par erreur.
  const halakhicHint = /shab|kasher|kasher|tefil|tznio|mouk|hila|sefer|torah|halakh|halacha|halaha|halaja|seif|siman|guemar|mishna|talmud|cohen|brah|berakh|nidda|kashr|peot|tsitsit|loulav|souka|sukka|mezou|tefil|shem|shabb|peah|maase|mitsv|mitzv|minhag|minag|habad|chabad|loubavitch|lubavitch|sefarad|séfarad|sfarad|ashken|ashkenaz|yemen|yémen|marocain|breslov|breslav|chitah|shitah|chitta|pesak|psak|posek|havdal|kiddush|kiddoush|qiddush|besamim|chofar|shofar|matza|matzo|hametz|hamets|pessah|pessach|pesah|rosh.?hashana|kippour|kippur|souccot|sukkot|hanouca|hanouka|hanukkah|chavouot|shavuot|pourim|purim|sicha|sichot|sihot|maamar|tanya|rebbe|admour|igrot|nigleh|nistar/i;
  // Détection MÉTA par LISTE BLANCHE (voir isConversationalMeta).
  // Auparavant : « premier message < 40 caractères ET aucun mot-clé halakhique »
  // — une définition par la NÉGATIVE. Toute question halakhique dont le
  // vocabulaire manquait à la liste partait vers DeepSeek : sans prompt système,
  // sans corpus, sans garde-fou, et la réponse était mise en cache 30 jours.
  // « C'est quoi le borer ? », « Quand allumer les bougies ? », « Trier les
  // aliments ? » passaient toutes par là. On ne court-circuite désormais que ce
  // qu'on reconnaît explicitement comme conversationnel ; dans le doute, la
  // question suit le chemin normal (corpus + prompt système complet).
  const isMetaQuestion = isFirstQuestion && text.length < 80
    && isConversationalMeta(text) && !halakhicHint.test(lower);
  if (isMetaQuestion) {
    return { ...MODELS.haiku, _meta: true };
  }

  // 2. Force Opus pour les users privilégiés (perk admin)
  if (forceOpus) return MODELS.opus;

  // 3. Abonnés "Beit Midrash et plus" : Opus toujours
  if (ALWAYS_OPUS_PLANS.has(plan)) return MODELS.opus;

  // 4. Aperçu Premium : free/anonyme avec compteur lifetime < 3 → Opus
  // Bloqué si IP a déjà servi 3 Aperçu aujourd'hui, ou si le quota global du jour est atteint
  if (!SUBSCRIBER_PLANS.has(plan) && previewUsed < PREVIEW_OPUS_LIMIT && !aperçuBlocked) {
    // Aperçu : Opus en effort 'medium' (TTFB plus court). Les abonnés payants
    // gardent 'high' (promesse « payant = profondeur Opus complète »).
    return { ...MODELS.opus, _aperçu: true, effort: 'medium' };
  }

  // 5. Khavroutha : Opus sur halakhique pointu uniquement
  // (idem que Sonnet/Opus auto, mais on garde la même heuristique pour ne pas spoiler)

  // 6. Triggers Opus — TOUT ce qui touche au halakhique pointu, citations, synthèse
  const opusKeywords = [
    // Lamdan / niveaux d'analyse
    'lamdan', 'synthèse', 'synthese', 'analyse', 'analyser', 'approfondir',
    'profondeur', 'compare', 'comparer', 'débat', 'debat', 'controverse',
    'machloket', 'mahloket', 'machaloket', 'plusieurs opinions', 'différentes opinions',
    // Périodes & sources
    'rishonim', 'aharonim', 'ahronim', 'guemara', 'gemara', 'talmud', 'tossafot',
    'tosafot', 'mishna', 'midrash', 'baraita', 'beraita', 'yerushalmi',
    // Poskim majeurs
    'rambam', 'ramban', 'rashba', 'ritva', 'rivash', 'rosh', 'rashi',
    'tur', 'beit yosef', 'shulchan aroukh', 'choulhan aroukh', 'choul\'han aroukh',
    'rama', 'rema', 'shach', 'taz', "ba'h", 'magen avraham', 'mishna berura',
    'biur halakha', 'pri megadim', 'shaagat aryeh', 'noda biyhuda', 'noda biyhouda',
    'kaf hahaim', 'ben ish hai', 'yabia omer', 'igrot moshe', 'minhat itzhak',
    "shulchan aroukh harav", 'admour hazaken', "ba'al hatanya", 'baal hatanya',
    'arouh hashulchan', 'kitsour shoulhan',
    // Concepts halakhiques denses
    'safek', 'sfeka', 'beriah', 'bittul', 'mouktsé', 'mouktse', 'mouqtse',
    'derabbanan', "d'oraita", 'doraita', 'kavanah', 'shogueg', 'mezid',
  ];
  if (opusKeywords.some(k => lower.includes(k))) return MODELS.opus;

  // 7. Citations hébraïques significatives (> 25 caractères) → souvent une source à analyser → Opus
  const heCount = (text.match(/[֐-׿]/g) || []).length;
  if (heCount > 25) return MODELS.opus;

  // 8. Par défaut : Sonnet 4.6 — qualité quasi équivalente à Opus pour le grand public,
  //    5× moins cher. Bon compromis qualité/coût.
  // Sur les users free post-Aperçu, on indique _would_use_opus si la question aurait
  // mérité Opus côté abonné — pour afficher le bandeau "aurait été Opus" côté client.
  if (!SUBSCRIBER_PLANS.has(plan)) {
    return { ...MODELS.sonnet, _standard_free: true };
  }
  return MODELS.sonnet;
}

// ── Plans, limites quotidiennes & mensuelles ──────────────────────────────
// Aperçu Premium : 3 questions Opus à vie offertes aux nouveaux comptes (kavod ha-mehadech)
const PREVIEW_OPUS_LIMIT = 3;
// Anti-abus : on plafonne aussi l'Aperçu par IP/jour et globalement par jour.
// Sans ces caps, clear-cookies + incognito = nouveau guest_id → 3 Aperçu de plus,
// répétable à l'infini. Avec : 3 Aperçu/IP/jour MAX (toutes guestIds confondues)
// et 100 Aperçu/jour MAX sur la planète (≈ 15 € de coût Opus pire cas).
const PREVIEW_IP_DAILY_LIMIT = 3;
const PREVIEW_GLOBAL_DAILY_LIMIT = 100;

// NB : ces limites ne s'appliquent qu'aux questions IA (Sonnet/Opus). Les
// questions couvertes par le corpus du Rav (corpus-first) sont GRATUITES et
// ILLIMITÉES pour tout le monde — elles ne décomptent pas ces quotas.
//
// CADENCE : TOUS les plans sont gouvernés au MOIS (une seule jauge lisible).
// Le cap quotidien est neutralisé partout (9999) → seul le mensuel mord. Le
// plafond mensuel borne le coût maximal → c'est lui qui garantit la marge.
//
// PROFIT GARANTI + AUCUN ILLIMITÉ : chaque plafond payant est calibré pour que,
// même si 100 % des questions étaient les plus lourdes possibles, le coût reste
// SOUS la recette. Pire cas recalculé (07/2026, tarifs corrigés ET tokens de
// cache comptés) : ~0,43 €/question Opus — 7 itérations, 12 outils, sortie au
// plafond, cache froid.
//   khavroutha 8 €   →  12 × 0,43 =  5,18 € (marge garantie ≥  2,82 €)
//   beit_midrash 25 €→  40 × 0,43 = 17,26 € (≥  7,74 €)
//   beit_midrash+ 50€→  80 × 0,43 = 34,51 € (≥ 15,49 €)
//   yeshiva 100 €    → 160 × 0,43 = 69,03 € (≥ 30,97 €)
//
// L'estimation précédente (0,55 €) reposait sur un tarif Opus erroné et ignorait
// les tokens de cache ; les deux erreurs se compensaient et le résultat était
// PLUS prudent que la réalité. Les plafonds n'ont donc jamais été à risque et
// restent INCHANGÉS.
//
// ⚠️ NE PAS recopier ces chiffres à la main — ils redeviendront faux au prochain
// changement de tarif. Ils sont recalculés depuis les constantes réelles par :
//     node scripts/cout-question.js
// (coûts en $, recettes en €, taux de change explicite via --eur).
const DAILY_LIMITS = {
  anonymous:      9999,        // gouverné au mois (voir MONTHLY_LIMITS)
  free:           9999,
  khavroutha:     9999,
  beit_midrash:   9999,
  beit_midrash_plus: 9999,
  yeshiva:        9999,
  lifetime:       9999,
  premium:        9999,
};

const MONTHLY_LIMITS = {
  anonymous:         3,        // dégustation — pousse à créer un compte
  free:             10,        // compte email (OTP) — 10 questions IA/mois (Sonnet)
  khavroutha:       12,        // soutien 8 €/mois   — Opus (marge garantie ≥ 1,40 €)
  beit_midrash:     40,        // soutien 25 €/mois  — Opus (≥ 3 €)
  beit_midrash_plus: 80,       // soutien 50 €/mois  — Opus (≥ 6 €)
  yeshiva:         160,        // soutien 100 €/mois — Opus (≥ 12 €)
  lifetime:         25,        // don unique 500 € — 25 Opus/mois à vie (~3 ans avant
                               // d'atteindre 500 € même en usage max → jamais illimité)
  premium:         160,        // ancien plan « illimité » → plafonné au niveau Yeshiva
};

// Plans payants (soutien récurrent ou don unique lifetime)
const SUBSCRIBER_PLANS = new Set(['khavroutha', 'beit_midrash', 'beit_midrash_plus', 'yeshiva', 'lifetime', 'premium']);
// Plans qui reçoivent Opus TOUJOURS (sauf méta-question triviale type "bonjour").
// PROMESSE PRODUIT : celui qui paie reçoit la meilleure qualité (Opus) pendant toute
// la durée de son abonnement — c'est ce que promet /soutenir ("accès aux réponses Opus").
// On y met donc TOUS les plans payants. Un abonné ne doit jamais recevoir du Sonnet sur
// une question halakhique simplement parce qu'elle ne contient pas de mot-clé "pointu".
const ALWAYS_OPUS_PLANS = new Set(SUBSCRIBER_PLANS);

const HELLOASSO_URL = 'https://www.helloasso.com/associations/association-hessed/formulaires/9';
const SOUTENIR_URL = '/soutenir.html';
const GUEST_COOKIE = 'daat_guest_id';

// ── Helpers identité ───────────────────────────────────────────────────────

function readCookie(req, name) {
  const header = req.headers.cookie || '';
  for (const pair of header.split(';')) {
    const idx = pair.indexOf('=');
    if (idx < 0) continue;
    const k = pair.slice(0, idx).trim();
    if (k === name) return decodeURIComponent(pair.slice(idx + 1).trim());
  }
  return null;
}

function genGuestId() {
  // UUID v4 simplifié — pas besoin de crypto fort, c'est juste un identifiant
  return 'guest_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 10);
}

// ── Cache des méta-réponses ────────────────────────────────────────────────
// "bonjour", "merci", "tu es qui", "comment ça marche" sont quasi-déterministes.
// On normalise (minuscule, sans ponctuation, espaces compactés) puis on fait un
// exact-match en KV. Un hit = 0 token LLM. TTL 14j (assez stable, refresh régulier).
// Version dans la clé : bumper METÀ_CACHE_VERSION invalide tout le cache d'un coup
// (utile si on change le ton/contenu des réponses méta dans le system prompt).
const META_CACHE_VERSION = 'v1';
const META_CACHE_TTL = 14 * 24 * 60 * 60;
function metaCacheKey(text) {
  const norm = String(text || '')
    .toLowerCase()
    .trim()
    .replace(/[!?.,;:'"«»()\[\]{}]/g, '')
    .replace(/\s+/g, ' ')
    .slice(0, 80);
  return `meta-cache:${META_CACHE_VERSION}:${norm}`;
}

// Renvoie { userId, plan, isGuest, guestIdSetCookie, forceOpus, previewUsed, planExpires }
async function identifyUser(req) {
  const user = getUserFromRequest(req);
  if (user?.email) {
    const [plan, forceOpusRaw, previewRaw, expiresRaw] = await Promise.all([
      kv.get(`user:plan:${user.email}`),
      kv.get(`user:force_opus:${user.email}`),
      kv.get(`user:preview_used:${user.email}`),
      kv.get(`user:plan_expires:${user.email}`),
    ]);
    // Vérif expiration : si plan payant expiré → downgrade vers free.
    // Comparaison de chaînes YYYY-MM-DD (les deux côtés sont dans ce format) :
    // indépendante du fuseau horaire et INCLUSIVE du jour d'expiration stocké
    // (l'abonné garde Opus jusqu'à la fin de son dernier jour, pas ~24h trop tôt).
    let effectivePlan = plan || 'free';
    if (SUBSCRIBER_PLANS.has(effectivePlan) && effectivePlan !== 'lifetime' && expiresRaw) {
      const todayStr = new Date().toISOString().slice(0, 10);
      const expiresStr = String(expiresRaw).slice(0, 10);
      if (todayStr > expiresStr) {
        effectivePlan = 'free';
      }
    }
    return {
      userId: user.email,
      plan: effectivePlan,
      isGuest: false,
      guestIdSetCookie: null,
      forceOpus: Boolean(forceOpusRaw),
      previewUsed: parseInt(previewRaw || '0', 10),
      planExpires: expiresRaw || null,
    };
  }
  // Anonyme — lire/créer guest_id
  let guestId = readCookie(req, GUEST_COOKIE);
  let setCookie = null;
  if (!guestId || !guestId.startsWith('guest_')) {
    guestId = genGuestId();
    setCookie = `${GUEST_COOKIE}=${encodeURIComponent(guestId)}; Path=/; HttpOnly; Secure; SameSite=None; Max-Age=${365 * 24 * 60 * 60}`;
  }
  const previewRaw = await kv.get(`user:preview_used:${guestId}`);
  return {
    userId: guestId,
    plan: 'anonymous',
    isGuest: true,
    guestIdSetCookie: setCookie,
    forceOpus: false,
    previewUsed: parseInt(previewRaw || '0', 10),
    planExpires: null,
  };
}

// Map tool name → executor
const TOOL_EXECUTORS = {
  daat_search_mareh_mekomot: executeMarehMekomotTool,
  daat_get_mareh_mekomot: executeMarehMekomotTool,
  daat_search_corpus: executeCorpusTool,
  daat_get_content: executeCorpusTool,
  sefaria_get_text: executeSefariaTool,
  sefaria_search: executeSefariaTool,
};

// ── Service d'une réponse corpus (cache KV → sinon reformulation Haiku) ──────
// Utilisé à DEUX endroits :
//  1. corpus-first du flux normal (avant Sonnet/Opus)
//  2. sauvetage à quota épuisé : le corpus du Rav reste ouvert même quand la
//     limite quotidienne/mensuelle est atteinte (les quotas ne rationnent que l'IA)
// `cs` est le résultat (non vide) de searchShabbatCorpus — la recherche reste chez
// l'appelant car le seuil varie (normal / strongOnly / rescue).
// Renvoie true si une réponse a été streamée (res.end() fait) ; false si rien n'a
// été écrit (l'appelant reprend son flux : Claude, ou la réponse 429).
async function serveCorpusAnswer({ req, res, cs, section, lastUserText, userId, isGuest, plan, rateKey = null, monthRateKey = null, doneExtra = {}, allowRawFallback = false }) {
  const top = cs.results[0];
  const others = cs.results.slice(1);
  const subs = top.subsection ? ` · ${top.subsection}` : '';
  const corpusSource = {
    siman: top.siman,
    simanTitle: top.simanTitle,
    sectionTitle: top.sectionTitle,
    subsection: top.subsection,
    sourceUrl: top.sourceUrl,
    score: parseFloat(top.score.toFixed(2)),
  };
  // En mode sauvetage les en-têtes SSE n'ont pas encore été posés (le flux normal
  // les pose avant rate_info). setHeader est inoffensif tant que rien n'est écrit :
  // si on ressort en false sans avoir écrit, l'appelant peut encore répondre 429 JSON.
  const ensureSse = () => {
    if (!res.headersSent) {
      res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
      res.setHeader('Cache-Control', 'no-cache, no-transform');
      res.setHeader('Connection', 'keep-alive');
      res.setHeader('X-Accel-Buffering', 'no');
    }
  };

  // ── Cache des reformulations : même question déjà répondue → 0 token LLM ──
  // Le lookup se fait APRÈS le match BM25 : un hit cache passe donc par les
  // mêmes garde-fous (strict, minScore, section) que la génération d'origine.
  // La clé ignore le bloc de profil : sinon la même question posée en 1re et en
  // 2e position produit deux clés différentes et le cache ne sert jamais.
  // Le profil sort de la RECHERCHE mais reste dans le PROMPT : sa signature doit
  // donc rester dans la clé, sinon un ashkénaze anglophone et un séfarade
  // francophone partagent la même réponse pendant 30 jours.
  const corpusKvKey = corpusCacheKey(
    stripProfileBlock(lastUserText),
    { section, lang: profileSignature(lastUserText) || 'fr' },
  );
  let cachedCorpus = null;
  try {
    const raw = await kv.get(corpusKvKey);
    // Le cache doit porter sur le MÊME siman que la recherche vient de trouver.
    // Sinon un texte mis en cache il y a 30 jours pour un autre siman est servi
    // sous la référence « Source : Siman X » calculée maintenant — une réponse
    // juste sous une source fausse, ou l'inverse. La clé de cache est dérivée du
    // texte de la question, pas du résultat : les deux peuvent diverger dès que
    // le corpus change (il change à chaque déploiement).
    // Le cache doit porter sur le MÊME EXTRAIT que la recherche vient de trouver.
    // La clé est dérivée du TEXTE de la question, pas du résultat : les deux
    // divergent dès que le corpus ou le moteur changent — c'est-à-dire à chaque
    // déploiement. Sans ce contrôle, un texte gardé 30 jours était servi sous la
    // référence « Source : Siman X » calculée maintenant : une réponse juste sous
    // une source fausse. Contrôler l'id du chunk (et pas seulement le siman)
    // invalide exactement ce qui a changé, sans purge globale — le corpus est
    // enrichi en continu, une purge à chaque déploiement coûterait le cache entier.
    // Les entrées écrites avant ce contrôle n'ont pas de chunkId : on retombe
    // alors sur le siman seul plutôt que de tout invalider.
    if (raw && typeof raw === 'object' && typeof raw.text === 'string' && raw.text.length > 50
        && String(raw.siman) === String(top.siman)
        // Exigence STRICTE de l'id d'extrait. La clause de compatibilité
        // « chunkId absent → on accepte » n'a plus d'objet (le préfixage des ids
        // a rendu toute entrée antérieure non concordante) et constituait un
        // risque latent : une réponse mise en cache AVANT la propagation de la
        // réserve « hors corpus, à vérifier » aurait pu être resservie sans elle.
        && raw.chunkId === top.id
        // ⚠️ La réserve du Rav est une propriété de la GÉNÉRATION, pas seulement
        // de l'extrait. Une réponse mise en cache avant que la réserve ne soit
        // propagée porte le bon extrait mais PAS l'avertissement : mesuré en
        // production, « c'est permis de manger de la viande et du fromage » a été
        // resservi sans la mise en garde « à confirmer auprès d'un Rav ». On
        // n'accepte donc le cache que si son état de réserve est identique — et
        // jamais du tout pour un extrait sous réserve dont le texte ne la porte pas.
        && Boolean(raw.caveat) === Boolean(top.caveat)
        && (!top.caveat || /hors corpus|à vérifier|טעון בדיקה|to be verified/i.test(raw.text))) {
      cachedCorpus = raw;
    }
  } catch (_) {}

  if (cachedCorpus) {
    ensureSse();
    const CHUNK = 48;
    for (let i = 0; i < cachedCorpus.text.length; i += CHUNK) {
      res.write(`data: ${JSON.stringify({ type: 'text', delta: cachedCorpus.text.slice(i, i + CHUNK) })}\n\n`);
    }
    res.write(`data: ${JSON.stringify({
      type: 'done',
      stop_reason: 'end_turn',
      iterations: 1,
      usage: { input_tokens: 0, output_tokens: 0 },
      provider: 'corpus-cache',
      ...doneExtra,
      corpus_source: corpusSource,
    })}\n\n`);
    // Gratuit : ni coût, ni décompte de quota. On trace quand même l'usage.
    try {
      await kv.lpush('logs:usage', JSON.stringify({
        ts: new Date().toISOString(),
        user: userId, is_guest: isGuest, plan,
        tokens_in: 0, tokens_out: 0, cost_usd: 0,
        provider: 'corpus-cache', model: 'cache',
        iterations: 1, stop_reason: 'end_turn',
        corpus_siman: top.siman, corpus_score: top.score,
      }));
      await kv.ltrim('logs:usage', 0, 499);
      await kv.sadd('users:known', userId);
      console.log(`[chat.js] corpus-cache HIT: ${userId} siman-${top.siman} "${String(lastUserText).slice(0, 40)}" ($0)`);
    } catch (err) {
      console.error('[chat.js] corpus-cache tracking error:', err?.message || err);
    }
    res.end();
    return true;
  }

  // Le corpus couvre QUATRE domaines, pas deux : OH quotidien (1-185), OH Shabbat
  // (242-365), YD Issour ve-Heter (87-118), YD Nidah (183-200). Cadrer le prompt
  // sur la seule `section` annonçait « les hilkhot Shabbat » pour les 9 241 chunks
  // du quotidien et « cacheroute » pour toute la nidah : Haiku reformulait alors
  // un extrait de tefila comme s'il s'agissait d'une question de Shabbat.
  // On dérive donc le domaine du siman RÉELLEMENT servi.
  const topNum = Number(top.siman);
  const corpusDom = section === 'yoreh-deah'
    ? (topNum >= 183
      ? { d: 'les hilkhot Nidah / Taharat haMishpaha (pureté familiale)',
          t: 'vesatot, ketamim, harhakot, hefsek tahara, chiva nekiyim, tevila',
          p: 'le principe halakhique' }
      : { d: 'les hilkhot Issour ve-Heter (cacheroute : bassar be-halav, taarovot…)',
          t: 'bassar be-halav, taarovet, ben yomo, nat bar nat',
          p: 'le principe halakhique' })
    : (topNum >= 242 && topNum <= 365
      ? { d: 'les hilkhot Shabbat',
          t: 'borer, bishoul, mouktsé',
          p: 'la mélakha (ou le principe halakhique)' }
      : { d: "les hilkhot de la journée du juif (Orah Haïm : netilat yadaïm, tsitsit, tefilin, birkot hachahar, keriat chema, tefila, berakhot, birkat hamazon…)",
          t: 'tsitsit, tefilin, netilat yadaïm, berakha, kavana',
          p: 'le principe halakhique' });
  const corpusDomain = corpusDom.d;
  const corpusTerms = corpusDom.t;
  const corpusSystem = `Tu es Daat, l'assistant halakhique de DAAT — site d'étude du Rav Yossef Haim Samama.

CONTEXTE : tu reçois une question d'utilisateur sur ${corpusDomain} et UN EXTRAIT précis du corpus (écrit par le Rav) qui répond à cette question.

TA MISSION : donner une réponse claire, complète et engageante, fidèle à l'extrait. L'utilisateur doit avoir la réponse dès la première ligne, puis comprendre pourquoi.

STRUCTURE ATTENDUE :
1. **Phrase d'accroche** (1re ligne) : la réponse directe, ATTRIBUÉE au corpus — ce que le Rav écrit, pas ce que TU autorises ("D'après le corpus du Rav, c'est permis lorsque…", "Non : il y a là un problème de …", "Ça dépend : si …, alors …"). L'accroche seule doit déjà répondre.
2. **Raisonnement** en 2-4 phrases : ${corpusDom.p === 'la mélakha (ou le principe halakhique)' ? 'quelle est la mélakha (ou le principe halakhique)' : 'quel est le principe halakhique'} en jeu, la logique du psak, les sources ou opinions clés si l'extrait les mentionne.
3. **Cas particuliers ou nuances** : uniquement s'ils sont dans l'extrait (ne pas extrapoler).
4. **Source finale** au format exact : *Source : Siman X · [titre de section]*

${top.caveat ? `
⚠️ RÉSERVE DE L'AUTEUR — OBLIGATOIRE : le Rav a lui-même marqué cet extrait « hors corpus, à vérifier ». Tu DOIS commencer ta réponse par la ligne exacte :
> ⚠️ Le Rav signale que ce passage est **hors corpus et à vérifier** — à lire comme une orientation, pas comme une source établie.
Puis répondre normalement, sans jamais présenter ce contenu comme tranché.
` : ''}
RÈGLES STRICTES :
- RESTE FIDÈLE à l'extrait. N'invente AUCUNE halakha qui n'y est pas explicitement.
- Termine TOUJOURS ta réponse par la ligne source. Ne coupe jamais avant elle — elle est la signature du psak.
- Si l'extrait n'aborde pas vraiment la question : « L'extrait du corpus traite de [sujet réel], mais ta question porte sur [Y] — pour une réflexion précise sur ce point, repose la question en mode étendu. » (puis source).
- **JAMAIS d'autorisation personnelle.** Tu peux RAPPORTER ce qu'écrit le corpus (« le Rav écrit que … est permis lorsque … »), mais jamais le convertir en feu vert pour cette personne (« tu peux », « pas de problème pour toi », « tu es dans la zone permissive »). Tu rapportes une source, tu ne donnes pas de psak.
- **N'extrapole jamais de l'extrait au cas de l'utilisateur** : son cas comporte des détails que l'extrait ne couvre pas. Si sa situation ajoute une condition absente de l'extrait, dis-le au lieu de trancher.
- Dès que la question porte sur un cas CONCRET, termine (AVANT la ligne source) par : « Pour ton cas précis, c'est à ton Rav de trancher. »
- **Glose de l'hébreu (sauf si tu réponds en hébreu)** : à sa **première occurrence**, chaque mot, terme ou citation en hébreu (${corpusTerms}) est **immédiatement suivi de sa traduction** (et d'une translittération pour un terme isolé), entre parenthèses, pour le lecteur qui ne lit pas l'hébreu — ex. : מוקצה (mouktsé — objet qu'on ne peut pas déplacer Shabbat) ; נר (ner — lampe). Inutile de re-gloser un mot déjà expliqué juste au-dessus ; ne laisse jamais un mot hébreu **non encore traduit** seul.
- Ton conversationnel et pédagogique, comme si tu expliquais à un ami curieux. Pas de listes à puces sauf vraie nécessité. Pas de markdown lourd.
- Ne dis JAMAIS que tu reformules un extrait — parle directement du sujet.`;

  let corpusUserMsg = `QUESTION DE L'UTILISATEUR :\n${lastUserText}\n\n`;
  corpusUserMsg += `EXTRAIT DU CORPUS (Siman ${top.siman} — ${top.simanTitle}${top.levelLabel ? ` · niveau ${top.levelLabel}` : ''} · ${top.sectionTitle}${subs}) :\n${top.text.trim()}`;
  if (others.length > 0) {
    corpusUserMsg += `\n\nAUTRES EXTRAITS PERTINENTS (en complément, plus faibles) :\n`;
    others.slice(0, 2).forEach((r, i) => {
      const ss = r.subsection ? ` · ${r.subsection}` : '';
      corpusUserMsg += `[${i + 1}] Siman ${r.siman} · ${r.sectionTitle}${ss} — ${r.text.trim().slice(0, 250)}…\n`;
    });
  }

  const corpusAbort = new AbortController();
  req.on('close', () => corpusAbort.abort());

  let corpusAnswer = '';
  let inTok = 0, outTok = 0;
  let corpusErrored = false;
  let corpusStopReason = null;
  // Budget de sortie : assez large pour accroche + raisonnement + nuances + source
  // sans jamais tronquer. Haiku 4.5 output ≈ $5/M tokens → 1200 tokens ≈ $0.006,
  // toujours 20× moins cher qu'Opus. Overridable via env pour ajuster sans deploy.
  const CORPUS_MAX_TOKENS = parseInt(process.env.CORPUS_MAX_TOKENS || '1600', 10);

  try {
    const stream = client.messages.stream({
      model: MODELS.haiku.id,
      max_tokens: CORPUS_MAX_TOKENS,
      system: corpusSystem,
      messages: [{ role: 'user', content: corpusUserMsg }],
    }, { signal: corpusAbort.signal });

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta?.type === 'text_delta') {
        const text = event.delta.text || '';
        if (text) {
          if (!corpusAnswer) ensureSse();
          corpusAnswer += text;
          res.write(`data: ${JSON.stringify({ type: 'text', delta: text })}\n\n`);
        }
      }
    }
    const final = await stream.finalMessage();
    if (final?.usage) {
      inTok = final.usage.input_tokens || 0;
      outTok = final.usage.output_tokens || 0;
    }
    corpusStopReason = final?.stop_reason || null;
    if (corpusStopReason === 'max_tokens') {
      console.warn(`[chat.js] corpus response TRUNCATED (hit max_tokens=${CORPUS_MAX_TOKENS}) siman-${top.siman} — consider bumping CORPUS_MAX_TOKENS`);
    }
  } catch (err) {
    corpusErrored = true;
    console.error('[chat.js] corpus Haiku error:', err?.message || err);
  }

  // Si la réponse a commencé à streamer, on doit la terminer proprement (impossible de fallback maintenant)
  if (corpusAnswer.length > 0) {
    const cost = (inTok * MODELS.haiku.in / 1000) + (outTok * MODELS.haiku.out / 1000);
    // Stream interrompu en cours OU cap max_tokens atteint : on signale
    // visiblement la coupure pour que l'utilisateur ne prenne pas une
    // réponse tronquée pour un psak complet.
    if (corpusErrored) {
      res.write(`data: ${JSON.stringify({ type: 'text', delta: '\n\n_(Réponse interrompue — repose ta question pour une réponse complète.)_' })}\n\n`);
    } else if (corpusStopReason === 'max_tokens') {
      res.write(`data: ${JSON.stringify({ type: 'text', delta: '\n\n_(Réponse tronquée par la limite de longueur — précise ta question pour la suite du raisonnement.)_' })}\n\n`);
    }
    res.write(`data: ${JSON.stringify({
      type: 'done',
      stop_reason: corpusErrored ? 'error' : (corpusStopReason || 'end_turn'),
      iterations: 1,
      usage: { input_tokens: inTok, output_tokens: outTok },
      provider: 'corpus-haiku',
      ...doneExtra,
      corpus_source: corpusSource,
    })}\n\n`);

    try {
      const todayKey = new Date().toISOString().slice(0, 10);
      const globalKey = `usage:global:${todayKey}`;
      const globalData = (await kv.get(globalKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
      await kv.set(globalKey, {
        tokens_in: globalData.tokens_in + inTok,
        tokens_out: globalData.tokens_out + outTok,
        cost_usd: parseFloat((globalData.cost_usd + cost).toFixed(6)),
        count: globalData.count + 1,
      });
      const userKey = `usage:${userId}:${todayKey}`;
      const userData = (await kv.get(userKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
      await kv.set(userKey, {
        tokens_in: userData.tokens_in + inTok,
        tokens_out: userData.tokens_out + outTok,
        cost_usd: parseFloat((userData.cost_usd + cost).toFixed(6)),
        count: userData.count + 1,
      });
      // Quota : par défaut, les réponses corpus NE décomptent PAS — le contenu
      // du corpus (écrit par le Rav) doit rester librement accessible à tous.
      // CORPUS_QUOTA_FREE=false pour rétablir le décompte si besoin (dans ce cas
      // le sauvetage à quota épuisé est désactivé et rateKey est bien fourni).
      // En cas d'erreur (réponse tronquée), on ne décompte jamais.
      if (process.env.CORPUS_QUOTA_FREE === 'false' && !corpusErrored && rateKey && monthRateKey) {
        await kv.incr(rateKey);
        const ttl = await kv.ttl(rateKey);
        if (ttl === -1 || ttl === -2) await kv.expire(rateKey, 24 * 60 * 60);
        await kv.incr(monthRateKey);
        const mttl = await kv.ttl(monthRateKey);
        if (mttl === -1 || mttl === -2) await kv.expire(monthRateKey, 35 * 24 * 60 * 60);
      }
      await kv.lpush('logs:usage', JSON.stringify({
        ts: new Date().toISOString(),
        user: userId, is_guest: isGuest, plan,
        tokens_in: inTok, tokens_out: outTok, cost_usd: cost,
        provider: 'corpus-haiku', model: MODELS.haiku.id,
        iterations: 1, stop_reason: corpusErrored ? 'error' : 'end_turn',
        corpus_siman: top.siman, corpus_score: top.score,
      }));
      await kv.ltrim('logs:usage', 0, 499);
      await kv.sadd('users:known', userId);
      // Mise en cache : uniquement les réponses complètes et saines.
      // Les prochains utilisateurs qui posent la même question → 0 €.
      if (!corpusErrored && corpusStopReason !== 'max_tokens' && corpusAnswer.length > 80) {
        await kv.set(corpusKvKey, { text: corpusAnswer, siman: top.siman, chunkId: top.id, caveat: Boolean(top.caveat) }, { ex: CORPUS_CACHE_TTL });
      }
      console.log(`[chat.js] corpus HIT: ${userId} siman-${top.siman} score=${top.score.toFixed(1)} +${inTok}in/${outTok}out ($${cost.toFixed(5)})`);
    } catch (err) {
      console.error('[chat.js] corpus usage tracking error:', err?.message || err);
    }

    res.end();
    return true;
  }
  // Aucune sortie streamée (erreur avant le premier token). Si l'appelant n'a
  // aucun autre recours (quota épuisé, budget Anthropic épuisé), on sert le texte
  // du Rav TEL QUEL, à coût nul : la promesse « le corpus du Rav reste consultable
  // sans limite » ne peut pas dépendre d'un appel payant. Sinon on rend la main.
  if (allowRawFallback) return serveRawCorpus({ res, cs, ensureSse, doneExtra, userId, plan, question: lastUserText, lang: req?.body?.lang });
  return false;
}

// ── Corpus BRUT, coût 0 € ───────────────────────────────────────────────────
// Dernier recours : les extraits du Rav, sans reformulation. Le cadrage est
// explicite — c'est une CITATION du corpus, jamais une réponse du chat, encore
// moins un psak. C'est ce qui permet au corpus de rester accessible quand plus
// aucun modèle n'est disponible.
// Cadrage du corpus brut — TRILINGUE. Le site est FR/HE/EN et les trois pages de
// chat postent sur la même API : servir l'avertissement « ce n'est pas un psak »
// en français à un lecteur hébréophone revient à ne pas l'avertir du tout, alors
// que le corps de l'extrait, lui, est souvent en hébreu et parfaitement lisible.
// ⚠️ Le texte ne promet PAS que l'extrait répond à la question : aucun modèle ne
// l'a lu. C'est une recherche par mots-clés, elle se trompe de sujet parfois — le
// dire est le seul garde-fou qui reste quand la reformulation est indisponible.
const RAW_CORPUS_I18N = {
  fr: {
    caveat: `> ⚠️ Le Rav a marqué ce passage **hors corpus, à vérifier** — orientation, pas source établie.\n\n`,
    head: `**Le modèle d'IA est momentanément indisponible.** Je ne peux donc ni lire ces passages ni vérifier qu'ils traitent bien de ton cas : voici, tel quel, ce que la recherche par mots-clés a rapproché de ta question. **Vérifie le titre ci-dessous avant de lire — il arrive que ce ne soit pas le bon sujet.** C'est une citation du corpus, pas une réponse rédigée, et surtout pas un psak.\n\n`,
    about: (h) => `> Cet extrait traite de : **${h.simanTitle || 'Siman ' + h.siman}**${h.sectionTitle ? ` — ${h.sectionTitle}` : ''}\n\n`,
    src: (h) => `\n\n*Source : Siman ${h.siman}${h.levelLabel ? ' · ' + h.levelLabel : ''}*`,
    foot: `\n\nPour toute question **lema'assé**, adresse-toi à ton Rav.`,
  },
  he: {
    caveat: `> ⚠️ הרב ציין כי קטע זה **מחוץ לחומר, טעון בדיקה** — כיוון בלבד, לא מקור מבורר.\n\n`,
    head: `**מנוע הבינה המלאכותית אינו זמין כרגע.** לכן איני יכול לקרוא את הקטעים הללו ולא לוודא שהם אכן עוסקים בשאלתך: לפניך, כמות שהוא, מה שחיפוש המילים העלה. **בדוק את הכותרת שלהלן לפני הקריאה — לעתים אין זה הנושא הנכון.** זהו ציטוט מן החומר, לא תשובה ערוכה, ובוודאי לא פסק הלכה.\n\n`,
    // Titre HÉBREU (simanTitleHe est renseigné pour la totalité du corpus) : le
    // titre français inséré dans une phrase hébraïque bascule le rendu en LTR.
    about: (h) => `> קטע זה עוסק ב: **${h.simanTitleHe || h.simanTitle || 'סימן ' + h.siman}**\n\n`,
    src: (h) => `\n\n*מקור : סימן ${h.siman}${h.levelLabel ? ' · ' + h.levelLabel : ''}*`,
    foot: `\n\nלכל שאלה **למעשה**, יש לפנות לרב.`,
  },
  en: {
    caveat: `> ⚠️ The Rav marked this passage **outside the corpus, to be verified** — an orientation, not an established source.\n\n`,
    head: `**The AI model is temporarily unavailable.** I therefore cannot read these passages or verify that they address your case: here, as-is, is what the keyword search matched to your question. **Check the heading below before reading — it is sometimes not the right topic.** This is a quotation from the corpus, not a written answer, and certainly not a psak.\n\n`,
    about: (h) => `> This excerpt is about: **${h.simanTitle || 'Siman ' + h.siman}**${h.sectionTitle ? ` — ${h.sectionTitle}` : ''}\n\n`,
    src: (h) => `\n\n*Source: Siman ${h.siman}${h.levelLabel ? ' · ' + h.levelLabel : ''}*`,
    foot: `\n\nFor any practical question (**lema'asse**), please ask your Rav.`,
  },
};

// ⚠️ La langue DÉCLARÉE par le client fait foi : chat-he.html et chat-en.html
// envoient déjà `lang` dans le corps de la requête. La deviner alors qu'elle est
// transmise produisait des écarts (une question hébraïque courte, une question
// française contenant une citation en hébreu…). La détection ne sert plus que de
// repli, pour le widget et chat.html qui n'envoient rien.
function resolveLang(declared, text) {
  const d = String(declared || '').toLowerCase().slice(0, 2);
  if (d === 'he' || d === 'en' || d === 'fr') return d;
  return detectLang(text);
}

function detectLang(text) {
  const t = String(text || '');
  const he = (t.match(/[\u05d0-\u05ea]/g) || []).length;
  const lat = (t.match(/[a-zA-ZÀ-ÿ]/g) || []).length;
  if (he > 3 && he >= lat) return 'he';
  if (/[àâäéèêëïîôöùûüçœ]|\b(?:est-ce|puis-je|peut-on|quelle?|pourquoi|comment|dois-je|faut-il|je|mon|ma|des|une?)\b/i.test(t)) return 'fr';
  if (lat > 0 && /\b(?:the|is|are|can|what|when|how|do|does|my|a|an|to|with)\b/i.test(t)) return 'en';
  return 'fr';
}

async function serveRawCorpus({ res, cs, ensureSse, doneExtra = {}, userId, plan, question = '', lang = null }) {
  const hits = (cs?.results || []).slice(0, 2);
  if (!hits.length) return false;
  const top = hits[0];
  const L = RAW_CORPUS_I18N[resolveLang(lang, question)] || RAW_CORPUS_I18N.fr;
  const parts = [];
  parts.push(L.head);
  hits.forEach((h, i) => {
    if (i > 0) parts.push('\n\n---\n\n');
    parts.push(L.about(h));
    if (h.caveat) parts.push(L.caveat);
    // La sous-section porte parfois une réserve écrite par le Rav lui-même
    // (« hors corpus, à vérifier ») : la taire reviendrait à diffuser le tableau
    // sans la mise en garde qui l'accompagne.
    const sub = h.subsection ? ` · ${h.subsection}` : '';
    if (h.sectionTitle || sub) parts.push(`*${(h.sectionTitle || '').trim()}${sub}*\n\n`);
    parts.push(h.text);
    parts.push(L.src(h));
  });
  parts.push(L.foot);
  const text = parts.join('');
  ensureSse();
  const CH = 64;
  for (let i = 0; i < text.length; i += CH) {
    res.write(`data: ${JSON.stringify({ type: 'text', delta: text.slice(i, i + CH) })}\n\n`);
  }
  res.write(`data: ${JSON.stringify({
    type: 'done', stop_reason: 'end_turn', iterations: 1,
    usage: { input_tokens: 0, output_tokens: 0 },
    provider: 'corpus-raw',
    ...doneExtra,
    corpus_source: { siman: top.siman, simanTitle: top.simanTitle, sourceUrl: top.sourceUrl, score: top.score },
  })}\n\n`);
  try {
    await kv.lpush('logs:usage', JSON.stringify({
      ts: new Date().toISOString(), user: userId, plan,
      tokens_in: 0, tokens_out: 0, cost_usd: 0,
      provider: 'corpus-raw', model: 'none', iterations: 1, stop_reason: 'end_turn',
      corpus_siman: top.siman, corpus_score: top.score,
    }));
    await kv.ltrim('logs:usage', 0, 499);
  } catch (_) {}
  console.log(`[chat.js] corpus RAW (0 €): ${userId} siman-${top.siman}`);
  res.end();
  return true;
}

// ── Sauvetage corpus à quota épuisé ─────────────────────────────────────────
// Les quotas ne rationnent que l'IA générative : si la question matche le corpus,
// on la sert au lieu du 429. Renvoie true si servie. Désactivé si le corpus
// décompte les quotas (CORPUS_QUOTA_FREE=false) — le 429 redevient légitime.
async function tryCorpusRescue({ req, res, messages, section, userId, isGuest, plan, scope }) {
  if (process.env.CORPUS_FIRST_ENABLED === 'false') return false;
  if (process.env.CORPUS_QUOTA_FREE === 'false') return false;
  const lastUserMsg = [...messages].reverse().find(
    (m) => m && m.role === 'user' && typeof m.content === 'string' && m.content.length > 0 && m.content.length <= 2000
  );
  if (!lastUserMsg) return false;
  let cs = null;
  try {
    cs = searchShabbatCorpus(lastUserMsg.content, {
      limit: 3,
      minScore: parseFloat(process.env.CORPUS_MIN_SCORE || '8'),
      strict: true,
      section,
    });
  } catch (err) {
    console.error('[chat.js] corpus rescue search error:', err?.message || err);
    return false;
  }
  if (!cs || cs.results.length === 0) return false;
  console.log(`[chat.js] corpus RESCUE (${scope}): ${userId} plan=${plan} → siman-${cs.results[0].siman}`);
  return serveCorpusAnswer({
    req, res, cs, section,
    lastUserText: lastUserMsg.content,
    userId, isGuest, plan,
    doneExtra: { is_aperçu: false, quota_rescued: scope },
    // À quota épuisé, l'appelant n'a aucun autre recours : si Haiku échoue avant
    // le 1er token, le corpus brut vaut infiniment mieux qu'un paywall.
    allowRawFallback: true,
  });
}

export default async function handler(req, res) {
  // CORS — credentials:include nécessite une origin spécifique autorisée (jamais *).
  // On ne reflète l'origine + Allow-Credentials que si elle est sur l'allow-list,
  // sinon un site tiers pourrait dépenser le quota d'un utilisateur connecté.
  let anyTextSent = false; // hissé hors du try : le catch en a besoin (repli corpus brut)
  const origin = req.headers.origin;
  if (isAllowedOrigin(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Vary', 'Origin');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Méthode non autorisée — utilisez POST' });
  }

  try {
    const { messages } = req.body || {};
    // Section halakhique (section-aware) : 'yoreh-deah' active la surcharge YD,
    // sinon 'orach-chaim' par défaut (prompt de base inchangé).
    const section = (req.body && req.body.section === 'yoreh-deah') ? 'yoreh-deah' : 'orach-chaim';

    // Validation
    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: 'Le champ "messages" doit être un tableau non vide' });
    }

    // Identifier l'utilisateur (email connecté OU guest_id par cookie)
    const { userId, plan, isGuest, guestIdSetCookie, forceOpus, previewUsed, planExpires } = await identifyUser(req);
    const today = new Date().toISOString().slice(0, 10);
    const currentMonth = today.slice(0, 7); // YYYY-MM
    const clientIp = getClientIp(req);
    const rateKey = `rate:${userId}:${today}`;
    const monthRateKey = `rate-month:${userId}:${currentMonth}`;
    const previewIpKey = `preview-ip:${clientIp}:${today}`;
    // Plafond MENSUEL par IP pour les visiteurs non connectés. Sans lui, un client
    // qui ne renvoie pas le cookie `daat_guest_id` obtient un quota neuf à chaque
    // requête : l'IA générative devenait illimitée et gratuite pour qui savait le
    // faire. Le plafond est volontairement TRÈS supérieur au quota individuel
    // (3 questions/mois) afin de ne jamais gêner un foyer, une yéchiva ou un
    // réseau partagé : il ne rattrape que l'effacement répété du cookie.
    // ⚠️ Il ne ration que l'IA générative : le corpus du Rav reste servi par
    // tryCorpusRescue, appelé AVANT le 429 — la promesse « corpus illimité » tient.
    const anonIpMonthKey = `rate-month-ip:${clientIp}:${currentMonth}`;
    const previewGlobalKey = `preview-global:${today}`;
    const limit = DAILY_LIMITS[plan] || DAILY_LIMITS.anonymous;
    const monthLimit = MONTHLY_LIMITS[plan] || MONTHLY_LIMITS.anonymous;
    // Crédits Opus achetés (1€/q, 10€/10q) — clé `credits:email`. Anonymes : impossible.
    const creditsKey = isGuest ? null : `credits:${userId}`;
    const [currentCount, rawMonthCount, previewIpCount, previewGlobalCount, opusCredits, anonIpMonthCount] = await Promise.all([
      kv.get(rateKey).then(v => parseInt(v || '0', 10)),
      kv.get(monthRateKey).then(v => parseInt(v || '0', 10)),
      kv.get(previewIpKey).then(v => parseInt(v || '0', 10)),
      kv.get(previewGlobalKey).then(v => parseInt(v || '0', 10)),
      creditsKey ? kv.get(creditsKey).then(v => parseInt(v || '0', 10)) : Promise.resolve(0),
      isGuest && clientIp ? kv.get(anonIpMonthKey).then(v => parseInt(v || '0', 10)) : Promise.resolve(0),
    ]);
    // Pour un visiteur non connecté, le compteur retenu est le PLUS ÉLEVÉ des deux
    // (cookie ou IP) : effacer le cookie ne remet donc plus le compteur à zéro.
    // Un compte connecté est identifié par son email et n'est jamais concerné.
    const ipQuotaHit = isGuest && ANON_IP_MONTHLY_LIMIT > 0 && anonIpMonthCount >= ANON_IP_MONTHLY_LIMIT;
    const currentMonthCount = ipQuotaHit ? Math.max(rawMonthCount, monthLimit) : rawMonthCount;
    // Journal : sans lui, un faux positif est INVISIBLE en exploitation (les
    // statistiques admin ne lisent que le compteur par utilisateur).
    // Journal : sans lui, un faux positif est invisible en exploitation. L'adresse
    // est HACHÉE — un log Vercel n'a pas à contenir d'adresse en clair — et
    // l'alerte n'est émise qu'aux passages de seuil, pas à chaque requête.
    if (isGuest && clientIp && anonIpMonthCount >= ANON_IP_ALERT_AT
        && (ipQuotaHit || anonIpMonthCount % 10 === 0)) {
      const ipHash = createHash('sha256').update(String(clientIp)).digest('hex').slice(0, 10);
      console.warn(`[chat.js] ip:${ipHash} — ${anonIpMonthCount} questions ce mois (cookie ${rawMonthCount}) — ${ipQuotaHit ? 'BLOQUÉE' : 'observation'}`);
    }
    // Flag : true si cette requête sera payée par un crédit (= forcera Opus, décrémentera credits)
    let usingCredit = false;
    // Caps anti-abus : si l'IP a déjà servi 3 Aperçu aujourd'hui OU si le quota global
    // anonyme du jour est atteint, on désactive l'Aperçu (l'user passe en Sonnet).
    // Les abonnés ne sont pas concernés (Aperçu ne s'applique pas à eux).
    const aperçuBlocked = previewIpCount >= PREVIEW_IP_DAILY_LIMIT || previewGlobalCount >= PREVIEW_GLOBAL_DAILY_LIMIT;

    // Définir le cookie guest_id si nouveau visiteur
    if (guestIdSetCookie) {
      res.setHeader('Set-Cookie', guestIdSetCookie);
    }

    // Limite QUOTIDIENNE atteinte → on autorise si crédits Opus disponibles
    if (currentCount >= limit) {
      if (opusCredits > 0) {
        // Cet utilisateur paie cette question avec un crédit → Opus garanti, décrémenté au tracking
        usingCredit = true;
      } else {
        // Sauvetage corpus : les quotas ne rationnent que l'IA générative. Si la
        // question matche le corpus du Rav, on la sert (cache ou Haiku ~0.002 €)
        // au lieu du 429 — la promesse « corpus gratuit et illimité » tient
        // aussi à quota épuisé.
        if (await tryCorpusRescue({ req, res, messages, section, userId, isGuest, plan, scope: 'daily' })) {
          return;
        }
        const resetTime = new Date();
        resetTime.setDate(resetTime.getDate() + 1);
        resetTime.setHours(0, 0, 0, 0);
        return res.status(429).json({
          error: 'limit_reached',
          type: 'limit_reached',
          scope: 'daily',
          plan,
          count: currentCount,
          limit,
          is_guest: isGuest,
          credits: opusCredits, // 0 = aucun crédit
          reset_date: resetTime.toISOString(),
          helloasso_url: HELLOASSO_URL,
          soutenir_url: SOUTENIR_URL,
          // Gratuit/anonyme sont gouvernés au MOIS (daily neutralisé à 9999) : ce
          // gate quotidien ne se déclenche donc que pour les payants qui touchent
          // leur garde-fou anti-rafale. La branche invité reste par sécurité.
          message: isGuest
            ? `Tu as utilisé tes questions IA gratuites. Crée un compte gratuit pour ${MONTHLY_LIMITS.free} questions IA/mois — le corpus du Rav reste illimité.`
            : `Tu as posé beaucoup de questions aujourd'hui (${limit}). Reviens demain, ou continue tout de suite avec des crédits Opus (1 € = 1 question permanente). Le corpus du Rav reste consultable sans limite.`,
        });
      }
    }

    // Limite MENSUELLE atteinte — c'est LE gate actif (les caps quotidiens sont
    // neutralisés à 9999, donc le gate quotidien ci-dessus ne se déclenche jamais).
    if (currentMonthCount >= monthLimit) {
      // Crédits Opus achetés (1 € = 1 question, permanents) → on laisse passer en
      // Opus au lieu de bloquer. Décrémenté au tracking (usingCredit).
      if (opusCredits > 0) {
        usingCredit = true;
      } else {
      // Sinon : sauvetage corpus (le corpus du Rav reste ouvert malgré le quota).
      if (await tryCorpusRescue({ req, res, messages, section, userId, isGuest, plan, scope: 'monthly' })) {
        return;
      }
      const nextMonth = new Date();
      nextMonth.setMonth(nextMonth.getMonth() + 1);
      nextMonth.setDate(1);
      nextMonth.setHours(0, 0, 0, 0);
      // Message adapté au public. Dans tous les cas : le corpus du Rav reste
      // consultable sans limite, et le compteur repart le 1er du mois prochain.
      const monthlyMessage = ipQuotaHit
        // ⚠️ Message DISTINCT quand c'est le compteur par ADRESSE qui a bloqué :
        // dire « tu as utilisé tes 3 questions » à quelqu'un dont le compteur
        // personnel est à zéro est faux, et incompréhensible pour un élève d'une
        // salle d'étude où quelqu'un d'autre a consommé le contingent.
        ? `Beaucoup de questions ont déjà été posées ce mois-ci depuis ta connexion Internet (elle est peut-être partagée — salle d'étude, famille, réseau mobile). Crée un compte gratuit : ton quota devient personnel et ce plafond ne te concerne plus. Le corpus du Rav, lui, reste consultable sans limite.`
        : isGuest
        ? `Tu as utilisé tes ${monthLimit} questions IA gratuites du mois. Crée un compte gratuit pour passer à ${MONTHLY_LIMITS.free} questions IA/mois. Le corpus du Rav, lui, reste consultable sans limite — et le compteur repart le mois prochain.`
        : SUBSCRIBER_PLANS.has(plan)
          ? `Tu as atteint ton quota mensuel (${monthLimit} questions IA). Le corpus du Rav reste consultable sans limite ; le compteur repart le mois prochain. Pour un plafond plus élevé, passe à un niveau supérieur.`
          : `Tu as utilisé tes ${monthLimit} questions IA gratuites du mois. Le corpus du Rav reste consultable sans limite ; le compteur repart le mois prochain. Pour la profondeur (analyse Opus) sans attendre, soutiens DAAT — 1 € = 1 question permanente.`;
      return res.status(429).json({
        error: 'limit_reached',
        type: 'limit_reached',
        scope: ipQuotaHit ? 'monthly_ip' : 'monthly',
        plan,
        count: ipQuotaHit ? anonIpMonthCount : currentMonthCount,
        limit: monthLimit,
        is_guest: isGuest,
        reset_date: nextMonth.toISOString(),
        soutenir_url: SOUTENIR_URL,
        helloasso_url: HELLOASSO_URL,
        message: monthlyMessage,
      });
      }
    }

    for (const m of messages) {
      if (!m || typeof m !== 'object') {
        return res.status(400).json({ error: 'Format de message invalide' });
      }
      if (!['user', 'assistant'].includes(m.role)) {
        return res.status(400).json({ error: `Rôle invalide : ${m.role}` });
      }
      if (typeof m.content !== 'string' || m.content.length === 0) {
        return res.status(400).json({ error: 'Le contenu du message doit être une chaîne non vide' });
      }
      if (m.content.length > 10000) {
        return res.status(400).json({ error: 'Message trop long (max 10000 caractères)' });
      }
    }

    // Garder les N derniers tours (qualité = plus de contexte récent)
    const trimmedMessages = messages.slice(-HISTORY_TURNS);

    if (trimmedMessages[0].role !== 'user') {
      return res.status(400).json({ error: 'Le premier message doit être de l\'utilisateur' });
    }

    // Compaction des tours antérieurs via DeepSeek (uniquement si > HISTORY_TURNS).
    // Économie : évite de renvoyer 10 000+ tokens d'historique à Claude.
    // Si DeepSeek absent ou échoue : on n'injecte rien (Claude perd juste le contexte ancien).
    const olderTurns = messages.length > HISTORY_TURNS ? messages.slice(0, -HISTORY_TURNS) : [];
    let historySummary = null;
    let deepseekUsage = { input_tokens: 0, output_tokens: 0 };
    if (olderTurns.length >= 4 && deepSeekAvailable()) {
      const r = await summarizeOlderTurns(olderTurns);
      if (r?.text) {
        historySummary = r.text;
        deepseekUsage.input_tokens += r.usage.input_tokens || 0;
        deepseekUsage.output_tokens += r.usage.output_tokens || 0;
      }
    }

    // Choisir le modèle adapté à la complexité (router cost-optimisé + Aperçu Premium + anti-abus)
    // Si l'utilisateur paie cette question avec un crédit Opus → on force Opus (qualité max)
    const model = usingCredit
      ? { ...MODELS.opus, _paid_credit: true }
      : pickModel(trimmedMessages, req.body?.model_hint, plan, previewUsed, aperçuBlocked, forceOpus);

    // En-têtes SSE
    res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache, no-transform');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');
    res.flushHeaders?.();

    // Premier event : info état de la session (pour bannière + UX progressive)
    const willBeCount = currentCount + 1;
    const remaining = Math.max(0, limit - willBeCount);
    // Restant mensuel : c'est la jauge affichée au gratuit/anonyme (cadence mois).
    const monthRemaining = Math.max(0, monthLimit - (currentMonthCount + 1));
    const previewRemaining = Math.max(0, PREVIEW_OPUS_LIMIT - previewUsed - (model._aperçu ? 1 : 0));
    // Statut affiché côté UI :
    //  - "aperçu"  : Free/anon en pleine phase Aperçu Premium (Opus offert)
    //  - "standard": Free/anon après Aperçu (Sonnet)
    //  - "premium" : Abonné (Khavroutha/Beit Midrash/Yeshiva/Lifetime)
    //  - "limit"   : Limite quotidienne ou mensuelle bientôt atteinte
    let uxStatus = 'standard';
    if (SUBSCRIBER_PLANS.has(plan)) uxStatus = 'premium';
    else if (model._aperçu) uxStatus = 'aperçu';
    else if (model._meta) uxStatus = 'meta';

    const rateInfoPayload = JSON.stringify({
      type: 'rate_info',
      plan,
      is_guest: isGuest,
      count: willBeCount,
      limit,
      remaining,
      month_count: currentMonthCount + 1,
      month_limit: monthLimit,
      month_remaining: monthRemaining,
      ux_status: uxStatus,
      preview_used: previewUsed,
      preview_remaining: previewRemaining,
      preview_limit: PREVIEW_OPUS_LIMIT,
      is_aperçu: Boolean(model._aperçu),
      aperçu_blocked: aperçuBlocked, // true si caps IP/global ont dégradé en Sonnet
      is_subscriber: SUBSCRIBER_PLANS.has(plan),
      model_tier: model.id?.includes('opus') ? 'opus' : (model.id?.includes('sonnet') ? 'sonnet' : 'haiku'),
      would_use_opus: Boolean(model._standard_free), // hint UI "aurait été Opus en Premium"
      helloasso_url: HELLOASSO_URL,
      soutenir_url: SOUTENIR_URL,
    });
    res.write(`data: ${rateInfoPayload}\n\n`);

    // ── Cache méta-réponses : exact-match KV avant tout appel LLM ──
    // Les méta-questions sont des premiers messages courts (cf. isMetaQuestion),
    // donc zéro contexte conversationnel → une réponse cachée est toujours valide.
    if (model._meta) {
      const lastUserText = trimmedMessages[trimmedMessages.length - 1].content;
      let cachedMeta = null;
      try { cachedMeta = await kv.get(metaCacheKey(lastUserText)); } catch (_) {}
      if (cachedMeta && typeof cachedMeta === 'string' && cachedMeta.length > 10) {
        // HIT — on streame la réponse cachée en chunks (garde le feel progressif)
        const CHUNK = 24;
        for (let i = 0; i < cachedMeta.length; i += CHUNK) {
          res.write(`data: ${JSON.stringify({ type: 'text', delta: cachedMeta.slice(i, i + CHUNK) })}\n\n`);
        }
        res.write(`data: ${JSON.stringify({
          type: 'done', stop_reason: 'end_turn', iterations: 1,
          usage: { input_tokens: 0, output_tokens: 0 }, provider: 'meta-cache',
        })}\n\n`);
        // La question compte dans les quotas, mais coût = 0
        try {
          await kv.incr(rateKey);
          const ttl = await kv.ttl(rateKey);
          if (ttl === -1 || ttl === -2) await kv.expire(rateKey, 24 * 60 * 60);
          await kv.incr(monthRateKey);
          const mttl = await kv.ttl(monthRateKey);
          if (mttl === -1 || mttl === -2) await kv.expire(monthRateKey, 35 * 24 * 60 * 60);
          await kv.sadd('users:known', userId);
          console.log(`[chat.js] meta-cache HIT: ${userId} "${lastUserText.slice(0, 30)}"`);
        } catch (err) {
          console.error('[chat.js] meta-cache HIT tracking error:', err?.message || err);
        }
        res.end();
        return;
      }
    }

    // ── Court-circuit DeepSeek pour méta-questions (≈ 4× moins cher que Haiku) ──
    // Salutations, "tu es qui", "comment ça marche", "merci". Pas de psak ici.
    // Si DeepSeek échoue/timeout, on retombe sur Claude (Haiku) normalement.
    if (model._meta && deepSeekAvailable()) {
      const lastUserText = trimmedMessages[trimmedMessages.length - 1].content;
      let metaAnswerText = '';
      const ds = await streamMetaQuestion(lastUserText, (delta) => {
        metaAnswerText += delta;
        res.write(`data: ${JSON.stringify({ type: 'text', delta })}\n\n`);
      });

      if (ds) {
        const dsCost =
          (ds.usage.input_tokens * DEEPSEEK_PRICING.in / 1000) +
          (ds.usage.output_tokens * DEEPSEEK_PRICING.out / 1000);

        res.write(`data: ${JSON.stringify({
          type: 'done',
          stop_reason: 'end_turn',
          iterations: 1,
          usage: ds.usage,
          provider: 'deepseek',
        })}\n\n`);

        try {
          const todayKey = new Date().toISOString().slice(0, 10);
          const globalKey = `usage:global:${todayKey}`;
          const globalData = (await kv.get(globalKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
          await kv.set(globalKey, {
            tokens_in: globalData.tokens_in + ds.usage.input_tokens,
            tokens_out: globalData.tokens_out + ds.usage.output_tokens,
            cost_usd: parseFloat((globalData.cost_usd + dsCost).toFixed(6)),
            count: globalData.count + 1,
          });
          const userKey = `usage:${userId}:${todayKey}`;
          const userData = (await kv.get(userKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
          await kv.set(userKey, {
            tokens_in: userData.tokens_in + ds.usage.input_tokens,
            tokens_out: userData.tokens_out + ds.usage.output_tokens,
            cost_usd: parseFloat((userData.cost_usd + dsCost).toFixed(6)),
            count: userData.count + 1,
          });
          await kv.incr(rateKey);
          await kv.incr(monthRateKey);
          const monthTtl = await kv.ttl(monthRateKey);
          if (monthTtl === -1 || monthTtl === -2) await kv.expire(monthRateKey, 35 * 24 * 60 * 60);
          const ttl = await kv.ttl(rateKey);
          if (ttl === -1 || ttl === -2) await kv.expire(rateKey, 24 * 60 * 60);
          await kv.lpush('logs:usage', JSON.stringify({
            ts: new Date().toISOString(),
            user: userId,
            is_guest: isGuest,
            plan,
            tokens_in: ds.usage.input_tokens,
            tokens_out: ds.usage.output_tokens,
            cost_usd: dsCost,
            provider: 'deepseek',
            model: 'deepseek-chat',
            iterations: 1,
            stop_reason: 'end_turn',
          }));
          await kv.ltrim('logs:usage', 0, 499);
          await kv.sadd('users:known', userId);
          // Stocker la réponse en cache méta — les prochains "bonjour" seront gratuits
          if (metaAnswerText.length > 10) {
            await kv.set(metaCacheKey(lastUserText), metaAnswerText, { ex: META_CACHE_TTL });
          }
          console.log(`[chat.js] usage tracked: ${userId} deepseek:meta +${ds.usage.input_tokens}in/${ds.usage.output_tokens}out ($${dsCost.toFixed(5)})`);
        } catch (err) {
          console.error('[chat.js] Erreur enregistrement usage (deepseek):', err?.message || err);
        }

        res.end();
        return;
      }
      // DeepSeek a échoué → on continue avec Claude Haiku (fallback transparent)
    }

    // ── Corpus-first : questions Shabbat avec réponse vetée dans le texte du Rav ──
    // Si la question matche fortement un chunk du corpus Shabbat (mode strict :
    // score ≥ 8 + ≥2 tokens originaux matchés), on demande à Haiku 4.5 de reformuler
    // l'extrait au lieu d'appeler Sonnet/Opus. Coût ~0.002 € vs ~0.05-0.12 € sinon.
    // Kill switch : env CORPUS_FIRST_ENABLED=false → bypass complet.
    // Abonnés payants toujours exclus : ils paient une réponse Sonnet/Opus
    // complète, pas une reformulation Haiku du corpus.
    // Pour Opus/Aperçu : corpus-first autorisé UNIQUEMENT sur un match TRÈS fort
    // (seuil élevé) → question bien couverte par le corpus servie en ~2s au lieu
    // de 10-60s ; sinon on garde la profondeur Opus. Abonnés payants toujours exclus.
    // Opus et Aperçu sont EXCLUS du corpus-first : ces questions halakhiques
    // profondes doivent passer par le chemin agentique complet (règle du בד"א,
    // vérification des séifim voisins sur Sefaria, prompt système entier).
    // Le corpus rapide est une reformulation Haiku d'UN seul extrait : sûre mais
    // trop mince pour trancher une sougya. Historique : l'élargissement à Opus
    // (PR #161, gain de latence) combiné à la hausse des scores de recherche
    // (PR #191) faisait intercepter massivement ces questions par le chemin
    // court — donc SANS les garde-fous introduits après l'incident borer.
    if (
      !model._meta &&
      !model._aperçu &&
      model.id !== MODELS.opus.id &&
      !SUBSCRIBER_PLANS.has(plan) &&
      process.env.CORPUS_FIRST_ENABLED !== 'false'
    ) {
      // On cherche le DERNIER message utilisateur (pas forcément le dernier du tableau :
      // un flux « regenerate » peut se terminer par un message assistant).
      const lastUserMsg = [...trimmedMessages].reverse().find((m) => m.role === 'user');
      const lastUserText = lastUserMsg ? lastUserMsg.content : null;
      const minScore = parseFloat(process.env.CORPUS_MIN_SCORE || '8');
      let cs = null;
      if (lastUserText) {
        try {
          // On restreint la recherche à la section de la conversation pour ne
          // jamais répondre Shabbat avec un extrait Yoreh De'ah (et inversement).
          cs = searchShabbatCorpus(lastUserText, { limit: 3, minScore, strict: true, section });
        } catch (err) {
          console.error('[chat.js] corpus search error (continue avec Claude):', err?.message || err);
        }
      }

      if (cs && cs.results.length > 0) {
        const served = await serveCorpusAnswer({
          req, res, cs, section, lastUserText, userId, isGuest, plan,
          rateKey, monthRateKey,
          // Le corpus a servi SANS consommer d'Aperçu Opus : on corrige la
          // métadonnée optimiste de rate_info pour que le client n'affiche ni
          // la fausse modale « Aperçu terminé » ni le badge Opus.
          doneExtra: {
            is_aperçu: false,
            aperçu_intercepted: Boolean(model._aperçu),
            preview_remaining: model._aperçu ? Math.max(0, PREVIEW_OPUS_LIMIT - previewUsed) : null,
          },
        });
        if (served) return;
        // Aucune sortie streamée (erreur Haiku avant le premier token) → fallback transparent vers Claude
      }
    }

    // Conversation working set : format de blocs (pour le tool use)
    let conversation = trimmedMessages.map(m => ({
      role: m.role,
      content: [{ type: 'text', text: m.content }],
    }));

    // Compaction d'historique : préfixer un résumé synthétique des anciens tours
    if (historySummary) {
      conversation.unshift(
        { role: 'user', content: [{ type: 'text', text: `Contexte de notre conversation précédente (résumé) :\n\n${historySummary}` }] },
        { role: 'assistant', content: [{ type: 'text', text: 'Bien noté, je tiens compte de ce contexte.' }] },
      );
    }

    // Pré-recherche RAG via DeepSeek : reformule la question, interroge le corpus,
    // injecte les meilleurs hits dans le dernier message user → élimine un round-trip
    // Claude sur la plupart des questions halakhiques SIMPLES.
    //
    // ⚠️ Gating strict — on saute le pré-RAG quand :
    //  - question complexe (déjà routée vers Opus) → Claude fait déjà sa propre orchestration
    //  - question longue (> 220 chars) → idem, sera tool-heavy de toute façon
    //  - conversation longue (> 4 turns) → contexte conversationnel suffit
    //  Sur ces cas le pré-RAG ajoute 3-5s upfront sans réduire les tool calls — c'est perdu.
    const isOpus = model.id === MODELS.opus.id;
    const lastUserText = trimmedMessages[trimmedMessages.length - 1].content;
    const skipPreRag = isOpus || (lastUserText?.length || 0) > 220 || trimmedMessages.length > 4;

    if (deepSeekAvailable() && !model._meta && !skipPreRag) {
      if (lastUserText && lastUserText.length >= 30) {
        try {
          const ref = await reformulateForCorpus(lastUserText);
          if (ref?.queries?.length) {
            deepseekUsage.input_tokens += ref.usage.input_tokens || 0;
            deepseekUsage.output_tokens += ref.usage.output_tokens || 0;

            const allHits = await Promise.all(ref.queries.map(q => searchCorpus(q, { limit: 3 })));
            const seen = new Set();
            const merged = [];
            for (const hits of allHits) {
              for (const h of (hits || [])) {
                if (!h?.id || seen.has(h.id)) continue;
                seen.add(h.id);
                merged.push(h);
                if (merged.length >= 4) break;
              }
              if (merged.length >= 4) break;
            }

            if (merged.length) {
              const blob = merged.map(h => {
                const where = h.siman ? ` (siman ${h.siman}${h.seif ? `:${h.seif}` : ''})` : '';
                const lvl = h.level ? ` [${h.level}]` : '';
                const srcs = (h.sources || []).slice(0, 3)
                  .map(s => typeof s === 'string' ? s : (s?.ref || ''))
                  .filter(Boolean).join(' ; ');
                return `[${h.id}] ${h.title}${where}${lvl}\n  ${(h.summary || '').slice(0, 240)}${srcs ? `\n  Sources : ${srcs}` : ''}`;
              }).join('\n\n');

              const lastIdx = conversation.length - 1;
              const last = conversation[lastIdx];
              const originalText = last.content.map(b => b.text || '').join('');
              conversation[lastIdx] = {
                role: 'user',
                content: [{
                  type: 'text',
                  text:
                    `<contexte_corpus_daat queries="${ref.queries.join(' | ')}">\n` +
                    `Entrées du corpus DAAT pré-sélectionnées par recherche automatique. ` +
                    `Cite-les si elles répondent à la question ; sinon ignore-les et utilise les outils habituels.\n\n` +
                    `${blob}\n` +
                    `</contexte_corpus_daat>\n\n` +
                    originalText,
                }],
              };
            }
          }
        } catch (err) {
          console.error('[chat.js] pre-RAG DeepSeek failed:', err?.message || err);
          // Fail open : on continue sans pré-contexte
        }
      }
    }

    const totalUsage = {
      input_tokens: 0,
      output_tokens: 0,
      cache_creation: 0,
      cache_read: 0,
    };
    // Ventilation par modèle réellement appelé. La synthèse forcée bascule
    // Opus → Sonnet en cours de route (voir iterModel plus bas) : tout facturer
    // au tarif du modèle routé surévaluerait ces requêtes.
    const usageByModel = new Map(); // id → { price, input, output, cacheCreate, cacheRead }

    let iterations = 0;
    let totalToolCalls = 0; // borne dure : plafonne le nombre de recherches avant synthèse
    // Les questions halakhiques profondes (Opus) reçoivent le budget élargi :
    // mieux vaut une réponse plus lente qu'une halakha non vérifiée.
    const deepHalakha = model.id === MODELS.opus.id;
    const maxIterations = deepHalakha ? MAX_TOOL_ITERATIONS_HALAKHA : MAX_TOOL_ITERATIONS;
    const maxToolCalls = deepHalakha ? MAX_TOOL_CALLS_HALAKHA : MAX_TOOL_CALLS;
    let stopReason = null;
    const startedAt = Date.now();
    let forcedSynthesis = false;
    // Types de blocs qui acceptent cache_control (les blocs thinking n'en acceptent pas)
    const CACHEABLE_BLOCKS = new Set(['text', 'image', 'tool_use', 'tool_result', 'document']);

    // Boucle agentique. À la dernière itération OU si on dépasse FORCE_SYNTHESIS_AFTER_MS,
    // on bascule sur tool_choice:none + thinking désactivé pour FORCER Claude à produire
    // du texte (pas d'autre tool_use possible). Garantit qu'on rend toujours une réponse.
    while (iterations < maxIterations) {
      iterations++;
      const elapsedBefore = Date.now() - startedAt;

      const forceSynthesis =
        iterations === maxIterations ||
        totalToolCalls >= maxToolCalls ||
        elapsedBefore > FORCE_SYNTHESIS_AFTER_MS;

      if (forceSynthesis && !forcedSynthesis) {
        forcedSynthesis = true;
        conversation.push({
          role: 'user',
          content: [{
            type: 'text',
            text: 'Ta recherche de sources s\'arrête ici (limite de temps ou d\'outils atteinte). Rédige maintenant ta réponse complète et structurée à ma question initiale, en t\'appuyant UNIQUEMENT sur ce que tu as déjà recueilli. N\'appelle plus aucun outil. IMPORTANT : ta vérification des sources est peut-être INCOMPLÈTE — tu ne dois donc formuler AUCUNE permission pratique. Expose l\'état des sources, signale explicitement ce que tu n\'as pas pu vérifier, et renvoie la conclusion pratique au Rav de l\'utilisateur.',
          }],
        });
        console.log(`[chat.js] forcing synthesis at iter ${iterations} (elapsed ${elapsedBefore}ms)`);
      }

      // Cache incrémental sur la conversation : sans breakpoint, chaque itération
      // d'outils repaie TOUT l'input (system + historique + tool_results) — c'est
      // ce qui épuise le budget input/minute de l'org et étrangle Opus aux heures
      // de pointe. On déplace un unique breakpoint sur le dernier bloc (max 4
      // breakpoints par requête : 1 system + 1 messages).
      for (const m of conversation) {
        if (Array.isArray(m.content)) {
          for (const b of m.content) { if (b && b.cache_control) delete b.cache_control; }
        }
      }
      const lastMsg = conversation[conversation.length - 1];
      if (lastMsg && Array.isArray(lastMsg.content) && lastMsg.content.length) {
        const lastBlock = lastMsg.content[lastMsg.content.length - 1];
        if (lastBlock && CACHEABLE_BLOCKS.has(lastBlock.type)) {
          lastBlock.cache_control = { type: 'ephemeral' };
        }
      }

      // Synthèse forcée : si le modèle principal est Opus, on bascule sur Sonnet
      // (rapide et solide) pour la réponse finale — aux heures de pointe, Opus
      // peut être étranglé (retries 429/529 silencieux du SDK) et ne produirait
      // rien avant le hard abort. Mieux vaut une bonne réponse Sonnet qu'un vide.
      const iterModel = (forceSynthesis && model.id === MODELS.opus.id) ? MODELS.sonnet : model;

      const streamParams = {
        model: iterModel.id,
        max_tokens: forceSynthesis ? FORCED_SYNTHESIS_MAX_TOKENS : MAX_TOKENS_OUTPUT,
        tools: ALL_TOOLS,
        system: [
          {
            type: 'text',
            text: buildSystemPrompt(section),
            cache_control: { type: 'ephemeral', ttl: '1h' },
          },
        ],
        messages: conversation,
      };
      if (forceSynthesis) {
        // tool_choice:none → Claude DOIT produire du texte (pas de tool_use possible)
        streamParams.tool_choice = { type: 'none' };
      } else {
        if (model.thinking) streamParams.thinking = model.thinking;
        if (model.effort) streamParams.output_config = { effort: model.effort };
      }

      // Hard abort (HARD_ABORT_MS, déf. 250s) : dernier filet de sécurité avant le kill Vercel (maxDuration 300s)
      const abortCtrl = new AbortController();
      const msUntilHardAbort = HARD_ABORT_MS - (Date.now() - startedAt);
      const abortTimer = setTimeout(() => {
        console.log(`[chat.js] HARD abort at ${Date.now() - startedAt}ms`);
        abortCtrl.abort();
      }, Math.max(msUntilHardAbort, 3000));

      let iterHadText = false;

      try {
        const stream = client.messages.stream(streamParams, { signal: abortCtrl.signal });

        for await (const event of stream) {
          if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
            iterHadText = true;
            anyTextSent = true;
            res.write(`data: ${JSON.stringify({ type: 'text', delta: event.delta.text })}\n\n`);
          }
        }

        const final = await stream.finalMessage();
        stopReason = final.stop_reason;

        totalUsage.input_tokens += final.usage.input_tokens || 0;
        totalUsage.output_tokens += final.usage.output_tokens || 0;
        totalUsage.cache_creation += final.usage.cache_creation_input_tokens || 0;
        totalUsage.cache_read += final.usage.cache_read_input_tokens || 0;

        const mu = usageByModel.get(iterModel.id)
          || { price: iterModel, input: 0, output: 0, cacheCreate: 0, cacheRead: 0 };
        mu.input += final.usage.input_tokens || 0;
        mu.output += final.usage.output_tokens || 0;
        mu.cacheCreate += final.usage.cache_creation_input_tokens || 0;
        mu.cacheRead += final.usage.cache_read_input_tokens || 0;
        usageByModel.set(iterModel.id, mu);

        conversation.push({ role: 'assistant', content: final.content });

        if (stopReason !== 'tool_use') break;

        const toolUses = final.content.filter(b => b.type === 'tool_use');
        if (toolUses.length === 0) break;
        totalToolCalls += toolUses.length;

        const toolResults = await Promise.all(
          toolUses.map(async (tu) => {
            try {
              const executor = TOOL_EXECUTORS[tu.name];
              if (!executor) {
                return {
                  type: 'tool_result',
                  tool_use_id: tu.id,
                  content: JSON.stringify({ error: `Outil inconnu : ${tu.name}` }),
                  is_error: true,
                };
              }
              const result = await executor(tu.name, tu.input);
              return { type: 'tool_result', tool_use_id: tu.id, content: result };
            } catch (err) {
              return {
                type: 'tool_result',
                tool_use_id: tu.id,
                content: JSON.stringify({ error: err.message || 'Erreur outil' }),
                is_error: true,
              };
            }
          })
        );

        for (const tu of toolUses) {
          res.write(`data: ${JSON.stringify({
            type: 'tool_use',
            tool: tu.name,
            input: tu.input,
          })}\n\n`);
        }

        conversation.push({ role: 'user', content: toolResults });

      } catch (err) {
        if (abortCtrl.signal.aborted) {
          stopReason = 'end_turn';
          console.log(`[chat.js] hard abort caught — iterHadText=${iterHadText}, elapsed=${Date.now() - startedAt}ms`);
          // Ne JAMAIS terminer en silence : l'utilisateur doit toujours voir quelque chose.
          if (!anyTextSent) {
            res.write(`data: ${JSON.stringify({
              type: 'text',
              delta: '⏱️ Désolé — le modèle a mis trop de temps à répondre (surcharge momentanée) et la génération a été interrompue avant le premier mot.\n\n**Repose ta question dans un instant** — en général, ça passe au deuxième essai.',
            })}\n\n`);
          } else {
            res.write(`data: ${JSON.stringify({
              type: 'text',
              delta: '\n\n---\n_⏱️ Réponse interrompue (temps limite dépassé). Repose la question pour obtenir la suite._',
            })}\n\n`);
          }
          break;
        }
        throw err;
      } finally {
        clearTimeout(abortTimer);
      }
    }

    // Réponse coupée net par le plafond de tokens : l'utilisateur DOIT le voir.
    // Le client n'exploite pas `stop_reason` — sans ce texte, une réponse
    // interrompue en plein raisonnement s'affiche comme une réponse complète.
    // C'est précisément là que le danger est maximal en halakha : la nuance
    // finale (« mais be-di'avad… », « c'est à ton Rav de trancher ») arrive à la
    // FIN. Une troncature silencieuse transforme une réponse nuancée en psak
    // tranché. Même logique que le chemin corpus, qui avertit déjà.
    if (stopReason === 'max_tokens') {
      res.write(`data: ${JSON.stringify({
        type: 'text',
        delta: anyTextSent
          ? '\n\n---\n_⚠️ Réponse tronquée par la limite de longueur — elle s\'arrête avant sa conclusion. Repose la question de façon plus ciblée pour obtenir la suite, et ne considère pas ce qui précède comme un raisonnement achevé._'
          : '⚠️ La réponse a été interrompue avant le premier mot. Repose ta question.',
      })}\n\n`);
    }

    // Envoyer le done final (côté UX, la conversation est terminée)
    const donePayload = JSON.stringify({
      type: 'done',
      stop_reason: stopReason,
      iterations,
      usage: totalUsage,
    });
    res.write(`data: ${donePayload}\n\n`);

    // ⚠️ Enregistrer l'usage AVANT res.end() — sinon Vercel kill le lambda
    // (le fire-and-forget ne marche pas en serverless Node, contrairement à Edge)
    try {
      const todayKey = new Date().toISOString().slice(0, 10);

      // Coût Claude — ventilé par modèle réellement appelé, tokens de cache inclus.
      // Les tokens du prompt système passent par cache_read (cache chaud) ou
      // cache_creation (reconstruction à froid) et n'apparaissent PAS dans
      // `input_tokens` : les omettre revenait à ne pas facturer l'essentiel de
      // l'entrée. Sur un prompt système de ~15 000 tokens, cela sous-estimait
      // chaque réponse Opus d'environ 0,008 $ à chaud et 0,15 $ à froid.
      let claudeCost = 0;
      for (const u of usageByModel.values()) {
        claudeCost +=
          (u.input * u.price.in / 1000) +
          (u.cacheRead * u.price.in * CACHE_READ_MULT / 1000) +
          (u.cacheCreate * u.price.in * CACHE_WRITE_MULT / 1000) +
          (u.output * u.price.out / 1000);
      }

      // Coût DeepSeek (reformulation RAG + résumé d'historique, si activé)
      const dsCost =
        (deepseekUsage.input_tokens * DEEPSEEK_PRICING.in / 1000) +
        (deepseekUsage.output_tokens * DEEPSEEK_PRICING.out / 1000);

      const costUsd = claudeCost + dsCost;
      // Tokens d'entrée réels = résidu non caché + lectures de cache + écritures.
      // `input_tokens` seul ne compte que le résidu : les statistiques de /admin
      // affichaient donc quelques centaines de tokens d'entrée par question alors
      // que le prompt système en fait ~15 000.
      const tokensIn = totalUsage.input_tokens + totalUsage.cache_read
        + totalUsage.cache_creation + deepseekUsage.input_tokens;
      const tokensOut = totalUsage.output_tokens + deepseekUsage.output_tokens;

      // Stats globales
      const globalKey = `usage:global:${todayKey}`;
      const globalData = (await kv.get(globalKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
      await kv.set(globalKey, {
        tokens_in: globalData.tokens_in + tokensIn,
        tokens_out: globalData.tokens_out + tokensOut,
        cost_usd: parseFloat((globalData.cost_usd + costUsd).toFixed(6)),
        count: globalData.count + 1,
      });

      // Stats par utilisateur (email OU guest_id)
      const userKey = `usage:${userId}:${todayKey}`;
      const userData = (await kv.get(userKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
      await kv.set(userKey, {
        tokens_in: userData.tokens_in + tokensIn,
        tokens_out: userData.tokens_out + tokensOut,
        cost_usd: parseFloat((userData.cost_usd + costUsd).toFixed(6)),
        count: userData.count + 1,
      });

      // Compteur quotidien (rate limit)
      await kv.incr(rateKey);
      const ttl = await kv.ttl(rateKey);
      if (ttl === -1 || ttl === -2) {
        await kv.expire(rateKey, 24 * 60 * 60);
      }

      // Compteur mensuel (token cap protecteur)
      await kv.incr(monthRateKey);
      const monthTtl = await kv.ttl(monthRateKey);
      if (monthTtl === -1 || monthTtl === -2) {
        await kv.expire(monthRateKey, 35 * 24 * 60 * 60); // ~35 jours pour couvrir le mois en cours
      }

      // Compteur mensuel par IP (visiteurs non connectés seulement). Il rend le
      // quota anonyme insensible à l'effacement du cookie `daat_guest_id`.
      if (isGuest && clientIp && ANON_IP_MONTHLY_LIMIT > 0) {
        await kv.incr(anonIpMonthKey);
        const ipTtl = await kv.ttl(anonIpMonthKey);
        if (ipTtl === -1 || ipTtl === -2) await kv.expire(anonIpMonthKey, 35 * 24 * 60 * 60);
      }

      // CRÉDITS OPUS — si cette question a été payée par un crédit (quota gratuit
      // dépassé mais credits > 0), on décrémente le solde de crédits, et on annule
      // l'incr quotidien/mensuel qu'on vient de faire (la question n'a pas consommé
      // le quota gratuit, elle a consommé un crédit acheté).
      if (usingCredit && creditsKey) {
        await Promise.all([
          kv.decr(creditsKey),
          kv.decr(rateKey),
          kv.decr(monthRateKey),
        ]);
        console.log(`[chat.js] credit consumed: ${userId} (credits left: ${opusCredits - 1})`);
      }

      // Incrément Aperçu Premium si on a servi du Opus à un free/anonyme
      // 1. Compteur lifetime par user (pas d'expiration)
      // 2. Cap par IP du jour (24h TTL) — anti clear-cookies
      // 3. Cap global du jour (24h TTL) — plafond budgétaire
      if (model._aperçu) {
        await Promise.all([
          kv.incr(`user:preview_used:${userId}`),
          kv.incr(previewIpKey),
          kv.incr(previewGlobalKey),
        ]);
        // TTL 24h sur les caps quotidiens (set seulement si pas déjà set)
        const [ipTtl, globalTtl] = await Promise.all([
          kv.ttl(previewIpKey),
          kv.ttl(previewGlobalKey),
        ]);
        if (ipTtl === -1 || ipTtl === -2) await kv.expire(previewIpKey, 24 * 60 * 60);
        if (globalTtl === -1 || globalTtl === -2) await kv.expire(previewGlobalKey, 24 * 60 * 60);
      }

      // Log rolling 500 dernières
      const logEntry = {
        ts: new Date().toISOString(),
        user: userId,
        is_guest: isGuest,
        plan,
        tokens_in: tokensIn,
        tokens_out: tokensOut,
        cost_usd: costUsd,
        provider: deepseekUsage.input_tokens > 0 ? 'claude+deepseek' : 'claude',
        model: model.id,
        // Modèles RÉELLEMENT appelés : diffère de `model` quand la synthèse
        // forcée bascule Opus → Sonnet.
        models_used: [...usageByModel.keys()],
        // Diagnostic du prompt caching — c'est ce qui permet de mesurer le taux
        // de cache réel. cache_read élevé = cache chaud (prompt à 0,1×) ;
        // cache_creation non nul = reconstruction à froid (2× en TTL 1 h),
        // ce qui arrive après chaque modification du prompt système.
        cache_read: totalUsage.cache_read,
        cache_creation: totalUsage.cache_creation,
        uncached_input: totalUsage.input_tokens,
        deepseek_tokens: deepseekUsage.input_tokens + deepseekUsage.output_tokens,
        iterations,
        stop_reason: stopReason,
      };
      await kv.lpush('logs:usage', JSON.stringify(logEntry));
      await kv.ltrim('logs:usage', 0, 499);

      // Liste des utilisateurs connus
      await kv.sadd('users:known', userId);
      console.log(`[chat.js] usage tracked: ${userId} model=${model.id} +${tokensIn}in/${tokensOut}out ($${costUsd.toFixed(5)}, ds=${deepseekUsage.input_tokens + deepseekUsage.output_tokens}tok)`);
    } catch (err) {
      console.error('[chat.js] Erreur enregistrement usage:', err?.message || err);
    }

    res.end();
  } catch (error) {
    console.error('[Daat chat API] error:', error);

    // Détection des erreurs Anthropic "quota épuisé côté admin/Anthropic"
    // - "You have reached your specified API usage limits" (limite mensuelle configurée)
    // - "rate_limit" / "credit_balance" / "billing"
    // On transforme en notre format `limit_reached` pour afficher le modal côté UI.
    const rawMessage = String(error?.message || error || '');
    const isQuotaExhausted =
      /reached your specified API usage limits/i.test(rawMessage) ||
      /credit balance is too low/i.test(rawMessage) ||
      /quota/i.test(rawMessage) && /exhaust/i.test(rawMessage);

    if (isQuotaExhausted) {
      // Avant le paywall : si la question correspond au corpus du Rav, on sert
      // l'extrait BRUT à coût nul. Le budget IA épuisé ne doit pas rendre
      // inaccessible du contenu qui n'a besoin d'aucun modèle pour être lu.
      if (!anyTextSent && !res.writableEnded) {
        try {
          const lastQ = [...(req.body?.messages || [])].reverse().find(
            (m) => m && m.role === 'user' && typeof m.content === 'string' && m.content.length > 0
          );
          if (lastQ) {
            const sec = req.body?.section === 'yoreh-deah' ? 'yoreh-deah' : 'orach-chaim';
            const cs = searchShabbatCorpus(lastQ.content, {
              limit: 3, minScore: parseFloat(process.env.CORPUS_MIN_SCORE || '8'), strict: true, section: sec,
            });
            if (cs && cs.results.length) {
              const ensure = () => {
                if (res.headersSent) return;
                res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
                res.setHeader('Cache-Control', 'no-cache, no-transform');
                res.setHeader('Connection', 'keep-alive');
                res.setHeader('X-Accel-Buffering', 'no');
              };
              const served = await serveRawCorpus({
                res, cs, ensureSse: ensure,
                doneExtra: { is_aperçu: false, anthropic_quota_exhausted: true },
                userId: 'unknown', plan: 'anonymous', question: lastQ.content, lang: req.body?.lang,
              });
              if (served) return;
            }
          }
        } catch (e) {
          console.error('[chat.js] repli corpus brut (quota Anthropic) échoué:', e?.message || e);
        }
      }
      const payload = {
        error: 'limit_reached',
        type: 'limit_reached',
        scope: 'anthropic_quota',
        is_guest: false, // peu importe, le message est le même
        soutenir_url: SOUTENIR_URL,
        helloasso_url: HELLOASSO_URL,
        message: "Le quota mensuel de l'IA est temporairement épuisé. Soutiens DAAT pour rétablir l'accès et permettre à l'étude de continuer.",
      };
      if (!res.headersSent) {
        return res.status(429).json(payload);
      }
      // En SSE : on envoie limit_reached au lieu d'error
      try {
        res.write(`data: ${JSON.stringify({ type: 'limit_reached', ...payload })}\n\n`);
        res.end();
      } catch (_) { /* connection closed */ }
      return;
    }

    if (!res.headersSent) {
      if (error instanceof Anthropic.AuthenticationError) {
        return res.status(500).json({ error: 'Configuration serveur invalide (clé API)' });
      }
      if (error instanceof Anthropic.RateLimitError) {
        return res.status(429).json({
          error: 'rate_limited',
          type: 'rate_limited',
          message: 'Trop de requêtes en même temps. Réessaie dans un instant.',
        });
      }
      if (error instanceof Anthropic.APIError) {
        // Message générique en français au lieu du payload Anthropic brut en anglais
        return res.status(error.status || 500).json({
          error: 'api_error',
          message: "Une erreur est survenue côté IA. Réessaie ou reviens dans un moment.",
        });
      }
      return res.status(500).json({ error: 'Erreur interne du serveur' });
    }

    try {
      const errorPayload = JSON.stringify({
        type: 'error',
        error: "Une erreur est survenue côté IA. Réessaie ou reviens dans un moment.",
      });
      res.write(`data: ${errorPayload}\n\n`);
      res.end();
    } catch (_) {
      // Connection closed
    }
  }
}
