// Client DeepSeek — fallback économique pour tâches "plomberie" autour de Claude.
//
// Activation : poser DEEPSEEK_API_KEY dans les variables d'env Vercel.
// Si la clé est absente, toutes les fonctions retournent null et le code
// appelant retombe sur Claude (Haiku/Sonnet). Aucune régression possible.
//
// Pricing DeepSeek (mai 2026, chat-v3) :
//   input  = $0.27 / 1M tokens  → 0.00027 / 1K
//   output = $1.10 / 1M tokens  → 0.0011  / 1K
// ≈ 4× moins cher que Haiku, ≈ 15× moins cher que Sonnet, ≈ 75× moins cher qu'Opus.
//
// Usages chez DAAT :
//   1. streamMetaQuestion()   — méta-questions courtes (salutations, "tu es qui")
//   2. summarizeOlderTurns()  — compaction d'historique > 16 tours
//   3. reformulateForCorpus() — pré-recherche RAG (élimine un round-trip Claude)
//
// JAMAIS sur le contenu halakhique final : Claude reste seul à émettre du psak.

const ENDPOINT = 'https://api.deepseek.com/v1/chat/completions';
const MODEL = 'deepseek-chat';
export const DEEPSEEK_PRICING = { in: 0.00027, out: 0.0011 }; // $ per 1K tokens

export function deepSeekAvailable() {
  return Boolean(process.env.DEEPSEEK_API_KEY);
}

async function call(messages, { max_tokens = 400, temperature = 0.2, timeout = 8000 } = {}) {
  if (!deepSeekAvailable()) return null;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(ENDPOINT, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.DEEPSEEK_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ model: MODEL, messages, max_tokens, temperature, stream: false }),
      signal: controller.signal,
    });
    if (!res.ok) {
      console.error('[deepseek] HTTP', res.status, (await res.text()).slice(0, 200));
      return null;
    }
    const data = await res.json();
    return {
      text: data.choices?.[0]?.message?.content || '',
      usage: {
        input_tokens: data.usage?.prompt_tokens || 0,
        output_tokens: data.usage?.completion_tokens || 0,
      },
    };
  } catch (err) {
    console.error('[deepseek] call error:', err?.message || err);
    return null;
  } finally {
    clearTimeout(timer);
  }
}

// 1. Méta-questions en streaming SSE (remplace Haiku pour bonjour/merci/etc.)
export async function streamMetaQuestion(userText, onDelta) {
  if (!deepSeekAvailable()) return null;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 12000);
  try {
    const res = await fetch(ENDPOINT, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.DEEPSEEK_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 200,
        temperature: 0.4,
        stream: true,
        messages: [
          {
            role: 'system',
            content:
              "Tu es Daat, l'IA pédagogique de DAAT TORAH (https://daattorah.com), une plateforme qui aide à étudier la halakha (loi juive) en français. Tu réponds en français, brièvement (1 à 3 phrases), UNIQUEMENT aux questions conversationnelles : salutations (bonjour, shalom), remerciements, \"tu es qui\", \"comment ça marche\". Reste chaleureux et concis. Si la question touche à la halakha, NE RÉPONDS PAS sur le fond — dis simplement : \"Pose-moi ta question halakhique précise, je suis là pour étudier avec toi.\" Tu cites Daat HaRav, le Rav Yossef Haim Samama, qui supervise le site, si on te demande qui te supervise.",
          },
          { role: 'user', content: userText },
        ],
      }),
      signal: controller.signal,
    });
    if (!res.ok || !res.body) {
      console.error('[deepseek-stream] HTTP', res.status);
      return null;
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';
    let usage = { input_tokens: 0, output_tokens: 0 };
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = line.slice(6).trim();
        if (payload === '[DONE]') continue;
        try {
          const json = JSON.parse(payload);
          const delta = json.choices?.[0]?.delta?.content;
          if (delta) {
            fullText += delta;
            try { onDelta?.(delta); } catch { /* client gone */ }
          }
          if (json.usage) {
            usage = {
              input_tokens: json.usage.prompt_tokens || 0,
              output_tokens: json.usage.completion_tokens || 0,
            };
          }
        } catch { /* skip malformed chunks */ }
      }
    }
    return { text: fullText, usage };
  } catch (err) {
    console.error('[deepseek-stream] error:', err?.message || err);
    return null;
  } finally {
    clearTimeout(timer);
  }
}

// 2. Résumé compact d'anciens tours de conversation (pour éviter de tout renvoyer à Claude).
export async function summarizeOlderTurns(turns) {
  if (!deepSeekAvailable() || !turns?.length) return null;
  const transcript = turns
    .map(t => `${t.role === 'user' ? 'Q' : 'R'}: ${String(t.content).slice(0, 800)}`)
    .join('\n');
  const r = await call(
    [
      {
        role: 'system',
        content:
          'Tu résumes une conversation Q&R sur la halakha juive. Produit un résumé factuel en français, 4 à 7 lignes, qui préserve : (1) les sujets halakhiques abordés, (2) les sources citées (siman, seif, auteurs), (3) les conclusions atteintes, (4) les préférences/contexte exprimés par l\'utilisateur. Aucune paraphrase superflue. Aucune information inventée. Commence directement par le résumé.',
      },
      { role: 'user', content: `Résume la conversation suivante :\n\n${transcript}` },
    ],
    { max_tokens: 350, temperature: 0 }
  );
  return r ? { text: r.text.trim(), usage: r.usage } : null;
}

// 3. Reformulation pour recherche corpus : 1 à 3 requêtes courtes en JSON.
export async function reformulateForCorpus(userText) {
  if (!deepSeekAvailable()) return null;
  const r = await call(
    [
      {
        role: 'system',
        content:
          'Tu reformules une question halakhique francophone en 1 à 3 requêtes courtes pour un moteur full-text. Réponds UNIQUEMENT en JSON valide : {"queries": ["...", "..."]}. Chaque requête : 2 à 6 mots-clés essentiels (français + termes halakhiques translittérés type "muktsé", "kavanah", "shabbat", "berakha", "siman 246"). Pas de phrase complète. Pas de ponctuation autre que les espaces. Pas de commentaire. Si la question est purement conversationnelle, retourne {"queries": []}.',
      },
      { role: 'user', content: userText },
    ],
    { max_tokens: 150, temperature: 0 }
  );
  if (!r?.text) return null;
  try {
    const match = r.text.match(/\{[\s\S]*\}/);
    if (!match) return null;
    const parsed = JSON.parse(match[0]);
    const queries = Array.isArray(parsed.queries)
      ? parsed.queries.filter(q => typeof q === 'string' && q.trim().length >= 2).slice(0, 3)
      : [];
    return { queries, usage: r.usage };
  } catch {
    return null;
  }
}
