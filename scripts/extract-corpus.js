#!/usr/bin/env node
// Extracteur du corpus DAAT — scanne tous les simanim disponibles (Hilkhot
// Shabbat / Orah Haïm ET Yoreh De'ah) et génère data/corpus-shabbat.json
// (index BM25-ready pour /api/chat-corpus et le corpus-first de /api/chat).
//
// Chaque chunk porte un champ `section` ('orach-chaim' | 'yoreh-deah') pour que
// la recherche puisse se restreindre à la section de la conversation, et un
// `sourceUrl` pointant vers la bonne route (/oh/N/base ou /yd/N/base).
//
// Chunking par siman :
// - 1 chunk par <div class="definition|remember|key-point">
// - 1 chunk par ligne du tableau "Cas pratiques modernes"
// - 1 chunk par bloc <h3> + paragraphes narratifs
// Métadonnées : siman, section, sectionTitle, subsection, type, simanTitle, sourceUrl

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const META_DIR = path.join(ROOT, 'data', 'simanim');
const OUTPUT_PATH = path.join(ROOT, 'data', 'corpus-shabbat.json');

// Sections scannées. `section` correspond exactement à la valeur utilisée par
// /api/chat (req.body.section) afin que le filtrage soit direct.
const SECTIONS = [
  { id: 'orach-chaim', dir: path.join(ROOT, 'sources', 'shabbat'), urlPrefix: '/oh', useMetaDir: true },
  // Orah Haïm quotidien (simanim 1-33+) : même section halakhique que Shabbat
  // (id 'orach-chaim' pour que le filtre de recherche du chat les couvre), mais
  // routes /oh-quotidien et titres stockés sous section 'oh-quotidien' dans le
  // catalogue → dispoId distinct pour la résolution des titres.
  { id: 'orach-chaim', dir: path.join(ROOT, 'sources', 'orah-haim'), urlPrefix: '/oh-quotidien', useMetaDir: false, dispoId: 'oh-quotidien' },
  // sources/yoreh-deah/ héberge DEUX sections du catalogue : 'yoreh-deah'
  // (issour ve-heter, 87-118) et 'nida' (183-200, physiquement dans le même
  // dossier). Sans la seconde clé, les 18 simanim de nidah sortaient du corpus
  // avec le titre générique « Siman 195 » et un titre hébreu VIDE : la recherche
  // perdait le bonus de titre sur toute la section — 551 chunks aveugles.
  { id: 'yoreh-deah', dir: path.join(ROOT, 'sources', 'yoreh-deah'), urlPrefix: '/yd', useMetaDir: false, dispoIds: ['yoreh-deah', 'nida'] },
];

// Cartes de titres pour les sections sans data/simanim/*.json (ex. Yoreh De'ah),
// construites depuis les manifestes simanim-disponibles{,-he}.json déjà maintenus.
function loadDispoMap(file) {
  try {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', file), 'utf8'));
    const m = {};
    for (const s of d.simanim || []) m[`${s.section || 'shabbat'}:${s.num}`] = s;
    return m;
  } catch { return {}; }
}
const DISPO_FR = loadDispoMap('simanim-disponibles.json');
const DISPO_HE = loadDispoMap('simanim-disponibles-he.json');

// Simanim indexés sans titre résolu : signalés en fin de build (voir plus bas).
const MISSING_TITLES = [];

// Résout titreFr / titreHe / sous-titre d'un siman selon sa section.
function resolveMeta(section, num) {
  if (section.useMetaDir) {
    const metaPath = path.join(META_DIR, `siman-${num}.json`);
    if (fs.existsSync(metaPath)) {
      try {
        const m = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
        return { titleFr: m.titleFr || `Siman ${num}`, titleHe: m.titleHe || '', subtitle: m.subtitle || '' };
      } catch { /* ignore */ }
    }
  }
  // Un même répertoire source peut héberger plusieurs sections du catalogue :
  // on essaie chaque clé candidate avant de retomber sur le libellé générique.
  const candidates = section.dispoIds || [section.dispoId || section.id];
  if (!candidates.includes(section.id)) candidates.push(section.id);
  let fr = null;
  let he = null;
  for (const id of candidates) {
    if (!fr) fr = DISPO_FR[`${id}:${num}`] || null;
    if (!he) he = DISPO_HE[`${id}:${num}`] || null;
  }
  // Un titre manquant doit être VISIBLE au build : sans ce signal, la section
  // nidah est restée sans titre (et donc mal indexée) pendant tout un chantier.
  if (!fr) MISSING_TITLES.push(`${section.id}:${num}`);
  return {
    titleFr: (fr && fr.title) || `Siman ${num}`,
    titleHe: (he && he.title) || (fr && fr.titleHe) || (fr && fr.numHe) || '',
    subtitle: '',
  };
}

// ── Helpers HTML → texte ───────────────────────────────────────────────────
function decodeEntities(s) {
  return s
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/&laquo;/g, '«').replace(/&raquo;/g, '»').replace(/&hellip;/g, '…')
    .replace(/&mdash;/g, '—').replace(/&ndash;/g, '–');
}

function htmlToText(html) {
  let s = html;
  s = s.replace(/<style[\s\S]*?<\/style>/gi, '');
  s = s.replace(/<script[\s\S]*?<\/script>/gi, '');
  s = s.replace(/<div class="page-break"[^>]*><\/div>/gi, '');
  s = s.replace(/<br\s*\/?>/gi, '\n');
  s = s.replace(/<\/(p|div|li|tr|h[1-6])>/gi, '\n');
  s = s.replace(/<\/td>/gi, ' · ');
  s = s.replace(/<li[^>]*>/gi, '• ');
  s = s.replace(/<[^>]+>/g, '');
  s = decodeEntities(s);
  s = s.replace(/[ \t]+/g, ' ');
  s = s.replace(/\n[ \t]+/g, '\n');
  s = s.replace(/\n{3,}/g, '\n\n');
  return s.trim();
}

// ── Extraction des chunks d'un fichier ─────────────────────────────────────
// ── Extracteurs spécifiques aux niveaux 3 et 4 ────────────────────────────
// Les pages n'ont pas toutes la même structure HTML. Le niveau 1 (et 2) utilise
// <h2 class="section-title"> ; le niveau 4 utilise <h2 class="section-title-fr">
// + des <div class="sa-block"> (un par séif du Choulhan Aroukh HaRav) ; le
// niveau 3 n'a que des <h2 id="…"> nus. Sans ces extracteurs, les niveaux 3 et 4
// produisaient 0 et 23 chunks — le Daat HaRav restait invisible pour le chat.

// Niveau 4 — Daat HaRav : un chunk par sa-block (texte hébreu du Choulhan Aroukh
// HaRav + son rendu français). On garde les deux ensemble : le français est ce
// que l'utilisateur tape, l'hébreu est la citation faisant autorité.
function extractDaatHaRav(siman, body) {
  const chunks = [];
  // Chaque séif est un <details class="seif-details"> contenant :
  //   <summary> avec <span class="seif-num">סעיף א</span>
  //   <div class="sa-block"> avec <p class="sa-he"> (texte du Choulhan Aroukh
  //   HaRav) et <p class="sa-fr"> (rendu français).
  // On découpe sur <details> plutôt que sur </div> : les blocs sont imbriqués
  // dans <details>, et un lookahead sur </div> n'en capturait qu'UN sur 30.
  const secTitles = [];
  const secRe = /<h2 class="section-title-fr"[^>]*>([\s\S]*?)<\/h2>/g;
  let sm;
  while ((sm = secRe.exec(body)) !== null) secTitles.push({ pos: sm.index, title: htmlToText(sm[1]) });

  const parts = body.split(/<details class="seif-details"[^>]*>/).slice(1);
  let cursor = 0;
  parts.forEach((part) => {
    cursor = body.indexOf(part, cursor);
    const seifNum = (part.match(/<span class="seif-num"[^>]*>([\s\S]*?)<\/span>/) || [])[1];
    const he = (part.match(/<p class="sa-he"[^>]*>([\s\S]*?)<\/p>/g) || []).map(htmlToText).join(' ').trim();
    const fr = (part.match(/<p class="sa-fr"[^>]*>([\s\S]*?)<\/p>/g) || []).map(htmlToText).join(' ').trim();
    const text = [fr, he].filter(Boolean).join('\n\n').trim();
    if (text.length < 40) return;
    // Titre de la section la plus proche EN AMONT de ce séif.
    let sectionTitle = 'Daat HaRav — Choulhan Aroukh HaRav';
    let sectionNum = 1;
    secTitles.forEach((st, i) => { if (st.pos < cursor) { sectionTitle = st.title; sectionNum = i + 1; } });
    chunks.push({
      id: `siman-${siman.num}-daatharav-${chunks.length + 1}`,
      siman: siman.num,
      sectionNum,
      sectionTitle,
      subsection: seifNum ? htmlToText(seifNum) : null,
      text,
      type: 'daat-harav',
    });
  });
  return chunks;
}

// Niveau 3 — Synthèse : sections délimitées par des <h2 id="…"> sans classe.
function extractSynthese(siman, body) {
  const chunks = [];
  const re = /<h2[^>]*id="[^"]*"[^>]*>([\s\S]*?)<\/h2>([\s\S]*?)(?=<h2[^>]*id="|<\/section|<\/main|<\/body|$)/g;
  let m, idx = 0;
  while ((m = re.exec(body)) !== null) {
    idx++;
    const sectionTitle = htmlToText(m[1]);
    if (/Plan de l'étude|Navigation|Sommaire/i.test(sectionTitle)) continue;
    const text = htmlToText(m[2]).trim();
    if (text.length < 60) continue;
    // Découpe les sections longues en morceaux d'environ 700 caractères,
    // sur les frontières de phrase, pour rester comparable aux autres niveaux.
    const parts = text.length <= 900 ? [text] : text.match(/[\s\S]{1,900}(?:\.|$)/g) || [text];
    parts.forEach((p) => {
      const t = p.trim();
      if (t.length < 60) return;
      chunks.push({
        id: `siman-${siman.num}-synth-${chunks.length + 1}`,
        siman: siman.num,
        sectionNum: idx,
        sectionTitle,
        subsection: null,
        text: t,
        type: 'synthese',
      });
    });
  }
  return chunks;
}

function extractChunks(siman, html) {
  const chunks = [];
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
  const body = bodyMatch ? bodyMatch[1] : html;

  // Tolérant aux attributs supplémentaires (ex. id="…" ajouté pour les ancres).
  const sectionRegex = /<h2 class="section-title"[^>]*>([\s\S]*?)<\/h2>([\s\S]*?)(?=<h2 class="section-title"[^>]*>|$)/g;
  let match;
  let sectionIndex = 0;
  while ((match = sectionRegex.exec(body)) !== null) {
    sectionIndex++;
    const sectionTitle = htmlToText(match[1]);
    const sectionContent = match[2];

    // Skip les sections bruyantes
    if (/Plan de l'étude|Le texte du Choul'han Aroukh|Mishnah Berurah — premières entrées|Questions de compréhension/.test(sectionTitle)) {
      continue;
    }

    // Cas pratiques modernes → 1 chunk par ligne du tableau
    if (/Cas pratiques modernes/i.test(sectionTitle)) {
      const rowRe = /<tr>\s*<td[^>]*><strong>([^<]+)<\/strong><\/td>\s*<td[^>]*>([\s\S]*?)<\/td>\s*<\/tr>/g;
      let row;
      while ((row = rowRe.exec(sectionContent)) !== null) {
        const situation = htmlToText(row[1]);
        const analysis = htmlToText(row[2]);
        const text = situation + ' — ' + analysis;
        if (text.length < 30) continue;
        chunks.push({
          id: `siman-${siman.num}-cas-${chunks.length + 1}`,
          siman: siman.num,
          sectionNum: sectionIndex,
          sectionTitle, subsection: 'Cas pratique : ' + situation,
          text, type: 'cas-pratique',
        });
      }
      continue;
    }

    // Blocs définition/remember/key-point
    const blockRe = /<div class="(definition|remember|key-point)"[^>]*>([\s\S]*?)<\/div>(?=\s*<(?:div class="(?:definition|remember|key-point|page-break)"|h\d|p\b|table\b|hr\b|\/section|\/body))/g;
    let block;
    let blockIdx = 0;
    while ((block = blockRe.exec(sectionContent)) !== null) {
      const text = htmlToText(block[2]);
      if (text.length < 40) continue;
      blockIdx++;
      chunks.push({
        id: `siman-${siman.num}-s${sectionIndex}-b${blockIdx}`,
        siman: siman.num,
        sectionNum: sectionIndex,
        sectionTitle, subsection: null,
        text, type: block[1],
      });
    }

    // Paragraphes narratifs (h3 + p)
    const h3Re = /<h3[^>]*>([\s\S]*?)<\/h3>([\s\S]*?)(?=<h3|<h2|$)/g;
    let h3m;
    while ((h3m = h3Re.exec(sectionContent)) !== null) {
      const h3Title = htmlToText(h3m[1]);
      const subClean = h3m[2].replace(/<div class="(definition|remember|key-point)"[^>]*>[\s\S]*?<\/div>/g, '');
      const text = htmlToText(subClean);
      if (text.length < 60) continue;
      chunks.push({
        id: `siman-${siman.num}-s${sectionIndex}-h3-${chunks.length}`,
        siman: siman.num,
        sectionNum: sectionIndex,
        sectionTitle, subsection: h3Title,
        text, type: 'narratif',
      });
    }
  }
  return chunks;
}

// ── Scan de tous les simanim, section par section ──────────────────────────
const allChunks = [];
// Les QUATRE niveaux d'étude sont indexés. Historiquement seul niveau-1-base
// était scanné : le chat ne voyait donc que 30 % de ce que le Rav a écrit, et
// le niveau 4 (Daat HaRav — 4,8 M de caractères, l'autorité du site) lui était
// totalement invisible. C'est ce qui rendait les réponses « corpus » minces :
// elles reformulaient une page débutant.
const LEVELS = [
  { file: 'niveau-1-base.html',        id: 'base',       label: 'Base',       urlSuffix: 'base' },
  { file: 'niveau-2-lamdan.html',      id: 'lamdan',     label: 'Lamdan',     urlSuffix: 'lamdan' },
  { file: 'niveau-3-synthese.html',    id: 'synthese',   label: 'Synthèse',   urlSuffix: 'synthese' },
  { file: 'niveau-4-daat-harav.html',  id: 'daat-harav', label: 'Daat HaRav', urlSuffix: 'daat-harav' },
];

const stats = { totalSimanim: 0, withChunks: 0, skipped: [], chunksPerSiman: {}, perSection: {}, perLevel: {} };

for (const section of SECTIONS) {
  if (!fs.existsSync(section.dir)) continue;
  stats.perSection[section.id] = 0;
  const simanDirs = fs.readdirSync(section.dir)
    .filter((d) => /^siman-\d+$/.test(d))
    .sort((a, b) => parseInt(a.slice(6)) - parseInt(b.slice(6)));

  for (const dir of simanDirs) {
    const simanNum = parseInt(dir.slice(6));
    const meta = resolveMeta(section, simanNum);
    let simanChunks = 0;

    for (const level of LEVELS) {
      const htmlPath = path.join(section.dir, dir, level.file);
      if (!fs.existsSync(htmlPath)) {
        // Absence normale pour certains niveaux (ex. simanim 304 et 322 n'ont pas
        // de niveau 4 : l'Admour HaZaken ne les a pas écrits — page passerelle).
        if (level.id === 'base') stats.skipped.push({ section: section.id, num: simanNum, reason: 'pas de niveau-1-base.html' });
        continue;
      }

      const html = fs.readFileSync(htmlPath, 'utf8');
      const bodyM = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
      const body = bodyM ? bodyM[1] : html;
      const chunks = level.id === 'daat-harav' ? extractDaatHaRav({ num: simanNum }, body)
                   : level.id === 'synthese'   ? extractSynthese({ num: simanNum }, body)
                   : extractChunks({ num: simanNum }, html);
      if (chunks.length === 0) continue;

      chunks.forEach((c) => {
        c.section = section.id;
        c.level = level.id;
        c.levelLabel = level.label;
        c.simanTitle = meta.titleFr;
        c.simanTitleHe = meta.titleHe;
        c.simanSubtitle = meta.subtitle || '';
        c.sourceUrl = `${section.urlPrefix}/${simanNum}/${level.urlSuffix}`;
      });

      stats.perLevel[level.id] = (stats.perLevel[level.id] || 0) + chunks.length;
      stats.perSection[section.id] += chunks.length;
      simanChunks += chunks.length;
      allChunks.push(...chunks);
    }

    if (simanChunks === 0) { stats.skipped.push({ section: section.id, num: simanNum, reason: 'aucun chunk extrait' }); continue; }
    stats.totalSimanim++;
    stats.withChunks++;
    stats.chunksPerSiman[`${section.id}:${simanNum}`] = simanChunks;
  }
}

const output = {
  meta: {
    generated: new Date().toISOString(),
    totalSimanim: stats.withChunks,
    totalChunks: allChunks.length,
    skipped: stats.skipped,
    perSection: stats.perSection,
    perLevel: stats.perLevel,
    source: 'sources/{shabbat,yoreh-deah}/siman-*/niveau-{1-base,2-lamdan,3-synthese,4-daat-harav}.html — les 4 niveaux ; champs `section` et `level` par chunk',
  },
  chunks: allChunks,
};

fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output), 'utf8');
const sizeKb = (fs.statSync(OUTPUT_PATH).size / 1024).toFixed(1);

console.log(`\n✓ Corpus généré : ${OUTPUT_PATH}`);
console.log(`  Simanim avec chunks : ${stats.withChunks}/${stats.totalSimanim}`);
console.log(`  Chunks totaux       : ${allChunks.length}`);
console.log(`  Taille JSON         : ${sizeKb} KB`);
console.log(`  Par section         : ${Object.entries(stats.perSection).map(([k, v]) => `${k}=${v}`).join(', ')}`);
console.log(`  Skipped (${stats.skipped.length})  : ${stats.skipped.map((s) => `${s.section || ''}#${s.num}`).slice(0, 5).join(',')}${stats.skipped.length > 5 ? '...' : ''}`);
if (MISSING_TITLES.length) {
  console.warn(`\n⚠️  ${MISSING_TITLES.length} siman(im) indexés SANS titre (recherche dégradée) : ${MISSING_TITLES.slice(0, 20).join(', ')}${MISSING_TITLES.length > 20 ? '…' : ''}`);
  console.warn('    → ajouter le siman au catalogue data/simanim-disponibles.json, ou sa clé de section à SECTIONS[].dispoIds.');
}

// Distribution chunks/siman
const counts = Object.values(stats.chunksPerSiman);
counts.sort((a, b) => a - b);
console.log(`  Chunks/siman p50    : ${counts[Math.floor(counts.length / 2)]}`);
console.log(`  Chunks/siman max    : ${counts[counts.length - 1]} (siman ${Object.keys(stats.chunksPerSiman).find((k) => stats.chunksPerSiman[k] === counts[counts.length - 1])})`);
