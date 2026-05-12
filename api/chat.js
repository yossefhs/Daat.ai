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
import { CORPUS_TOOLS, executeCorpusTool } from './_corpus.js';
import { MAREH_MEKOMOT_TOOLS, executeMarehMekomotTool } from './_mareh_mekomot.js';
import { getUserFromRequest } from './_auth.js';

const client = new Anthropic();

const MAX_TOOL_ITERATIONS = 8; // agentic loop (mareh_mekomot + corpus + Sefaria)
const ALL_TOOLS = [...MAREH_MEKOMOT_TOOLS, ...CORPUS_TOOLS, ...SEFARIA_TOOLS];

// ── Limites quotidiennes par plan ──────────────────────────────────────────
const DAILY_LIMITS = {
  anonymous: 3,    // visiteur sans compte
  free: 15,        // compte email (OTP)
  premium: 99999,  // donateur — illimité
};
const HELLOASSO_URL = 'https://www.helloasso.com/associations/association-hessed/formulaires/9';
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

// Renvoie { userId, plan, isGuest, guestIdSetCookie }
async function identifyUser(req) {
  const user = getUserFromRequest(req);
  if (user?.email) {
    const plan = (await kv.get(`user:plan:${user.email}`)) || 'free';
    return { userId: user.email, plan, isGuest: false, guestIdSetCookie: null };
  }
  // Anonyme — lire/créer guest_id
  let guestId = readCookie(req, GUEST_COOKIE);
  let setCookie = null;
  if (!guestId || !guestId.startsWith('guest_')) {
    guestId = genGuestId();
    // Cookie cross-site (le chat tourne sur daatai.vercel.app, embarqué dans daattorah.com)
    setCookie = `${GUEST_COOKIE}=${encodeURIComponent(guestId)}; Path=/; HttpOnly; Secure; SameSite=None; Max-Age=${365 * 24 * 60 * 60}`;
  }
  return { userId: guestId, plan: 'anonymous', isGuest: true, guestIdSetCookie: setCookie };
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
    const { userId, plan, isGuest, guestIdSetCookie } = await identifyUser(req);
    const today = new Date().toISOString().slice(0, 10);
    const rateKey = `rate:${userId}:${today}`;
    const limit = DAILY_LIMITS[plan] || DAILY_LIMITS.anonymous;
    const currentCount = parseInt((await kv.get(rateKey)) || 0, 10);

    // Définir le cookie guest_id si nouveau visiteur
    if (guestIdSetCookie) {
      res.setHeader('Set-Cookie', guestIdSetCookie);
    }

    // Limite atteinte → renvoyer un blocage clair avec lien HelloAsso
    if (currentCount >= limit) {
      const resetTime = new Date();
      resetTime.setDate(resetTime.getDate() + 1);
      resetTime.setHours(0, 0, 0, 0);
      return res.status(429).json({
        error: 'limit_reached',
        type: 'limit_reached',
        plan,
        count: currentCount,
        limit,
        is_guest: isGuest,
        reset_date: resetTime.toISOString(),
        helloasso_url: HELLOASSO_URL,
        message: isGuest
          ? `Tu as utilisé tes ${limit} questions gratuites aujourd'hui. Connecte-toi avec ton email pour 15 questions/jour, ou soutiens DAAT pour un accès illimité.`
          : `Tu as atteint ta limite quotidienne de ${limit} questions. Reviens demain ou soutiens DAAT pour un accès illimité.`,
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

    // Garder les 24 derniers tours
    const trimmedMessages = messages.slice(-24);

    if (trimmedMessages[0].role !== 'user') {
      return res.status(400).json({ error: 'Le premier message doit être de l\'utilisateur' });
    }

    // En-têtes SSE
    res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache, no-transform');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');
    res.flushHeaders?.();

    // Premier event : info sur la consommation actuelle (pour bannière progressive)
    // currentCount = avant cette question. La question en cours sera ajoutée à la fin.
    const willBeCount = currentCount + 1;
    const remaining = Math.max(0, limit - willBeCount);
    const rateInfoPayload = JSON.stringify({
      type: 'rate_info',
      plan,
      is_guest: isGuest,
      count: willBeCount,
      limit,
      remaining,
      helloasso_url: HELLOASSO_URL,
    });
    res.write(`data: ${rateInfoPayload}\n\n`);

    // Conversation working set : on travaille avec un format de blocs (pour le tool use)
    // Le client envoie des messages texte simple — on les convertit en blocs.
    let conversation = trimmedMessages.map(m => ({
      role: m.role,
      content: [{ type: 'text', text: m.content }],
    }));

    const totalUsage = {
      input_tokens: 0,
      output_tokens: 0,
      cache_creation: 0,
      cache_read: 0,
    };

    let iterations = 0;
    let stopReason = null;

    // Boucle agentique : tant que Claude veut utiliser un outil, on exécute et on relance.
    while (iterations < MAX_TOOL_ITERATIONS) {
      iterations++;

      // (Plus de notice générique — chaque tool_use envoie sa propre notice détaillée)

      const stream = client.messages.stream({
        model: 'claude-opus-4-7',
        max_tokens: 8192,
        thinking: { type: 'adaptive' },
        output_config: { effort: 'high' },
        tools: ALL_TOOLS,
        system: [
          {
            type: 'text',
            text: SYSTEM_PROMPT,
            cache_control: { type: 'ephemeral', ttl: '1h' },
          },
        ],
        messages: conversation,
      });

      // Stream les deltas de texte au client (pour la réponse finale uniquement)
      for await (const event of stream) {
        if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
          const payload = JSON.stringify({ type: 'text', delta: event.delta.text });
          res.write(`data: ${payload}\n\n`);
        }
      }

      const final = await stream.finalMessage();
      stopReason = final.stop_reason;

      // Cumuler l'usage
      totalUsage.input_tokens += final.usage.input_tokens || 0;
      totalUsage.output_tokens += final.usage.output_tokens || 0;
      totalUsage.cache_creation += final.usage.cache_creation_input_tokens || 0;
      totalUsage.cache_read += final.usage.cache_read_input_tokens || 0;

      // Ajouter la réponse complète de Claude (tous les blocs : text + tool_use) à la conversation
      conversation.push({
        role: 'assistant',
        content: final.content,
      });

      // Si pas d'appel d'outil → fin de la conversation
      if (stopReason !== 'tool_use') {
        break;
      }

      // Récupérer tous les tool_use de la réponse
      const toolUses = final.content.filter(b => b.type === 'tool_use');
      if (toolUses.length === 0) {
        break; // safety
      }

      // Exécuter chaque outil (en parallèle, dispatch sur le bon executor)
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
            return {
              type: 'tool_result',
              tool_use_id: tu.id,
              content: result,
            };
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

      // Notifier le client des sources consultées
      for (const tu of toolUses) {
        const sourcePayload = JSON.stringify({
          type: 'tool_use',
          tool: tu.name,
          input: tu.input,
        });
        res.write(`data: ${sourcePayload}\n\n`);
      }

      // Ajouter les résultats d'outils comme un message user
      conversation.push({
        role: 'user',
        content: toolResults,
      });
    }

    // Envoyer le done final
    const donePayload = JSON.stringify({
      type: 'done',
      stop_reason: stopReason,
      iterations,
      usage: totalUsage,
    });
    res.write(`data: ${donePayload}\n\n`);
    res.end();

    // Enregistrer l'usage dans Vercel KV (analytics non-bloquant)
    (async () => {
      try {
        const todayKey = new Date().toISOString().slice(0, 10);

        // Coûts Claude Opus 4.7 (prix actuels)
        const inputCost = 0.015 / 1000; // $0.015 par 1K tokens
        const outputCost = 0.06 / 1000; // $0.06 par 1K tokens
        const costUsd = (totalUsage.input_tokens * inputCost) + (totalUsage.output_tokens * outputCost);

        // Incrémenter les stats globales
        const globalKey = `usage:global:${todayKey}`;
        const globalData = (await kv.get(globalKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        await kv.set(globalKey, {
          tokens_in: globalData.tokens_in + totalUsage.input_tokens,
          tokens_out: globalData.tokens_out + totalUsage.output_tokens,
          cost_usd: parseFloat((globalData.cost_usd + costUsd).toFixed(6)),
          count: globalData.count + 1,
        });

        // Incrémenter les stats par utilisateur (email OU guest_id)
        const userKey = `usage:${userId}:${todayKey}`;
        const userData = (await kv.get(userKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        await kv.set(userKey, {
          tokens_in: userData.tokens_in + totalUsage.input_tokens,
          tokens_out: userData.tokens_out + totalUsage.output_tokens,
          cost_usd: parseFloat((userData.cost_usd + costUsd).toFixed(6)),
          count: userData.count + 1,
        });

        // Incrémenter le compteur de questions (rate limit quotidien)
        await kv.incr(rateKey);
        const ttl = await kv.ttl(rateKey);
        if (ttl === -1 || ttl === -2) {
          await kv.expire(rateKey, 24 * 60 * 60);
        }

        // Log d'utilisation (rolling 500 dernières)
        const logEntry = {
          ts: new Date().toISOString(),
          user: userId,
          is_guest: isGuest,
          plan,
          tokens_in: totalUsage.input_tokens,
          tokens_out: totalUsage.output_tokens,
          cost_usd: costUsd,
          model: 'claude-opus-4-7',
          iterations,
          stop_reason: stopReason,
        };
        await kv.lpush('logs:usage', JSON.stringify(logEntry));
        await kv.ltrim('logs:usage', 0, 499);

        // Ajouter à la liste des utilisateurs connus (email OU guest_id)
        await kv.sadd('users:known', userId);
      } catch (err) {
        console.error('[chat.js] Erreur enregistrement usage:', err.message);
      }
    })();
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
