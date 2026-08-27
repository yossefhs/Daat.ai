// Module corpus DAAT — base de connaissance interne du site
//
// Expose deux outils Claude :
// - daat_search_corpus : cherche dans le corpus DAAT par mots-clés / tags
// - daat_get_content : récupère un contenu précis par son ID
//
// ⚠️ DEUX SOURCES, ne pas les confondre :
//  1. data/corpus-shabbat.json — LE corpus du site : 10 824 chunks extraits des
//     4 niveaux d'étude de 241 simanim (Orah Haim + Yoreh De'ah), régénéré par
//     `npm run build`. C'est la source PRINCIPALE, interrogée en BM25 via
//     _corpus-search.js (index partagé avec le routage corpus-first de chat.js,
//     donc aucun coût de chargement supplémentaire).
//  2. data/corpus.json — 28 entrées éditoriales écrites à la main (simanim 242,
//     243, 246). Pédagogie rédigée du Rav, avec `sources` et `internalLinks`.
//     Complément, pas substitut.
//
// Historique : jusqu'en 07/2026 ces deux outils n'interrogeaient QUE le fichier
// à 28 entrées, alors que leur description annonçait 124 simanim. En mode
// approfondi le modèle recevait donc 0 résultat sur tout siman ≠ 242/243/246 et
// répondait de mémoire — d'où des réponses inventées ou déformées (ex. siman 318
// seif 12) et de faux « le corpus ne couvre pas ce siman ».

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import {
  searchCorpus as searchSiteCorpus,
  getChunkById,
  getSimanChunks,
  getCorpusStats,
  corpusPerimeter,
} from './_corpus-search.js';

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
  // Store Redis — chargé lazy pour ne pas bloquer si KV non configuré
  if (!process.env.KV_REST_API_URL || !process.env.KV_REST_API_TOKEN) {
    return [];
  }
  try {
    const { kv } = await import('./_kv.js');
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

// Découpe un texte en MOTS pour la comparaison. Historiquement le scoring
// utilisait haystack.includes(token) : une recherche « bishoul ahar tseliya »
// faisait remonter les entrées « Kountress Aharon » (« ahar » ⊂ « Aharon »), qui
// passaient alors devant les vrais extraits. On compare désormais mot à mot.
function wordSet(str) {
  return new Set(
    String(str || '').toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
      .split(/[^a-z0-9א-ת]+/)
      .filter(Boolean)
  );
}

function score(entry, queryTokens) {
  const titleWords = wordSet(entry.title);
  const bodyWords = wordSet(
    (entry.summary || '') + ' ' + (entry.content || '') + ' ' + 'siman ' + (entry.siman || '')
  );
  const tags = (entry.tags || []).map(t => String(t).toLowerCase());
  let s = 0, matched = 0, strong = false;
  for (const tok of queryTokens) {
    const t = tok.toLowerCase();
    if (!t) continue;
    const inTitle = titleWords.has(t);
    const inTag = tags.includes(t);
    if (!inTitle && !inTag && !bodyWords.has(t)) continue;
    matched++;
    if (inTitle || inTag) strong = true;
    s += 1 + (inTitle ? 3 : 0) + (inTag ? 5 : 0);
  }
  // Ces 28 entrées ne couvrent que 3 simanim et sont placées EN TÊTE des
  // résultats : un seul mot commun ne doit pas suffire à les y faire entrer.
  if (matched < 2 && !strong) return 0;
  return s;
}

function tokenize(query) {
  return query
    .toLowerCase()
    .replace(/[^\w\sא-ת'-]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length >= 2);
}

// Longueur de l'extrait renvoyé par daat_search_corpus. Assez long pour que le
// modèle juge de la pertinence sans re-fetch, assez court pour que 5 résultats
// tiennent dans ~1000 tokens.
const EXCERPT_CHARS = 700;
// Plafond de daat_get_content : 14 chunks du corpus dépassent 20 000 caractères
// (seifim fleuves du niveau Daat HaRav, jusqu'à 68 k). Sans plafond, un seul
// appel d'outil ferait exploser la fenêtre de contexte et le budget temps.
const FULL_CHARS = 14000;

function excerpt(text, max) {
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  if (t.length <= max) return t;
  const cut = t.slice(0, max);
  const lastStop = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf(' — '), cut.lastIndexOf(' '));
  return (lastStop > max * 0.6 ? cut.slice(0, lastStop) : cut).trim() + '…';
}

// Un chunk du corpus du site → forme de hit commune. Les clés `title`, `seif`,
// `summary` et `sources` sont conservées telles quelles : le pré-RAG de chat.js
// (bloc <contexte_corpus_daat>) les lit déjà sous ces noms.
// Réserve écrite par le Rav sur son propre contenu (« hors corpus, à vérifier »,
// « Note de méthode … à confirmer auprès d'un Rav »). Elle DOIT parvenir au
// modèle : sur le chemin agentique, c'est lui qui rédige la réponse, et sans
// cette information il présente comme établi un passage que le Rav a écarté.
// Le champ booléen ne suffit pas — on ajoute une phrase, que le modèle lit.
const CAVEAT_NOTE = "⚠️ RÉSERVE DE L'AUTEUR : le Rav a marqué ce passage « hors corpus, à vérifier ». Ne le présente JAMAIS comme tranché ni comme « le corpus du Rav dit que » ; formule au conditionnel et renvoie explicitement au Rav.";

function formatChunkHit(c) {
  const full = String(c.text || '');
  return {
    id: c.id,
    title: c.simanTitle || `Siman ${c.siman}`,
    section: c.section || null,
    siman: c.siman,
    seif: c.subsection || null,
    level: c.level || null,
    levelLabel: c.levelLabel || null,
    origin: 'site',
    url: c.sourceUrl || null,
    tags: [],
    summary: excerpt(full, EXCERPT_CHARS),
    hasMore: full.length > EXCERPT_CHARS,
    ...(c.caveat ? { caveat: true, caveatNote: CAVEAT_NOTE } : {}),
    sources: [],
    internalLinks: [],
  };
}

// Détecte un numéro de siman écrit dans la requête (« siman 318 », « OH 318 »,
// « 318:12 »). Filet de sécurité : si la recherche plein texte ne rend rien, on
// sait quand même où regarder.
function simanFromQuery(query) {
  const m = String(query || '').match(/\b(?:siman|simane?|oh|o\.h\.|yd|y\.d\.)?\s*(\d{1,3})\b/i);
  if (!m) return null;
  const n = parseInt(m[1], 10);
  return n >= 1 && n <= 365 ? n : null;
}

export async function searchCorpus(query, options = {}) {
  const limit = Math.min(options.limit || 5, 12);
  const section = options.section || null;
  const askedSiman = options.siman != null ? parseInt(options.siman, 10) : null;

  // ── Cas 1 : siman explicitement demandé → on rend ses chunks, classés par
  // pertinence vis-à-vis de la question. Aucun garde-fou de recherche ne peut
  // alors faire écran (c'est le cas d'usage « montre-moi le siman 318 seif 12 »).
  if (Number.isFinite(askedSiman)) {
    const chunks = getSimanChunks(askedSiman, { section, question: query });
    return chunks.slice(0, limit).map(formatChunkHit);
  }

  // ── Cas 2 : recherche plein corpus (10 824 chunks).
  // minScore bas et strict=false, à l'inverse du ROUTAGE (minScore 8, strict) :
  // ici le modèle a explicitement demandé à chercher, un résultat moyen vaut
  // toujours mieux que rien — c'est le silence qui le fait répondre de mémoire.
  let siteHits = [];
  try {
    siteHits = (searchSiteCorpus(query, {
      limit: limit * 2, minScore: 1.0, strict: false, section,
    })?.results) || [];
  } catch (err) {
    console.error('[corpus] site search error:', err.message);
  }

  // ── Cas 3 : filet de sécurité — rien trouvé mais un numéro de siman est écrit
  // dans la requête.
  if (siteHits.length === 0) {
    const guessed = simanFromQuery(query);
    if (guessed) {
      siteHits = getSimanChunks(guessed, { section, question: query }).slice(0, limit);
    }
  }

  // ── Entrées éditoriales (data/corpus.json) + dynamiques (KV).
  // Elles ne couvrent que 3 simanim (242, 243, 246) mais leur champ `content`
  // est long : n'importe quelle question y trouve 2 mots communs. Placées en
  // tête sans condition, elles monopolisaient 2 résultats sur 3 et chassaient
  // le vrai extrait (mesuré : 65 % de rappel top-3 au lieu de 90 %).
  // On ne les retient donc que si le siman qu'elles traitent est CONFIRMÉ
  // pertinent — soit par la recherche plein corpus, soit parce que la question
  // le nomme. Dans ce cas seulement elles passent devant : sur leur siman, la
  // pédagogie rédigée du Rav vaut mieux qu'un extrait de page.
  // Uniquement les 2 MEILLEURS résultats plein corpus : un siman qui n'apparaît
  // qu'au 6ᵉ rang n'est pas le sujet de la question, et promouvoir son entrée
  // éditoriale en tête reviendrait à reproduire le problème qu'on corrige.
  const relevantSimanim = new Set(siteHits.slice(0, 2).map(h => h.siman));
  const namedSiman = simanFromQuery(query);
  if (namedSiman) relevantSimanim.add(namedSiman);

  const entries = await getAllEntries();
  const tokens = tokenize(query);
  const editorial = tokens.length
    ? entries
        .filter(e => e.siman == null || relevantSimanim.has(parseInt(e.siman, 10)))
        .map(e => ({ entry: e, s: score(e, tokens) }))
        .filter(x => x.s > 0)
        .sort((a, b) => b.s - a.s)
        .slice(0, 2)
        .map(x => formatHit(x.entry))
    : [];

  const out = [];
  const seen = new Set();
  for (const h of [...editorial, ...siteHits.map(formatChunkHit)]) {
    if (!h.id || seen.has(h.id)) continue;
    seen.add(h.id);
    out.push(h);
    if (out.length >= limit) break;
  }
  return out;
}

function formatHit(entry) {
  return {
    id: entry.id,
    title: entry.title,
    section: entry.section,
    siman: entry.siman,
    seif: entry.seif,
    level: entry.level,
    origin: 'editorial',
    tags: entry.tags || [],
    summary: entry.summary || '',
    sources: entry.sources || [],
    internalLinks: entry.internalLinks || [],
  };
}

export async function getEntryById(id) {
  const entries = await getAllEntries();
  const editorial = entries.find(e => e.id === id);
  if (editorial) return editorial;
  const chunk = getChunkById(id);
  if (!chunk) return null;
  // Forme « entrée » attendue par les appelants, à partir d'un chunk du site.
  return {
    id: chunk.id,
    title: chunk.simanTitle || `Siman ${chunk.siman}`,
    section: chunk.section || null,
    siman: chunk.siman,
    seif: chunk.subsection || null,
    level: chunk.level || null,
    levelLabel: chunk.levelLabel || null,
    origin: 'site',
    url: chunk.sourceUrl || null,
    summary: excerpt(chunk.text, EXCERPT_CHARS),
    content: chunk.text || '',
    ...(chunk.caveat ? { caveat: true, caveatNote: CAVEAT_NOTE } : {}),
    sources: [],
    internalLinks: chunk.sourceUrl ? [chunk.sourceUrl] : [],
    tags: [],
  };
}

// Définition des outils Claude
export const CORPUS_TOOLS = [
  {
    name: 'daat_search_corpus',
    description: 'Recherche dans le corpus DAAT.AI — le texte RÉEL des pages du site (les 4 niveaux d\'étude de chaque siman : Base, Lamdan, Synthèse, et Daat HaRav qui contient le Choulhan Aroukh de l\'Admour HaZaken traduit seif par seif). Utilise CET outil EN PRIORITÉ avant Sefaria et AVANT de répondre de mémoire. Retourne des extraits avec leurs IDs ; utilise ensuite daat_get_content pour lire un seif en entier avant de le citer.',
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Mots-clés à chercher (français, hébreu, ou translittération). Écris le vocabulaire halakhique classique plutôt que des mots modernes. Exemples : "bishoul ahar tseliya kli sheni", "mouktsé mahmat hisaron kis", "hazara plata", "basar bè-halav taarovot".',
        },
        siman: {
          type: 'integer',
          description: 'Numéro de siman, si la question porte explicitement sur un siman précis (ex. 318). Renvoie alors les extraits DE CE SIMAN classés par pertinence — à utiliser dès que tu connais le siman, c\'est le moyen le plus fiable d\'obtenir le texte exact.',
        },
        section: {
          type: 'string',
          enum: ['orach-chaim', 'yoreh-deah'],
          description: 'Restreint la recherche à une section. Le corpus couvre Orah Haim (dont Hilkhot Shabbat 242-365) et Yoreh De\'ah (87-118 et 183-200).',
        },
        limit: {
          type: 'integer',
          description: 'Nombre maximum de résultats (défaut 5, max 12)',
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'daat_get_content',
    description: 'Récupère le contenu COMPLET d\'une entrée du corpus DAAT par son ID (ex. le texte intégral d\'un seif du Choulhan Aroukh HaRav). À utiliser SYSTÉMATIQUEMENT après daat_search_corpus avant de citer ou de conclure : l\'extrait de recherche est tronqué, et la conclusion d\'un seif (« mais be-di\'avad on permet… ») se trouve souvent à la fin.',
    input_schema: {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'L\'ID renvoyé par daat_search_corpus (ex: "siman-318-daatharav-12", "siman-246-overview").',
        },
      },
      required: ['id'],
    },
  },
];

export async function executeCorpusTool(toolName, input) {
  if (toolName === 'daat_search_corpus') {
    const results = await searchCorpus(input.query, {
      limit: input.limit,
      siman: input.siman,
      section: input.section,
    });
    if (results.length === 0) {
      // Message explicite : sans lui, le modèle interprète le silence comme
      // « ce siman n'est pas couvert » et l'annonce à l'utilisateur — ce qui est
      // faux. Un résultat vide veut dire « reformule », jamais « pas couvert ».
      const stats = getCorpusStats();
      let perimeter = `${stats.totalSimanim} simanim`;
      try { perimeter = corpusPerimeter().summary; } catch { /* corpus indisponible */ }
      return JSON.stringify({
        results: [],
        count: 0,
        // ⚠️ Nuance importante : l'ancienne note interdisait TOUJOURS de dire
        // « non couvert ». C'était juste pour un siman DANS le périmètre (un
        // mauvais matching n'est pas une absence) mais faux pour un sujet qui
        // n'y est pas du tout — et c'est ce qui poussait le modèle à servir un
        // siman d'un autre domaine plutôt que d'avouer l'absence. On donne donc
        // le périmètre RÉEL et on distingue les deux cas.
        note: `Aucun extrait ne correspond à ces mots-clés. Périmètre réel du corpus : ${perimeter}. ` +
          `Si le sujet demandé est DANS ce périmètre, cela ne signifie PAS qu'il est absent : reformule avec le vocabulaire halakhique classique, ou rappelle cet outil avec le paramètre "siman" si tu connais le numéro, et n'annonce jamais à l'utilisateur que ce siman n'est pas couvert. ` +
          `S'il est HORS de ce périmètre (Pessah, Souccot, Pourim, deuil, mariage…), dis-le simplement et appuie-toi sur Sefaria — c'est honnête, et infiniment préférable à un extrait d'un autre domaine présenté comme la source du Rav.`,
      });
    }
    return JSON.stringify({ results, count: results.length });
  }

  if (toolName === 'daat_get_content') {
    const entry = await getEntryById(input.id);
    if (!entry) {
      return JSON.stringify({ error: `Aucune entrée trouvée avec l'ID "${input.id}". Relance daat_search_corpus pour obtenir un ID valide.` });
    }
    const content = String(entry.content || '');
    const truncated = content.length > FULL_CHARS;
    return JSON.stringify({
      id: entry.id,
      title: entry.title,
      section: entry.section,
      siman: entry.siman,
      seif: entry.seif,
      level: entry.level,
      levelLabel: entry.levelLabel,
      origin: entry.origin || 'editorial',
      url: entry.url || null,
      summary: entry.summary,
      content: truncated ? content.slice(0, FULL_CHARS) + '\n\n[…extrait tronqué…]' : content,
      truncated,
      sources: entry.sources || [],
      internalLinks: entry.internalLinks || [],
      tags: entry.tags || [],
      ...(entry.caveat ? { caveat: true, caveatNote: entry.caveatNote || CAVEAT_NOTE } : {}),
    });
  }

  return JSON.stringify({ error: `Outil corpus inconnu : ${toolName}` });
}

// Helpers pour l'admin (CRUD sur entrées dynamiques via KV)
export async function addDynamicEntry(entry) {
  if (!process.env.KV_REST_API_URL) {
    throw new Error('Store Redis non configuré — impossible d\'ajouter un contenu dynamique. Ajoute KV_REST_API_URL et KV_REST_API_TOKEN aux variables d\'environnement.');
  }
  const { kv } = await import('./_kv.js');
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
  const { kv } = await import('./_kv.js');
  await kv.del(`daat:corpus:entry:${id}`);
  await kv.srem('daat:corpus:ids', id);
  return { ok: true };
}

export async function listDynamicEntries() {
  return loadDynamicEntries();
}
