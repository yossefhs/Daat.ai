#!/usr/bin/env node
/**
 * DAAT — Générateur d'images Open Graph (SVG 1200×630)
 *
 * Génère une image OG par siman à partir des données JSON dans
 * data/simanim/. Génère aussi og-default.svg pour les pages génériques.
 *
 * Usage :
 *   node scripts/generate-og-image.js          # tous les simanim
 *   node scripts/generate-og-image.js --siman 242
 *   node scripts/generate-og-image.js --default
 *
 * Output : assets/img/og/siman-{N}.svg + assets/img/og/og-default.svg
 *
 * Note : Format SVG car les bots OG (Facebook, Twitter, Slack, WhatsApp,
 * LinkedIn) acceptent les SVG vectoriels. Très léger (~3 KB chacun) et
 * permet du texte hébreu sans rasterisation.
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');
const DATA_DIR = resolve(ROOT, 'data', 'simanim');
const OUT_DIR  = resolve(ROOT, 'assets', 'img', 'og');

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

// -- Helpers --
const args = process.argv.slice(2);
const flag = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const has  = (n) => args.includes(n);

const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');

// -- Couleurs DAAT --
const COLORS = {
  parchment: '#F5F0E8',
  parchmentSoft: '#FBF7EF',
  parchmentDark: '#EDE3CE',
  gold: '#B8972A',
  goldLight: '#D4B255',
  navy: '#1A1F3A',
  text: '#1A1F3A',
  textMid: '#3D4266',
};

// -- Wrap text by character length (rough) --
function wrap(text, maxLen) {
  if (!text) return [''];
  const words = text.split(/\s+/);
  const lines = [];
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > maxLen) {
      lines.push(cur.trim());
      cur = w;
    } else {
      cur = (cur + ' ' + w).trim();
    }
  }
  if (cur) lines.push(cur);
  return lines;
}

// -- Render a single OG image --
function renderOG({ titleFr, titleHe, numberLabel, subtitle }) {
  const titleLines = wrap(titleFr, 28).slice(0, 3);
  const subtitleLines = wrap(subtitle || '', 60).slice(0, 2);

  const fontImport = `
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Frank+Ruhl+Libre:wght@500;700;900&family=Inter:wght@400;500;600&display=swap');
  `;

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <style>${fontImport}
      .bg          { fill: ${COLORS.parchment}; }
      .border-frame{ fill: none; stroke: ${COLORS.gold}; stroke-width: 4; }
      .border-inner{ fill: none; stroke: ${COLORS.gold}; stroke-width: 1.5; opacity: 0.4; }
      .label       { font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 600;
                     letter-spacing: 6px; fill: ${COLORS.gold}; text-transform: uppercase; }
      .title-fr    { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 64px;
                     font-weight: 600; fill: ${COLORS.navy}; }
      .title-he    { font-family: 'Frank Ruhl Libre', serif; font-size: 96px; font-weight: 900;
                     fill: ${COLORS.gold}; direction: rtl; }
      .subtitle    { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 24px;
                     font-style: italic; fill: ${COLORS.textMid}; }
      .number      { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 44px;
                     font-weight: 500; fill: ${COLORS.gold}; }
      .brand-he    { font-family: 'Frank Ruhl Libre', serif; font-size: 32px; font-weight: 700;
                     fill: ${COLORS.gold}; }
      .brand-en    { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600;
                     letter-spacing: 4px; fill: ${COLORS.textMid}; text-transform: uppercase; }
      .brand-tag   { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 16px;
                     font-style: italic; fill: ${COLORS.textMid}; }
    </style>

    <!-- Subtle paper grain -->
    <pattern id="grain" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <rect width="40" height="40" fill="${COLORS.parchment}"/>
      <circle cx="3" cy="7"  r="0.6" fill="${COLORS.parchmentDark}" opacity="0.3"/>
      <circle cx="22" cy="18" r="0.4" fill="${COLORS.parchmentDark}" opacity="0.25"/>
      <circle cx="35" cy="32" r="0.5" fill="${COLORS.parchmentDark}" opacity="0.3"/>
      <circle cx="11" cy="28" r="0.3" fill="${COLORS.parchmentDark}" opacity="0.2"/>
    </pattern>

    <!-- Manuscript margin (left) -->
    <linearGradient id="margin" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="${COLORS.parchmentDark}" stop-opacity="0.55"/>
      <stop offset="80%" stop-color="${COLORS.parchmentDark}" stop-opacity="0.0"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect class="bg" x="0" y="0" width="1200" height="630"/>
  <rect x="0" y="0" width="1200" height="630" fill="url(#grain)"/>

  <!-- Manuscript margin -->
  <rect x="0" y="0" width="80" height="630" fill="url(#margin)"/>
  <line x1="80" y1="0" x2="80" y2="630" stroke="${COLORS.gold}" stroke-width="2" opacity="0.6"/>

  <!-- Outer frame -->
  <rect class="border-frame" x="32" y="32" width="1136" height="566" rx="6"/>
  <rect class="border-inner" x="48" y="48" width="1104" height="534" rx="3"/>

  <!-- Top label -->
  <text class="label" x="120" y="120">CHOULHAN AROUKH · ÉTUDE EN FRANÇAIS</text>

  <!-- Number en français + hébreu -->
  ${numberLabel ? `<text class="number" x="120" y="180">${esc(numberLabel)}</text>` : ''}

  <!-- Hebrew title (top right) -->
  <text class="title-he" x="1140" y="220" text-anchor="end">${esc(titleHe || '')}</text>

  <!-- Title FR (multi-line) -->
  ${titleLines.map((line, i) => `<text class="title-fr" x="120" y="${280 + i * 78}">${esc(line)}</text>`).join('\n  ')}

  <!-- Subtitle (multi-line) -->
  ${subtitleLines.map((line, i) => `<text class="subtitle" x="120" y="${460 + i * 32}">${esc(line)}</text>`).join('\n  ')}

  <!-- Footer brand -->
  <line x1="120" y1="535" x2="1080" y2="535" stroke="${COLORS.gold}" stroke-width="1" opacity="0.4"/>
  <text class="brand-he" x="120" y="575">דעת</text>
  <text class="brand-en" x="180" y="572">DAAT</text>
  <text class="brand-tag" x="1080" y="575" text-anchor="end">daattorah.com</text>
</svg>
`;
}

// -- Render a default OG (no specific siman) --
function renderDefault() {
  return renderOG({
    numberLabel: 'דעת התורה לעומקה',
    titleFr: "L'étude halakhique en français",
    titleHe: 'דעת',
    subtitle: 'Choulhan Aroukh par siman, en 3 niveaux — Base, Lamdan, Synthèse',
  });
}

// -- Process simanim --
function getSimanFiles() {
  return readdirSync(DATA_DIR)
    .filter(f => /^siman-\d+\.json$/.test(f))
    .map(f => resolve(DATA_DIR, f));
}

function generateForSiman(filepath) {
  const data = JSON.parse(readFileSync(filepath, 'utf8'));
  const svg = renderOG({
    numberLabel: `Siman ${data.number} · ${data.numberHe}`,
    titleFr: data.titleFr,
    titleHe: data.titleHe,
    subtitle: data.subtitle || data.description?.slice(0, 100),
  });
  const outPath = join(OUT_DIR, `siman-${data.number}.svg`);
  writeFileSync(outPath, svg, 'utf8');
  console.log(`✓ ${outPath} (${(svg.length / 1024).toFixed(1)} KB)`);
}

// -- Main --
const onlySiman = flag('--siman');
const onlyDefault = has('--default');

if (onlyDefault) {
  const out = join(OUT_DIR, 'og-default.svg');
  writeFileSync(out, renderDefault(), 'utf8');
  console.log(`✓ ${out}`);
} else if (onlySiman) {
  generateForSiman(join(DATA_DIR, `siman-${onlySiman}.json`));
} else {
  // All simanim + default
  const files = getSimanFiles();
  for (const f of files) generateForSiman(f);

  const def = join(OUT_DIR, 'og-default.svg');
  writeFileSync(def, renderDefault(), 'utf8');
  console.log(`✓ ${def}`);

  console.log(`\n🎨 ${files.length + 1} images OG générées dans ${OUT_DIR}`);
}
