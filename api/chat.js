// Vercel Serverless Function — Endpoint chat de Daat (l'IA pédagogique de DAAT.AI)
// - Claude Opus 4.7 avec tool use (Sefaria API) en boucle agentique
// - Prompt caching (TTL 1h) sur le system prompt long
// - Adaptive thinking (effort: high)
// - Streaming SSE pour l'affichage progressif
// - Multi-turn (l'historique est envoyé par le client à chaque appel)

import Anthropic from '@anthropic-ai/sdk';
import { SYSTEM_PROMPT } from './_system-prompt.js';
import { SEFARIA_TOOLS, executeSefariaTool } from './_sefaria.js';

const client = new Anthropic();

const MAX_TOOL_ITERATIONS = 6; // garde-fou agentic loop

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

      // Notifier le client qu'on commence (utile pour les itérations avec tool use)
      if (iterations > 1) {
        const noticePayload = JSON.stringify({
          type: 'notice',
          message: `Recherche dans Sefaria... (${iterations - 1})`,
        });
        res.write(`data: ${noticePayload}\n\n`);
      }

      const stream = client.messages.stream({
        model: 'claude-opus-4-7',
        max_tokens: 8192,
        thinking: { type: 'adaptive' },
        output_config: { effort: 'high' },
        tools: SEFARIA_TOOLS,
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

      // Exécuter chaque outil (en parallèle)
      const toolResults = await Promise.all(
        toolUses.map(async (tu) => {
          try {
            const result = await executeSefariaTool(tu.name, tu.input);
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
