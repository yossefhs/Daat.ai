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

// ── IDENTITÉ DES OUVRAGES ───────────────────────────────────────────────────
// Constat A (tests de l'interface publique, septembre 2026) : interrogé sur
// « Choul'han Aroukh HaRav 317:4 », le modèle a appelé
// Shulchan_Arukh,_Orach_Chayim.317.4 — le Choul'han Aroukh de R. Yossef Karo —
// et a attribué le passage à l'Admour HaZaken. L'outil ne rendait que
// { ref, title, hebrew, english } : rien n'y nommait l'AUTEUR, et « title »
// (« Shulchan Arukh, Orach Chayim 317 ») se lit comme le titre demandé.
// Chaque résultat porte désormais l'identité de l'ouvrage RÉELLEMENT servi
// (work, author, work_he), l'URL publique du passage, et une note explicite
// pour les paires confusables. Le modèle doit comparer `work` à l'ouvrage que
// l'utilisateur a nommé AVANT d'attribuer quoi que ce soit.
const WORKS = [
  // [préfixe de l'indexTitle Sefaria, ouvrage (FR), auteur, nature, note de confusion]
  ['Shulchan Arukh HaRav', "Choul'han Aroukh HaRav", 'Rabbi Chnéour Zalman de Liadi (Admour HaZaken)', 'texte primaire',
    "Ceci est le Choul'han Aroukh HaRav (Admour HaZaken), NON le Choul'han Aroukh de R. Yossef Karo (ref Shulchan_Arukh,_…)."],
  ['Shulchan Arukh', "Choul'han Aroukh", 'Rabbi Yossef Karo (Mehaber) ; gloses (הגה) : Rama', 'texte primaire',
    "Ceci est le Choul'han Aroukh de R. Yossef Karo, NON le Choul'han Aroukh HaRav de l'Admour HaZaken (ref Shulchan_Arukh_HaRav,_…)."],
  ['Kitzur Shulchan Arukh', "Kitsour Choul'han Aroukh", 'Rabbi Chlomo Ganzfried', 'texte primaire',
    "Ceci est le Kitsour (abrégé) de R. Ganzfried, NON le Choul'han Aroukh ni le Choul'han Aroukh HaRav."],
  ['Seder Birkat HaNehenin', 'Séder Birkot HaNehenin', 'Rabbi Chnéour Zalman de Liadi (Admour HaZaken)', 'texte primaire', null],
  ['Tanya', 'Tanya (Likoutei Amarim)', 'Rabbi Chnéour Zalman de Liadi (Admour HaZaken)', 'texte primaire', null],
  ['Likkutei Torah', 'Likoutei Torah', 'Rabbi Chnéour Zalman de Liadi (Admour HaZaken)', 'texte primaire', null],
  ['Torah Or', 'Torah Or', 'Rabbi Chnéour Zalman de Liadi (Admour HaZaken)', 'texte primaire', null],
  ['Mishnah Berurah', 'Michna Beroura', "Rabbi Israël Meïr Kagan (Hafets Haïm)", 'commentaire', null],
  ['Biur Halakha', "Bi'our Halakha", "Rabbi Israël Meïr Kagan (Hafets Haïm)", 'commentaire', null],
  ['Sha\'ar HaTziyun', "Cha'ar HaTsiyoun", "Rabbi Israël Meïr Kagan (Hafets Haïm)", 'commentaire', null],
  ['Arukh HaShulchan', "Aroukh HaChoul'han", 'Rabbi Yehiel Mikhel Epstein', 'texte primaire', null],
  ['Beit Yosef', 'Beit Yossef', 'Rabbi Yossef Karo', 'commentaire', null],
  ['Tur', 'Tour', 'Rabbi Yaakov ben Acher', 'texte primaire', null],
  ['Mishneh Torah', 'Michné Torah', 'Rambam (Maïmonide)', 'texte primaire', null],
  ['Magen Avraham', 'Magen Avraham', 'Rabbi Avraham Gombiner', 'commentaire', null],
  ['Turei Zahav', 'Taz (Tourei Zahav)', 'Rabbi David HaLevi Segal', 'commentaire', null],
  ['Siftei Kohen', 'Chakh (Siftei Kohen)', 'Rabbi Chabtaï HaKohen', 'commentaire', null],
  ['Rashi on ', 'Rachi', 'Rabbi Chlomo Yitshaki', 'commentaire', null],
  ['Tosafot on ', 'Tossafot', 'école des Tossafistes', 'commentaire', null],
  ['Jerusalem Talmud', 'Talmud Yerouchalmi', 'Amoraïm d’Erets Israël', 'texte primaire', null],
  ['Mishnah ', 'Michna', 'Tannaïm (rédaction : Rabbi Yehouda HaNassi)', 'texte primaire', null],
  ['Zohar', 'Zohar', 'attribué à Rabbi Chimon bar Yohaï', 'texte primaire', null],
];
const BAVLI = new Set(['Berakhot', 'Shabbat', 'Eruvin', 'Pesachim', 'Shekalim', 'Yoma', 'Sukkah', 'Beitzah', 'Rosh Hashanah', 'Taanit', 'Megillah', 'Moed Katan', 'Chagigah', 'Yevamot', 'Ketubot', 'Nedarim', 'Nazir', 'Sotah', 'Gittin', 'Kiddushin', 'Bava Kamma', 'Bava Metzia', 'Bava Batra', 'Sanhedrin', 'Makkot', 'Shevuot', 'Avodah Zarah', 'Horayot', 'Zevachim', 'Menachot', 'Chullin', 'Bekhorot', 'Arakhin', 'Temurah', 'Keritot', 'Meilah', 'Tamid', 'Niddah']);
const TANAKH = new Set(['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'I Samuel', 'II Samuel', 'I Kings', 'II Kings', 'Isaiah', 'Jeremiah', 'Ezekiel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 'Psalms', 'Proverbs', 'Job', 'Song of Songs', 'Ruth', 'Lamentations', 'Ecclesiastes', 'Esther', 'Daniel', 'Ezra', 'Nehemiah', 'I Chronicles', 'II Chronicles']);

// Titre d'index déduit d'une ref au format URL (« Shulchan_Arukh,_Orach_Chayim.317.4 »
// → « Shulchan Arukh, Orach Chayim »). Sert de repli quand Sefaria ne renvoie
// pas `indexTitle` (entrées de cache antérieures, ancien format).
export function indexTitleFromRef(ref) {
  const r = String(ref || '').replace(/_/g, ' ').trim();
  // Coupe à la première composante numérique (« .317 », « 19a », « 6:16 »).
  const m = r.match(/^(.*?)(?:[.\s:]+\d+[ab]?(?:[.:]\d+[ab]?)*(?:-\d+[ab]?(?:[.:]\d+)*)?)?\s*$/);
  return (m && m[1] ? m[1] : r).replace(/[,\s]+$/, '').trim();
}

/**
 * Identité de l'ouvrage réellement servi. `data` est la réponse Sefaria v3
 * (peut être absente pour une entrée de cache) ; `ref` la ref demandée.
 */
// Forme URL d'une ref : « Shulchan Arukh HaRav, Orach Chayim 317:4 » ou
// « Shulchan_Arukh_HaRav,_Orach_Chayim.317.4 » → « Shulchan_Arukh_HaRav,_Orach_Chayim.317.4 ».
export function toUrlRef(ref) {
  let s = String(ref || '').trim().replace(/ /g, '_').replace(/:/g, '.');
  s = s.replace(/_(?=\d)/, '.'); // premier séparateur titre→numéro
  return s;
}

export function describeWork(ref, data) {
  const indexTitle = (data && (data.indexTitle || data.book)) || indexTitleFromRef(ref);
  const out = {
    work: indexTitle,
    work_he: (data && data.heRef) || null,
    author: null,
    nature: 'texte primaire',
    attribution_note: null,
    // L'URL est formée depuis la ref RÉELLEMENT servie : c'est le seul lien que
    // le modèle a le droit d'afficher (jamais une URL construite « au jugé »).
    url: 'https://www.sefaria.org/' + encodeURIComponent(toUrlRef(ref)).replace(/%2C/g, ',').replace(/%2E/g, '.'),
  };
  // Ordre : les préfixes les plus longs d'abord, pour que « Shulchan Arukh HaRav »
  // gagne sur « Shulchan Arukh ».
  const sorted = [...WORKS].sort((a, b) => b[0].length - a[0].length);
  for (const [prefix, workFr, author, nature, note] of sorted) {
    if (indexTitle.startsWith(prefix)) {
      out.work = `${indexTitle} — ${workFr}`;
      out.author = author;
      out.nature = nature;
      out.attribution_note = note;
      return out;
    }
  }
  if (BAVLI.has(indexTitle)) {
    out.work = `${indexTitle} — Talmud Bavli, traité ${indexTitle}`;
    out.author = 'Amoraïm de Babylonie (rédaction : Rav Achi et Ravina)';
    return out;
  }
  if (TANAKH.has(indexTitle)) {
    out.work = `${indexTitle} — Tanakh`;
    out.author = 'Tanakh';
    return out;
  }
  out.attribution_note = "Ouvrage non répertorié par l'outil : identifie l'auteur à partir du titre AVANT d'attribuer, et dis si tu ne le connais pas avec certitude.";
  return out;
}

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
      // Sefaria répond 404 avec un corps JSON explicite sur les références qui
      // n'existent pas : « We have no text for Shulchan Arukh, Orach Chayim
      // 318:99 », « Shulchan Arukh, Orach Chayim ends at Siman 697 ». Transmettre
      // ce message est décisif : « Sefaria HTTP 404 » se lit comme une panne
      // passagère, alors que le vrai message dit que LA RÉFÉRENCE EST FAUSSE —
      // c'est ce qui doit empêcher le modèle de la citer malgré tout.
      let detail = '';
      try { detail = (await response.json())?.error || ''; } catch (_) { /* corps non-JSON */ }
      return {
        ref, hebrew: '', english: '',
        error: detail
          ? `Référence inexistante sur Sefaria — ${detail} Ne cite PAS cette référence et n'en reconstruis pas le texte : vérifie le bon numéro avant de conclure.`
          : `Sefaria HTTP ${response.status}`,
      };
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

    // Versions réellement servies : le lecteur doit savoir que l'anglais est une
    // TRADUCTION (et laquelle), pas la parole de l'auteur.
    const versions = Array.isArray(data.versions)
      ? data.versions.filter(v => v && (v.language === 'he' || v.language === 'en'))
          .map(v => ({ language: v.language, versionTitle: v.versionTitle || null }))
      : [];

    const result = {
      ref,
      ref_resolved: data.ref || null,
      hebrew: hebrew || '',
      english: english || '',
      title: data.title || data.indexTitle || ref,
      indexTitle: data.indexTitle || null,
      heRef: data.heRef || null,
      versions,
    };

    // Réponse 200 mais sans aucun texte : sans ce garde-fou le modèle reçoit un
    // résultat d'apparence valide et en conclut que la référence est bonne.
    if (!result.hebrew && !result.english) {
      return {
        ...result,
        error: `Sefaria n'a renvoyé aucun texte pour « ${ref} » — la référence est probablement mal formée ou inexistante. Ne la cite pas et n'en reconstruis pas le contenu.`,
      };
    }

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
    const results = hits.slice(0, 5).map(h => {
      const ref = h._source?.ref || h._id;
      const w = describeWork(ref, null);
      return {
        ref,
        title: h._source?.heRef || h._source?.ref || '',
        work: w.work,
        author: w.author,
        snippet: stripHtml((h.highlight?.naive_lemmatizer?.[0] || h._source?.exact || '').slice(0, 300)),
        categories: h._source?.path || [],
        note: 'Un résultat de recherche localise un passage ; il ne prouve pas son contenu — lis-le avec sefaria_get_text avant de le citer.',
      };
    });

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
    description:
      "Récupère le texte hébreu (et la traduction anglaise quand elle existe) d'une référence Sefaria précise, avec l'identité de l'ouvrage RÉELLEMENT servi (champs work, author, url). " +
      "À utiliser avant de citer une source ou d'attribuer une position. " +
      "⚠️ Des ouvrages distincts portent des noms voisins et des identifiants différents — ne les substitue jamais l'un à l'autre : " +
      "« Shulchan_Arukh,_Orach_Chayim.N.M » = Choul'han Aroukh de R. Yossef Karo (avec gloses du Rama) ; " +
      "« Shulchan_Arukh_HaRav,_Orach_Chayim.N.M » = Choul'han Aroukh HaRav de l'Admour HaZaken ; " +
      "« Kitzur_Shulchan_Arukh.N.M » = Kitsour de R. Ganzfried ; « Mishnah_Berurah.N.M » ; « Arukh_HaShulchan,_Orach_Chaim.N.M » ; " +
      "« Seder_Birkat_HaNehenin.N.M » ; « Tanya,_Part_I.N » ; « Shabbat.19a » (Bavli) ; « Mishneh_Torah,_Sabbath.6.16 » ; « Genesis.1.1 ». " +
      "Compare toujours le champ `work` du résultat à l'ouvrage demandé par l'utilisateur : si l'ouvrage demandé n'est pas celui servi, dis-le et n'attribue pas le passage à l'ouvrage demandé. " +
      "Un résultat sans erreur prouve que la référence existe, pas qu'elle soutient l'affirmation : lis le texte.",
    input_schema: {
      type: 'object',
      properties: {
        ref: {
          type: 'string',
          description: 'La référence Sefaria au format URL (underscores, virgules, points). Exemples : "Shulchan_Arukh,_Orach_Chayim.246.1" (Karo) · "Shulchan_Arukh_HaRav,_Orach_Chayim.246.1" (Admour HaZaken) · "Shabbat.19a" · "Mishneh_Torah,_Sabbath.6.16". Une plage est possible : "Shulchan_Arukh_HaRav,_Orach_Chayim.319.4-5".',
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
      // Même en erreur, on nomme l'ouvrage que la ref DÉSIGNAIT : « la référence
      // n'existe pas » doit se lire « ce passage du Choul'han Aroukh HaRav n'existe
      // pas », jamais « prends le Choul'han Aroukh à la place ».
      const w = describeWork(result.ref, null);
      return JSON.stringify({
        error: result.error,
        ref: result.ref,
        work_requested: w.work,
        note: "Aucun texte servi : ne cite pas ce passage, ne le reconstruis pas, et ne le remplace pas silencieusement par un autre ouvrage. Si tu proposes une autre source, nomme-la explicitement comme différente.",
      });
    }
    // Tronquer les textes très longs pour éviter d'exploser le contexte
    const MAX = 4000;
    const w = describeWork(result.ref, {
      indexTitle: result.indexTitle, ref: result.ref_resolved, heRef: result.heRef,
    });
    return JSON.stringify({
      ref: result.ref,
      ref_resolved: result.ref_resolved || null,
      work: w.work,
      work_he: w.work_he,
      author: w.author,
      nature: w.nature,
      attribution_note: w.attribution_note,
      url: w.url,
      versions: result.versions || [],
      hebrew: result.hebrew.slice(0, MAX),
      english: result.english.slice(0, MAX),
      english_is_translation: Boolean(result.english),
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
