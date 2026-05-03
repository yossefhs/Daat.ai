// Module pesakim DAAT — registre de psakim atomiques
// Indexe data/pesakim.json (psakim atomiques validés par le Rav Yossef Haim Samama)
//
// Expose deux outils Claude :
// - daat_search_pesakim : cherche un psak atomique par mots-clés / minhag / siman
// - daat_get_pesak       : récupère un psak précis par son ID

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PESAKIM_PATH = join(__dirname, '..', 'data', 'pesakim.json');

let _pesakim = null;

function loadPesakim() {
  if (_pesakim) return _pesakim;
  try {
    const raw = readFileSync(PESAKIM_PATH, 'utf-8');
    _pesakim = JSON.parse(raw);
  } catch (err) {
    console.error('[pesakim] Failed to load pesakim.json:', err.message);
    _pesakim = { meta: {}, pesakim: [] };
  }
  return _pesakim;
}

function getAllPesakim() {
  return loadPesakim().pesakim || [];
}

function searchPesakim({ query, minhag, siman, category, limit = 5 }) {
  const all = getAllPesakim();
  const q = (query || '').toLowerCase().trim();
  const qWords = q.split(/\s+/).filter(w => w.length > 2);

  const scored = all.map(p => {
    let score = 0;
    const text = [
      p.question || '',
      p.category || '',
      JSON.stringify(p.psak || {}),
      (p.tags || []).join(' '),
      p.id || ''
    ].join(' ').toLowerCase();

    // Word matches in question/psak/tags
    for (const w of qWords) {
      if (text.includes(w)) score += 3;
      if ((p.question || '').toLowerCase().includes(w)) score += 5;
      if ((p.tags || []).some(t => t.toLowerCase().includes(w))) score += 2;
    }

    // Minhag boost
    if (minhag && p.psak && p.psak[minhag.toLowerCase()]) score += 4;

    // Siman exact match
    if (siman && (String(p.siman) === String(siman) || String(p.siman || '').includes(String(siman)))) score += 8;

    // Category match
    if (category && (p.category || '').toLowerCase().includes(category.toLowerCase())) score += 4;

    return { p, score };
  });

  return scored
    .filter(x => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(x => x.p);
}

function getPesak(id) {
  const all = getAllPesakim();
  return all.find(p => p.id === id) || null;
}

// === EXECUTORS ===

export async function executePesakimTool(toolName, input) {
  if (toolName === 'daat_search_pesakim') {
    const { query, minhag, siman, category, limit } = input || {};
    const results = searchPesakim({ query, minhag, siman, category, limit: limit || 5 });
    if (results.length === 0) {
      return JSON.stringify({
        ok: true,
        results: [],
        message: 'Aucun pesak atomique correspondant. Daat doit consulter le corpus standard ou Sefaria.',
      });
    }
    // Return concise summaries
    return JSON.stringify({
      ok: true,
      count: results.length,
      results: results.map(p => ({
        id: p.id,
        question: p.question,
        siman: p.siman,
        seif: p.seif,
        category: p.category,
        stringency: p.stringency,
        psak_default: p.psak?.default || null,
        psak_by_minhag: {
          sefarade: p.psak?.sefarade || null,
          ashkenaze: p.psak?.ashkenaze || null,
          habad: p.psak?.habad || null,
        },
        alternative: p.alternative || null,
        sources_summary: (p.sources || []).map(s => s.label).join(' · '),
        tags: p.tags || [],
        reviewer: p.reviewer,
        reviewedAt: p.reviewedAt,
      })),
    });
  }

  if (toolName === 'daat_get_pesak') {
    const { id } = input || {};
    if (!id) return JSON.stringify({ ok: false, error: 'id requis' });
    const p = getPesak(id);
    if (!p) return JSON.stringify({ ok: false, error: `Pesak ${id} non trouvé` });
    return JSON.stringify({ ok: true, pesak: p });
  }

  return JSON.stringify({ ok: false, error: `Outil pesakim inconnu : ${toolName}` });
}

// === TOOL DEFINITIONS for Anthropic API ===

export const PESAKIM_TOOLS = [
  {
    name: 'daat_search_pesakim',
    description:
      "Cherche dans le registre de PSAKIM ATOMIQUES de DAAT (questions pratiques précises avec leurs réponses validées par le Rav Yossef Haim Samama). " +
      "À CONSULTER EN PREMIER pour toute question halakhique pratique précise — c'est la source de vérité la plus fiable. " +
      "Retourne jusqu'à 5 psakim correspondants, avec leur réponse par minhag (sefarade / ashkenaze / habad / default), leurs sources canoniques, et leur niveau de stringency. " +
      "Utilise minhag={'sefarade'|'ashkenaze'|'habad'} pour booster un minhag spécifique. Utilise siman pour filtrer.",
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description:
            'Question ou mots-clés à chercher (en français, hébreu translittéré ou anglais). Ex: "louer voiture non-juif Shabbat", "tsedaka oneg Shabbat", "havlaah airbnb"',
        },
        minhag: {
          type: 'string',
          enum: ['sefarade', 'ashkenaze', 'habad'],
          description: 'Minhag à privilégier dans le scoring (optionnel)',
        },
        siman: {
          type: 'string',
          description: 'Siman précis (ex: "246", "243", "242") pour filtrer (optionnel)',
        },
        category: {
          type: 'string',
          description: 'Catégorie thématique (ex: "shabbat-oneg", "shabbat-non-juif", "shabbat-kavod") (optionnel)',
        },
        limit: {
          type: 'number',
          description: 'Nombre max de résultats (défaut 5, max 10)',
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'daat_get_pesak',
    description:
      "Récupère le contenu COMPLET d'un pesak atomique par son ID (ex: 'pesak-246-01'). " +
      "À utiliser après daat_search_pesakim quand tu as identifié le pesak pertinent et tu veux son texte intégral, ses sources complètes, et ses détails par minhag.",
    input_schema: {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: "ID du pesak (ex: 'pesak-246-01')",
        },
      },
      required: ['id'],
    },
  },
];
