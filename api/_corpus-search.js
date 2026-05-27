// Recherche BM25 dans le corpus Shabbat (1500+ chunks).
// Utilisé par /api/chat-corpus (endpoint dédié) et — à terme — par /api/chat
// comme premier filtre avant routage Opus/Sonnet.
//
// Tokenisation FR + hébreu, stopwords, synonymes halakhiques, garde-fou keyToken.

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CORPUS_PATH = join(__dirname, '..', 'data', 'corpus-shabbat.json');

let _corpus = null;
let _idf = null;
let _avgdl = 0;
let _N = 0;

const STOPWORDS = new Set([
  'le','la','les','de','des','du','et','ou','un','une','en','a','au','aux',
  'que','qu','qui','quoi','ce','cette','ces','est','sont','etre','avoir','pas','ne',
  'on','je','tu','il','elle','nous','vous','ils','elles','se','sa','son','ses',
  'mon','ma','mes','ton','ta','tes','dans','sur','par','pour','avec','sans',
  'mais','donc','car','si','plus','moins','tres','peu','tout','tous','toute',
  'comment','pourquoi','quand','ou','y','d','l','s','c','j','m','n','t',
  'ca','oui','non','apres','avant','ici','meme','aussi',
  'fait','faire','faut','peut','peuvent','dire','dit','quel','quelle',
  'the','an','of','to','in','is','are','was','were','be','been','this','that',
]);

const SYNONYMS = {
  'cuire': ['bishoul','cuisson'], 'cuisson': ['bishoul'],
  'chauffer': ['bishoul','rechauffer'], 'rechauffer': ['bishoul','ein'],
  'cholent': ['bishoul','hatmana'], 'chamin': ['bishoul','hatmana'],
  'the': ['iroui','liquide'], 'cafe': ['iroui','liquide'],
  'eau': ['liquide','mayim'], 'temperature': ['yad','soledet','chaud'],
  'trier': ['borer','tri'], 'separer': ['borer','separation'],
  'salade': ['aliments','okhel'], 'passoire': ['tamis','crible','instrument'],
  'eplucher': ['epluchage','derekh','akhila'],
  'mouktse': ['muqtse','mouqtse','deplacement'], 'deplacer': ['mouktse','tiltoul','porter'],
  'porter': ['mouktse','tiltoul'], 'objet': ['mouktse','kli'],
  'casser': ['nolad','brise'], 'argent': ['kis','hisaron'],
  'shabbat': ['chabbat','sabbat','shabbos'], 'chabbat': ['shabbat','sabbat','shabbos'],
  'shabbos': ['shabbat','chabbat'],
  'permis': ['mutar'], 'interdit': ['assour','isour'],
  'vaisselle': ['kelim','plat','ustensile'],
  'cuir': ['bishoul'], 'rotir': ['bishoul','tsoli'],
  'mehaber': ['choulhan','aroukh','maran'], 'rama': ['rama','ashkenaze'],
  'nouer': ['qosher','noeud'], 'noeud': ['qosher'],
  'ecrire': ['kotev','ecriture'], 'effacer': ['mohek'],
  'allumer': ['mavir','feu'], 'eteindre': ['mekhabe','feu'],
  'electricite': ['hashmal','electrique'],
};

function normalizeToken(s) {
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/['’‘]/g, '').replace(/[^a-z֐-׿0-9]/g, '');
}

export function tokenize(text) {
  return String(text || '')
    .split(/[\s,.;:!?()«»""'‘’\-—–_/]+/)
    .map(normalizeToken)
    .filter((t) => t.length >= 2 && !STOPWORDS.has(t));
}

function expandQuery(tokens) {
  const expanded = new Map();
  tokens.forEach((t) => {
    expanded.set(t, (expanded.get(t) || 0) + 1.0);
    if (SYNONYMS[t]) {
      SYNONYMS[t].forEach((syn) => {
        const n = normalizeToken(syn);
        if (n.length >= 2) expanded.set(n, Math.max(expanded.get(n) || 0, 0.6));
      });
    }
  });
  return expanded;
}

function loadAndIndex() {
  if (_corpus) return;
  try {
    const raw = readFileSync(CORPUS_PATH, 'utf-8');
    _corpus = JSON.parse(raw);
  } catch (err) {
    console.error('[corpus-search] Failed to load corpus-shabbat.json:', err.message);
    _corpus = { meta: {}, chunks: [] };
    _idf = new Map();
    _avgdl = 1;
    _N = 0;
    return;
  }
  _N = _corpus.chunks.length;
  const df = new Map();
  let totalLen = 0;
  for (const c of _corpus.chunks) {
    const tokens = tokenize(
      c.text + ' ' + (c.subsection || '') + ' ' + c.sectionTitle + ' ' +
      (c.simanTitle || '') + ' ' + (c.simanTitleHe || '')
    );
    c._tokens = tokens;
    c._tokenCount = tokens.length;
    c._tfMap = new Map();
    for (const t of tokens) c._tfMap.set(t, (c._tfMap.get(t) || 0) + 1);
    totalLen += tokens.length;
    new Set(tokens).forEach((t) => df.set(t, (df.get(t) || 0) + 1));
  }
  _idf = new Map();
  df.forEach((freq, term) => _idf.set(term, Math.log(1 + (_N - freq + 0.5) / (freq + 0.5))));
  _avgdl = totalLen / Math.max(1, _N);
  console.log(`[corpus-search] Indexed ${_N} chunks from ${(_corpus.meta?.totalSimanim) || '?'} simanim`);
}

function getIdf(term) {
  if (_idf.has(term)) return _idf.get(term);
  return Math.log(1 + (_N + 0.5) / 0.5);
}

function scoreChunk(chunk, queryTerms, keyTokens) {
  const k1 = 1.5, b = 0.75;
  const tf = chunk._tfMap;
  // Garde-fou keyToken : au moins un des tokens originaux à haute IDF doit matcher
  if (keyTokens.length && !keyTokens.some((t) => tf.get(t))) return 0;

  const dl = chunk._tokenCount;
  let score = 0;
  queryTerms.forEach((boost, term) => {
    const f = tf.get(term);
    if (!f) return;
    const idf = getIdf(term);
    const num = f * (k1 + 1);
    const den = f + k1 * (1 - b + b * dl / _avgdl);
    score += boost * idf * (num / den);
  });
  // Bonus titre de section / subsection
  const titleStr = chunk.sectionTitle + ' ' + (chunk.subsection || '');
  const titleSet = new Set(tokenize(titleStr));
  let titleBonus = 0;
  queryTerms.forEach((boost, term) => {
    if (titleSet.has(term)) titleBonus += boost * getIdf(term) * 0.8;
  });
  // Boost de type
  if (chunk.type === 'cas-pratique') score *= 1.15;
  if (chunk.type === 'definition') score *= 1.1;
  return score + titleBonus;
}

export function searchCorpus(question, opts = {}) {
  loadAndIndex();
  const limit = opts.limit || 3;
  const minScore = opts.minScore ?? 1.5;
  const tokens = tokenize(question);
  if (tokens.length === 0) return { results: [], keyTokens: [], totalChunks: _N };

  // Key tokens = les 2 tokens originaux de plus haute IDF
  const byIdf = tokens.map((t) => ({ t, idf: getIdf(t) })).sort((a, b) => b.idf - a.idf);
  const keyTokens = byIdf.slice(0, 2).map((x) => x.t);

  const expanded = expandQuery(tokens);
  const scored = [];
  for (const c of _corpus.chunks) {
    const s = scoreChunk(c, expanded, keyTokens);
    if (s >= minScore) scored.push({ chunk: c, score: s });
  }
  scored.sort((a, b) => b.score - a.score);
  return {
    results: scored.slice(0, limit).map((r) => ({
      siman: r.chunk.siman,
      simanTitle: r.chunk.simanTitle,
      simanTitleHe: r.chunk.simanTitleHe,
      sectionNum: r.chunk.sectionNum,
      sectionTitle: r.chunk.sectionTitle,
      subsection: r.chunk.subsection,
      type: r.chunk.type,
      text: r.chunk.text,
      score: r.score,
      sourceUrl: r.chunk.sourceUrl,
    })),
    keyTokens,
    totalChunks: _N,
  };
}

export function getCorpusStats() {
  loadAndIndex();
  return { totalChunks: _N, totalSimanim: _corpus?.meta?.totalSimanim || 0, avgdl: _avgdl };
}
