#!/usr/bin/env node
// Régénère data/simanim-disponibles.json — le catalogue des titres, lu par la
// page d'accueil, contenu.html, la navigation, la lettre d'information ET par
// scripts/extract-corpus.js (qui y prend le titre de chaque chunk du corpus).
//
// ⚠️ DEUX DÉFAUTS CORRIGÉS ICI, tous deux destructeurs :
//  1. Ce script ne scannait que sources/shabbat/ tout en RÉÉCRIVANT le fichier
//     entier : le lancer supprimait les 235 entrées des autres sections
//     (oh-quotidien 185, yoreh-deah 32, nida 18). CLAUDE.md le documentait
//     pourtant comme faisant partie de `npm run build` — une mine.
//  2. Il n'écrivait ni `section`, ni `titleHe`, ni `titleEn` : même les 124
//     simanim conservés perdaient leurs titres hébreu et anglais.
//
// Il FUSIONNE désormais : il rafraîchit ce qu'il sait lire du disque (titre FR,
// niveaux présents, chemin) et PRÉSERVE tout le reste. Il ne supprime jamais une
// entrée. C'est ce qui le rend sûr à lancer au build — et donc ce qui rend
// automatique l'entrée d'un nouveau siman dans le corpus et dans la recherche.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const OUTPUT = path.join(ROOT, 'data', 'simanim-disponibles.json');

// Mêmes répertoires que scripts/extract-corpus.js. `sectionFor` traite le cas de
// sources/yoreh-deah/, qui héberge DEUX sections du catalogue.
const SECTIONS = [
  { dir: path.join(ROOT, 'sources', 'shabbat'), rel: 'sources/shabbat', sectionFor: () => 'shabbat' },
  { dir: path.join(ROOT, 'sources', 'orah-haim'), rel: 'sources/orah-haim', sectionFor: () => 'oh-quotidien' },
  { dir: path.join(ROOT, 'sources', 'yoreh-deah'), rel: 'sources/yoreh-deah', sectionFor: (n) => (n >= 183 ? 'nida' : 'yoreh-deah') },
];

const TITLE_RE = /<title>\s*Siman\s+([^\s—-]+)\s*[—-]\s*([^·|]+?)\s*(?:·|\|)/i;
const H1_RE = /<h1[^>]*class="siman-title-fr"[^>]*>\s*Siman\s+([^\s—-]+)\s*[—-]\s*([^<]+?)\s*<\/h1>/i;

function extractTitle(htmlPath) {
  try {
    const html = fs.readFileSync(htmlPath, 'utf8');
    const m = html.match(H1_RE) || html.match(TITLE_RE);
    return m ? { numHe: m[1].trim(), title: m[2].trim() } : null;
  } catch { return null; }
}

function detectLevels(dir) {
  const files = fs.readdirSync(dir);
  return {
    n1: files.some((f) => /^niveau-1[^-]*\.html$/.test(f) || /^niveau-1-[a-z]+\.html$/.test(f)),
    n2: files.some((f) => /^niveau-2-[a-z]+\.html$/.test(f)),
    n3: files.some((f) => /^niveau-3-[a-z]+\.html$/.test(f)),
    n4: files.some((f) => /^niveau-4-[a-z-]+\.html$/.test(f)),
  };
}

function levelsLabel(levels) {
  const count = Object.values(levels).filter(Boolean).length;
  if (count === 4) return 'complet';
  if (levels.n4 && !levels.n1) return 'daat-harav';
  if (count >= 1) return `partiel-${count}`;
  return 'index-seul';
}

// Index des entrées existantes, par section:num — rien n'est jamais perdu.
let previous = { simanim: [] };
try { previous = JSON.parse(fs.readFileSync(OUTPUT, 'utf8')); } catch { /* premier passage */ }
const kept = new Map();
for (const s of previous.simanim || []) kept.set(`${s.section || 'shabbat'}:${s.num}`, { ...s });

const created = [];
const missingTranslations = [];
let scanned = 0;

for (const section of SECTIONS) {
  if (!fs.existsSync(section.dir)) continue;
  const dirs = fs.readdirSync(section.dir, { withFileTypes: true })
    .filter((d) => d.isDirectory() && /^siman-\d+$/.test(d.name))
    .map((d) => d.name)
    .sort((a, b) => Number(a.split('-')[1]) - Number(b.split('-')[1]));

  for (const dirName of dirs) {
    const num = Number(dirName.split('-')[1]);
    const dir = path.join(section.dir, dirName);
    const indexPath = path.join(dir, 'index.html');
    if (!fs.existsSync(indexPath)) continue;
    scanned++;

    const sec = section.sectionFor(num);
    const key = `${sec}:${num}`;
    const existing = kept.get(key);
    const extracted = extractTitle(indexPath);
    const levels = detectLevels(dir);

    // Le titre rédigé à la main dans le catalogue fait FOI : il est souvent plus
    // riche que le <h1> (il porte la glose entre parenthèses). On ne le remplace
    // que s'il est absent — sinon on rafraîchit seulement l'état du disque.
    const entry = {
      num,
      numHe: (existing && existing.numHe) || (extracted && extracted.numHe) || '',
      title: (existing && existing.title) || (extracted && extracted.title) || `Siman ${num}`,
      ...(existing && existing.titleHe ? { titleHe: existing.titleHe } : {}),
      ...(existing && existing.titleEn ? { titleEn: existing.titleEn } : {}),
      section: sec,
      levels,
      status: levelsLabel(levels),
      path: `${section.rel}/${dirName}/index.html`,
    };
    if (!existing) {
      created.push(`${sec}:${num}`);
      if (!extracted) console.warn(`[warn] ${sec}:${num} — aucun titre lisible dans index.html`);
    }
    if (!entry.titleHe || !entry.titleEn) missingTranslations.push(`${sec}:${num}`);
    kept.set(key, entry);
  }
}

// ORDRE PRÉSERVÉ. Un simple réordonnancement produirait un diff de 4 500 lignes
// sur un fichier que douze autres fichiers lisent et que plusieurs sessions
// touchent — un nid à conflits pour rien. On garde l'ordre du fichier précédent
// et on ajoute les nouveaux à la fin de leur section.
const order = new Map();
(previous.simanim || []).forEach((s, i) => order.set(`${s.section || 'shabbat'}:${s.num}`, i));
const simanim = [...kept.entries()]
  .sort(([ka, a], [kb, b]) => {
    const ia = order.has(ka) ? order.get(ka) : Number.MAX_SAFE_INTEGER;
    const ib = order.has(kb) ? order.get(kb) : Number.MAX_SAFE_INTEGER;
    if (ia !== ib) return ia - ib;
    return (a.section || '').localeCompare(b.section || '') || a.num - b.num;
  })
  .map(([, v]) => v);

function countsOf(list) {
  return {
    total: list.length,
    complet: list.filter((s) => s.status === 'complet').length,
    daatHarav: list.filter((s) => s.status === 'daat-harav').length,
    partiel: list.filter((s) => String(s.status).startsWith('partiel')).length,
  };
}
const counts = countsOf(simanim);
// ⚠️ meta.bySection est lu par les TROIS pages d'accueil (index.html, -he, -en)
// pour afficher « N simanim disponibles » par section. Sans lui, elles retombent
// sur meta.counts et annoncent 359 au lieu de 124 sur la section Shabbat —
// une dégradation SILENCIEUSE. Ne pas le retirer.
const bySectionMeta = {};
for (const sec of [...new Set(simanim.map((s) => s.section))]) {
  bySectionMeta[sec] = { counts: countsOf(simanim.filter((s) => s.section === sec)) };
}

fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
fs.writeFileSync(OUTPUT, JSON.stringify({
  meta: {
    version: '3.0',
    description: 'Index des simanim présents sur disque. Régénéré au build par scripts/generate-simanim-index.js — FUSION : ce script ne supprime jamais une entrée et ne remplace jamais un titre écrit à la main.',
    lastUpdated: new Date().toISOString().slice(0, 10),
    counts,
    bySection: bySectionMeta,
  },
  simanim,
}, null, 2) + '\n', 'utf8');

const bySection = {};
for (const s of simanim) bySection[s.section] = (bySection[s.section] || 0) + 1;
console.log(`✓ Catalogue : ${counts.total} simanim (${Object.entries(bySection).map(([k, v]) => `${k}=${v}`).join(', ')}), ${scanned} répertoires scannés`);
if (created.length) console.log(`  Nouveaux : ${created.length} — ${created.slice(0, 10).join(', ')}${created.length > 10 ? '…' : ''}`);
if (missingTranslations.length) {
  console.warn(`\n⚠️  ${missingTranslations.length} siman(im) sans titre hébreu ou anglais (à rédiger à la main — le générateur ne traduit pas) :`);
  console.warn(`    ${missingTranslations.slice(0, 15).join(', ')}${missingTranslations.length > 15 ? '…' : ''}`);
}
