#!/usr/bin/env node
/**
 * convert-og-png.js — Convertit les 124 OG SVG en PNG 1200×630 pour
 * Facebook et WhatsApp (qui ne lisent pas les SVG en preview de partage).
 *
 * - Garde les SVG existants (LinkedIn/X/Slack/Discord les supportent)
 * - Génère un PNG par siman en parallèle (assets/img/og/siman-N.png)
 * - Convertit aussi og-default.svg → og-default.png
 *
 * Stratégie meta tags : og:image en PNG (Facebook/WhatsApp), conserver
 * SVG en fallback via twitter:image (X supporte les 2).
 */

import { Resvg } from '@resvg/resvg-js';
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { resolve, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');
const OG_DIR = resolve(ROOT, 'assets/img/og');

const svgFiles = readdirSync(OG_DIR).filter(f => f.endsWith('.svg'));
console.log(`Conversion de ${svgFiles.length} SVG → PNG (1200×630)...\n`);

let totalBytes = 0;
let converted = 0;
let skipped = 0;

for (const file of svgFiles) {
  const svgPath = resolve(OG_DIR, file);
  const pngPath = svgPath.replace(/\.svg$/, '.png');

  // Idempotence : skip si PNG déjà à jour
  try {
    const svgStat = statSync(svgPath);
    const pngStat = statSync(pngPath);
    if (pngStat.mtime >= svgStat.mtime) {
      skipped++;
      continue;
    }
  } catch {
    // PNG n'existe pas, on convertit
  }

  const svgBuf = readFileSync(svgPath);
  const resvg = new Resvg(svgBuf, {
    fitTo: { mode: 'width', value: 1200 }, // force 1200px de large → 630 de haut au ratio
    font: {
      // utiliser les polices système si dispo, sinon fallback
      loadSystemFonts: true,
    },
  });
  const pngBuf = resvg.render().asPng();
  writeFileSync(pngPath, pngBuf);
  totalBytes += pngBuf.length;
  converted++;
  if (converted % 20 === 0) {
    console.log(`  ${converted} convertis...`);
  }
}

console.log(`\n✓ ${converted} PNG générés (${(totalBytes / 1024 / 1024).toFixed(1)} MB total, moy ${Math.round(totalBytes / converted / 1024)} KB)`);
console.log(`· ${skipped} déjà à jour (skip)`);
