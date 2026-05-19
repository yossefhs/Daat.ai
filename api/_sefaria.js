// Module d'intégration avec l'API Sefaria (gratuite)
// https://www.sefaria.org/api/v3/texts/{ref}
//
// Usage : récupère le texte hébreu et la traduction d'une référence Sefaria
// pour ancrer les réponses de Claude dans des sources réelles (anti-hallucination).
//
// Cache KV : les textes Sefaria (versets, pages de Guemara, Choulhan Aroukh)
// sont IMMUABLES. On les met en cache 30 jours → économise un round-trip réseau
// + les tokens de réponse Sefaria pour les références populaires (Berakhot 17a
// demandé des centaines de fois/mois). Le cache est gaté : si KV échoue, on
// retombe transparemment sur le fetch direct (zéro régression).

import { kv } from './_kv.js';

const SEFARIA_BASE = 'https://www.sefaria.org/api';
const SEFARIA_CACHE_TTL = 30 * 24 * 60 * 60; // 30 jours

/**
 * Récupère un texte depuis Sefaria.
 * @param {string} ref - Référence Sefaria au format URL (ex: "Shulchan_Arukh,_Orach_Chayim.246.1")
 * @returns {Promise<{ref: string, hebrew: string, english: string, error?: string}>}
 */
export async function fetchSefariaText(ref) {
  // 1. Tentative de lecture cache (texte immuable → cache long)
  const cacheKey = `sefaria:text:${ref}`;
  try {
    const cached = await kv.get(cacheKey);
    if (cached && typeof cached === 'object' && cached.hebrew !== undefined) {
      return { ...cached, _cached: true };
    }
  } catch (_) {
    // KV indisponible → on continue sur le fetch direct
  }

  try {
    // Encoder la référence pour l'URL
    const encodedRef = encodeURIComponent(ref).replace(/%2C/g, ',').replace(/%2F/g, '/');
    const url = `${SEFARIA_BASE}/v3/texts/${encodedRef}?return_format=text_only`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    const response = await fetch(url, {
      signal: controller.signal,
      headers: { 'Accept': 'application/json' },
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      return { ref, hebrew: '', english: '', error: `Sefaria HTTP ${response.status}` };
    }

    const data = await response.json();

    // L'API v3 retourne data.versions[] avec les différentes versions
    let hebrew = '';
    let english = '';

    if (data.versions && Array.isArray(data.versions)) {
      for (const v of data.versions) {
        const text = Array.isArray(v.text) ? v.text.join(' ') : (v.text || '');
        if (v.language === 'he' && !hebrew) hebrew = text;
        if (v.language === 'en' && !english) english = text;
      }
    }

    // Fallback : champs directs (ancien format)
    if (!hebrew && data.he) hebrew = Array.isArray(data.he) ? data.he.join(' ') : data.he;
    if (!english && data.text) english = Array.isArray(data.text) ? data.text.join(' ') : data.text;

    // Nettoyer le HTML basique
    hebrew = stripHtml(hebrew);
    english = stripHtml(english);

    const result = {
      ref,
      hebrew: hebrew || '',
      english: english || '',
      title: data.title || data.indexTitle || ref,
    };

    // 2. Écriture cache — uniquement si on a vraiment du contenu (pas de réponse vide)
    if (result.hebrew || result.english) {
      try {
        await kv.set(cacheKey, result, { ex: SEFARIA_CACHE_TTL });
      } catch (_) {
        // KV en écriture indisponible → tant pis, on renvoie quand même le résultat
      }
    }

    return result;
  } catch (err) {
    return {
      ref,
      hebrew: '',
      english: '',
      error: err.name === 'AbortError' ? 'Timeout Sefaria' : (err.message || 'Erreur Sefaria'),
    };
  }
}

/**
 * Recherche dans Sefaria.
 * @param {string} query - Requête de recherche
 * @returns {Promise<{results: Array, error?: string}>}
 */
export async function searchSefaria(query) {
  try {
    const url = `${SEFARIA_BASE}/search-wrapper`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    const response = await fetch(url, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        query,
        type: 'text',
        size: 5,
      }),
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      return { results: [], error: `Sefaria search HTTP ${response.status}` };
    }

    const data = await response.json();
    const hits = (data.hits && data.hits.hits) || [];
    const results = hits.slice(0, 5).map(h => ({
      ref: h._source?.ref || h._id,
      title: h._source?.heRef || h._source?.ref || '',
      snippet: stripHtml((h.highlight?.naive_lemmatizer?.[0] || h._source?.exact || '').slice(0, 300)),
      categories: h._source?.path || [],
    }));

    return { results };
  } catch (err) {
    return {
      results: [],
      error: err.name === 'AbortError' ? 'Timeout Sefaria search' : (err.message || 'Erreur Sefaria search'),
    };
  }
}

function stripHtml(text) {
  if (!text) return '';
  return text
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

// Définition des outils Sefaria au format Anthropic tool use
export const SEFARIA_TOOLS = [
  {
    name: 'sefaria_get_text',
    description: 'Récupère le texte hébreu et anglais d\'une référence Sefaria précise. Utilise cet outil AVANT de citer une source pour vérifier son contenu exact et éviter toute hallucination. Exemples de refs : "Shulchan_Arukh,_Orach_Chayim.246.1", "Shabbat.19a", "Mishneh_Torah,_Sabbath.6.16", "Genesis.1.1".',
    input_schema: {
      type: 'object',
      properties: {
        ref: {
          type: 'string',
          description: 'La référence Sefaria au format URL (avec underscores et virgules). Exemple : "Shulchan_Arukh,_Orach_Chayim.246.1"',
        },
      },
      required: ['ref'],
    },
  },
  {
    name: 'sefaria_search',
    description: 'Recherche dans la base Sefaria pour trouver des sources pertinentes sur un sujet. Utilise cet outil quand l\'utilisateur pose une question dont tu ne connais pas la référence exacte, pour découvrir les sources avant de répondre.',
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'La requête de recherche, en français, anglais ou hébreu. Exemples : "shevitat kelim", "sekhar shabbat", "prêt non-juif Shabbat".',
        },
      },
      required: ['query'],
    },
  },
];

/**
 * Exécute un appel d'outil Sefaria.
 * @param {string} toolName
 * @param {object} input
 * @returns {Promise<string>} Résultat formaté en string pour le tool_result.
 */
export async function executeSefariaTool(toolName, input) {
  if (toolName === 'sefaria_get_text') {
    const result = await fetchSefariaText(input.ref);
    if (result.error) {
      return JSON.stringify({ error: result.error, ref: result.ref });
    }
    // Tronquer les textes très longs pour éviter d'exploser le contexte
    const MAX = 4000;
    return JSON.stringify({
      ref: result.ref,
      title: result.title,
      hebrew: result.hebrew.slice(0, MAX),
      english: result.english.slice(0, MAX),
      truncated: result.hebrew.length > MAX || result.english.length > MAX,
    });
  }

  if (toolName === 'sefaria_search') {
    const result = await searchSefaria(input.query);
    if (result.error) {
      return JSON.stringify({ error: result.error });
    }
    return JSON.stringify({ results: result.results });
  }

  return JSON.stringify({ error: `Outil inconnu : ${toolName}` });
}
