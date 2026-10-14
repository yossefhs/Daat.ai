#!/usr/bin/env node
/**
 * DAAT — Générateur d'images Open Graph PNG (1200×630) par niveau
 *
 * Génère 5 images PNG par siman :
 *   - siman-{N}-base.png       (Mehaber, nombre de séifim du Mehaber)
 *   - siman-{N}-lamdan.png     (Approfondissement Rishonim/Acharonim)
 *   - siman-{N}-synthese.png   (Synthèse et règles à retenir)
 *   - siman-{N}-daat-harav.png (Chitah de l'Admour HaZaken — SA HaRav)
 *   - siman-{N}.png            (Index neutre, 4 niveaux)
 *
 * Plus og-default.png pour les pages génériques.
 *
 * Usage :
 *   node scripts/generate-og-image-png.js          # tous les simanim
 *   node scripts/generate-og-image-png.js 299 301
 *   node scripts/generate-og-image-png.js --default
 *
 * Output : assets/img/og/*.png
 *
 * Dépendances : @resvg/resvg-js (déjà installé)
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Resvg } from '@resvg/resvg-js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');
const DATA_DIR = resolve(ROOT, 'data', 'simanim');
const OUT_DIR  = resolve(ROOT, 'assets', 'img', 'og');
const FONTS_DIR = resolve(ROOT, 'assets', 'fonts');

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

// Charger les polices
const frankRuhlFont = readFileSync(join(FONTS_DIR, 'FrankRuhlLibre.ttf'));
const cormorantFont = readFileSync(join(FONTS_DIR, 'CormorantGaramond.ttf'));

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

// -- Wrap text by character length --
function wrap(text, maxLen) {
  if (!text) return [''];
  const words = text.split(/\s+/);
  const lines = [];
  let cur = '';
  for (const w of words) {
    const test = (cur + ' ' + w).trim();
    if (test.length > maxLen) {
      if (cur) lines.push(cur);
      cur = w;
    } else {
      cur = test;
    }
  }
  if (cur) lines.push(cur);
  return lines;
}

// -- Render SVG for a level --
function renderOG({ titleFr, titleHe, numberLabel, subtitle }) {
  // Adapter la taille du titre hébreu selon sa longueur (titres longs : plus petit, pas de débordement)
  const heLength = (titleHe || '').length;
  const heFontSize = heLength > 50 ? 42 : heLength > 40 ? 46 : heLength > 35 ? 52 : heLength > 25 ? 62 : 70;
  
  // Découper le titre hébreu par mots (coupure naturelle, sans débordement)
  let heLines = [];
  if (titleHe) {
    heLines = titleHe.length > 28 ? wrap(titleHe, 28).slice(0, 3) : [titleHe];
  }
  
  // Position Y du titre hébreu (ajusté pour ne pas chevaucher)
  const heBaseY = 190;
  const heLineHeight = heFontSize + 8;
  
  // Titre français : wrap plus court pour éviter le débordement
  const titleLines = wrap(titleFr, 32).slice(0, 2);
  const frFontSize = titleLines.length > 1 ? 48 : 54;
  
  // Position Y du français (après l'hébreu avec marge)
  const frStartY = heBaseY + (heLines.length * heLineHeight) + 35;
  const frLineHeight = frFontSize + 10;
  
  // Subtitle : plus bas encore
  const subtitleLines = wrap(subtitle || '', 70).slice(0, 2);
  const subStartY = frStartY + (titleLines.length * frLineHeight) + 30;
  
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <style>
      .bg          { fill: ${COLORS.parchment}; }
      .border-frame{ fill: none; stroke: ${COLORS.gold}; stroke-width: 4; }
      .border-inner{ fill: none; stroke: ${COLORS.gold}; stroke-width: 1.5; opacity: 0.4; }
      .label       { font-family: 'Inter', sans-serif; font-size: 16px; font-weight: 600;
                     letter-spacing: 5px; fill: ${COLORS.gold}; text-transform: uppercase; }
      .title-fr    { font-family: 'Cormorant Garamond', Georgia, serif; font-size: ${frFontSize}px;
                     font-weight: 600; fill: ${COLORS.navy}; }
      .title-he    { font-family: 'Frank Ruhl Libre', serif; font-size: ${heFontSize}px; font-weight: 900;
                     fill: ${COLORS.gold}; direction: rtl; }
      .subtitle    { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 19px;
                     font-style: italic; fill: ${COLORS.textMid}; }
      .number      { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 26px;
                     font-weight: 500; fill: ${COLORS.gold}; letter-spacing: 2px; }
      .brand-he    { font-family: 'Frank Ruhl Libre', serif; font-size: 32px; font-weight: 700;
                     fill: ${COLORS.gold}; }
      .brand-en    { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600;
                     letter-spacing: 4px; fill: ${COLORS.textMid}; text-transform: uppercase; }
      .brand-tag   { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 16px;
                     font-style: italic; fill: ${COLORS.textMid}; }
    </style>

    <pattern id="grain" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <rect width="40" height="40" fill="${COLORS.parchment}"/>
      <circle cx="3" cy="7"  r="0.6" fill="${COLORS.parchmentDark}" opacity="0.3"/>
      <circle cx="22" cy="18" r="0.4" fill="${COLORS.parchmentDark}" opacity="0.25"/>
      <circle cx="35" cy="32" r="0.5" fill="${COLORS.parchmentDark}" opacity="0.3"/>
      <circle cx="11" cy="28" r="0.3" fill="${COLORS.parchmentDark}" opacity="0.2"/>
    </pattern>

    <linearGradient id="margin" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="${COLORS.parchmentDark}" stop-opacity="0.55"/>
      <stop offset="80%" stop-color="${COLORS.parchmentDark}" stop-opacity="0.0"/>
    </linearGradient>
  </defs>

  <rect class="bg" x="0" y="0" width="1200" height="630"/>
  <rect x="0" y="0" width="1200" height="630" fill="url(#grain)"/>

  <rect x="0" y="0" width="80" height="630" fill="url(#margin)"/>
  <line x1="80" y1="0" x2="80" y2="630" stroke="${COLORS.gold}" stroke-width="2" opacity="0.6"/>

  <rect class="border-frame" x="32" y="32" width="1136" height="566" rx="6"/>
  <rect class="border-inner" x="48" y="48" width="1104" height="534" rx="3"/>

  <text class="label" x="120" y="88">CHOULHAN AROUKH · ÉTUDE EN FRANÇAIS</text>

  ${numberLabel ? `<text class="number" x="120" y="135">${esc(numberLabel)}</text>` : ''}

  ${heLines.map((line, i) => `<text class="title-he" x="1080" y="${heBaseY + i * heLineHeight}" text-anchor="end">${esc(line)}</text>`).join('\n  ')}

  ${titleLines.map((line, i) => `<text class="title-fr" x="120" y="${frStartY + i * frLineHeight}">${esc(line)}</text>`).join('\n  ')}

  ${subtitleLines.map((line, i) => `<text class="subtitle" x="120" y="${subStartY + i * 26}">${esc(line)}</text>`).join('\n  ')}

  <line x1="120" y1="545" x2="1080" y2="545" stroke="${COLORS.gold}" stroke-width="1" opacity="0.4"/>
  <text class="brand-he" x="120" y="582">דעת</text>
  <text class="brand-en" x="185" y="580">DAAT</text>
  <text class="brand-tag" x="1080" y="580" text-anchor="end">daattorah.com</text>
</svg>
`;
}

// -- Convert SVG to PNG --
function svgToPng(svgString) {
  const resvg = new Resvg(svgString, {
    fitTo: {
      mode: 'width',
      value: 1200,
    },
    font: {
      loadSystemFonts: false,
      fontFiles: [
        join(FONTS_DIR, 'FrankRuhlLibre.ttf'),
        join(FONTS_DIR, 'CormorantGaramond.ttf'),
      ],
    },
  });
  const pngData = resvg.render();
  return pngData.asPng();
}

// -- Generate 5 images for a siman --
async function generateForSiman(filepath) {
  const data = JSON.parse(readFileSync(filepath, 'utf8'));
  const simanNum = data.number;
  const titleHe = data.titleHe;
  const titleFr = data.titleFr;
  const numberLabel = `Siman ${simanNum} · ${data.numberHe || ''}`;
  
  // Récupérer le nombre de seifim du Mehaber depuis data/seifim-count.json
  let nbSeifimMehaber = null;
  const seifsPath = resolve(ROOT, 'data', 'seifim-count.json');
  if (existsSync(seifsPath)) {
    const seifsData = JSON.parse(readFileSync(seifsPath, 'utf8'));
    const key = `shabbat_${simanNum}`;
    nbSeifimMehaber = seifsData[key]?.shulchan_arukh || null;
  }
  
  // Vérifier si c'est un siman-passerelle (304, 322)
  const isBridge = [304, 322].includes(simanNum);

  // Titre Mehaber (en-tête du siman) pour la seule image Base du 301 ;
  // les autres niveaux gardent titleHe du JSON (הַאֵיךְ …).
  const TITLE_HE_BASE = {
    301: 'באיזה כלים מותר לצאת בשבת ואיזה מהם אסורים',
  };

  const onlySuffix = flag('--suffix'); // ex. --suffix base

  const levels = [
    {
      suffix: 'base',
      subtitle: nbSeifimMehaber 
        ? `Texte du Choulhan Aroukh (Mehaber) et du Rama — ${nbSeifimMehaber} seifim, traduction et explications`
        : 'Texte du Choulhan Aroukh (Mehaber) et du Rama — traduction et explications',
    },
    {
      suffix: 'lamdan',
      subtitle: `Approfondissement : Rishonim et A'haronim sur le Siman ${simanNum}`,
    },
    {
      suffix: 'synthese',
      subtitle: `Synthèse et règles à retenir du Siman ${simanNum}`,
    },
    {
      suffix: 'daat-harav',
      subtitle: isBridge
        ? 'Page-passerelle : discussion par analogie (pas de siman dans le Choulhan Aroukh HaRav)'
        : `La chitah de l'Admour HaZaken — Choulhan Aroukh HaRav, siman ${simanNum}`,
    },
    {
      suffix: '',
      subtitle: `Siman ${simanNum} — Choulhan Aroukh et commentaires, en 4 niveaux`,
    },
  ];
  
  let totalSize = 0;
  for (const level of levels) {
    if (onlySuffix && level.suffix !== onlySuffix) continue;
    const svg = renderOG({
      titleFr,
      titleHe: (level.suffix === 'base' && TITLE_HE_BASE[simanNum]) || titleHe,
      numberLabel,
      subtitle: level.subtitle,
    });
    
    const png = svgToPng(svg);
    const filename = level.suffix 
      ? `siman-${simanNum}-${level.suffix}.png` 
      : `siman-${simanNum}.png`;
    const outPath = join(OUT_DIR, filename);
    writeFileSync(outPath, png);
    totalSize += png.length;
    console.log(`✓ ${outPath} (${(png.length / 1024).toFixed(1)} KB)`);
  }
  return totalSize;
}

// -- Generate og-default.png --
async function writeDefault() {
  const svg = renderOG({
    numberLabel: 'דעת התורה לעומקה',
    titleFr: "L'étude halakhique en français",
    titleHe: 'דעת',
    subtitle: 'Choulhan Aroukh par siman, en 4 niveaux — Base, Lamdan, Synthèse, Daat HaRav',
  });
  
  const png = svgToPng(svg);
  const outPath = join(OUT_DIR, 'og-default.png');
  writeFileSync(outPath, png);
  console.log(`✓ ${outPath} (${(png.length / 1024).toFixed(1)} KB)`);
  return png.length;
}

// -- Process simanim --
function getSimanFiles() {
  const range = flag('--range');
  let lo = -Infinity, hi = Infinity;
  if (range) {
    const m = /^(\d+)-(\d+)$/.exec(range);
    if (!m) { console.error('--range attend la forme 242-365'); process.exit(1); }
    lo = Number(m[1]); hi = Number(m[2]);
  }
  
  // Si --siman est fourni avec plusieurs numéros, on les parse
  const onlySimanim = args.filter(arg => /^\d+$/.test(arg)).map(Number);
  if (onlySimanim.length > 0) {
    return onlySimanim.map(n => join(DATA_DIR, `siman-${n}.json`));
  }
  
  return readdirSync(DATA_DIR)
    .filter(f => /^siman-\d+\.json$/.test(f))
    .filter(f => { const n = Number(f.match(/\d+/)[0]); return n >= lo && n <= hi; })
    .map(f => resolve(DATA_DIR, f));
}

// -- Main --
const onlyDefault = has('--default');

(async () => {
  let totalSize = 0;
  
  if (onlyDefault) {
    totalSize = await writeDefault();
  } else {
    const files = getSimanFiles();
    for (const f of files) {
      totalSize += await generateForSiman(f);
    }
    if (!flag('--range') && args.length === 0) {
      totalSize += await writeDefault();
    }
    console.log(`\n🎨 ${files.length * 5 + (args.length === 0 ? 1 : 0)} images OG PNG générées dans ${OUT_DIR}`);
    console.log(`📦 Taille totale: ${(totalSize / 1024 / 1024).toFixed(2)} MB`);
  }
})();
