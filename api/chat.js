// Vercel Serverless Function — Endpoint chat de Daat (l'IA pédagogique de DAAT.AI)
// - Claude Opus 4.7 avec tool use (Sefaria API) en boucle agentique
// - Prompt caching (TTL 1h) sur le system prompt long
// - Adaptive thinking (effort: high)
// - Streaming SSE pour l'affichage progressif
// - Multi-turn (l'historique est envoyé par le client à chaque appel)

import Anthropic from '@anthropic-ai/sdk';
import { kv } from '@vercel/kv';
import { SYSTEM_PROMPT } from './_system-prompt.js';
import { SEFARIA_TOOLS, executeSefariaTool } from './_sefaria.js';
import { CORPUS_TOOLS, executeCorpusTool, searchCorpus } from './_corpus.js';
import { MAREH_MEKOMOT_TOOLS, executeMarehMekomotTool } from './_mareh_mekomot.js';
import { getUserFromRequest } from './_auth.js';
import {
  deepSeekAvailable,
  streamMetaQuestion,
  summarizeOlderTurns,
  reformulateForCorpus,
  DEEPSEEK_PRICING,
} from './_deepseek.js';

const client = new Anthropic();

const MAX_TOOL_ITERATIONS = 6; // 5 itérations outils + 1 synthèse forcée
const MAX_TOKENS_OUTPUT = 4096; // cap output ; Claude s'arrête naturellement avant
const HISTORY_TURNS = 16;       // 16 derniers tours (plus de contexte = meilleure réponse)

// Vercel Hobby plafonne à ~90s. On force la synthèse (tool_choice: none) dès
// qu'on dépasse cette durée OU à la dernière itération, garantissant qu'il
// reste assez de temps pour streamer une réponse textuelle complète.
const FORCE_SYNTHESIS_AFTER_MS = 50_000;
const HARD_ABORT_MS = 80_000; // dernier recours : abort à 80s (5s avant Vercel)
const ALL_TOOLS = [...MAREH_MEKOMOT_TOOLS, ...CORPUS_TOOLS, ...SEFARIA_TOOLS];

// ── Routing modèles — priorité QUALITÉ, économies opportunistes ──
// Haiku ($0.001/$0.005) → Sonnet ($0.003/$0.015) → Opus ($0.015/$0.06)
const MODELS = {
  haiku:  { id: 'claude-haiku-4-5',  thinking: null,                  effort: null,    in: 0.001, out: 0.005 },
  sonnet: { id: 'claude-sonnet-4-6', thinking: { type: 'adaptive' },  effort: null,    in: 0.003, out: 0.015 },
  opus:   { id: 'claude-opus-4-7',   thinking: { type: 'adaptive' },  effort: 'high',  in: 0.015, out: 0.06  },
};

// Heuristique : qualité d'abord. Routage selon plan + Aperçu Premium pour les nouveaux.
// 1. Méta-questions courtes → DeepSeek/Haiku (zéro coût, zéro perte qualité)
// 2. Subscribers (Beit Midrash+) → Opus toujours
// 3. Khavroutha → Opus sur halakhique pointu, Sonnet ailleurs
// 4. Free/anonyme avec previewUsed < 3 → Aperçu Premium Opus (compte à vie)
// 5. Free/anonyme après Aperçu → Sonnet (qualité standard)
// 6. forceOpus = perk admin manuel : Opus sur tout (sauf méta)
function pickModel(messages, hint, plan, previewUsed, forceOpus) {
  // Hint explicite du client (ex: depuis une page Lamdan/Synthèse) — gagne toujours
  if (hint === 'opus' || hint === 'sonnet' || hint === 'haiku') return MODELS[hint];

  const lastUser = [...messages].reverse().find(m => m.role === 'user');
  const text = (lastUser?.content || '').toString().trim();
  const lower = text.toLowerCase();

  // 1. Méta-questions très courtes — toujours DeepSeek/Haiku (toutes catégories d'users)
  const isFirstQuestion = messages.length <= 1;
  const halakhicHint = /shab|kasher|kasher|tefil|tznio|mouk|hila|sefer|torah|halakh|halacha|halaha|halaja|seif|siman|guemar|mishna|talmud|cohen|brah|berakh|nidda|kashr|peot|tsitsit|loulav|souka|sukka|mezou|tefil|shem|shabb|peah|maase|mitsv|mitzv/i;
  const isMetaQuestion = isFirstQuestion && text.length < 40 && !halakhicHint.test(lower);
  if (isMetaQuestion) {
    return { ...MODELS.haiku, _meta: true };
  }

  // 2. Force Opus pour les users privilégiés (perk admin)
  if (forceOpus) return MODELS.opus;

  // 3. Abonnés "Beit Midrash et plus" : Opus toujours
  if (ALWAYS_OPUS_PLANS.has(plan)) return MODELS.opus;

  // 4. Aperçu Premium : free/anonyme avec compteur lifetime < 3 → Opus (incrémenté côté serveur)
  if (!SUBSCRIBER_PLANS.has(plan) && previewUsed < PREVIEW_OPUS_LIMIT) {
    return { ...MODELS.opus, _aperçu: true };
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

const DAILY_LIMITS = {
  anonymous:         5,        // visiteur sans compte (était 3 → 5 pour mieux convertir)
  free:              8,        // compte email (OTP)
  khavroutha:       30,        // soutien 8 €/mois (HelloAsso) ou 18 €/mois (Qonto Tomhei Adaat)
  beit_midrash:    100,        // soutien 25 €/mois (HelloAsso) ou 36 €/mois (Qonto)
  beit_midrash_plus: 150,      // soutien 50 €/mois (Qonto)
  yeshiva:         300,        // soutien 80-100 €/mois — 3 sous-comptes
  lifetime:        100,        // don unique 500 € = équivalent Beit Midrash à vie
  premium:       99999,        // ancien plan, conservé pour compatibilité
};

const MONTHLY_LIMITS = {
  anonymous:        100,
  free:             150,
  khavroutha:       600,
  beit_midrash:    2000,
  beit_midrash_plus: 3000,
  yeshiva:         6000,
  lifetime:        2000,
  premium:        99999,
};

// Plans qui débloquent la qualité Opus sur les questions halakhiques
const SUBSCRIBER_PLANS = new Set(['khavroutha', 'beit_midrash', 'beit_midrash_plus', 'yeshiva', 'lifetime', 'premium']);
// Plans qui ont Opus TOUJOURS (sauf méta) — Khavroutha n'a Opus que sur halakhique pointu
const ALWAYS_OPUS_PLANS = new Set(['beit_midrash', 'beit_midrash_plus', 'yeshiva', 'lifetime']);

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
    // Vérif expiration : si plan payant expiré → downgrade vers free
    let effectivePlan = plan || 'free';
    if (SUBSCRIBER_PLANS.has(effectivePlan) && effectivePlan !== 'lifetime' && expiresRaw) {
      const expiresAt = new Date(expiresRaw).getTime();
      if (Date.now() > expiresAt) {
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

export default async function handler(req, res) {
  // CORS — credentials:include nécessite origin spécifique (pas *)
  const origin = req.headers.origin || '*';
  res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Access-Control-Allow-Credentials', 'true');
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

    // Validation
    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: 'Le champ "messages" doit être un tableau non vide' });
    }

    // Identifier l'utilisateur (email connecté OU guest_id par cookie)
    const { userId, plan, isGuest, guestIdSetCookie, forceOpus, previewUsed, planExpires } = await identifyUser(req);
    const today = new Date().toISOString().slice(0, 10);
    const currentMonth = today.slice(0, 7); // YYYY-MM
    const rateKey = `rate:${userId}:${today}`;
    const monthRateKey = `rate-month:${userId}:${currentMonth}`;
    const limit = DAILY_LIMITS[plan] || DAILY_LIMITS.anonymous;
    const monthLimit = MONTHLY_LIMITS[plan] || MONTHLY_LIMITS.anonymous;
    const currentCount = parseInt((await kv.get(rateKey)) || 0, 10);
    const currentMonthCount = parseInt((await kv.get(monthRateKey)) || 0, 10);

    // Définir le cookie guest_id si nouveau visiteur
    if (guestIdSetCookie) {
      res.setHeader('Set-Cookie', guestIdSetCookie);
    }

    // Limite QUOTIDIENNE atteinte
    if (currentCount >= limit) {
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
        reset_date: resetTime.toISOString(),
        helloasso_url: HELLOASSO_URL,
        soutenir_url: SOUTENIR_URL,
        message: isGuest
          ? `Tu as utilisé tes ${limit} questions gratuites aujourd'hui. Connecte-toi avec ton email pour ${DAILY_LIMITS.free} questions/jour, ou soutiens DAAT pour débloquer plus.`
          : `Tu as atteint ta limite quotidienne de ${limit} questions. Reviens demain ou soutiens DAAT.`,
      });
    }

    // Limite MENSUELLE atteinte (cap protecteur pour l'asso)
    if (currentMonthCount >= monthLimit) {
      const nextMonth = new Date();
      nextMonth.setMonth(nextMonth.getMonth() + 1);
      nextMonth.setDate(1);
      nextMonth.setHours(0, 0, 0, 0);
      return res.status(429).json({
        error: 'limit_reached',
        type: 'limit_reached',
        scope: 'monthly',
        plan,
        count: currentMonthCount,
        limit: monthLimit,
        is_guest: isGuest,
        reset_date: nextMonth.toISOString(),
        soutenir_url: SOUTENIR_URL,
        message: `Tu as atteint ton quota mensuel (${monthLimit} questions). Reviens le mois prochain, ou passe à un niveau supérieur pour plus de questions.`,
      });
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

    // Choisir le modèle adapté à la complexité (router cost-optimisé + Aperçu Premium)
    const model = pickModel(trimmedMessages, req.body?.model_hint, plan, previewUsed, forceOpus);

    // En-têtes SSE
    res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache, no-transform');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');
    res.flushHeaders?.();

    // Premier event : info état de la session (pour bannière + UX progressive)
    const willBeCount = currentCount + 1;
    const remaining = Math.max(0, limit - willBeCount);
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
      ux_status: uxStatus,
      preview_used: previewUsed,
      preview_remaining: previewRemaining,
      preview_limit: PREVIEW_OPUS_LIMIT,
      is_aperçu: Boolean(model._aperçu),
      is_subscriber: SUBSCRIBER_PLANS.has(plan),
      model_tier: model.id?.includes('opus') ? 'opus' : (model.id?.includes('sonnet') ? 'sonnet' : 'haiku'),
      would_use_opus: Boolean(model._standard_free), // hint UI "aurait été Opus en Premium"
      helloasso_url: HELLOASSO_URL,
      soutenir_url: SOUTENIR_URL,
    });
    res.write(`data: ${rateInfoPayload}\n\n`);

    // ── Court-circuit DeepSeek pour méta-questions (≈ 4× moins cher que Haiku) ──
    // Salutations, "tu es qui", "comment ça marche", "merci". Pas de psak ici.
    // Si DeepSeek échoue/timeout, on retombe sur Claude (Haiku) normalement.
    if (model._meta && deepSeekAvailable()) {
      const lastUserText = trimmedMessages[trimmedMessages.length - 1].content;
      const ds = await streamMetaQuestion(lastUserText, (delta) => {
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
          console.log(`[chat.js] usage tracked: ${userId} deepseek:meta +${ds.usage.input_tokens}in/${ds.usage.output_tokens}out ($${dsCost.toFixed(5)})`);
        } catch (err) {
          console.error('[chat.js] Erreur enregistrement usage (deepseek):', err?.message || err);
        }

        res.end();
        return;
      }
      // DeepSeek a échoué → on continue avec Claude Haiku (fallback transparent)
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

    let iterations = 0;
    let stopReason = null;
    const startedAt = Date.now();
    let forcedSynthesis = false;

    // Boucle agentique. À la dernière itération OU si on dépasse FORCE_SYNTHESIS_AFTER_MS,
    // on bascule sur tool_choice:none + thinking désactivé pour FORCER Claude à produire
    // du texte (pas d'autre tool_use possible). Garantit qu'on rend toujours une réponse.
    while (iterations < MAX_TOOL_ITERATIONS) {
      iterations++;
      const elapsedBefore = Date.now() - startedAt;

      const forceSynthesis =
        iterations === MAX_TOOL_ITERATIONS ||
        elapsedBefore > FORCE_SYNTHESIS_AFTER_MS;

      if (forceSynthesis && !forcedSynthesis) {
        forcedSynthesis = true;
        conversation.push({
          role: 'user',
          content: [{
            type: 'text',
            text: 'Tu as déjà consulté suffisamment de sources. Synthétise maintenant ta réponse complète et structurée à ma question initiale, en t\'appuyant uniquement sur ce que tu as déjà recueilli. N\'appelle plus aucun outil.',
          }],
        });
        console.log(`[chat.js] forcing synthesis at iter ${iterations} (elapsed ${elapsedBefore}ms)`);
      }

      const streamParams = {
        model: model.id,
        max_tokens: forceSynthesis ? 1500 : MAX_TOKENS_OUTPUT,
        tools: ALL_TOOLS,
        system: [
          {
            type: 'text',
            text: SYSTEM_PROMPT,
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

      // Hard abort à 80s : dernier filet de sécurité avant le kill Vercel ~90s
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
            res.write(`data: ${JSON.stringify({ type: 'text', delta: event.delta.text })}\n\n`);
          }
        }

        const final = await stream.finalMessage();
        stopReason = final.stop_reason;

        totalUsage.input_tokens += final.usage.input_tokens || 0;
        totalUsage.output_tokens += final.usage.output_tokens || 0;
        totalUsage.cache_creation += final.usage.cache_creation_input_tokens || 0;
        totalUsage.cache_read += final.usage.cache_read_input_tokens || 0;

        conversation.push({ role: 'assistant', content: final.content });

        if (stopReason !== 'tool_use') break;

        const toolUses = final.content.filter(b => b.type === 'tool_use');
        if (toolUses.length === 0) break;

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
          break;
        }
        throw err;
      } finally {
        clearTimeout(abortTimer);
      }
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

      // Coût Claude (modèle effectivement utilisé)
      const claudeCost =
        (totalUsage.input_tokens * model.in / 1000) +
        (totalUsage.output_tokens * model.out / 1000);

      // Coût DeepSeek (reformulation RAG + résumé d'historique, si activé)
      const dsCost =
        (deepseekUsage.input_tokens * DEEPSEEK_PRICING.in / 1000) +
        (deepseekUsage.output_tokens * DEEPSEEK_PRICING.out / 1000);

      const costUsd = claudeCost + dsCost;
      const tokensIn = totalUsage.input_tokens + deepseekUsage.input_tokens;
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

      // Incrément Aperçu Premium si on a servi du Opus à un free/anonyme dans le compteur lifetime
      if (model._aperçu) {
        await kv.incr(`user:preview_used:${userId}`);
        // Pas d'expiration : c'est un compteur lifetime
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

    if (!res.headersSent) {
      if (error instanceof Anthropic.AuthenticationError) {
        return res.status(500).json({ error: 'Configuration serveur invalide (clé API)' });
      }
      if (error instanceof Anthropic.RateLimitError) {
        return res.status(429).json({ error: 'Trop de requêtes. Réessayez dans un instant.' });
      }
      if (error instanceof Anthropic.APIError) {
        return res.status(error.status || 500).json({ error: error.message });
      }
      return res.status(500).json({ error: 'Erreur interne du serveur' });
    }

    try {
      const errorPayload = JSON.stringify({
        type: 'error',
        error: error.message || 'Erreur lors de la génération',
      });
      res.write(`data: ${errorPayload}\n\n`);
      res.end();
    } catch (_) {
      // Connection closed
    }
  }
}
