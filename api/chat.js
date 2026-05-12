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
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
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

    // Vérifier les limites de taux par utilisateur
    const user = getUserFromRequest(req);
    const email = user?.email || 'anonymous';
    const today = new Date().toISOString().slice(0, 10);
    const rateKey = `rate:${email}:${today}`;
    const plan = (await kv.get(`user:plan:${email}`)) || 'free';
    const limits = { free: 20, premium: 9999, anonymous: 5 };
    const limit = limits[plan] || 5;
    const currentCount = (await kv.get(rateKey)) || 0;

    if (currentCount >= limit) {
      const resetTime = new Date();
      resetTime.setDate(resetTime.getDate() + 1);
      resetTime.setHours(0, 0, 0, 0);
      const resetIso = resetTime.toISOString();
      return res.status(400).json({
        type: 'error',
        error: {
          type: 'invalid_request_error',
          message: `You have reached your specified API usage limits. You will regain access on ${resetIso.split('T')[0]} at 00:00 UTC.`,
        },
        request_id: `req_${Date.now()}`,
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
        const user = getUserFromRequest(req);
        const email = user?.email || 'anonymous';
        const today = new Date().toISOString().slice(0, 10);

        // Coûts Claude Opus 4.7 (prix actuels)
        const inputCost = 0.015 / 1000; // $0.015 par 1K tokens
        const outputCost = 0.06 / 1000; // $0.06 par 1K tokens
        const costUsd = (totalUsage.input_tokens * inputCost) + (totalUsage.output_tokens * outputCost);

        // Incrémenter les stats globales
        const globalKey = `usage:global:${today}`;
        const globalData = (await kv.get(globalKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        await kv.set(globalKey, {
          tokens_in: globalData.tokens_in + totalUsage.input_tokens,
          tokens_out: globalData.tokens_out + totalUsage.output_tokens,
          cost_usd: parseFloat((globalData.cost_usd + costUsd).toFixed(6)),
          count: globalData.count + 1,
        });

        // Incrémenter les stats par utilisateur
        const userKey = `usage:${email}:${today}`;
        const userData = (await kv.get(userKey)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        await kv.set(userKey, {
          tokens_in: userData.tokens_in + totalUsage.input_tokens,
          tokens_out: userData.tokens_out + totalUsage.output_tokens,
          cost_usd: parseFloat((userData.cost_usd + costUsd).toFixed(6)),
          count: userData.count + 1,
        });

        // Incrémenter le compteur de questions (rate limit)
        const rateKey = `rate:${email}:${today}`;
        await kv.incr(rateKey);
        if (await kv.ttl(rateKey) === -1) {
          await kv.expire(rateKey, 24 * 60 * 60);
        }

        // Ajouter le log d'utilisation
        const logEntry = {
          ts: new Date().toISOString(),
          user: email,
          tokens_in: totalUsage.input_tokens,
          tokens_out: totalUsage.output_tokens,
          cost_usd: costUsd,
          model: 'claude-opus-4-7',
          iterations,
          stop_reason: stopReason,
        };
        await kv.lpush('logs:usage', JSON.stringify(logEntry));
        // Garder seulement les 500 derniers logs
        await kv.ltrim('logs:usage', 0, 499);

        // Ajouter l'email à la liste des utilisateurs connus
        await kv.sadd('users:known', email);
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
