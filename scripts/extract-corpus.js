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

// ── RÉPERTOIRES SOURCES NON DÉCLARÉS ────────────────────────────────────────
// Si le Rav ouvre un domaine dans un NOUVEAU répertoire (sources/pessah/…),
// SECTIONS ne le connaît pas : rien n'entre dans le corpus, et le build annonce
// « 359/359 simanim » en sortant au vert, comme si le répertoire n'existait pas.
// Il pourrait écrire un traité entier sans que rien ne le lui dise. On compare
// donc ce qui est SUR LE DISQUE à ce qui est DÉCLARÉ, et on crie.
function unknownSourceDirs(declared) {
  const base = path.join(ROOT, 'sources');
  if (!fs.existsSync(base)) return [];
  const known = new Set(declared.map((sec) => path.resolve(sec.dir)));
  const out = [];
  for (const d of fs.readdirSync(base, { withFileTypes: true })) {
    if (!d.isDirectory()) continue;
    const full = path.join(base, d.name);
    if (known.has(path.resolve(full))) continue;
    let simanim = 0;
    try {
      simanim = fs.readdirSync(full).filter((x) => /^siman-\d+$/.test(x)).length;
    } catch { /* ignore */ }
    if (simanim > 0) out.push({ dir: `sources/${d.name}`, simanim });
  }
  return out;
}

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
      caveat: SECTION_CAVEAT_RE.test(text) || undefined,
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

// Niveau 3 — Synthèse : sections délimitées par des <h2> nus.
// ⚠️ L'ancienne version EXIGEAIT un attribut id : les pages de synthèse du Yoreh
// De'ah utilisent des <h2> sans id, elles produisaient donc 0 chunk — 50 fichiers
// entièrement invisibles pour le chat, sans le moindre signal.
function extractSynthese(siman, body) {
  const chunks = [];
  const re = /<h2(?![^>]*class="section-title")[^>]*>([\s\S]*?)<\/h2>([\s\S]*?)(?=<h2(?![^>]*class="section-title")|<\/section|<\/main|<\/body|$)/g;
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

// Troisième structure de synthèse : des <div class="syn-section"> dont le titre
// est un <div class="syn-title">, sans aucun <h2>. Trouvée sur le siman 246, que
// l'avertissement « fichier présent mais 0 chunk » a permis de repérer.
function extractSynSection(siman, body) {
  const chunks = [];
  const re = /<div class="syn-section"[^>]*>([\s\S]*?)(?=<div class="syn-section"|<\/main|<\/body|$)/g;
  let m, idx = 0;
  while ((m = re.exec(body)) !== null) {
    idx++;
    const block = m[1];
    const titleM = block.match(/<div class="syn-title"[^>]*>([\s\S]*?)<\/div>/);
    const sectionTitle = titleM ? htmlToText(titleM[1]) : `Synthèse ${idx}`;
    const text = htmlToText(block).trim();
    if (text.length < 60) continue;
    const parts = text.length <= 900 ? [text] : text.match(/[\s\S]{1,900}(?:\.|$)/g) || [text];
    parts.forEach((pp) => {
      const t = pp.trim();
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

// Encadrés typés (definition / remember / key-point), appariés par COMPTAGE DE
// PROFONDEUR.
// ⚠️ L'ancienne expression régulière exigeait, APRÈS le </div> fermant, un
// élément d'une liste blanche (h2, p, table, autre encadré…). Trois situations
// très courantes cassaient cet appariement :
//   · l'encadré est le DERNIER de sa section (rien ne suit) ;
//   · le Rav insère une bannière de commentaire `<!-- ===== 3. … ===== -->`
//     entre deux sections, ce qui suffit à faire échouer le lookahead ;
//   · un <div> non listé suit l'encadré.
// Mesuré : 927 encadrés sur 4 332 (21 %) étaient perdus, et le texte de 725
// d'entre eux n'existait NULLE PART dans le corpus — or ce sont précisément les
// conclusions pratiques que le Rav écrit en fin de section (« Le pain reste
// jusqu'à la bénédiction », « Balayer d'abord, à cause du kazayit »).
// Le comptage de profondeur ferme exactement le bon </div>, y compris quand
// l'encadré en contient d'autres, et ne dépend plus de ce qui suit.
// Types d'encadrés reconnus. Les huit derniers sont la charpente du niveau
// LAMDAN — la hakira, la question, la réponse, le fondement, la mah'loket, la
// nafka mina, la carte de Rishon, la conclusion. Ils n'étaient dans aucune
// liste : des dizaines de milliers d'occurrences n'entraient dans le corpus que
// par accident, via le filet narratif, ou pas du tout.
// ⚠️ Les encadrés du niveau LAMDAN (hakira-box, rishon-card, pilpul-box,
// machloket-box, nafka-mina-box, yesod-box, teruts-box, kashya-box, pesak-box,
// rav-box) ne sont PAS dans cette liste, et c'''est une décision, pas un oubli.
// Les indexer fait passer le corpus de 21 451 à 29 288 chunks — du vrai pilpoul
// du Rav, aujourd'''hui invisible. Mais mesuré : le banc hold-out tombe de 51 %
// à 47 % et le top-3 de 63 % à 60 %, par concurrence entre simanim voisins.
// Or les deux bancs ne contiennent AUCUNE question de niveau lamdan : ils
// mesurent le coût de ce contenu et jamais son bénéfice. Trancher sur cette
// seule base serait du sur-ajustement. À reprendre avec un banc de questions
// de pilpoul — voir la note dans le rapport de session.
const BLOCK_TYPES = 'definition|remember|key-point';

function typedBlocks(content) {
  const out = [];
  const openRe = new RegExp(`<div class="(${BLOCK_TYPES})"[^>]*>`, 'g');
  let m;
  while ((m = openRe.exec(content)) !== null) {
    const type = m[1];
    const start = openRe.lastIndex;
    const tagRe = /<div\b[^>]*>|<\/div\s*>/g;
    tagRe.lastIndex = start;
    let depth = 1;
    let end = content.length;
    let t;
    while ((t = tagRe.exec(content)) !== null) {
      if (t[0][1] === '/') {
        depth -= 1;
        if (depth === 0) { end = t.index; break; }
      } else {
        depth += 1;
      }
    }
    out.push({ type, html: content.slice(start, end) });
    openRe.lastIndex = end;
  }
  return out;
}

function extractChunks(siman, html) {
  const chunks = [];
  const caveatSections = new Set();
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
  const body = bodyMatch ? bodyMatch[1] : html;

  // Tolérant aux attributs supplémentaires (ex. id="…" ajouté pour les ancres).
  // ⚠️ La classe peut être COMPOSÉE : « section-title section-title--he » (483
  // occurrences, 48 fichiers). L'ancienne expression exigeait le guillemet juste
  // après « section-title » : les 13 sections du niveau Lamdan du siman 253
  // étaient donc invisibles, et la page rendait 1 chunk de 118 caractères sur
  // 40 Ko — le pilpoul du Rav, perdu.
  const sectionRegex = /<h2[^>]*class="[^"]*\bsection-title\b[^"]*"[^>]*>([\s\S]*?)<\/h2>([\s\S]*?)(?=<h2[^>]*class="[^"]*\bsection-title\b[^"]*"|$)/g;
  let match;
  let sectionIndex = 0;
  while ((match = sectionRegex.exec(body)) !== null) {
    sectionIndex++;
    const sectionTitle = htmlToText(match[1]);
    const sectionContent = match[2];
    // La réserve de tête vaut pour TOUS les chunks de la section, pas seulement
    // pour le fragment dans lequel la phrase tombe.
    if (SECTION_CAVEAT_RE.test(htmlToText(sectionContent))) caveatSections.add(sectionIndex);

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
    let blockIdx = 0;
    for (const block of typedBlocks(sectionContent)) {
      const text = htmlToText(block.html);
      if (text.length < 40) continue;
      blockIdx++;
      chunks.push({
        id: `siman-${siman.num}-s${sectionIndex}-b${blockIdx}`,
        siman: siman.num,
        sectionNum: sectionIndex,
        sectionTitle, subsection: null,
        text, type: block.type,
      });
    }

    // Paragraphes narratifs (h3 + p)
    let h3Count = 0;
    const h3Re = /<h3[^>]*>([\s\S]*?)<\/h3>([\s\S]*?)(?=<h3|<h2|$)/g;
    let h3m;
    while ((h3m = h3Re.exec(sectionContent)) !== null) {
      const h3Title = htmlToText(h3m[1]);
      const subClean = h3m[2].replace(new RegExp(`<div class="(?:${BLOCK_TYPES})"[^>]*>[\\s\\S]*?<\\/div>`, 'g'), '');
      const text = htmlToText(subClean);
      if (text.length < 60) continue;
      h3Count++;
      chunks.push({
        id: `siman-${siman.num}-s${sectionIndex}-h3-${chunks.length}`,
        siman: siman.num,
        sectionNum: sectionIndex,
        sectionTitle, subsection: h3Title,
        text, type: 'narratif',
      });
    }

    // 🕳️ FILET. Une section sans <h3> ET sans bloc typé ne produisait AUCUN
    // chunk, silencieusement. Sur la synthèse du siman 243, six sections
    // disparaissaient ainsi — dont l'axiome central, l'arbre de décision et les
    // cinq voies de sortie du Séif Beit ; une vraie question était alors servie
    // par un extrait de TSITSIT sous « Source : Siman 20 ». Le défaut était
    // invisible : la page produisait 18 chunks, donc aucun avertissement.
    // Mesuré au build : 467 fichiers captaient moins de la moitié de leur texte.
    if (blockIdx === 0 && h3Count === 0 && !TOC_RE.test(sectionTitle.trim())) {
      const text = htmlToText(sectionContent).trim();
      if (text.length >= 60 && !TOC_RE.test(text)) {
        const parts = text.length <= 900 ? [text] : text.match(/[\s\S]{1,900}(?:\.|$)/g) || [text];
        parts.forEach((pp) => {
          const t = pp.trim();
          if (t.length < 60) return;
          chunks.push({
            id: `siman-${siman.num}-s${sectionIndex}-n${chunks.length + 1}`,
            siman: siman.num,
            sectionNum: sectionIndex,
            sectionTitle, subsection: null,
            text: t, type: 'narratif',
          });
        });
      }
    }
  }
  // Estampillage final : couvre aussi la branche « Cas pratiques modernes », qui
  // sort de la boucle par `continue`.
  if (caveatSections.size) {
    for (const c of chunks) if (caveatSections.has(c.sectionNum)) c.caveat = true;
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
// ⚠️ Un même niveau porte des NOMS DE FICHIER différents selon la section :
// Hilkhot Shabbat a `niveau-4-daat-harav.html` (route /oh/N/daat-harav) tandis que
// le Yoreh De'ah a `niveau-4-halakha.html` (route /yd/N/halakha). Le nom était codé
// en dur : les 50 niveaux 4 du Yoreh De'ah n'étaient JAMAIS ouverts, donc invisibles
// pour le chat. Chaque niveau déclare donc ses variantes de nom, avec le suffixe
// d'URL correspondant (vérifié contre les rewrites de vercel.json).
const LEVELS = [
  { id: 'base',       label: 'Base',       variants: [{ file: 'niveau-1-base.html',       urlSuffix: 'base' }] },
  { id: 'lamdan',     label: 'Lamdan',     variants: [{ file: 'niveau-2-lamdan.html',     urlSuffix: 'lamdan' }] },
  { id: 'synthese',   label: 'Synthèse',   variants: [{ file: 'niveau-3-synthese.html',   urlSuffix: 'synthese' }] },
  { id: 'daat-harav', label: 'Daat HaRav', variants: [
      { file: 'niveau-4-daat-harav.html', urlSuffix: 'daat-harav' },
      // ⚠️ id PROPRE : ces pages ne sont PAS le Choulhan Aroukh HaRav. Les
      // étiqueter 'daat-harav' contredisait le prompt système, qui interdit
      // d'attribuer une chitah de l'Admour HaZaken sur ces simanim.
      { file: 'niveau-4-halakha.html',    urlSuffix: 'halakha', id: 'halakha', label: 'Halakha' },
  ] },
];

// L'extracteur est choisi d'après la STRUCTURE RÉELLE du fichier, jamais d'après
// son nom de niveau : c'est le codage en dur qui a rendu 100 fichiers invisibles.
// Un futur niveau nommé autrement sera lu correctement sans modifier ce script.
// ── Retrait du « chrome » de page ──────────────────────────────────────────
// Filigrane, avertissement, navigation entre niveaux et pied de page sont tous en
// QUEUE de body : ils étaient donc happés par la DERNIÈRE section de chaque page.
// Mesuré : 550 chunks sur 16 171 contenaient « © 5786 · Retour à l'accueil ·
// ♥ Soutenir » — du bruit que BM25 indexait comme du contenu.
const CHROME_MARKERS = [
  /<nav[\s>]/i,
  /<footer[\s>]/i,
  /<div[^>]*class="yh-watermark"/i,
  /<div[^>]*class="disclaimer"/i,
];
function stripChrome(body) {
  // Sélecteur de langue et bandeau de dédicace : en TÊTE, retirés isolément.
  let b = body
    .replace(/<div[^>]*class="lang-switcher[^"]*"[\s\S]{0,2000}?<\/div>\s*/i, '')
    .replace(/<div[^>]*id="dedicace-banner"[\s\S]{0,2000}?<\/div>\s*/i, '');
  let cut = b.length;
  for (const re of CHROME_MARKERS) {
    const m = b.match(re);
    if (m && m.index < cut) cut = m.index;
  }
  // Garde-fou : ne jamais tronquer avant la moitié de la page. Un marqueur trouvé
  // trop tôt signale une structure inattendue — mieux vaut garder du bruit que
  // perdre de la halakha.
  return cut >= b.length * 0.5 ? b.slice(0, cut) : b;
}

// Pages-passerelles : « l'Admour HaZaken n'a pas rédigé ce siman ». Aucun texte
// du Rav à indexer — leur prose et leur liste « Sources pour approfondir » ne
// doivent pas sortir sous le label Daat HaRav avec un sourceUrl /N/daat-harav.
// ⚠️ UNIQUEMENT le marqueur de TITRE. Une première version acceptait aussi la
// phrase « l'Admour HaZaken n'a pas rédigé… » trouvée n'importe où dans la page :
// elle happait TOUT le niveau 4 de la cacheroute (Yoreh De'ah 87-118, 30 Ko de
// halakha chacun), qui ne fait que mentionner ce fait au passage. Le contrôle
// aurait supprimé du corpus le contenu que ce même commit vient d'y faire entrer.
const BRIDGE_RE = /<h1[^>]*>[^<]*passerelle[^<]*<\/h1>/i;

// Réserves écrites par le Rav dans le titre d'un tableau ou d'une sous-section.
const CAVEAT_RE = /hors\s+corpus|[àa]\s+v[ée]rifier|non\s+v[ée]rifi[ée]|sous\s+r[ée]serve/i;

// Réserve écrite par le Rav en TÊTE DE SECTION, hors de tout titre : « Note de
// méthode. … Elles ne figurent pas dans le corpus du siman ; … à confirmer
// auprès d'un Rav avant toute application. » Elle vaut pour TOUTE la section.
// Le filet découpe la section en fragments de 900 caractères : la note ne tombe
// que dans le PREMIER, le contenu opératoire part dans les suivants. Mesuré :
// 137 chunks de ces sections sortaient sans réserve — dont 101 créés par ce
// même filet — et remontaient en TÊTE sur le chemin gratuit, servis sous
// « D'après le corpus du Rav », l'exact contraire de ce que la page en dit.
const SECTION_CAVEAT_RE = /Note de m[ée]thode|ne figurent pas dans le corpus|[àa] confirmer aupr[èe]s d(?:'|\u2019)un Rav|[àa] confirmer aupr[èe]s du Rav/i;

// Tables des matières : le filet les captait comme du contenu (extractSynthese
// les filtrait déjà). 394 chunks de pure navigation, sans valeur d'étude.
const TOC_RE = /^(?:\ud83d\udcd1\s*)?(?:Table des mati[èe]res|Sommaire|Plan de l|\u05ea\u05d5\u05db\u05df \u05d4\u05e2\u05e0\u05d9\u05d9\u05e0\u05d9\u05dd|Contents|Navigation)/i;

// L'extracteur est choisi d'après la STRUCTURE du fichier — jamais d'après son
// nom de niveau (c'est ce codage en dur qui avait rendu 100 fichiers invisibles).
// ⚠️ NE PAS remplacer ce choix par un « meilleur de N » fondé sur la couverture :
// mesuré, l'extracteur le plus grossier gagne alors partout et détruit le typage
// dont dépend le classement (cas-pratique 473 → 6, synthese 4 776 → 15 201).
// Le trou réel — des sections captées à vide — se comble DANS extractChunks.
function pickExtractor(body) {
  if (/<details class="seif-details"|<div class="sa-block"/.test(body)) return 'daat-harav';
  if (/<h2 class="section-title"/.test(body)) return 'sections';
  if (/<div class="syn-section"/.test(body)) return 'syn-section';
  return 'synthese';
}

function bestExtraction(num, body) {
  const plain = htmlToText(body).length || 1;
  const kind = pickExtractor(body);
  const fn = kind === 'daat-harav'  ? extractDaatHaRav
           : kind === 'syn-section' ? extractSynSection
           : kind === 'synthese'    ? extractSynthese
           : extractChunks;
  let chunks = [];
  try { chunks = fn({ num }, body) || []; } catch { chunks = []; }
  const coverage = chunks.reduce((a, c) => a + (c.text ? c.text.length : 0), 0) / plain;
  return { kind, chunks, coverage };
}

// Fichiers de niveau PRÉSENTS mais dont l'extraction ne produit aucun chunk :
// c'est le symptôme d'une structure HTML non reconnue. Le défaut est resté
// silencieux pendant tout le chantier Yoreh De'ah — on le signale désormais.
const EMPTY_LEVELS = [];
// Fichiers dont l'extraction ne capte qu'une fraction du texte : gabarit non
// reconnu. C'est ce silence-là qui a fait perdre 66 % de la synthèse du siman 243.
const LOW_COVERAGE = [];
// Pages-passerelles écartées (aucun texte du Rav à indexer).
const BRIDGE_SKIPPED = [];

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
      const variant = level.variants.find((v) => fs.existsSync(path.join(section.dir, dir, v.file)));
      if (!variant) {
        // Absence normale pour certains niveaux (ex. simanim 304 et 322 n'ont pas
        // de niveau 4 : l'Admour HaZaken ne les a pas écrits — page passerelle).
        if (level.id === 'base') stats.skipped.push({ section: section.id, num: simanNum, reason: 'pas de niveau-1-base.html' });
        continue;
      }
      const htmlPath = path.join(section.dir, dir, variant.file);

      const html = fs.readFileSync(htmlPath, 'utf8');
      const bodyM = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
      const body = stripChrome(bodyM ? bodyM[1] : html);
      // Page-passerelle : rien à indexer (test limité au niveau 4 — les niveaux
      // 1-3 des MÊMES simanim citent la phrase sans être des passerelles).
      if (level.id === 'daat-harav' && BRIDGE_RE.test(body)) {
        BRIDGE_SKIPPED.push(`${section.id}:${simanNum}`);
        continue;
      }
      const { kind, chunks, coverage } = bestExtraction(simanNum, body);
      if (!chunks.length) {
        EMPTY_LEVELS.push(`${section.id}:${simanNum}/${level.id} (${variant.file})`);
        continue;
      }
      // Couverture faible = gabarit mal reconnu. Visible au build, jamais muet.
      if (coverage < 0.5 && htmlToText(body).length > 3000) {
        LOW_COVERAGE.push(`${section.id}:${simanNum}/${level.id} — ${Math.round(coverage * 100)} % capté (${variant.file}, « ${kind} »)`);
      }

      chunks.forEach((c) => {
        c.section = section.id;
        c.level = variant.id || level.id;
        c.levelLabel = variant.label || level.label;
        c.simanTitle = meta.titleFr;
        c.simanTitleHe = meta.titleHe;
        c.simanSubtitle = meta.subtitle || '';
        c.sourceUrl = `${section.urlPrefix}/${simanNum}/${variant.urlSuffix}`;
        // ID GLOBALEMENT UNIQUE. Le numéro de siman seul est ambigu : /oh-quotidien
        // et /yd partagent 35 numéros (87-118, 183-185), et deux niveaux d'un même
        // siman peuvent forger la même suite « s2-b3 ». getChunkById() fait un
        // .find() : le premier chunk portant l'id gagne, et l'outil daat_get_content
        // sert alors le texte d'une AUTRE page sous la référence que la recherche
        // vient de rendre — une source fausse, le mécanisme du faux heter borer.
        c.id = `${section.id === 'yoreh-deah' ? 'yd' : 'oh'}-${c.level}-${c.id}`;
        // ⚠️ RÉSERVE DE L'AUTEUR. Le Rav marque lui-même certains tableaux
        // « hors corpus, à vérifier ». Ces passages restent indexés — ils sont
        // utiles — mais le drapeau voyage AVEC la donnée, pour qu'aucun chemin
        // d'affichage ne puisse les servir en taisant la mise en garde.
        if (CAVEAT_RE.test(`${c.subsection || ''} ${c.sectionTitle || ''}`)) c.caveat = true;
      });

      stats.perLevel[variant.id || level.id] = (stats.perLevel[variant.id || level.id] || 0) + chunks.length;
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
const UNKNOWN_DIRS = unknownSourceDirs(SECTIONS);
if (UNKNOWN_DIRS.length) {
  console.error(`\n⛔ ${UNKNOWN_DIRS.length} répertoire(s) source NON DÉCLARÉ(S) — leur contenu n'entre PAS dans le corpus :`);
  UNKNOWN_DIRS.forEach((u) => console.error(`    ${u.dir}/ — ${u.simanim} siman(im) ignorés`));
  console.error('    → déclarer le répertoire dans SECTIONS (scripts/extract-corpus.js) ET dans');
  console.error('      scripts/generate-simanim-index.js, ajouter les rewrites dans vercel.json,');
  console.error("      et vérifier que api/chat.js accepte l'identifiant de section correspondant.");
  console.error('    Sans cela le chat ne verra jamais ce contenu, et rien ne le signalera.\n');
}
if (BRIDGE_SKIPPED.length) {
  console.log(`  Passerelles écartées : ${BRIDGE_SKIPPED.length} (${BRIDGE_SKIPPED.slice(0, 8).join(', ')}${BRIDGE_SKIPPED.length > 8 ? '…' : ''})`);
}
if (LOW_COVERAGE.length) {
  console.warn(`\n⚠️  ${LOW_COVERAGE.length} fichier(s) dont l'extraction capte MOINS DE LA MOITIÉ du texte :`);
  LOW_COVERAGE.slice(0, 15).forEach((e) => console.warn(`    ${e}`));
  if (LOW_COVERAGE.length > 15) console.warn(`    … et ${LOW_COVERAGE.length - 15} autre(s)`);
}
if (EMPTY_LEVELS.length) {
  console.warn(`\n⚠️  ${EMPTY_LEVELS.length} fichier(s) de niveau présents mais SANS chunk extrait (structure HTML non reconnue) :`);
  EMPTY_LEVELS.slice(0, 15).forEach((e) => console.warn(`    ${e}`));
  if (EMPTY_LEVELS.length > 15) console.warn(`    … et ${EMPTY_LEVELS.length - 15} autre(s)`);
}
if (MISSING_TITLES.length) {
  console.warn(`\n⚠️  ${MISSING_TITLES.length} siman(im) indexés SANS titre (recherche dégradée) : ${MISSING_TITLES.slice(0, 20).join(', ')}${MISSING_TITLES.length > 20 ? '…' : ''}`);
  console.warn('    → ajouter le siman au catalogue data/simanim-disponibles.json, ou sa clé de section à SECTIONS[].dispoIds.');
}

// Distribution chunks/siman
const counts = Object.values(stats.chunksPerSiman);
counts.sort((a, b) => a - b);
console.log(`  Chunks/siman p50    : ${counts[Math.floor(counts.length / 2)]}`);
console.log(`  Chunks/siman max    : ${counts[counts.length - 1]} (siman ${Object.keys(stats.chunksPerSiman).find((k) => stats.chunksPerSiman[k] === counts[counts.length - 1])})`);
