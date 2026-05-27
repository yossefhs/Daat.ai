#!/usr/bin/env node
// POC : extraction du corpus à partir des fichiers niveau-1-base.html
// Découpe chaque siman en chunks atomiques (définition, key-point, cas pratiques, etc.)
// Génère data/corpus-poc.json pour la recherche client-side.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const SIMANIM_POC = [
  { num: 308, title: 'Mouktsé', titleHe: 'מוקצה', topic: 'mouktsé — objets interdits au déplacement Shabbat' },
  { num: 318, title: 'Bishoul', titleHe: 'בישול', topic: 'bishoul — cuisson Shabbat' },
  { num: 319, title: 'Borer',   titleHe: 'בורר',   topic: 'borer — trier Shabbat' },
];

// ── Helpers HTML → texte propre ────────────────────────────────────────────
function decodeEntities(s) {
  return s
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&laquo;/g, '«')
    .replace(/&raquo;/g, '»')
    .replace(/&hellip;/g, '…')
    .replace(/&mdash;/g, '—')
    .replace(/&ndash;/g, '–');
}

function htmlToText(html) {
  let s = html;
  // Retire les conteneurs invisibles (style, script, page-break)
  s = s.replace(/<style[\s\S]*?<\/style>/gi, '');
  s = s.replace(/<script[\s\S]*?<\/script>/gi, '');
  s = s.replace(/<div class="page-break"[^>]*><\/div>/gi, '');
  // Convertit les éléments structurels en sauts de ligne logiques
  s = s.replace(/<br\s*\/?>/gi, '\n');
  s = s.replace(/<\/(p|div|li|tr|h[1-6])>/gi, '\n');
  s = s.replace(/<\/td>/gi, ' · ');
  s = s.replace(/<li[^>]*>/gi, '• ');
  // Retire toutes les balises restantes
  s = s.replace(/<[^>]+>/g, '');
  // Décodage entités + normalisation whitespace
  s = decodeEntities(s);
  s = s.replace(/[ \t]+/g, ' ');
  s = s.replace(/\n[ \t]+/g, '\n');
  s = s.replace(/\n{3,}/g, '\n\n');
  return s.trim();
}

function htmlToFormatted(html) {
  // Version légèrement enrichie pour affichage : garde <strong>, <em>, <bdi>, listes
  let s = html;
  s = s.replace(/<style[\s\S]*?<\/style>/gi, '');
  s = s.replace(/<script[\s\S]*?<\/script>/gi, '');
  s = s.replace(/<div class="page-break"[^>]*><\/div>/gi, '');
  // Garde les classes décoratives utiles (he, he-q), retire les autres
  s = s.replace(/\sstyle="[^"]*"/g, '');
  s = s.replace(/<span class="[^"]*">/g, '<span>');
  s = s.replace(/<div class="(definition|remember|key-point|sacred-text he|sacred-text|translation|quick-recap)"[^>]*>/g, '<div class="poc-block poc-$1">');
  // Normalise whitespace
  s = s.replace(/\s+/g, ' ');
  return s.trim();
}

// ── Extraction des sections d'un fichier niveau-1-base.html ────────────────
function extractChunks(siman, html) {
  const chunks = [];
  // On ne garde que le contenu du <body>
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
  const body = bodyMatch ? bodyMatch[1] : html;

  // Découpe par <h2 class="section-title">
  const sectionRegex = /<h2 class="section-title">([\s\S]*?)<\/h2>([\s\S]*?)(?=<h2 class="section-title">|$)/g;
  let match;
  let sectionIndex = 0;
  while ((match = sectionRegex.exec(body)) !== null) {
    sectionIndex++;
    const rawSectionTitle = match[1];
    const sectionContent = match[2];
    const sectionTitle = htmlToText(rawSectionTitle);

    // Skip les sections trop techniques pour la recherche utilisateur
    if (/Plan de l'étude|Le texte du Choul'han Aroukh|Mishnah Berurah — premières entrées|Questions de compréhension/.test(sectionTitle)) {
      // Le texte du CA contient les 17/19/52 seifim hébreux bruts → trop volumineux et bruité pour le POC
      continue;
    }

    // Stratégie de chunking par section :
    // - Chaque <div class="definition|remember|key-point"> = 1 chunk
    // - Chaque ligne de la table "Cas pratiques modernes" = 1 chunk
    // - Sinon : on garde les paragraphes entre h3 comme 1 chunk
    const blockRegex = /<div class="(definition|remember|key-point)"[^>]*>([\s\S]*?)<\/div>(?=\s*(?:<div class="(?:definition|remember|key-point)"|<h\d|<p|<table|$))/g;
    const tableRowRegex = /<tr>\s*<td[^>]*><strong>([^<]+)<\/strong><\/td>\s*<td[^>]*>([\s\S]*?)<\/td>\s*<\/tr>/g;

    // Cas spécial : section "Cas pratiques modernes" → 1 chunk par ligne du tableau
    if (/Cas pratiques modernes/i.test(sectionTitle)) {
      let rowMatch;
      while ((rowMatch = tableRowRegex.exec(sectionContent)) !== null) {
        const situation = htmlToText(rowMatch[1]);
        const analysis = htmlToText(rowMatch[2]);
        const text = situation + ' — ' + analysis;
        if (text.length < 30) continue;
        chunks.push({
          id: `siman-${siman.num}-cas-${chunks.length + 1}`,
          siman: siman.num,
          sectionNum: sectionIndex,
          sectionTitle: sectionTitle,
          subsection: 'Cas pratique : ' + situation,
          text: text,
          textFormatted: `<strong>${situation}</strong> — ${analysis}`,
          type: 'cas-pratique',
        });
      }
      continue;
    }

    // Cas général : extraire les blocs définition/remember/key-point
    let blockMatch;
    const blockMatches = [];
    const blockTypeRegex = /<div class="(definition|remember|key-point)"[^>]*>([\s\S]*?)<\/div>(?=\s*<(?:div class="(?:definition|remember|key-point|page-break)"|h\d|p\b|table\b|hr\b|\/section|\/body))/g;
    while ((blockMatch = blockTypeRegex.exec(sectionContent)) !== null) {
      blockMatches.push({ type: blockMatch[1], html: blockMatch[2] });
    }
    blockMatches.forEach((b, i) => {
      const text = htmlToText(b.html);
      if (text.length < 40) return;
      chunks.push({
        id: `siman-${siman.num}-s${sectionIndex}-b${i + 1}`,
        siman: siman.num,
        sectionNum: sectionIndex,
        sectionTitle: sectionTitle,
        subsection: null,
        text: text,
        textFormatted: htmlToText(b.html), // version simple pour le POC
        type: b.type,
      });
    });

    // Paragraphes "narratifs" (h3 + p) → 1 chunk par <h3>
    const h3Regex = /<h3>([\s\S]*?)<\/h3>([\s\S]*?)(?=<h3|<h2|$)/g;
    let h3Match;
    while ((h3Match = h3Regex.exec(sectionContent)) !== null) {
      const h3Title = htmlToText(h3Match[1]);
      // Récupère le texte des <p> de cette sous-section (hors blocs déjà capturés)
      const sub = h3Match[2];
      // Retire les blocs définition/remember/key-point (déjà comptés)
      const subClean = sub.replace(/<div class="(definition|remember|key-point)"[^>]*>[\s\S]*?<\/div>/g, '');
      const text = htmlToText(subClean);
      if (text.length < 60) continue;
      chunks.push({
        id: `siman-${siman.num}-s${sectionIndex}-h3-${chunks.length}`,
        siman: siman.num,
        sectionNum: sectionIndex,
        sectionTitle: sectionTitle,
        subsection: h3Title,
        text: text,
        textFormatted: text,
        type: 'narratif',
      });
    }
  }

  return chunks;
}

// ── Main ───────────────────────────────────────────────────────────────────
const allChunks = [];
for (const siman of SIMANIM_POC) {
  const filePath = path.join(ROOT, 'sources', 'shabbat', `siman-${siman.num}`, 'niveau-1-base.html');
  if (!fs.existsSync(filePath)) {
    console.warn(`⚠️  Manquant : ${filePath}`);
    continue;
  }
  const html = fs.readFileSync(filePath, 'utf8');
  const chunks = extractChunks(siman, html);
  // Ajoute le contexte siman à chaque chunk
  chunks.forEach((c) => {
    c.simanTitle = siman.title;
    c.simanTitleHe = siman.titleHe;
    c.simanTopic = siman.topic;
    c.sourceUrl = `/sources/shabbat/siman-${siman.num}/niveau-1-base.html`;
  });
  console.log(`Siman ${siman.num} (${siman.title}) : ${chunks.length} chunks extraits`);
  allChunks.push(...chunks);
}

const output = {
  meta: {
    generated: new Date().toISOString(),
    simanim: SIMANIM_POC.map((s) => s.num),
    totalChunks: allChunks.length,
    note: 'POC corpus retrieval — extraction des niveau-1-base.html pour 3 simanim',
  },
  chunks: allChunks,
};

const outPath = path.join(ROOT, 'data', 'corpus-poc.json');
fs.writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf8');
console.log(`\n✓ ${allChunks.length} chunks écrits dans ${outPath}`);
console.log(`  Taille : ${(fs.statSync(outPath).size / 1024).toFixed(1)} KB`);
