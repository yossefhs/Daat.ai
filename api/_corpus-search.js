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
  // Mots vides ajoutés après l'incident borer : sans eux, « ai-je le droit de
  // faire cuire » retenait « ai » et « droit » comme tokens-clés (les mots de plus
  // haute IDF servent de portail) et le mot porteur « cuire » était ignoré.
  'ai','as','ont','avons','avez','avait','avais','etait','etais','suis','es','sommes','etes',
  'me','te','lui','leur','eux','moi','toi','soi','en','y',
  'chez','vers','depuis','pendant','entre','sous','hors','contre','selon',
  'quelque','quelques','chose','choses','truc','trucs','maniere','facon',
  'veux','veut','veulent','voulais','vouloir','voudrais',
  'dois','doit','doivent','devoir','devrais',
  'puis','peux','pouvez','pouvons','pourrais','pouvoir','pourra',
  'droit','besoin','envie','possible','permission',
  'autre','autres','tel','telle','tels','telles','certains','certaines',
  'falloir','faudrait','faisant','faites','fais',
  'maintenant','aujourd','hui','hier','demain','alors','ensuite','puisque',
  'merci','bonjour','shalom','svp','question','savoir','explique','expliquer',
  'vraiment','juste','simplement','peut-etre','environ','sorte',
]);

// Expressions multi-mots, normalisées AVANT la tokenisation. Sans cela « pommes
// de terre » matche « pommes » (le fruit, siman 290 berakhot) — c'est exactement
// ce qui a fait manquer le siman 319 sur une question de borer.
const MULTIWORD = [
  [/pommes?\s+de\s+terre/g, 'pommedeterre'],
  [/petits?\s+pois/g, 'petitspois'],
  [/papier\s+(?:hygienique|toilette)/g, 'papiertoilette'],
  [/eau\s+chaude/g, 'eauchaude'],
  [/mal\s+(?:a\s+la\s+|de\s+)?tete/g, 'maltete'],
  [/mal\s+au\s+ventre/g, 'malventre'],
  [/lait\s+maternel/g, 'laitmaternel'],
  [/machine\s+a\s+laver/g, 'machinelaver'],
  [/salle\s+de\s+bain/g, 'sallebain'],
  [/eau\s+bouillante/g, 'eaubouillante'],
];

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
  // ── Vocabulaire réel des utilisateurs (ajouté après l'incident borer 2026-07) ──
  // Le corpus est écrit en langue halakhique ; les gens écrivent en langue courante.
  'retirer': ['borer','enlever','tri'], 'enlever': ['borer','tri'], 'oter': ['borer','tri'],
  'melange': ['borer','melanges','tri'], 'melanges': ['borer','tri'], 'melangee': ['borer','tri'],
  'pesolet': ['psolet','dechet'], 'psolet': ['pesolet','dechet'],
  'raper': ['tohen','moudre','broyer'], 'moudre': ['tohen'], 'ecraser': ['tohen','lash','broyer'],
  'hacher': ['tohen','couper'], 'broyer': ['tohen'], 'mixer': ['tohen'],
  'medicament': ['malade','refoua','remede','soin'], 'cachet': ['malade','refoua','remede'],
  'comprime': ['malade','refoua','remede'], 'fievre': ['malade','soin','refoua'],
  'malade': ['refoua','soin','maladie'], 'douleur': ['malade','soin','refoua'],
  'maltete': ['malade','refoua','soin'], 'malventre': ['malade','refoua','soin'],
  'soigner': ['malade','refoua','soin'], 'medecin': ['malade','refoua'],
  'doucher': ['laver','rehitsa','bain'], 'douche': ['laver','rehitsa','bain'],
  'laver': ['rehitsa','bain','ablution'], 'bain': ['rehitsa','laver'], 'sallebain': ['rehitsa','laver'],
  'baigner': ['rehitsa','laver','bain'],
  'creme': ['sikha','oindre','huile','pommade'], 'pommade': ['sikha','oindre'],
  'parfum': ['sikha','besamim'], 'oindre': ['sikha'],
  'bijou': ['bijoux','ornement','takhchit','femme'], 'bijoux': ['ornement','takhchit','femme'],
  'bague': ['bijoux','ornement','takhchit'], 'collier': ['bijoux','ornement','takhchit'],
  'boucle': ['bijoux','ornement','takhchit'], 'montre': ['bijoux','ornement','takhchit'],
  'incendie': ['feu','dlika','sauvetage'], 'brule': ['feu','incendie'], 'flamme': ['feu'],
  'pain': ['lehem','michne','pains'], 'pains': ['lehem','michne'],
  'bougies': ['bougie','hadlaka','allumage','nerot'], 'bougie': ['hadlaka','allumage','nerot'],
  'bougeoir': ['bougie','chandelier','mouktse','deplacement'], 'chandelier': ['bougie','bougeoir'],
  'heure': ['moment','zman','horaire'], 'moment': ['zman','heure'],
  'cuire': ['bishoul','mevashel','cuisson'], 'cuisiner': ['bishoul','mevashel','cuisson'],
  'plata': ['kira','plaque','hatmana'], 'plaque': ['kira','plata','hatmana'],
  'marmite': ['kira','kedera','plata'], 'casserole': ['kira','kedera','marmite'],
  'ongles': ['ongle','preparatifs'], 'insecte': ['tsida','capturer','animal'],
  'mouche': ['tsida','capturer','insecte'], 'attraper': ['tsida','capturer'],
  'lacets': ['qosher','noeud','nouer'], 'balayer': ['balai','maison','nettoyer'],
  'circoncision': ['mila','brit'], 'sauver': ['pikouah','nefesh','sauvetage'],
  'voyage': ['voyageur','chemin','route'], 'kidouch': ['kiddoush','vin'],
  'havdala': ['avdala','besamim'], 'epices': ['besamim','avdala'],
};

// ── Règles de CO-OCCURRENCE ──
// Un mot isolé est ambigu ; la COMBINAISON ne l'est pas. « retirer » seul ne dit
// rien ; « retirer » + « mélange / plat / parmi » désigne sans ambiguïté le borer.
// C'est le levier principal : les questions réelles décrivent une SITUATION, pas
// une mélakha. Chaque règle n'ajoute des termes que si les deux familles sont là.
const CONCEPT_RULES = [
  { any: ['retirer','enlever','oter','sortir','separer','trier','choisir','prendre','isoler','ecarter'],
    ctx: ['melange','plat','assiette','salade','parmi','milieu','bol','morceaux','aliments','nourriture','petitspois','pommedeterre','legumes','fruits','poisson','arretes'],
    add: ['borer','berira','okhel','pesolet','tri'], w: 2.4 },
  { any: ['chaud','rechauffer','remettre','reposer','poser'],
    ctx: ['plata','plaque','kira','marmite','casserole','four','feu'],
    add: ['hazara','kira','plata','hatmana','bishoul'], w: 2.0 },
  { any: ['mal','douleur','malade','fievre','soigner','medicament','cachet','comprime'],
    ctx: ['tete','ventre','gorge','dent','enfant','bebe','prendre','maltete','malventre'],
    add: ['malade','refoua','soin','maladie'], w: 2.2 },
  { any: ['deplacer','bouger','toucher','ranger'],
    ctx: ['objet','mouktse','bougie','bougeoir','chandelier','argent','telephone','outil','casse','inutile'],
    add: ['mouktse','tiltoul','deplacement'], w: 1.8 },
  { any: ['sortir','porter','mettre'],
    ctx: ['bijoux','bague','collier','boucle','ornement','femme'],
    add: ['bijoux','ornement','takhchit'], w: 2.0 },
  { any: ['allumer','allumage','heure','moment','avant'],
    ctx: ['bougies','bougie','nerot','hadlaka'],
    add: ['hadlaka','bougies','zman','moment'], w: 1.8 },
];

function normalizeToken(s) {
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/['’‘]/g, '').replace(/[^a-z֐-׿0-9]/g, '');
}

// Pré-normalise la chaîne ENTIÈRE (minuscules, sans accents) puis remplace les
// expressions multi-mots, avant tout découpage en tokens.
function preNormalize(text) {
  let t = String(text || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  for (const [re, rep] of MULTIWORD) t = t.replace(re, rep);
  return t;
}

export function tokenize(text) {
  return preNormalize(text)
    .split(/[\s,.;:!?()«»""'‘’\-—–_/]+/)
    .map(normalizeToken)
    .filter((t) => t.length >= 2 && !STOPWORDS.has(t));
}

// Termes de CONCEPT déduits des règles de co-occurrence. Ils servent aussi de
// clés d'accès au garde-fou keyToken : si l'on a reconnu que la question porte
// sur le borer, les chunks qui parlent de borer doivent pouvoir passer, même
// s'ils ne nomment jamais « pomme de terre ».
function conceptTerms(tokens) {
  const set = new Set(tokens);
  const out = new Set();
  CONCEPT_RULES.forEach((rule) => {
    if (rule.any.some((w) => set.has(w)) && rule.ctx.some((w) => set.has(w))) {
      rule.add.forEach((t) => { const n = normalizeToken(t); if (n.length >= 2) out.add(n); });
    }
  });
  return out;
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
  // Co-occurrence : n'ajoute les termes de concept que si les DEUX familles de
  // mots sont présentes — évite d'injecter « borer » dès qu'on lit « prendre ».
  const set = new Set(tokens);
  CONCEPT_RULES.forEach((rule) => {
    if (rule.any.some((w) => set.has(w)) && rule.ctx.some((w) => set.has(w))) {
      rule.add.forEach((term) => {
        const n = normalizeToken(term);
        if (n.length >= 2) expanded.set(n, Math.max(expanded.get(n) || 0, rule.w));
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

function scoreChunk(chunk, queryTerms, keyTokens, originalTokens, strict, conceptKeys = []) {
  const k1 = 1.5, b = 0.75;
  const tf = chunk._tfMap;
  // Garde-fou keyToken : au moins un token original à haute IDF doit matcher —
  // OU un terme de concept reconnu par les règles de co-occurrence. Sans cette
  // seconde porte, une question dont le mot le plus rare est un ALIMENT (« pomme
  // de terre ») n'atteint jamais les chunks de la mélakha concernée (borer).
  if (keyTokens.length
      && !keyTokens.some((t) => tf.get(t))
      && !conceptKeys.some((t) => tf.get(t))) return 0;
  // Mode strict (prod) : au moins 2 tokens distincts doivent matcher (les termes
  // de concept comptent, sinon le strict annule le bénéfice des règles).
  if (strict) {
    // Exigence PROPORTIONNELLE à la longueur de la question. Exiger 2 tokens
    // correspondants sur une question de 2 mots utiles (« le feu », « médicament
    // tête ») élimine presque tout : en production cela rendait 6 questions sur
    // 32 totalement vides. On exige 2 matchs seulement à partir de 4 tokens.
    const need = originalTokens.length >= 4 ? 2 : 1;
    let matched = 0;
    for (const t of originalTokens) { if (tf.get(t)) matched++; if (matched >= need) break; }
    if (matched < need) for (const t of conceptKeys) { if (tf.get(t)) matched++; if (matched >= need) break; }
    if (matched < need) return 0;
  }

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
  const strict = opts.strict === true;
  // Filtre de section optionnel ('orach-chaim' | 'yoreh-deah'). Absent → tout le
  // corpus (rétro-compatible). Les anciens chunks sans champ `section` ne sont
  // jamais exclus, pour éviter toute régression silencieuse.
  const section = opts.section || null;
  const tokens = tokenize(question);
  if (tokens.length === 0) return { results: [], keyTokens: [], totalChunks: _N };

  // Key tokens = les 2 tokens originaux de plus haute IDF, choisis UNIQUEMENT
  // parmi ceux qui EXISTENT dans le corpus. getIdf() attribue l'IDF maximale à
  // tout mot inconnu : une faute de frappe, une marque ou une expression absente
  // devenait donc le « portail » du garde-fou keyToken et mettait TOUS les chunks
  // à zéro — la recherche ne renvoyait alors plus rien (ex. « râper des carottes »).
  const known = tokens.filter((t) => _idf.has(t));
  const byIdf = [...new Set(known)].map((t) => ({ t, idf: getIdf(t) })).sort((a, b) => b.idf - a.idf);
  const keyTokens = byIdf.slice(0, 2).map((x) => x.t);
  const conceptKeys = [...conceptTerms(tokens)];
  // Idem pour le mode strict : n'exiger que des tokens réellement indexables.
  const originalSet = [...new Set(known.length ? known : tokens)];

  const expanded = expandQuery(tokens);
  const scored = [];
  for (const c of _corpus.chunks) {
    if (section && c.section && c.section !== section) continue;
    const s = scoreChunk(c, expanded, keyTokens, originalSet, strict, conceptKeys);
    if (s >= minScore) scored.push({ chunk: c, score: s });
  }
  scored.sort((a, b) => b.score - a.score);
  return {
    results: scored.slice(0, limit).map((r) => ({
      siman: r.chunk.siman,
      section: r.chunk.section || null,
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

// ── Cache KV des réponses corpus reformulées ───────────────────────────────
// La même question revient souvent ("c'est quoi le borer ?"). On cache la
// reformulation Haiku : 1re personne → ~0.005 €, toutes les suivantes → 0 €.
// Clé versionnée : bumper CORPUS_CACHE_VERSION invalide tout le cache d'un coup
// (à faire si on change le system prompt de reformulation).
// La clé inclut la section pour ne jamais servir une réponse Shabbat sur une
// conversation Yoreh De'ah (et inversement).
export const CORPUS_CACHE_VERSION = 'v1';
export const CORPUS_CACHE_TTL = 30 * 24 * 60 * 60; // 30 jours
export function corpusCacheKey(text, { section = 'orach-chaim', lang = 'fr' } = {}) {
  const norm = String(text || '')
    .toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '') // sans accents → meilleur hit rate
    .replace(/[!?.,;:'"«»()\[\]{}]/g, '')
    .replace(/\s+/g, ' ')
    .trim() // en DERNIER : la ponctuation retirée peut laisser un espace final
    .slice(0, 120);
  return `corpus-cache:${CORPUS_CACHE_VERSION}:${section}:${lang}:${norm}`;
}

export function getCorpusStats() {
  loadAndIndex();
  return { totalChunks: _N, totalSimanim: _corpus?.meta?.totalSimanim || 0, avgdl: _avgdl };
}
