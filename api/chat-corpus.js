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
// Budget de sortie : assez large pour accroche + raisonnement + nuances + source
// sans jamais tronquer. 1200 tokens ≈ ~900 mots FR ≈ $0.006 (20× moins qu'Opus).
const MAX_OUTPUT_TOKENS = parseInt(process.env.CORPUS_MAX_TOKENS || '1200', 10);
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

function buildSystemPrompt(lang, section) {
  const langName = lang === 'en' ? 'English' : lang === 'he' ? 'Hebrew' : 'French';
  const domain = section === 'yoreh-deah'
    ? "les hilkhot Issour ve-Heter (cacheroute : bassar be-halav, taarovot…)"
    : 'les hilkhot Shabbat';
  const terms = section === 'yoreh-deah'
    ? 'bassar be-halav, taarovet, ben yomo, nat bar nat'
    : 'borer, bishoul, mouktsé';
  return `Tu es Daat, l'assistant halakhique de DAAT — site d'étude du Rav Yossef Haim Samama.

CONTEXTE : tu reçois une question d'utilisateur sur ${domain} et UN EXTRAIT précis du corpus (écrit par le Rav) qui répond à cette question.

TA MISSION : donner une réponse claire, complète et engageante, fidèle à l'extrait. L'utilisateur doit avoir la réponse dès la première ligne, puis comprendre pourquoi.

STRUCTURE ATTENDUE :
1. **Phrase d'accroche** (1re ligne) : la réponse directe — permis, interdit, ça dépend — avec l'idée-clé qui résume ("Oui, à condition que…", "Non, car il y a un problème de …", "Ça dépend : si …, alors …"). L'accroche seule doit déjà répondre.
2. **Raisonnement** en 2-4 phrases : quelle est la mélakha (ou le principe halakhique) en jeu, la logique du psak, les sources ou opinions clés si l'extrait les mentionne.
3. **Cas particuliers ou nuances** : uniquement s'ils sont dans l'extrait (ne pas extrapoler).
4. **Source finale** au format exact : *Source : Siman X · [titre de section]*

RÈGLES STRICTES :
- RESTE FIDÈLE à l'extrait. N'invente AUCUNE halakha qui n'y est pas explicitement.
- Termine TOUJOURS ta réponse par la ligne source. Ne coupe jamais avant elle — elle est la signature du psak.
- Si l'extrait n'aborde pas vraiment la question : « L'extrait du corpus traite de [sujet réel], mais ta question porte sur [Y] — pour une réflexion précise sur ce point, repose la question à Daat IA en mode étendu. » (puis source).
- Pour décision pratique sensible : ajoute « Consulte un Rav pour ton cas précis. » AVANT la source.
- Conserve les termes hébreux en transcription (${terms}) — ne les sur-traduis pas.
- Réponds dans la langue de la question (par défaut : ${langName}).
- Ton conversationnel et pédagogique, comme si tu expliquais à un ami curieux. Pas de listes à puces sauf vraie nécessité. Pas de markdown lourd.
- Ne dis JAMAIS que tu reformules un extrait — parle directement du sujet.`;
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
  const section = body?.section === 'yoreh-deah' ? 'yoreh-deah' : 'orach-chaim';

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
    searchResult = searchCorpus(question, { limit: 3, minScore: 1.5, section });
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

  // ── Mode brut (body.raw) : renvoie les extraits du corpus SANS reformulation
  // IA — zéro coût, zéro modèle. La base doit être consultable telle quelle.
  if (body?.raw === true || body?.raw === '1' || body?.raw === 1) {
    sseWrite(res, 'done', { usage: { input_tokens: 0, output_tokens: 0 }, cost_eur: 0, raw: true });
    return res.end();
  }

  // ── Cas 2 : match → Haiku reformule ──
  const top = searchResult.results[0];
  const others = searchResult.results.slice(1);
  const systemPrompt = buildSystemPrompt(lang, section);
  const userMsg = buildUserMessage(question, top, others);

  let inputTokens = 0;
  let outputTokens = 0;
  let stopReason = null;

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
    stopReason = final?.stop_reason || null;
    if (stopReason === 'max_tokens') {
      console.warn(`[chat-corpus] response TRUNCATED (hit max_tokens=${MAX_OUTPUT_TOKENS}) siman-${top.siman}`);
      sseWrite(res, 'delta', { text: '\n\n_(Réponse tronquée par la limite de longueur — précise ta question pour la suite du raisonnement.)_' });
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
    stop_reason: stopReason,
    model: HAIKU.id,
  });
  return res.end();
}
