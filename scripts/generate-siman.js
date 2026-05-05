#!/usr/bin/env node
/**
 * DAAT — Générateur de page index de siman
 *
 * Génère la page d'accueil d'un siman (sources/shabbat/siman-XXX/index.html)
 * à partir d'un fichier JSON de données.
 *
 * Usage :
 *   node scripts/generate-siman.js --siman 247
 *   node scripts/generate-siman.js --file data/simanim/siman-247.json
 *
 * Met aussi à jour sitemap.xml automatiquement (sauf --no-sitemap).
 *
 * Le générateur produit la page **index** d'un siman uniquement. Les pages
 * niveau-1-base / niveau-2-lamdan / niveau-3-synthese restent rédigées
 * manuellement (chaque siman a son propre pilpoul).
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');

// ---------- 1) Parse args ----------
const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : null;
};
const has = (name) => args.includes(name);

const simanArg = flag('--siman');
const fileArg  = flag('--file');
const noSitemap = has('--no-sitemap');

if (!simanArg && !fileArg) {
  console.error('Usage : node scripts/generate-siman.js --siman 247');
  console.error('     ou : node scripts/generate-siman.js --file data/simanim/siman-247.json');
  process.exit(1);
}

const dataPath = fileArg
  ? resolve(ROOT, fileArg)
  : resolve(ROOT, 'data', 'simanim', `siman-${simanArg}.json`);

if (!existsSync(dataPath)) {
  console.error(`Fichier de données introuvable : ${dataPath}`);
  process.exit(1);
}

const data = JSON.parse(readFileSync(dataPath, 'utf8'));

// ---------- 2) Helpers ----------
const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');

// pour les attributs HTML — pas de break-out de quotes
const escAttr = (s) => esc(s);

const SITE = 'https://daattorah.com';

// ---------- 3) Construction du JSON-LD ----------
function buildJsonLd(d) {
  const url = `${SITE}/sources/shabbat/siman-${d.number}/`;
  const graph = [
    {
      "@type": ["Article", "LearningResource"],
      "@id": `${url}#article`,
      "headline": `Siman ${d.number} — ${d.titleFr}`,
      "alternativeHeadline": d.titleHe,
      "description": d.description,
      "url": url,
      "image": `${SITE}/assets/img/yh-logo.png`,
      "inLanguage": "fr-FR",
      "isAccessibleForFree": true,
      "learningResourceType": "Cours d'étude halakhique",
      "educationalLevel": ["Débutant", "Intermédiaire", "Avancé"],
      "teaches": d.teaches || [],
      "keywords": d.keywords || '',
      "author": { "@id": `${SITE}/#rav-samama` },
      "publisher": { "@id": `${SITE}/#organization` },
      "isPartOf": { "@id": `${SITE}/sources/shabbat/#webpage` },
      "citation": d.citations || [],
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Accueil", "item": `${SITE}/` },
        { "@type": "ListItem", "position": 2, "name": "Orah Haïm — Hilkhot Shabbat", "item": `${SITE}/sources/shabbat/` },
        { "@type": "ListItem", "position": 3, "name": `Siman ${d.number}`, "item": url }
      ]
    }
  ];

  if (d.faq && d.faq.length) {
    graph.push({
      "@type": "FAQPage",
      "mainEntity": d.faq.map(({ q, a }) => ({
        "@type": "Question",
        "name": q,
        "acceptedAnswer": { "@type": "Answer", "text": a }
      }))
    });
  }

  return JSON.stringify({ "@context": "https://schema.org", "@graph": graph }, null, 2);
}

// ---------- 4) Build FAQ HTML ----------
function buildFaqHtml(faq) {
  if (!faq || !faq.length) return '';
  const items = faq.map(({ q, a }) => `
      <details>
        <summary>${esc(q)}</summary>
        <p class="daat-faq-answer">${a}</p>
      </details>`).join('\n');
  return `
    <section class="daat-faq">
      <h2>Questions fréquentes — Siman ${esc(faq.length && '')}</h2>
      ${items}
    </section>`;
}

// ---------- 5) Build levels HTML ----------
function buildLevelsHtml(levels) {
  if (!levels || !levels.length) return '';
  return levels.map((lvl) => `
      <article class="daat-level-card">
        <div class="daat-level-bar bar-${lvl.bar || lvl.num}"></div>
        <p style="font-family: var(--daat-font-sans); font-size: 11px; letter-spacing: 2px; color: var(--daat-text-muted); margin-bottom: 8px;">NIVEAU 0${lvl.num}</p>
        <h3 style="font-family: var(--daat-font-hebrew); direction: rtl; font-size: 22px; color: var(--daat-navy); margin-bottom: 4px;">${esc(lvl.nameHe)}</h3>
        <h3 style="font-family: var(--daat-font-serif); font-size: 20px; font-weight: 500; color: var(--daat-navy); margin-bottom: 12px;">${esc(lvl.nameFr)}</h3>
        <p style="color: var(--daat-text-mid); margin-bottom: 16px;">${esc(lvl.desc)}</p>
        <a href="${escAttr(lvl.href)}" class="daat-btn daat-btn-secondary">📖 Étudier</a>
        ${lvl.pdf ? `<a href="${escAttr(lvl.pdf)}" class="daat-btn daat-btn-ghost" target="_blank" style="margin-left: 8px;">📄 PDF</a>` : ''}
      </article>`).join('\n');
}

// ---------- 6) HTML template ----------
function render(d) {
  const url = `${SITE}/sources/shabbat/siman-${d.number}/`;
  const titleSeo = `Siman ${d.number} — ${d.titleFr} · Choulhan Aroukh · Étude en français | DAAT`;
  const ogImage = `${SITE}/assets/img/yh-logo.png`;
  const jsonLd = buildJsonLd(d);
  const levelsHtml = buildLevelsHtml(d.levels);
  const faqHtml = (d.faq || []).map(({ q, a }) => `
        <details>
          <summary>${esc(q)}</summary>
          <p class="daat-faq-answer">${a}</p>
        </details>`).join('\n');

  return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="../../../favicon.svg">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${esc(titleSeo)}</title>
  <meta name="description" content="${escAttr(d.description)}">
  <meta name="author" content="Rav Yossef Haim Samama">
  <meta name="keywords" content="${escAttr(d.keywords || '')}">
  <link rel="canonical" href="${url}">

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="DAAT דעת">
  <meta property="og:title" content="Siman ${d.number} — ${esc(d.titleFr)} (Choulhan Aroukh)">
  <meta property="og:description" content="${escAttr(d.description)}">
  <meta property="og:url" content="${url}">
  <meta property="og:image" content="${ogImage}">
  <meta property="og:locale" content="fr_FR">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Siman ${d.number} — ${esc(d.titleFr)}">
  <meta name="twitter:description" content="${escAttr(d.description)}">
  <meta name="twitter:image" content="${ogImage}">

  <script type="application/ld+json">
${jsonLd}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&family=Frank+Ruhl+Libre:wght@400;500;700;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../../assets/css/daat.css">
</head>
<body class="daat-reset daat-body">

  <header class="daat-header">
    <a href="../../../index.html" class="daat-logo">
      <span class="daat-logo-he">דעת</span>
      <span class="daat-logo-en">DAAT</span>
    </a>
    <nav class="daat-nav">
      <a href="../../../index.html">Accueil</a>
      <a href="../../../sources/shabbat/">Hilkhot Shabbat</a>
      <a href="../../../chat.html">💬 IA Daat</a>
      <a href="../../../soutenir.html" class="daat-btn-ghost">♥ Soutenir</a>
    </nav>
  </header>

  <div class="daat-breadcrumb">
    <div class="daat-breadcrumb-inner">
      <a href="../../../index.html">Accueil</a>
      <span class="sep">›</span>
      <a href="../../../sources/shabbat/">Hilkhot Shabbat</a>
      <span class="sep">›</span>
      <span class="current">Siman ${d.number}</span>
    </div>
  </div>

  <div class="daat-hero">
    <div class="daat-hero-inner">
      <p class="daat-hero-meta">Orah Haïm · Hilkhot Shabbat · Siman ${esc(d.numberHe || '')}</p>
      <p class="daat-hero-title-he" aria-hidden="true">${esc(d.titleHe)}</p>
      <h1 class="daat-hero-title-fr" style="margin: 0;">Siman ${d.number} — ${esc(d.titleFr)}</h1>
      ${d.subtitle ? `<p class="daat-hero-subtitle">${esc(d.subtitle)}</p>` : ''}
    </div>
  </div>

  <main class="daat-content">

    ${d.seifText ? `
    <section class="daat-source-citation" style="margin-bottom: 40px;">
      <p class="daat-hebrew-block">${d.seifText.he}</p>
      <p style="margin-top: 16px; font-style: normal;">${d.seifText.fr}</p>
      <cite>Choulhan Aroukh, Orah Haïm ${d.number}${d.seifText.seif ? ':' + d.seifText.seif : ''}</cite>
    </section>` : ''}

    <h2 style="font-family: var(--daat-font-serif); font-size: 28px; color: var(--daat-navy); margin-bottom: 24px;">Les 3 niveaux d'étude</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 60px;">
      ${levelsHtml}
    </div>

    ${faqHtml ? `
    <section class="daat-faq">
      <h2>Questions fréquentes — Siman ${d.number}</h2>
      ${faqHtml}
    </section>` : ''}

  </main>

  <footer class="daat-footer">
    <p>DAAT דעת — © 5786 / 2026 · <a href="../../../index.html">Retour à l'accueil</a> · Initié par le Rav Yossef Haim Samama</p>
  </footer>

  <link rel="stylesheet" href="../../../assets/css/chat-widget.css">
  <script>window.DAAT_CHAT_API_URL = 'https://daatai.vercel.app/api/chat';</script>
  <script src="../../../assets/js/chat-widget.js" defer></script>
</body>
</html>
`;
}

// ---------- 7) Update sitemap.xml ----------
function updateSitemap(simanNumber) {
  const sitemapPath = resolve(ROOT, 'sitemap.xml');
  if (!existsSync(sitemapPath)) {
    console.warn('  sitemap.xml introuvable — skipped');
    return;
  }
  let xml = readFileSync(sitemapPath, 'utf8');
  const today = new Date().toISOString().slice(0, 10);

  const simanUrl = `${SITE}/sources/shabbat/siman-${simanNumber}/`;
  if (xml.includes(`<loc>${simanUrl}</loc>`)) {
    console.log(`  sitemap : siman-${simanNumber} déjà présent`);
    return;
  }

  const block = `
  <url>
    <loc>${simanUrl}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>${SITE}/sources/shabbat/siman-${simanNumber}/niveau-1-base.html</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>${SITE}/sources/shabbat/siman-${simanNumber}/niveau-2-lamdan.html</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>${SITE}/sources/shabbat/siman-${simanNumber}/niveau-3-synthese.html</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
`;

  xml = xml.replace('</urlset>', block + '</urlset>');
  writeFileSync(sitemapPath, xml, 'utf8');
  console.log(`  sitemap : entrées ajoutées pour siman-${simanNumber}`);
}

// ---------- 8) Run ----------
const html = render(data);
const outDir  = resolve(ROOT, 'sources', 'shabbat', `siman-${data.number}`);
const outPath = join(outDir, 'index.html');

if (!existsSync(outDir)) {
  mkdirSync(outDir, { recursive: true });
  console.log(`📁 Dossier créé : ${outDir}`);
}

if (existsSync(outPath) && !has('--force')) {
  console.error(`⚠  ${outPath} existe déjà. Utilise --force pour écraser.`);
  process.exit(1);
}

writeFileSync(outPath, html, 'utf8');
console.log(`✓ Page générée : ${outPath}`);

if (!noSitemap) {
  updateSitemap(data.number);
}

console.log(`\nProchaine étape : créer les pages niveau-1-base.html, niveau-2-lamdan.html`);
console.log(`et niveau-3-synthese.html dans ${outDir} (rédaction manuelle, chaque siman est unique).`);
