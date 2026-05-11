#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SHABBAT_DIR = path.join(ROOT, 'sources', 'shabbat');
const OUTPUT = path.join(ROOT, 'data', 'simanim-disponibles.json');

const TITLE_RE = /<title>\s*Siman\s+([^\s—-]+)\s*[—-]\s*([^·|]+?)\s*(?:·|\|)/i;
const H1_RE = /<h1[^>]*class="siman-title-fr"[^>]*>\s*Siman\s+([^\s—-]+)\s*[—-]\s*([^<]+?)\s*<\/h1>/i;

function extractTitle(htmlPath) {
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

function main() {
  if (!fs.existsSync(SHABBAT_DIR)) {
    console.error(`Missing directory: ${SHABBAT_DIR}`);
    process.exit(1);
  }
  const dirs = fs
    .readdirSync(SHABBAT_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory() && /^siman-\d+$/.test(d.name))
    .map((d) => d.name)
    .sort((a, b) => Number(a.split('-')[1]) - Number(b.split('-')[1]));

  const simanim = [];
  let skipped = 0;
  for (const dirName of dirs) {
    const num = Number(dirName.split('-')[1]);
    const dir = path.join(SHABBAT_DIR, dirName);
    const indexPath = path.join(dir, 'index.html');
    if (!fs.existsSync(indexPath)) {
      skipped++;
      continue;
    }
    const titleData = extractTitle(indexPath);
    if (!titleData) {
      skipped++;
      console.warn(`[warn] No title extracted for ${dirName}`);
      continue;
    }
    const levels = detectLevels(dir);
    simanim.push({
      num,
      numHe: titleData.numHe,
      title: titleData.title,
      levels,
      status: levelsLabel(levels),
      path: `sources/shabbat/${dirName}/index.html`,
    });
  }

  const counts = {
    total: simanim.length,
    complet: simanim.filter((s) => s.status === 'complet').length,
    daatHarav: simanim.filter((s) => s.status === 'daat-harav').length,
    partiel: simanim.filter((s) => s.status.startsWith('partiel')).length,
  };

  const output = {
    meta: {
      version: '2.0',
      description:
        'Index auto-généré des simanim disponibles sur disque. Régénéré au build par scripts/generate-simanim-index.js.',
      lastUpdated: new Date().toISOString().slice(0, 10),
      counts,
    },
    simanim,
  };

  fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
  fs.writeFileSync(OUTPUT, JSON.stringify(output, null, 2) + '\n', 'utf8');
  console.log(
    `Generated ${OUTPUT}: ${counts.total} simanim (complet=${counts.complet}, daat-harav=${counts.daatHarav}, partiel=${counts.partiel}), skipped=${skipped}`
  );
}

main();
