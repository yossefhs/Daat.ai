// /api/chat-corpus
//
// POST { question: string, lang?: 'fr'|'en'|'he' }
//   → SSE stream :
//     event: search    data: { results: [...], keyTokens, totalChunks }
//     event: delta     data: { text }  (Haiku reformulation streaming)
//     event: done      data: { usage: { input_tokens, output_tokens }, cost_eur }
//   ou
//     event: nomatch   data: { keyTokens, totalChunks }
//     event: done      data: { ... }
//
// GET ?stats=1 → { totalChunks, totalSimanim }
//
// Coût ~0.002 € par requête (Haiku 4.5) vs ~0.12 € en Opus.
// Conçu pour être appelé directement par /poc-corpus.html en attendant
// l'intégration dans /api/chat.

import Anthropic from '@anthropic-ai/sdk';
import { searchCorpus, getCorpusStats } from './_corpus-search.js';
import { kv } from './_kv.js';
import { getClientIp } from './_http.js';

const client = new Anthropic();

const HAIKU = { id: 'claude-haiku-4-5', in: 0.001, out: 0.005 }; // €/1000 tokens
const MAX_OUTPUT_TOKENS = 350;
const SCORE_THRESHOLD = 3.0; // en dessous, on considère "match faible"

// ── Anti-abus : endpoint public non authentifié qui appelle l'API payante Haiku.
// On limite par IP et globalement (par jour) pour éviter qu'un tiers ne fasse
// grimper la facture en bouclant. Surchargeable via variables d'environnement.
const RL_PER_IP_DAY = parseInt(process.env.CORPUS_RL_PER_IP_DAY || '60', 10);
const RL_GLOBAL_DAY = parseInt(process.env.CORPUS_RL_GLOBAL_DAY || '5000', 10);

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// Incrémente les compteurs IP + global et renvoie true si la limite est dépassée.
// En cas d'erreur KV (ou KV non configuré), on laisse passer (fail-open) pour ne
// pas casser l'endpoint si Redis est indisponible.
async function isRateLimited(ip) {
  try {
    const today = new Date().toISOString().slice(0, 10);
    const ipKey = `corpus:rl:ip:${ip}:${today}`;
    const globalKey = `corpus:rl:global:${today}`;

    const ipCount = await kv.incr(ipKey);
    if (ipCount === 1) await kv.expire(ipKey, 24 * 60 * 60);
    if (ipCount > RL_PER_IP_DAY) return true;

    const globalCount = await kv.incr(globalKey);
    if (globalCount === 1) await kv.expire(globalKey, 24 * 60 * 60);
    if (globalCount > RL_GLOBAL_DAY) return true;

    return false;
  } catch (err) {
    console.error('[chat-corpus] rate-limit KV error (fail-open):', err?.message || err);
    return false;
  }
}

function sseWrite(res, event, data) {
  res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
}

function buildSystemPrompt(lang) {
  const langName = lang === 'en' ? 'English' : lang === 'he' ? 'Hebrew' : 'French';
  return `Tu es l'assistant de DAAT — site d'étude halakhique du Rav Yossef Haim Samama.

Tu reçois :
1. Une QUESTION d'utilisateur sur les hilkhot Shabbat
2. UN EXTRAIT précis du corpus écrit par le Rav (avec son siman + section)

Ta tâche : répondre à la question en reformulant l'extrait en 2-4 phrases conversationnelles et fluides.

RÈGLES STRICTES :
- RESTE FIDÈLE à l'extrait. N'invente AUCUNE halakha qui n'y est pas explicitement.
- Si l'extrait ne couvre pas vraiment la nuance demandée, dis-le honnêtement : « L'extrait ne couvre pas directement cette nuance — pour une réflexion contextuelle, repose la question à Daat IA en mode étendu. »
- Termine TOUJOURS par la source au format : « *Source : Siman X §Y — [titre de section]* »
- Pour les décisions pratiques sensibles ou cas-limites, ajoute : « consulte un Rav pour ton cas précis. »
- Pas de markdown lourd (pas de listes à puces sauf si vraiment nécessaire), texte naturel.
- Conserve les termes hébreux en transcription (borer, bishoul, mouktsé) — ne les sur-traduis pas.
- Réponds dans la langue de la question (par défaut : ${langName}).
- Ne mentionne PAS que tu reformules un extrait — réponds DIRECTEMENT comme si tu savais.`;
}

function buildUserMessage(question, topResult, otherResults) {
  const sec = topResult.subsection ? ` · ${topResult.subsection}` : '';
  let msg = `QUESTION DE L'UTILISATEUR :\n${question}\n\n`;
  msg += `EXTRAIT DU CORPUS (Siman ${topResult.siman} — ${topResult.simanTitle} · ${topResult.sectionTitle}${sec}) :\n`;
  msg += topResult.text.trim();
  if (otherResults && otherResults.length > 0) {
    msg += `\n\nAUTRES EXTRAITS PERTINENTS (en complément, plus faibles) :\n`;
    otherResults.slice(0, 2).forEach((r, i) => {
      const ss = r.subsection ? ` · ${r.subsection}` : '';
      msg += `[${i + 1}] Siman ${r.siman} · ${r.sectionTitle}${ss} — ${r.text.trim().slice(0, 250)}…\n`;
    });
  }
  return msg;
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(204).end();

  if (req.method === 'GET') {
    if (req.query?.stats === '1') {
      try {
        const stats = getCorpusStats();
        return res.status(200).json({ ok: true, ...stats });
      } catch (e) {
        return res.status(500).json({ error: e?.message || 'stats error' });
      }
    }
    return res.status(405).json({ error: 'POST required' });
  }

  if (req.method !== 'POST') return res.status(405).json({ error: 'POST required' });

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  const question = String(body?.question || '').trim();
  const lang = (body?.lang || 'fr').slice(0, 2);

  if (!question) return res.status(400).json({ error: 'question required' });
  if (question.length > 800) return res.status(400).json({ error: 'question too long (max 800 chars)' });

  // ── Anti-abus : limite par IP + globale (avant tout appel payant) ──
  if (await isRateLimited(getClientIp(req))) {
    res.setHeader('Retry-After', '3600');
    return res.status(429).json({ error: 'Trop de requêtes. Réessaie plus tard.' });
  }

  // ── Recherche corpus ──
  let searchResult;
  try {
    searchResult = searchCorpus(question, { limit: 3, minScore: 1.5 });
  } catch (e) {
    console.error('[chat-corpus] search error:', e);
    return res.status(500).json({ error: 'corpus search failed' });
  }

  // ── Setup SSE ──
  res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache, no-transform');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no');
  if (typeof res.flushHeaders === 'function') res.flushHeaders();

  // ── Cas 1 : aucun match ──
  if (!searchResult.results.length) {
    sseWrite(res, 'nomatch', {
      keyTokens: searchResult.keyTokens,
      totalChunks: searchResult.totalChunks,
      message: 'Aucun extrait pertinent dans le corpus indexé. Fallback Daat IA recommandé.',
    });
    sseWrite(res, 'done', { usage: { input_tokens: 0, output_tokens: 0 }, cost_eur: 0 });
    return res.end();
  }

  // ── Envoie le résultat de recherche tout de suite (feedback rapide) ──
  sseWrite(res, 'search', {
    results: searchResult.results,
    keyTokens: searchResult.keyTokens,
    totalChunks: searchResult.totalChunks,
    topScore: searchResult.results[0].score,
    confidence: searchResult.results[0].score >= SCORE_THRESHOLD ? 'high' : 'medium',
  });

  // ── Cas 2 : match → Haiku reformule ──
  const top = searchResult.results[0];
  const others = searchResult.results.slice(1);
  const systemPrompt = buildSystemPrompt(lang);
  const userMsg = buildUserMessage(question, top, others);

  let inputTokens = 0;
  let outputTokens = 0;

  try {
    const stream = client.messages.stream({
      model: HAIKU.id,
      max_tokens: MAX_OUTPUT_TOKENS,
      system: systemPrompt,
      messages: [{ role: 'user', content: userMsg }],
    });

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta?.type === 'text_delta') {
        const text = event.delta.text || '';
        if (text) sseWrite(res, 'delta', { text });
      } else if (event.type === 'message_start' && event.message?.usage) {
        inputTokens = event.message.usage.input_tokens || 0;
      } else if (event.type === 'message_delta' && event.usage) {
        outputTokens = event.usage.output_tokens || outputTokens;
      }
    }

    const final = await stream.finalMessage();
    if (final?.usage) {
      inputTokens = final.usage.input_tokens || inputTokens;
      outputTokens = final.usage.output_tokens || outputTokens;
    }
  } catch (err) {
    console.error('[chat-corpus] Haiku stream error:', err);
    sseWrite(res, 'error', { message: err?.message || 'Haiku error' });
    sseWrite(res, 'done', { usage: { input_tokens: inputTokens, output_tokens: outputTokens }, cost_eur: 0 });
    return res.end();
  }

  const costEur = (inputTokens * HAIKU.in + outputTokens * HAIKU.out) / 1000;
  sseWrite(res, 'done', {
    usage: { input_tokens: inputTokens, output_tokens: outputTokens },
    cost_eur: costEur,
    model: HAIKU.id,
  });
  return res.end();
}
