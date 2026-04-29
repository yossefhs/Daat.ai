// Vercel Serverless Function — Endpoint chat de Daat (l'IA pédagogique de DAAT.AI)
// Appelle Claude Opus 4.7 avec :
// - Prompt caching (TTL 1h) sur le system prompt long
// - Adaptive thinking (effort: high)
// - Streaming SSE pour l'affichage progressif
// - Multi-turn (l'historique est envoyé par le client à chaque appel)

import Anthropic from '@anthropic-ai/sdk';
import { SYSTEM_PROMPT } from './_system-prompt.js';

const client = new Anthropic();

export default async function handler(req, res) {
  // CORS preflight (sécurité : également défini dans vercel.json)
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

    // Garde-fou : tronquer les conversations très longues (garder les 24 derniers tours)
    const trimmedMessages = messages.slice(-24);

    // Première message doit être "user"
    if (trimmedMessages[0].role !== 'user') {
      return res.status(400).json({ error: 'Le premier message doit être de l\'utilisateur' });
    }

    // En-têtes SSE pour streaming
    res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache, no-transform');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no'); // désactive le buffering proxy
    res.flushHeaders?.();

    const stream = client.messages.stream({
      model: 'claude-opus-4-7',
      max_tokens: 8192,
      thinking: { type: 'adaptive' },
      output_config: { effort: 'high' },
      system: [
        {
          type: 'text',
          text: SYSTEM_PROMPT,
          cache_control: { type: 'ephemeral', ttl: '1h' },
        },
      ],
      messages: trimmedMessages,
    });

    // Stream les deltas de texte au client
    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
        const payload = JSON.stringify({ type: 'text', delta: event.delta.text });
        res.write(`data: ${payload}\n\n`);
      }
    }

    // Récupère le message final pour l'usage et les métadonnées de cache
    const final = await stream.finalMessage();
    const donePayload = JSON.stringify({
      type: 'done',
      stop_reason: final.stop_reason,
      usage: {
        input_tokens: final.usage.input_tokens,
        output_tokens: final.usage.output_tokens,
        cache_creation: final.usage.cache_creation_input_tokens || 0,
        cache_read: final.usage.cache_read_input_tokens || 0,
      },
    });
    res.write(`data: ${donePayload}\n\n`);
    res.end();
  } catch (error) {
    console.error('[Daat chat API] error:', error);

    // Si la réponse n'a pas encore commencé, envoyer JSON
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

    // Sinon — envoyer un événement d'erreur dans le flux SSE
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
