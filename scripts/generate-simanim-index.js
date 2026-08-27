#!/usr/bin/env node
/**
 * DAAT — Générateur de data/simanim-disponibles.json (v2.1, section-aware)
 *
 * Scanne sources/{shabbat,orah-haim,yoreh-deah} et produit l'index complet
 * avec sections : shabbat · oh-quotidien · yoreh-deah · nida (≥183).
 *
 * IMPORTANT : fusionne avec le JSON existant — les champs title/titleHe/titleEn/numHe
 * déjà présents sont conservés si l'extraction HTML échoue (protection contre les
 * variations de <title>). L'ancienne version (shabbat-only) écrasait l'index
 * section-aware, d'où son retrait du build (commit 6843dcda8) ; cette version
 * est réintégrable au build sans perte.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const OUTPUT = path.join(ROOT, 'data', 'simanim-disponibles.json');

// (répertoire physique, section par défaut, fonction section par numéro)
const SOURCES = [
  { dir: 'shabbat', section: () => 'shabbat' },
  { dir: 'orah-haim', section: () => 'oh-quotidien' },
  { dir: 'yoreh-deah', section: (num) => (num >= 183 ? 'nida' : 'yoreh-deah') },
];

const TITLE_RE = /<title>\s*Siman\s+([^\s—-]+)\s*[—-]\s*([^·|]+?)\s*(?:·|\|)/i;
const H1_RE = /<h1[^>]*class="siman-title-fr"[^>]*>\s*Siman\s+([^\s—-]+)\s*[—-]\s*([^<]+?)\s*<\/h1>/i;

function extractTitle(htmlPath) {
  if (!fs.existsSync(htmlPath)) return null;
  const html = fs.readFileSync(htmlPath, 'utf8');
  let m = html.match(H1_RE);
  if (m) return { numHe: m[1].trim(), title: m[2].trim() };
  m = html.match(TITLE_RE);
  if (m) return { numHe: m[1].trim(), title: m[2].trim() };
  return null;
}

function detectLevels(dir) {
  const files = fs.readdirSync(dir);
  return {
    n1: files.some((f) => /^niveau-1/.test(f)),
    n2: files.some((f) => /^niveau-2/.test(f)),
    n3: files.some((f) => /^niveau-3/.test(f)),
    n4: files.some((f) => /^niveau-4/.test(f)),
  };
}

function levelsLabel(levels) {
  const count = Object.values(levels).filter(Boolean).length;
  if (count === 4) return 'complet';
  if (levels.n4 && !levels.n1) return 'daat-harav';
  if (count >= 1) return `partiel-${count}`;
  return 'index-seul';
}

// L'hébreu du <title> n'est un numHe que s'il contient des lettres hébraïques
function looksHebrew(s) {
  return /[֐-׿]/.test(s || '');
}

function main() {
  // 1. Index existant → réserve de titres (title/titleHe/titleEn/numHe)
  let previous = {};
  if (fs.existsSync(OUTPUT)) {
    try {
      const prev = JSON.parse(fs.readFileSync(OUTPUT, 'utf8'));
      for (const s of prev.simanim || []) previous[s.path] = s;
    } catch (e) {
      console.warn('JSON existant illisible, régénération from scratch:', e.message);
    }
  }

  const simanim = [];
  let skipped = 0;

  for (const src of SOURCES) {
    const baseDir = path.join(ROOT, 'sources', src.dir);
    if (!fs.existsSync(baseDir)) continue;
    const dirs = fs
      .readdirSync(baseDir, { withFileTypes: true })
      .filter((d) => d.isDirectory() && /^siman-\d+$/.test(d.name))
      .map((d) => d.name)
      .sort((a, b) => Number(a.split('-')[1]) - Number(b.split('-')[1]));

    for (const dirName of dirs) {
      const num = Number(dirName.split('-')[1]);
      const dir = path.join(baseDir, dirName);
      const relPath = `sources/${src.dir}/${dirName}/index.html`;
      const indexPath = path.join(dir, 'index.html');
      if (!fs.existsSync(indexPath)) { skipped++; continue; }

      const prev = previous[relPath] || {};
      // Lecture HTML UNIQUEMENT si l'info manque dans le JSON précédent :
      // sur ce disque (iCloud) chaque read peut coûter très cher, et les titres
      // ne changent pas — le merge garantit zéro perte.
      const fr = prev.title && prev.numHe ? null : extractTitle(indexPath);
      const he = prev.titleHe ? null : extractTitle(path.join(dir, 'index-he.html'));
      const en = prev.titleEn ? null : extractTitle(path.join(dir, 'index-en.html'));

      const numHe = prev.numHe || (fr && looksHebrew(fr.numHe) ? fr.numHe : null)
        || (he && looksHebrew(he.numHe) ? he.numHe : null) || String(num);

      const entry = {
        num,
        numHe,
        title: prev.title || (fr && fr.title) || `Siman ${num}`,
        titleHe: prev.titleHe || (he && he.title) || undefined,
        titleEn: prev.titleEn || (en && en.title) || undefined,
        section: src.section(num),
        levels: detectLevels(dir),
        status: null,
        path: relPath,
      };
      entry.status = levelsLabel(entry.levels);
      if (!entry.titleHe) delete entry.titleHe;
      if (!entry.titleEn) delete entry.titleEn;
      simanim.push(entry);
    }
  }

  const bySection = {};
  for (const s of simanim) {
    bySection[s.section] = bySection[s.section] || { counts: { total: 0, complet: 0 } };
    bySection[s.section].counts.total++;
    if (s.status === 'complet') bySection[s.section].counts.complet++;
  }

  const out = {
    meta: {
      version: '2.1',
      description:
        "Index auto-généré des simanim disponibles sur disque (sections shabbat, oh-quotidien, yoreh-deah, nida). Régénéré au build par scripts/generate-simanim-index.js — les titres existants (title/titleHe/titleEn) sont fusionnés, jamais perdus.",
      lastUpdated: new Date().toISOString().slice(0, 10),
      counts: {
        total: simanim.length,
        complet: simanim.filter((s) => s.status === 'complet').length,
        daatHarav: simanim.filter((s) => s.status === 'daat-harav').length,
        partiel: simanim.filter((s) => s.status.startsWith('partiel')).length,
      },
      bySection,
    },
    simanim,
  };

  fs.writeFileSync(OUTPUT, JSON.stringify(out, null, 2) + '\n', 'utf8');
  const secSummary = Object.entries(bySection)
    .map(([k, v]) => `${k}:${v.counts.total}`)
    .join(' · ');
  console.log(`simanim-disponibles.json : ${simanim.length} simanim (${secSummary})${skipped ? ` — ${skipped} sans index.html ignorés` : ''}`);
}

main();
