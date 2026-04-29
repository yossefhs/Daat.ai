// Module corpus DAAT — base de connaissance interne du site
// Indexe le contenu de data/corpus.json + (futur) entrées dynamiques via Vercel KV.
//
// Expose deux outils Claude :
// - daat_search_corpus : cherche dans le corpus DAAT par mots-clés / tags
// - daat_get_content : récupère un contenu précis par son ID

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CORPUS_PATH = join(__dirname, '..', 'data', 'corpus.json');

let _corpus = null;

function loadCorpus() {
  if (_corpus) return _corpus;
  try {
    const raw = readFileSync(CORPUS_PATH, 'utf-8');
    _corpus = JSON.parse(raw);
  } catch (err) {
    console.error('[corpus] Failed to load corpus.json:', err.message);
    _corpus = { meta: {}, entries: [] };
  }
  return _corpus;
}

/**
 * Récupère toutes les entrées (statiques + dynamiques via KV si dispo).
 */
export async function getAllEntries() {
  const staticEntries = loadCorpus().entries || [];
  const dynamicEntries = await loadDynamicEntries();
  return [...staticEntries, ...dynamicEntries];
}

/**
 * Charge les entrées dynamiques depuis Vercel KV si configuré.
 * Retourne [] si KV non configuré (silencieux).
 */
async function loadDynamicEntries() {
  // Vercel KV via @vercel/kv — chargé lazy pour ne pas bloquer si non installé
  if (!process.env.KV_REST_API_URL || !process.env.KV_REST_API_TOKEN) {
    return [];
  }
  try {
    const { kv } = await import('@vercel/kv');
    const ids = (await kv.smembers('daat:corpus:ids')) || [];
    if (ids.length === 0) return [];
    const entries = await Promise.all(
      ids.map(async (id) => {
        try {
          return await kv.get(`daat:corpus:entry:${id}`);
        } catch {
          return null;
        }
      })
    );
    return entries.filter(Boolean);
  } catch (err) {
    console.error('[corpus] KV load error:', err.message);
    return [];
  }
}

function score(entry, queryTokens) {
  const haystack = (
    (entry.title || '') + ' ' +
    (entry.summary || '') + ' ' +
    (entry.content || '') + ' ' +
    (entry.tags || []).join(' ') + ' ' +
    'siman ' + (entry.siman || '') + ' seif ' + (entry.seif || '')
  ).toLowerCase();
  let s = 0;
  for (const tok of queryTokens) {
    const t = tok.toLowerCase();
    if (!t) continue;
    if (haystack.includes(t)) {
      // Pondération : tag exact / titre > contenu
      const inTitle = (entry.title || '').toLowerCase().includes(t);
      const inTag = (entry.tags || []).some(tag => tag.toLowerCase() === t);
      s += 1 + (inTitle ? 3 : 0) + (inTag ? 5 : 0);
    }
  }
  return s;
}

function tokenize(query) {
  return query
    .toLowerCase()
    .replace(/[^\w\sא-ת'-]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length >= 2);
}

export async function searchCorpus(query, options = {}) {
  const limit = options.limit || 5;
  const entries = await getAllEntries();
  const tokens = tokenize(query);
  if (tokens.length === 0) {
    return entries.slice(0, limit).map(e => formatHit(e));
  }
  const scored = entries
    .map(e => ({ entry: e, s: score(e, tokens) }))
    .filter(x => x.s > 0)
    .sort((a, b) => b.s - a.s)
    .slice(0, limit);

  return scored.map(x => formatHit(x.entry));
}

function formatHit(entry) {
  return {
    id: entry.id,
    title: entry.title,
    section: entry.section,
    siman: entry.siman,
    seif: entry.seif,
    level: entry.level,
    tags: entry.tags || [],
    summary: entry.summary || '',
    sources: entry.sources || [],
    internalLinks: entry.internalLinks || [],
  };
}

export async function getEntryById(id) {
  const entries = await getAllEntries();
  return entries.find(e => e.id === id) || null;
}

// Définition des outils Claude
export const CORPUS_TOOLS = [
  {
    name: 'daat_search_corpus',
    description: 'Recherche dans le corpus DAAT.AI (la base de connaissance INTERNE de Rav Yossef Haim Samama et de la plateforme). Utilise CET outil EN PRIORITÉ avant Sefaria — ce corpus contient la pédagogie spécifique du Rav, les niveaux d\'étude, les liens vers les pages internes du site. Retourne une liste de résumés avec leurs IDs.',
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Mots-clés à chercher (français, hébreu, ou translittération). Exemples : "shevitat kelim", "siman 246", "prêt non-juif", "sekhar shabbat".',
        },
        limit: {
          type: 'integer',
          description: 'Nombre maximum de résultats (défaut 5)',
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'daat_get_content',
    description: 'Récupère le contenu COMPLET d\'une entrée du corpus DAAT par son ID. Utilise cet outil après daat_search_corpus pour lire le détail d\'une entrée pertinente.',
    input_schema: {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'L\'ID de l\'entrée (ex: "siman-246-overview", "siman-246-shitot").',
        },
      },
      required: ['id'],
    },
  },
];

export async function executeCorpusTool(toolName, input) {
  if (toolName === 'daat_search_corpus') {
    const results = await searchCorpus(input.query, { limit: input.limit });
    return JSON.stringify({ results, count: results.length });
  }

  if (toolName === 'daat_get_content') {
    const entry = await getEntryById(input.id);
    if (!entry) {
      return JSON.stringify({ error: `Aucune entrée trouvée avec l'ID "${input.id}"` });
    }
    return JSON.stringify({
      id: entry.id,
      title: entry.title,
      siman: entry.siman,
      seif: entry.seif,
      level: entry.level,
      summary: entry.summary,
      content: entry.content,
      sources: entry.sources || [],
      internalLinks: entry.internalLinks || [],
      tags: entry.tags || [],
    });
  }

  return JSON.stringify({ error: `Outil corpus inconnu : ${toolName}` });
}

// Helpers pour l'admin (CRUD sur entrées dynamiques via KV)
export async function addDynamicEntry(entry) {
  if (!process.env.KV_REST_API_URL) {
    throw new Error('Vercel KV non configuré — impossible d\'ajouter un contenu dynamique. Active Vercel KV dans le dashboard puis ajoute KV_REST_API_URL et KV_REST_API_TOKEN aux variables d\'environnement.');
  }
  const { kv } = await import('@vercel/kv');
  if (!entry.id) {
    entry.id = `dynamic-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }
  entry.addedAt = new Date().toISOString();
  await kv.set(`daat:corpus:entry:${entry.id}`, entry);
  await kv.sadd('daat:corpus:ids', entry.id);
  return entry;
}

export async function deleteDynamicEntry(id) {
  if (!process.env.KV_REST_API_URL) {
    throw new Error('Vercel KV non configuré');
  }
  const { kv } = await import('@vercel/kv');
  await kv.del(`daat:corpus:entry:${id}`);
  await kv.srem('daat:corpus:ids', id);
  return { ok: true };
}

export async function listDynamicEntries() {
  return loadDynamicEntries();
}
