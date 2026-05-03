// Module mareh_mekomot DAAT — registre de questions halakhiques avec leurs sources
// Indexe data/mareh_mekomot.json (positions multi-sources des classiques + poskim par minhag)
//
// CE N'EST PAS UN REGISTRE DE PSAKIM. C'est un outil d'étude qui présente
// ce que chaque autorité dit (Mehaber, Rama, Mishna Brura, Choulchan Aroukh
// haRav, Yabia Omer, Igrot Moshe, etc.). Daat doit ensuite conclure avec :
//   "Cette analyse présente ce que disent les sources. Ce n'est pas un psak
//   halakha. Pour ton cas concret, consulte ton Rav."
//
// Expose deux outils Claude :
// - daat_search_mareh_mekomot : cherche une question halakhique avec ses sources
// - daat_get_mareh_mekomot    : récupère une entrée complète par son ID

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const MM_PATH = join(__dirname, '..', 'data', 'mareh_mekomot.json');

let _mm = null;

function loadMM() {
  if (_mm) return _mm;
  try {
    const raw = readFileSync(MM_PATH, 'utf-8');
    _mm = JSON.parse(raw);
  } catch (err) {
    console.error('[mareh_mekomot] Failed to load:', err.message);
    _mm = { meta: {}, entries: [] };
  }
  return _mm;
}

function getAllEntries() {
  return loadMM().entries || [];
}

function searchEntries({ query, minhag, siman, category, limit = 5 }) {
  const all = getAllEntries();
  const q = (query || '').toLowerCase().trim();
  const qWords = q.split(/\s+/).filter(w => w.length > 2);

  const scored = all.map(e => {
    let score = 0;
    const haystack = [
      e.question || '',
      e.category || '',
      JSON.stringify(e.positions || []),
      e.synthesis_neutre || '',
      (e.tags || []).join(' '),
      e.id || ''
    ].join(' ').toLowerCase();

    for (const w of qWords) {
      if (haystack.includes(w)) score += 3;
      if ((e.question || '').toLowerCase().includes(w)) score += 6;
      if ((e.tags || []).some(t => t.toLowerCase().includes(w))) score += 2;
    }

    if (siman && (String(e.siman) === String(siman) || String(e.siman || '').includes(String(siman)))) score += 8;
    if (category && (e.category || '').toLowerCase().includes(category.toLowerCase())) score += 4;

    return { e, score };
  });

  return scored
    .filter(x => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(x => x.e);
}

function getEntry(id) {
  return getAllEntries().find(e => e.id === id) || null;
}

/**
 * Filtre les positions selon le minhag de l'utilisateur.
 * Retourne TOUJOURS les sources "tous" (Guemara, Rambam, Choulchan Aroukh, Tour…),
 * PLUS les sources spécifiques au minhag de l'utilisateur.
 */
function filterPositionsByMinhag(positions, minhag) {
  if (!Array.isArray(positions)) return [];
  const m = (minhag || '').toLowerCase();
  return positions.filter(p => {
    const pm = (p.minhag || 'tous').toLowerCase();
    if (pm === 'tous') return true;
    if (m && pm === m) return true;
    return false;
  });
}

function summarizeEntry(e, minhag) {
  const filtered = filterPositionsByMinhag(e.positions, minhag);
  return {
    id: e.id,
    question: e.question,
    siman: e.siman,
    seif: e.seif,
    category: e.category,
    clarity: e.clarity,
    clarity_note: e.clarity_note || null,
    positions: filtered.map(p => ({
      name: p.name,
      label_he: p.label_he || null,
      scope: p.scope,
      minhag: p.minhag,
      text: p.text,
      ref: p.ref,
      url: p.url || null,
    })),
    synthesis_neutre: e.synthesis_neutre,
    alternative_dans_sources: e.alternative_dans_sources || null,
    tags: e.tags || [],
    disclaimer: "Cette analyse présente ce que disent les sources. Ce n'est PAS un psak halakha. Pour ton cas concret, consulte ton Rav."
  };
}

// === EXECUTORS ===

export async function executeMarehMekomotTool(toolName, input) {
  if (toolName === 'daat_search_mareh_mekomot') {
    const { query, minhag, siman, category, limit } = input || {};
    const results = searchEntries({ query, minhag, siman, category, limit: limit || 5 });
    if (results.length === 0) {
      return JSON.stringify({
        ok: true,
        results: [],
        message: 'Aucune entrée correspondante dans le registre. Daat doit consulter le corpus standard ou Sefaria.',
      });
    }
    return JSON.stringify({
      ok: true,
      count: results.length,
      results: results.map(e => summarizeEntry(e, minhag)),
    });
  }

  if (toolName === 'daat_get_mareh_mekomot') {
    const { id, minhag } = input || {};
    if (!id) return JSON.stringify({ ok: false, error: 'id requis' });
    const e = getEntry(id);
    if (!e) return JSON.stringify({ ok: false, error: `Entrée ${id} non trouvée` });
    return JSON.stringify({ ok: true, entry: summarizeEntry(e, minhag) });
  }

  return JSON.stringify({ ok: false, error: `Outil mareh_mekomot inconnu : ${toolName}` });
}

// === TOOL DEFINITIONS for Anthropic API ===

export const MAREH_MEKOMOT_TOOLS = [
  {
    name: 'daat_search_mareh_mekomot',
    description:
      "Cherche dans le registre **מראי מקומות** de DAAT — questions halakhiques pratiques associées aux positions des sources classiques (Guemara, Rambam, Choulchan Aroukh, Rama, Tour) et des poskim par minhag (Mishna Brura/Igrot Moshe pour Ashkénazes ; Yabia Omer/Yalkout Yossef/Ben Ish Hai pour Séfarades ; Choulchan Aroukh haRav pour Habad). " +
      "**CE N'EST PAS UN REGISTRE DE PSAKIM** — c'est un outil d'étude. Chaque entrée présente ce que dit chaque autorité. " +
      "**À CONSULTER EN PREMIER** pour toute question halakhique pratique. Si une entrée correspond, présente les positions filtrées par le minhag de l'utilisateur, puis termine TOUJOURS par : 'Cette analyse présente ce que disent les sources. Ce n'est pas un psak halakha. Pour ton cas concret, consulte ton Rav.' " +
      "Le champ `clarity` indique : 'shulchan-aroukh-tranche' (le Mehaber dit clairement מותר/אסור — tu peux transmettre directement) ou 'requires-rav' (מחלוקת ou ambiguïté — présente sans trancher).",
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Question ou mots-clés (FR/HE/EN). Ex: "louer voiture non-juif", "tsedaka oneg", "havlaa airbnb".',
        },
        minhag: {
          type: 'string',
          enum: ['sefarade', 'ashkenaze', 'habad'],
          description: "Minhag de l'utilisateur — filtre les positions : tu reçois les sources 'tous' (communes : Guemara, Rambam, Choulchan Aroukh, Tour) + les sources spécifiques au minhag.",
        },
        siman: {
          type: 'string',
          description: 'Siman précis pour filtrer (ex: "246", "243", "242").',
        },
        category: {
          type: 'string',
          description: 'Catégorie (ex: "shabbat-oneg", "shabbat-non-juif", "shabbat-kavod").',
        },
        limit: {
          type: 'number',
          description: 'Nombre max de résultats (défaut 5, max 10).',
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'daat_get_mareh_mekomot',
    description:
      "Récupère une entrée COMPLÈTE du registre מראי מקומות par ID (ex : '246-q01'), filtrée par minhag de l'utilisateur. " +
      "À utiliser après daat_search_mareh_mekomot quand tu as identifié l'entrée pertinente.",
    input_schema: {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: "ID de l'entrée (ex: '246-q01', '242-q03').",
        },
        minhag: {
          type: 'string',
          enum: ['sefarade', 'ashkenaze', 'habad'],
          description: "Minhag pour filtrer les positions (recommandé).",
        },
      },
      required: ['id'],
    },
  },
];
