#!/usr/bin/env node
/**
 * Génère le plan Daat Yomi (5 jours/semaine — dim-jeu, saut ven+sam).
 *
 * Règle hybride (5 séifim / jour) :
 *   - Si un siman ≤5 séifim → tout le siman tient sur 1 jour
 *   - Si un siman >5 séifim → on le découpe en lots de 5 séifim consécutifs
 *     (1-5, 6-10, 11-N), chaque lot = 1 jour.
 *
 * Entrées :
 *   - /data/simanim-disponibles.json          (FR)
 *   - /data/simanim-disponibles-en.json       (EN)
 *   - /data/simanim-disponibles-he.json       (HE)
 *
 * Sorties :
 *   - /data/limoud-plan.json
 *   - /limoud/jour-NNN.html / -en.html / -he.html
 *   - /limoud/index.html / index-en.html / index-he.html
 *   - bandeau injecté dans /index.html / -en / -he (markers <!-- BANDEAU DAAT YOMI -->)
 *
 * Règle des jours d'étude :
 *   - Étude : dim (0), lun (1), mar (2), mer (3), jeu (4)
 *   - Pause : ven (5), sam (6)
 *   - Date de départ : 2026-06-08 (lundi) = Jour 1
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'limoud');
const DATA_DIR = path.join(ROOT, 'data');

const START_DATE_ISO = '2026-06-08'; // lundi
const SITE_URL = 'https://daattorah.com';
const SEIFIM_PER_DAY = 5;

// ─── Nombre de séifim par siman (extrait des niveau-1-base.html) ─────────
// Compté via le pattern utilisé par scripts/audit-seifim-coverage.py
// (Seif latin/translit/héb, Séif, סעיף). Régénéré le 2026-06-08.
const SEIFIM_COUNT = {
  242: 1,  243: 2,  244: 6,  245: 2,  246: 5,  247: 6,  248: 4,  249: 4,
  250: 2,  251: 2,  252: 6,  253: 4,  254: 8,  255: 3,  256: 1,  257: 7,
  258: 4,  259: 6,  260: 2,  261: 4,  262: 3,  263: 9,  264: 8,  265: 4,
  266: 10, 267: 3,  268: 10, 269: 1,  270: 2,  271: 10, 272: 10, 273: 7,
  274: 4,  275: 10, 276: 5,  277: 5,  278: 1,  279: 7,  280: 2,  281: 1,
  282: 7,  283: 1,  284: 7,  285: 7,  286: 5,  287: 1,  288: 10, 289: 2,
  290: 2,  291: 6,  292: 2,  293: 3,  294: 5,  295: 1,  296: 8,  297: 5,
  298: 10, 299: 10, 300: 1,  301: 14, 302: 10, 303: 11, 304: 3,  305: 11,
  306: 10, 307: 11, 308: 14, 309: 5,  310: 9,  311: 9,  312: 10, 313: 10,
  314: 10, 315: 10, 316: 10, 317: 7,  318: 10, 319: 10, 320: 11, 321: 10,
  322: 6,  323: 10, 324: 10, 325: 10, 326: 10, 327: 4,  328: 13, 329: 9,
  330: 10, 331: 10, 332: 4,  333: 3,  334: 11, 335: 5,  336: 10, 337: 4,
  338: 8,  339: 7,  340: 10, 341: 3,  342: 1,  343: 1,  344: 2,  345: 10,
  346: 3,  347: 1,  348: 1,  349: 5,  350: 3,  351: 1,  352: 2,  353: 3,
  354: 2,  355: 5,  356: 2,  357: 3,  358: 10, 359: 1,  360: 3,  361: 2,
  362: 10, 363: 12, 364: 5,  365: 8
};

// ─── Helpers date ──────────────────────────────────────────────────────────
function isStudyDay(date) {
  const dow = date.getUTCDay(); // 0=dim ... 6=sam
  return dow >= 0 && dow <= 4;
}

function addDays(date, n) {
  const d = new Date(date.getTime());
  d.setUTCDate(d.getUTCDate() + n);
  return d;
}

function parseISODate(s) {
  const [y, m, d] = s.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}

function toISODate(d) {
  return d.toISOString().slice(0, 10);
}

function getCurrentStudyDay(today, startDate) {
  if (today < startDate) return 0;
  let dayNum = 0;
  const cur = new Date(startDate.getTime());
  while (cur < today) {
    if (isStudyDay(cur)) dayNum++;
    cur.setUTCDate(cur.getUTCDate() + 1);
  }
  if (isStudyDay(today)) dayNum++;
  return dayNum;
}

// ─── Localisation ──────────────────────────────────────────────────────────
const DAYS_FR = ['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'];
const DAYS_EN = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
const DAYS_HE = ['ראשון','שני','שלישי','רביעי','חמישי','שישי','שבת'];

const MONTHS_FR = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
const MONTHS_EN = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const MONTHS_HE = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];

function fmtDate(d, lang) {
  const day = d.getUTCDate();
  const month = d.getUTCMonth();
  const year = d.getUTCFullYear();
  const dow = d.getUTCDay();
  if (lang === 'en') return `${DAYS_EN[dow]}, ${MONTHS_EN[month]} ${day}, ${year}`;
  if (lang === 'he') return `יום ${DAYS_HE[dow]}, ${day} ב${MONTHS_HE[month]} ${year}`;
  return `${DAYS_FR[dow]} ${day} ${MONTHS_FR[month]} ${year}`;
}

// ─── Chargement données ───────────────────────────────────────────────────
function loadJSON(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

const simanimFR = loadJSON(path.join(DATA_DIR, 'simanim-disponibles.json'));
const simanimEN = loadJSON(path.join(DATA_DIR, 'simanim-disponibles-en.json'));
const simanimHE = loadJSON(path.join(DATA_DIR, 'simanim-disponibles-he.json'));

const titleByNum = (idx) => {
  const m = {};
  for (const s of idx.simanim) m[s.num] = s;
  return m;
};
const enByNum = titleByNum(simanimEN);
const heByNum = titleByNum(simanimHE);

// ─── Construction des "lots" (avant assignation des dates) ────────────────
// Chaque "lot" = un jour d'étude. Pour un siman de N séifim :
//   - N ≤ 5  → 1 lot couvrant tout le siman
//   - N > 5  → ceil(N/5) lots de 5 séifim consécutifs
const lots = [];
for (const s of simanimFR.simanim) {
  const num = s.num;
  const nbSeifim = SEIFIM_COUNT[num] || 1;
  if (nbSeifim <= SEIFIM_PER_DAY) {
    lots.push({
      siman: s,
      nbSeifim,
      seifRange: [1, nbSeifim],
      lotIndex: 1,
      lotTotal: 1
    });
  } else {
    const lotTotal = Math.ceil(nbSeifim / SEIFIM_PER_DAY);
    let start = 1;
    let lotIndex = 1;
    while (start <= nbSeifim) {
      const end = Math.min(start + SEIFIM_PER_DAY - 1, nbSeifim);
      lots.push({
        siman: s,
        nbSeifim,
        seifRange: [start, end],
        lotIndex,
        lotTotal
      });
      start = end + 1;
      lotIndex++;
    }
  }
}

const totalDays = lots.length;

// ─── Calcul des dates des jours d'étude ────────────────────────────────────
const startDate = parseISODate(START_DATE_ISO);
const dayDates = [];
{
  let cur = new Date(startDate.getTime());
  while (dayDates.length < totalDays) {
    if (isStudyDay(cur)) dayDates.push(new Date(cur.getTime()));
    cur.setUTCDate(cur.getUTCDate() + 1);
  }
}

// ─── Construction du plan ─────────────────────────────────────────────────
const entries = lots.map((lot, i) => {
  const date = dayDates[i];
  const num = lot.siman.num;
  const enS = enByNum[num] || {};
  const heS = heByNum[num] || {};
  const [seifStart, seifEnd] = lot.seifRange;
  return {
    dayNumber: i + 1,
    date: toISODate(date),
    dow: date.getUTCDay(),
    siman: {
      num,
      numHe: lot.siman.numHe,
      title: lot.siman.title,
      titleEn: enS.title || lot.siman.title,
      titleHe: heS.title || lot.siman.title,
      path: lot.siman.path
    },
    seifRange: [seifStart, seifEnd],
    seifCount: seifEnd - seifStart + 1,
    lotIndex: lot.lotIndex,
    lotTotal: lot.lotTotal,
    levels: lot.siman.levels,
    status: lot.siman.status
  };
});

// ─── Groupement par "semaine" (5 jours dim→jeu) ───────────────────────────
function getSundayOfWeek(d) {
  const dow = d.getUTCDay();
  return addDays(d, -dow);
}

const weeks = [];
{
  let curWeekKey = null;
  let curGroup = null;
  for (const e of entries) {
    const dt = parseISODate(e.date);
    const sunday = getSundayOfWeek(dt);
    const key = toISODate(sunday);
    if (key !== curWeekKey) {
      curWeekKey = key;
      curGroup = { weekStart: key, days: [] };
      weeks.push(curGroup);
    }
    curGroup.days.push(e);
  }
}

// ─── Sortie data/limoud-plan.json ──────────────────────────────────────────
const planJSON = {
  meta: {
    version: '2.0',
    description: 'Plan Daat Yomi — 5 séifim/jour max (lots de 5), 5 jours par semaine (dim-jeu).',
    startDate: START_DATE_ISO,
    endDate: entries[entries.length - 1].date,
    totalDays: entries.length,
    totalSeifim: Object.values(SEIFIM_COUNT).reduce((a, b) => a + b, 0),
    seifimPerDay: SEIFIM_PER_DAY,
    studyDaysPerWeek: 5,
    studyDows: [0, 1, 2, 3, 4],
    skipDows: [5, 6],
    skipReason: 'Vendredi = préparation Shabbat. Samedi = Shabbat.'
  },
  entries,
  weeks
};

fs.mkdirSync(DATA_DIR, { recursive: true });
fs.writeFileSync(path.join(DATA_DIR, 'limoud-plan.json'),
  JSON.stringify(planJSON, null, 2) + '\n', 'utf8');
console.log(`✓ data/limoud-plan.json (${entries.length} jours, fin = ${planJSON.meta.endDate})`);

// ─── Génération pages jour-NNN.html ────────────────────────────────────────
fs.mkdirSync(OUT_DIR, { recursive: true });

const COMMON_HEAD = `  <meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Frank+Ruhl+Libre:wght@400;500;700&family=Inter:wght@400;500;600&display=swap">
  <link rel="stylesheet" href="/assets/css/daat.css">
  <link rel="stylesheet" href="/assets/css/daat-enhance.css">`;

const PAGE_CSS = `
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Cormorant Garamond',Georgia,serif;background:var(--cream);color:var(--text-dark);line-height:1.7;font-size:18px}
    header{background:var(--navy);height:70px;display:flex;align-items:center;justify-content:space-between;padding:0 40px;position:sticky;top:0;z-index:100;border-bottom:2px solid var(--gold)}
    .logo{display:flex;align-items:center;gap:12px;text-decoration:none}
    .logo-hebrew{font-family:'Frank Ruhl Libre',serif;font-size:28px;font-weight:700;color:var(--gold);letter-spacing:2px}
    .logo-latin{font-family:'Cormorant Garamond',serif;font-size:13px;color:rgba(255,255,255,.85);letter-spacing:4px;text-transform:uppercase}
    nav{display:flex;gap:24px;align-items:center}
    nav a{color:rgba(255,255,255,.9);text-decoration:none;font-family:'Inter',sans-serif;font-size:13px;letter-spacing:1px;text-transform:uppercase}
    nav a:hover,nav a.active{color:var(--gold)}
    .lang-switcher{display:inline-flex;gap:6px;margin-left:16px}
    .lang-switcher a{padding:4px 8px;border:1px solid rgba(197,165,90,.4);border-radius:3px;font-size:11px}
    .lang-switcher a.active{background:var(--gold);color:var(--navy)}
    main{max-width:860px;margin:0 auto;padding:60px 24px 80px}
    .day-tag{font-family:'Inter',sans-serif;font-size:12px;letter-spacing:3px;text-transform:uppercase;color:var(--gold);margin-bottom:12px}
    h1.day-title{font-family:'Cormorant Garamond',serif;font-size:42px;font-weight:600;color:var(--navy);margin-bottom:8px;line-height:1.18}
    h1.day-title .seif-info{font-size:24px;color:var(--gold);font-style:italic;display:block;margin-top:6px;font-weight:500}
    .day-date{font-style:italic;color:var(--text-mid);margin-bottom:32px;font-size:18px}
    .siman-card{background:#fff;border:1px solid rgba(197,165,90,.25);border-left:4px solid var(--gold);border-radius:6px;padding:28px 32px;margin-bottom:28px;box-shadow:0 2px 8px rgba(11,28,58,.04)}
    .siman-num{font-family:'Frank Ruhl Libre',serif;font-size:14px;color:var(--gold);letter-spacing:2px;margin-bottom:6px}
    .siman-title{font-family:'Cormorant Garamond',serif;font-size:26px;color:var(--navy);font-weight:500;margin-bottom:18px}
    .seif-focus{margin:14px 0 4px;padding:12px 16px;background:rgba(197,165,90,.10);border-left:3px solid var(--gold);border-radius:4px;font-family:'Cormorant Garamond',serif;font-size:17px;color:var(--text-dark);font-style:italic}
    .seif-focus strong{color:var(--navy);font-style:normal;font-weight:600}
    [dir="rtl"] .seif-focus{border-left:none;border-right:3px solid var(--gold)}
    .levels-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-top:16px}
    .level-link{display:block;padding:14px 16px;background:var(--cream);border:1px solid rgba(197,165,90,.3);border-radius:4px;text-decoration:none;color:var(--text-dark);font-family:'Inter',sans-serif;font-size:13px;letter-spacing:1px;text-transform:uppercase;text-align:center;transition:.18s}
    .level-link:hover{background:var(--gold);color:var(--navy);border-color:var(--gold)}
    .level-link .ln{display:block;font-weight:600;color:var(--navy);font-size:11px;margin-bottom:4px;letter-spacing:2px}
    .nav-days{display:flex;justify-content:space-between;align-items:center;margin-top:48px;padding-top:24px;border-top:1px solid rgba(197,165,90,.2);font-family:'Inter',sans-serif;font-size:13px}
    .nav-days a{color:var(--navy);text-decoration:none;padding:10px 18px;border:1px solid var(--navy);border-radius:3px;letter-spacing:1px;text-transform:uppercase}
    .nav-days a:hover{background:var(--navy);color:var(--gold)}
    .nav-days .placeholder{visibility:hidden}
    .breadcrumb{font-family:'Inter',sans-serif;font-size:12px;color:var(--text-mid);margin-bottom:24px;letter-spacing:1px}
    .breadcrumb a{color:var(--navy);text-decoration:none}
    .breadcrumb a:hover{color:var(--gold)}
    [dir="rtl"] .siman-card{border-left:none;border-right:4px solid var(--gold)}
    [dir="rtl"] .nav-days{flex-direction:row-reverse}
    @media (max-width:640px){
      h1.day-title{font-size:30px}
      h1.day-title .seif-info{font-size:18px}
      main{padding:40px 18px 60px}
      .siman-card{padding:22px 18px}
      header{padding:0 16px;height:60px}
      .logo-latin{display:none}
      nav{gap:14px}
    }
  </style>`;

const HEADER_FR = `<header>
  <a class="logo" href="/index.html"><span class="logo-hebrew">דעת</span><span class="logo-latin">Daat Torah</span></a>
  <nav>
    <a href="/index.html">Accueil</a>
    <a href="/limoud/index.html" class="active">Daat Yomi</a>
    <a href="/chat.html">IA Daat</a>
    <a href="/about.html">À propos</a>
    <span class="lang-switcher">
      <a href="LANG_FR_LINK" class="active">FR</a>
      <a href="LANG_HE_LINK">HE</a>
      <a href="LANG_EN_LINK">EN</a>
    </span>
  </nav>
</header>`;

const HEADER_EN = `<header>
  <a class="logo" href="/index-en.html"><span class="logo-hebrew">דעת</span><span class="logo-latin">Daat Torah</span></a>
  <nav>
    <a href="/index-en.html">Home</a>
    <a href="/limoud/index-en.html" class="active">Daat Yomi</a>
    <a href="/chat-en.html">Daat AI</a>
    <a href="/about-en.html">About</a>
    <span class="lang-switcher">
      <a href="LANG_FR_LINK">FR</a>
      <a href="LANG_HE_LINK">HE</a>
      <a href="LANG_EN_LINK" class="active">EN</a>
    </span>
  </nav>
</header>`;

const HEADER_HE = `<header>
  <a class="logo" href="/index-he.html"><span class="logo-hebrew">דעת</span><span class="logo-latin">Daat Torah</span></a>
  <nav>
    <a href="/index-he.html">בית</a>
    <a href="/limoud/index-he.html" class="active">דעת יומי</a>
    <a href="/chat-he.html">דעת AI</a>
    <a href="/about-he.html">אודות</a>
    <span class="lang-switcher">
      <a href="LANG_FR_LINK">FR</a>
      <a href="LANG_HE_LINK" class="active">HE</a>
      <a href="LANG_EN_LINK">EN</a>
    </span>
  </nav>
</header>`;

const LEVEL_LABELS = {
  fr: { tag:'Niveau', n1:'Base', n2:'Lamdan', n3:'Synthèse', n4:'Daat HaRav' },
  en: { tag:'Level',  n1:'Base', n2:'Lamdan', n3:'Synthesis', n4:'Daat HaRav' },
  he: { tag:'רמה',    n1:'בסיס', n2:'למדן',   n3:'סיכום',     n4:'דעת הרב' }
};

const LEVEL_SUFFIX = { fr:'', en:'-en', he:'-he' };
const LEVEL_FILES = {
  n1:'niveau-1-base',
  n2:'niveau-2-lamdan',
  n3:'niveau-3-synthese',
  n4:'niveau-4-daat-harav'
};

function siteRelative(p) {
  if (!p) return '/';
  return '/' + p.replace(/index\.html$/, '');
}

function buildLevelLinks(entry, lang) {
  const dir = siteRelative(entry.siman.path);
  const labels = LEVEL_LABELS[lang];
  const suffix = LEVEL_SUFFIX[lang];
  const out = [];
  for (const lvl of ['n1','n2','n3','n4']) {
    if (!entry.levels || !entry.levels[lvl]) continue;
    const href = `${dir}${LEVEL_FILES[lvl]}${suffix}.html`;
    out.push(`<a class="level-link" href="${href}"><span class="ln">${labels.tag} ${lvl.slice(1)}</span>${labels[lvl]}</a>`);
  }
  return out.join('\n            ');
}

function dayFileName(dayNum, lang) {
  const n = String(dayNum).padStart(3, '0');
  if (lang === 'fr') return `jour-${n}.html`;
  if (lang === 'en') return `jour-${n}-en.html`;
  return `jour-${n}-he.html`;
}

// ─── Helpers de titre / sous-titre tenant compte des lots ──────────────────
function buildTitleParts(entry, lang) {
  const [a, b] = entry.seifRange;
  const isSplit = entry.lotTotal > 1;
  const lotSuffix = isSplit ? ` (${entry.lotIndex}/${entry.lotTotal})` : '';
  const rangeText = a === b ? String(a) : `${a}-${b}`;
  const seifPart = (label, total) => `(${label} ${rangeText} / ${total})`;
  const total = SEIFIM_COUNT[entry.siman.num] || entry.seifCount;
  if (lang === 'fr') {
    const base = `Jour ${entry.dayNumber} — Siman ${entry.siman.num}`;
    if (!isSplit) return { titleShort: base, titleHtml: base };
    return {
      titleShort: `${base} ${seifPart('séif', total)}${lotSuffix}`,
      titleHtml: `${base}<span class="seif-info">${seifPart('séif', total)}${lotSuffix}</span>`
    };
  }
  if (lang === 'en') {
    const base = `Day ${entry.dayNumber} — Siman ${entry.siman.num}`;
    if (!isSplit) return { titleShort: base, titleHtml: base };
    return {
      titleShort: `${base} ${seifPart('seif', total)}${lotSuffix}`,
      titleHtml: `${base}<span class="seif-info">${seifPart('seif', total)}${lotSuffix}</span>`
    };
  }
  // he
  const base = `יום ${entry.dayNumber} — סימן ${entry.siman.num}`;
  if (!isSplit) return { titleShort: base, titleHtml: base };
  return {
    titleShort: `${base} ${seifPart('סעיף', total)}${lotSuffix}`,
    titleHtml: `${base}<span class="seif-info">${seifPart('סעיף', total)}${lotSuffix}</span>`
  };
}

function buildFocusLine(entry, lang) {
  const [a, b] = entry.seifRange;
  const single = a === b;
  if (entry.lotTotal === 1 && entry.seifCount === SEIFIM_COUNT[entry.siman.num]) {
    // Le siman entier tient sur 1 jour : pas besoin du bandeau "concentre-toi"
    return '';
  }
  if (lang === 'fr') {
    const range = single ? `<strong>${a}</strong>` : `<strong>${a} à ${b}</strong>`;
    return `<p class="seif-focus">Concentre-toi sur ${single ? 'le séif' : 'les séifim'} ${range} aujourd'hui ${entry.lotTotal > 1 ? `(lot ${entry.lotIndex} sur ${entry.lotTotal})` : ''}.</p>`;
  }
  if (lang === 'en') {
    const range = single ? `<strong>${a}</strong>` : `<strong>${a} to ${b}</strong>`;
    return `<p class="seif-focus">Focus on ${single ? 'seif' : 'seifim'} ${range} today ${entry.lotTotal > 1 ? `(part ${entry.lotIndex} of ${entry.lotTotal})` : ''}.</p>`;
  }
  // he
  const range = single ? `<strong>${a}</strong>` : `<strong>${a}-${b}</strong>`;
  return `<p class="seif-focus">התמקד היום ב${single ? 'סעיף' : 'סעיפים'} ${range} ${entry.lotTotal > 1 ? `(חלק ${entry.lotIndex} מתוך ${entry.lotTotal})` : ''}.</p>`;
}

function renderDayPage(entry, lang) {
  const n = String(entry.dayNumber).padStart(3, '0');
  const dt = parseISODate(entry.date);
  const dateStr = fmtDate(dt, lang);
  const isHE = lang === 'he';
  const htmlLang = lang === 'fr' ? 'fr' : (lang === 'en' ? 'en' : 'he');
  const dir = isHE ? 'rtl' : 'ltr';

  let header;
  const fileFR = dayFileName(entry.dayNumber, 'fr');
  const fileEN = dayFileName(entry.dayNumber, 'en');
  const fileHE = dayFileName(entry.dayNumber, 'he');
  if (lang === 'fr') header = HEADER_FR
    .replace('LANG_FR_LINK', fileFR).replace('LANG_HE_LINK', fileHE).replace('LANG_EN_LINK', fileEN);
  else if (lang === 'en') header = HEADER_EN
    .replace('LANG_FR_LINK', fileFR).replace('LANG_HE_LINK', fileHE).replace('LANG_EN_LINK', fileEN);
  else header = HEADER_HE
    .replace('LANG_FR_LINK', fileFR).replace('LANG_HE_LINK', fileHE).replace('LANG_EN_LINK', fileEN);

  const titleParts = buildTitleParts(entry, lang);
  const isSplit = entry.lotTotal > 1;
  const [a, b] = entry.seifRange;
  const total = SEIFIM_COUNT[entry.siman.num] || entry.seifCount;

  const localTitle = (lang === 'en' ? entry.siman.titleEn : (lang === 'he' ? entry.siman.titleHe : entry.siman.title));

  const descByLang = {
    fr: isSplit
      ? `Étude du jour : Siman ${entry.siman.num} séif ${a}-${b} (lot ${entry.lotIndex}/${entry.lotTotal}). ${localTitle}. Plan Daat Yomi (5 séifim/jour max, dim-jeu).`
      : `Étude du jour : Siman ${entry.siman.num} — ${localTitle}. Plan Daat Yomi (5 séifim/jour max, dim-jeu).`,
    en: isSplit
      ? `Today's learning: Siman ${entry.siman.num} seif ${a}-${b} (part ${entry.lotIndex}/${entry.lotTotal}). ${localTitle}. Daat Yomi plan (max 5 seifim/day, Sun-Thu).`
      : `Today's learning: Siman ${entry.siman.num} — ${localTitle}. Daat Yomi plan (max 5 seifim/day, Sun-Thu).`,
    he: isSplit
      ? `לימוד היום: סימן ${entry.siman.num} סעיף ${a}-${b} (חלק ${entry.lotIndex}/${entry.lotTotal}). ${localTitle}. תוכנית דעת יומי (עד 5 סעיפים ליום, ראשון-חמישי).`
      : `לימוד היום: סימן ${entry.siman.num} — ${localTitle}. תוכנית דעת יומי (עד 5 סעיפים ליום, ראשון-חמישי).`
  };

  const t = {
    fr: {
      tag:'Daat Yomi · Jour ' + entry.dayNumber,
      bcHome:'Accueil', bcLimoud:'Daat Yomi', bcDay:`Jour ${entry.dayNumber}`,
      prev:'← Jour précédent', next:'Jour suivant →', index:'Voir le plan complet',
      sub:'Daat Yomi (dim-jeu) — 5 séifim/jour max',
      siman:'Siman',
      pageTitle:`${titleParts.titleShort} · Daat Yomi | Daat Torah`,
      pageDesc:descByLang.fr
    },
    en: {
      tag:'Daat Yomi · Day ' + entry.dayNumber,
      bcHome:'Home', bcLimoud:'Daat Yomi', bcDay:`Day ${entry.dayNumber}`,
      prev:'← Previous day', next:'Next day →', index:'See the full plan',
      sub:'Daat Yomi (Sun-Thu) — max 5 seifim/day',
      siman:'Siman',
      pageTitle:`${titleParts.titleShort} · Daat Yomi | Daat Torah`,
      pageDesc:descByLang.en
    },
    he: {
      tag:'דעת יומי · יום ' + entry.dayNumber,
      bcHome:'בית', bcLimoud:'דעת יומי', bcDay:`יום ${entry.dayNumber}`,
      prev:'יום קודם →', next:'← יום הבא', index:'לתוכנית המלאה',
      sub:'דעת יומי (ראשון-חמישי) — עד 5 סעיפים ליום',
      siman:'סימן',
      pageTitle:`${titleParts.titleShort} · דעת יומי | Daat Torah`,
      pageDesc:descByLang.he
    }
  }[lang];

  const numHe = entry.siman.numHe;

  const prevNum = entry.dayNumber - 1;
  const nextNum = entry.dayNumber + 1;
  const prevHref = prevNum >= 1 ? dayFileName(prevNum, lang) : null;
  const nextHref = nextNum <= totalDays ? dayFileName(nextNum, lang) : null;
  const idxHref = lang === 'fr' ? 'index.html' : (lang === 'en' ? 'index-en.html' : 'index-he.html');

  const levelLinks = buildLevelLinks(entry, lang);
  const focusLine = buildFocusLine(entry, lang);

  const canonical = `${SITE_URL}/limoud/${dayFileName(entry.dayNumber, lang)}`;

  return `<!DOCTYPE html>
<html lang="${htmlLang}" dir="${dir}">
<head>
${COMMON_HEAD}
  <title>${t.pageTitle}</title>
  <meta name="description" content="${t.pageDesc}">
  <link rel="canonical" href="${canonical}">
  <link rel="alternate" hreflang="fr" href="${SITE_URL}/limoud/${dayFileName(entry.dayNumber, 'fr')}">
  <link rel="alternate" hreflang="en" href="${SITE_URL}/limoud/${dayFileName(entry.dayNumber, 'en')}">
  <link rel="alternate" hreflang="he" href="${SITE_URL}/limoud/${dayFileName(entry.dayNumber, 'he')}">
  <link rel="alternate" hreflang="x-default" href="${SITE_URL}/limoud/${dayFileName(entry.dayNumber, 'fr')}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="${titleParts.titleShort}">
  <meta property="og:description" content="${t.pageDesc}">
  <meta property="og:url" content="${canonical}">
  <meta property="og:image" content="${SITE_URL}/assets/img/og/og-default.svg">
${PAGE_CSS}
</head>
<body>
${header}
<main id="main">
  <div class="breadcrumb">
    <a href="/${lang === 'fr' ? 'index.html' : (lang === 'en' ? 'index-en.html' : 'index-he.html')}">${t.bcHome}</a> · <a href="${idxHref}">${t.bcLimoud}</a> · ${t.bcDay}
  </div>
  <div class="day-tag">${t.tag}</div>
  <h1 class="day-title">${titleParts.titleHtml}</h1>
  <div class="day-date">${dateStr} · <span style="opacity:.8">${t.sub}</span></div>

  <div class="siman-card">
    <div class="siman-num">${t.siman} ${entry.siman.num} · ${numHe}</div>
    <div class="siman-title">${localTitle}</div>
    <div class="levels-list">
            ${levelLinks}
    </div>
    ${focusLine}
  </div>

  <nav class="nav-days" aria-label="${lang === 'he' ? 'ניווט בין ימים' : (lang === 'en' ? 'Day navigation' : 'Navigation entre jours')}">
    ${prevHref ? `<a href="${prevHref}">${t.prev}</a>` : `<span class="placeholder">·</span>`}
    <a href="${idxHref}">${t.index}</a>
    ${nextHref ? `<a href="${nextHref}">${t.next}</a>` : `<span class="placeholder">·</span>`}
  </nav>
</main>
</body>
</html>`;
}

let count = 0;
for (const entry of entries) {
  for (const lang of ['fr','en','he']) {
    const html = renderDayPage(entry, lang);
    const file = path.join(OUT_DIR, dayFileName(entry.dayNumber, lang));
    fs.writeFileSync(file, html, 'utf8');
    count++;
  }
}
console.log(`✓ ${count} pages jour-NNN générées dans /limoud/`);

// ─── Index calendrier groupé par semaine ───────────────────────────────────
function renderIndex(lang) {
  const isHE = lang === 'he';
  const htmlLang = lang === 'fr' ? 'fr' : (lang === 'en' ? 'en' : 'he');
  const dir = isHE ? 'rtl' : 'ltr';

  const fileFR = 'index.html';
  const fileEN = 'index-en.html';
  const fileHE = 'index-he.html';
  let header;
  if (lang === 'fr') header = HEADER_FR
    .replace('LANG_FR_LINK', fileFR).replace('LANG_HE_LINK', fileHE).replace('LANG_EN_LINK', fileEN);
  else if (lang === 'en') header = HEADER_EN
    .replace('LANG_FR_LINK', fileFR).replace('LANG_HE_LINK', fileHE).replace('LANG_EN_LINK', fileEN);
  else header = HEADER_HE
    .replace('LANG_FR_LINK', fileFR).replace('LANG_HE_LINK', fileHE).replace('LANG_EN_LINK', fileEN);

  const t = {
    fr: {
      title:'Daat Yomi — Plan d\'étude quotidien',
      sub:`Lots de 5 séifim maximum par jour, 5 jours par semaine (dimanche → jeudi). Pause le vendredi (préparation Shabbat) et le Shabbat.`,
      week:'Semaine',
      day:'Jour',
      siman:'Siman',
      seif:'séif',
      from:'Du',
      to:'au',
      start:`Début : ${fmtDate(parseISODate(entries[0].date), 'fr')}`,
      end:`Fin : ${fmtDate(parseISODate(entries[entries.length-1].date), 'fr')}`,
      total:`${entries.length} jours d'étude · 5 j/semaine`,
      pageTitle:'Daat Yomi — Plan d\'étude quotidien | Daat Torah',
      pageDesc:`Plan d'étude quotidien du Choulhan Aroukh : ${entries.length} jours, 5 séifim/jour maximum, 5 jours par semaine (dimanche-jeudi).`
    },
    en: {
      title:'Daat Yomi — Daily study plan',
      sub:`Up to 5 seifim per day, 5 days a week (Sunday → Thursday). Friday (Shabbat preparation) and Shabbat are off.`,
      week:'Week',
      day:'Day',
      siman:'Siman',
      seif:'seif',
      from:'From',
      to:'to',
      start:`Start: ${fmtDate(parseISODate(entries[0].date), 'en')}`,
      end:`End: ${fmtDate(parseISODate(entries[entries.length-1].date), 'en')}`,
      total:`${entries.length} study days · 5 days/week`,
      pageTitle:'Daat Yomi — Daily study plan | Daat Torah',
      pageDesc:`Daily learning plan of the Shulchan Aruch: ${entries.length} days, up to 5 seifim/day, 5 days a week (Sunday-Thursday).`
    },
    he: {
      title:'דעת יומי — תוכנית לימוד יומית',
      sub:`עד 5 סעיפים ליום, 5 ימים בשבוע (ראשון → חמישי). שישי (הכנה לשבת) ושבת — אין לימוד.`,
      week:'שבוע',
      day:'יום',
      siman:'סימן',
      seif:'סעיף',
      from:'מ-',
      to:'עד',
      start:`התחלה: ${fmtDate(parseISODate(entries[0].date), 'he')}`,
      end:`סיום: ${fmtDate(parseISODate(entries[entries.length-1].date), 'he')}`,
      total:`${entries.length} ימי לימוד · 5 ימים בשבוע`,
      pageTitle:'דעת יומי — תוכנית לימוד יומית | Daat Torah',
      pageDesc:`תוכנית לימוד יומית בשולחן ערוך: ${entries.length} ימים, עד 5 סעיפים ליום, 5 ימים בשבוע (ראשון-חמישי).`
    }
  }[lang];

  const indexFile = lang === 'fr' ? 'index.html' : (lang === 'en' ? 'index-en.html' : 'index-he.html');
  const canonical = `${SITE_URL}/limoud/${indexFile}`;

  // Génération HTML des semaines
  const weeksHTML = weeks.map((w, idx) => {
    const wkNum = idx + 1;
    const first = w.days[0];
    const last = w.days[w.days.length - 1];
    const firstDate = parseISODate(first.date);
    const lastDate = parseISODate(last.date);
    const rangeStr = `${fmtDate(firstDate, lang)} ${t.to} ${fmtDate(lastDate, lang)}`;
    const days = w.days.map(e => {
      const dt = parseISODate(e.date);
      const dowName = lang === 'en' ? DAYS_EN[dt.getUTCDay()] : (lang === 'he' ? DAYS_HE[dt.getUTCDay()] : DAYS_FR[dt.getUTCDay()]);
      const title = (lang === 'en' ? e.siman.titleEn : (lang === 'he' ? e.siman.titleHe : e.siman.title));
      const numHe = e.siman.numHe;
      const [a, b] = e.seifRange;
      const isSplit = e.lotTotal > 1;
      const rangeText = a === b ? String(a) : `${a}-${b}`;
      // Cellule "Siman X · séif A-B (K/N)" si split, sinon "Siman X"
      const simanLine = isSplit
        ? `<strong>${t.siman} ${e.siman.num}</strong> · ${t.seif} ${rangeText} (${e.lotIndex}/${e.lotTotal})`
        : `<strong>${t.siman} ${e.siman.num}</strong> · ${numHe}`;
      return `      <a class="day-item${isSplit ? ' is-split' : ''}" href="${dayFileName(e.dayNumber, lang)}">
        <span class="day-meta"><span class="day-dow">${dowName}</span> · <span class="day-num">${t.day} ${e.dayNumber}</span> · <span class="day-date">${dt.getUTCDate()}/${(dt.getUTCMonth()+1)}</span></span>
        <span class="day-siman">${simanLine}</span>
        <span class="day-title">${title}</span>
      </a>`;
    }).join('\n');
    return `    <section class="week">
      <header class="week-head"><div class="week-num">${t.week} ${wkNum}</div><div class="week-range">${rangeStr}</div></header>
      <div class="week-days">
${days}
      </div>
    </section>`;
  }).join('\n');

  const INDEX_CSS = `
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Cormorant Garamond',Georgia,serif;background:var(--cream);color:var(--text-dark);line-height:1.65;font-size:18px}
    header{background:var(--navy);height:70px;display:flex;align-items:center;justify-content:space-between;padding:0 40px;position:sticky;top:0;z-index:100;border-bottom:2px solid var(--gold)}
    .logo{display:flex;align-items:center;gap:12px;text-decoration:none}
    .logo-hebrew{font-family:'Frank Ruhl Libre',serif;font-size:28px;font-weight:700;color:var(--gold);letter-spacing:2px}
    .logo-latin{font-family:'Cormorant Garamond',serif;font-size:13px;color:rgba(255,255,255,.85);letter-spacing:4px;text-transform:uppercase}
    nav{display:flex;gap:24px;align-items:center}
    nav a{color:rgba(255,255,255,.9);text-decoration:none;font-family:'Inter',sans-serif;font-size:13px;letter-spacing:1px;text-transform:uppercase}
    nav a:hover,nav a.active{color:var(--gold)}
    .lang-switcher{display:inline-flex;gap:6px;margin-left:16px}
    .lang-switcher a{padding:4px 8px;border:1px solid rgba(197,165,90,.4);border-radius:3px;font-size:11px}
    .lang-switcher a.active{background:var(--gold);color:var(--navy)}
    main{max-width:1080px;margin:0 auto;padding:60px 24px 80px}
    .page-tag{font-family:'Inter',sans-serif;font-size:12px;letter-spacing:3px;text-transform:uppercase;color:var(--gold);margin-bottom:10px}
    h1.page-title{font-family:'Cormorant Garamond',serif;font-size:48px;font-weight:600;color:var(--navy);margin-bottom:14px;line-height:1.15}
    .page-sub{color:var(--text-mid);font-size:18px;font-style:italic;margin-bottom:18px;max-width:760px}
    .meta-strip{display:flex;flex-wrap:wrap;gap:18px;font-family:'Inter',sans-serif;font-size:12px;color:var(--text-mid);letter-spacing:1px;text-transform:uppercase;padding:14px 0;border-top:1px solid rgba(197,165,90,.25);border-bottom:1px solid rgba(197,165,90,.25);margin-bottom:36px}
    .meta-strip span{display:inline-flex;align-items:center;gap:6px}
    .week{margin-bottom:36px;background:#fff;border:1px solid rgba(197,165,90,.2);border-radius:6px;overflow:hidden;box-shadow:0 1px 4px rgba(11,28,58,.04)}
    .week-head{background:var(--navy);color:#fff;padding:16px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid var(--gold)}
    .week-num{font-family:'Inter',sans-serif;font-size:13px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--gold)}
    .week-range{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:16px;color:rgba(255,255,255,.85)}
    .week-days{display:grid;grid-template-columns:repeat(5,1fr)}
    .day-item{display:flex;flex-direction:column;gap:6px;padding:18px 16px;text-decoration:none;color:var(--text-dark);border-right:1px solid rgba(197,165,90,.18);transition:.18s;background:#fff}
    .day-item:last-child{border-right:none}
    .day-item:hover{background:var(--cream)}
    .day-item.is-split{background:linear-gradient(135deg,#fff 70%,rgba(197,165,90,.07))}
    .day-item.is-split:hover{background:linear-gradient(135deg,var(--cream) 70%,rgba(197,165,90,.12))}
    .day-meta{font-family:'Inter',sans-serif;font-size:11px;letter-spacing:1px;color:var(--text-mid);text-transform:uppercase}
    .day-meta .day-dow{color:var(--gold);font-weight:600}
    .day-siman{font-family:'Frank Ruhl Libre',serif;font-size:15px;color:var(--navy)}
    .day-title{font-size:15px;line-height:1.4;color:var(--text-dark)}
    [dir="rtl"] .day-item{border-right:none;border-left:1px solid rgba(197,165,90,.18)}
    [dir="rtl"] .day-item:last-child{border-left:none}
    @media (max-width:900px){
      .week-days{grid-template-columns:repeat(2,1fr)}
      .day-item{border-right:none;border-bottom:1px solid rgba(197,165,90,.18)}
    }
    @media (max-width:500px){
      .week-days{grid-template-columns:1fr}
      h1.page-title{font-size:34px}
      main{padding:40px 18px}
    }
  </style>`;

  return `<!DOCTYPE html>
<html lang="${htmlLang}" dir="${dir}">
<head>
${COMMON_HEAD}
  <title>${t.pageTitle}</title>
  <meta name="description" content="${t.pageDesc}">
  <link rel="canonical" href="${canonical}">
  <link rel="alternate" hreflang="fr" href="${SITE_URL}/limoud/index.html">
  <link rel="alternate" hreflang="en" href="${SITE_URL}/limoud/index-en.html">
  <link rel="alternate" hreflang="he" href="${SITE_URL}/limoud/index-he.html">
  <link rel="alternate" hreflang="x-default" href="${SITE_URL}/limoud/index.html">
  <meta property="og:type" content="website">
  <meta property="og:title" content="${t.title}">
  <meta property="og:description" content="${t.pageDesc}">
  <meta property="og:url" content="${canonical}">
${INDEX_CSS}
</head>
<body>
${header}
<main id="main">
  <div class="page-tag">Daat Yomi</div>
  <h1 class="page-title">${t.title}</h1>
  <p class="page-sub">${t.sub}</p>
  <div class="meta-strip">
    <span>${t.start}</span>
    <span>${t.end}</span>
    <span>${t.total}</span>
  </div>

${weeksHTML}
</main>
</body>
</html>`;
}

for (const lang of ['fr','en','he']) {
  const html = renderIndex(lang);
  const file = lang === 'fr' ? 'index.html' : (lang === 'en' ? 'index-en.html' : 'index-he.html');
  fs.writeFileSync(path.join(OUT_DIR, file), html, 'utf8');
}
console.log(`✓ Index calendrier généré (3 langues) dans /limoud/`);

// ─── Bandeau homepage (snippet inséré dans index.html / -en / -he) ────────
function bannerSnippet(lang) {
  const t = {
    fr: {
      tag: 'Daat Yomi — étude quotidienne',
      todayLabel: 'Aujourd\'hui',
      jourLabel: 'Jour',
      simanLabel: 'Siman',
      seifLabel: 'séif',
      cta: 'Étudier maintenant →',
      indexCta: 'Voir le plan complet',
      shabbat: 'Shabbat shalom — reprise dimanche',
      friday: 'Reprise dimanche',
      beforeStart: `Le Daat Yomi commence le ${fmtDate(parseISODate(START_DATE_ISO), 'fr')}`,
      finished: 'Plan terminé — mazal tov ! 🎉',
      sub: '5 séifim/jour max · dim → jeu'
    },
    en: {
      tag: 'Daat Yomi — daily study',
      todayLabel: 'Today',
      jourLabel: 'Day',
      simanLabel: 'Siman',
      seifLabel: 'seif',
      cta: 'Study now →',
      indexCta: 'See the full plan',
      shabbat: 'Shabbat shalom — resumes Sunday',
      friday: 'Resumes Sunday',
      beforeStart: `Daat Yomi starts on ${fmtDate(parseISODate(START_DATE_ISO), 'en')}`,
      finished: 'Plan completed — mazal tov! 🎉',
      sub: 'Max 5 seifim/day · Sun → Thu'
    },
    he: {
      tag: 'דעת יומי — לימוד יומי',
      todayLabel: 'היום',
      jourLabel: 'יום',
      simanLabel: 'סימן',
      seifLabel: 'סעיף',
      cta: 'ללמוד עכשיו ←',
      indexCta: 'לתוכנית המלאה',
      shabbat: 'שבת שלום — נחזור ביום ראשון',
      friday: 'נחזור ביום ראשון',
      beforeStart: `דעת יומי מתחיל ב-${fmtDate(parseISODate(START_DATE_ISO), 'he')}`,
      finished: 'התוכנית הושלמה — מזל טוב! 🎉',
      sub: 'עד 5 סעיפים ליום · ראשון → חמישי'
    }
  }[lang];

  const indexFile = lang === 'fr' ? 'index.html' : (lang === 'en' ? 'index-en.html' : 'index-he.html');

  // Compact entries:
  // [dayNum, 'YYYY-MM-DD', sNum, 'numHe', 'title', seifStart, seifEnd, lotIndex, lotTotal]
  const compact = entries.map(e => [
    e.dayNumber,
    e.date,
    e.siman.num,
    e.siman.numHe,
    (lang === 'en' ? e.siman.titleEn : (lang === 'he' ? e.siman.titleHe : e.siman.title)),
    e.seifRange[0],
    e.seifRange[1],
    e.lotIndex,
    e.lotTotal
  ]);

  return `
<!-- ── BANDEAU DAAT YOMI ──────────────────────────────────────────── -->
<section class="daat-yomi-banner" id="daat-yomi-banner" data-start="${START_DATE_ISO}" data-total="${totalDays}" aria-label="${t.tag}">
  <div class="dy-inner">
    <div class="dy-tag">${t.tag} · <span class="dy-sub">${t.sub}</span></div>
    <div class="dy-content" id="dy-content"></div>
    <div class="dy-cta">
      <a id="dy-cta-link" class="dy-btn dy-btn-primary" href="/limoud/${indexFile}">${t.cta}</a>
      <a class="dy-btn dy-btn-secondary" href="/limoud/${indexFile}">${t.indexCta}</a>
    </div>
  </div>
</section>
<style>
  .daat-yomi-banner{background:linear-gradient(135deg,var(--navy) 0%,#0e2447 100%);color:#fff;padding:48px 40px;border-top:2px solid var(--gold);border-bottom:2px solid var(--gold)}
  .daat-yomi-banner .dy-inner{max-width:1080px;margin:0 auto;text-align:center}
  .daat-yomi-banner .dy-tag{font-family:'Inter',sans-serif;font-size:12px;letter-spacing:3px;text-transform:uppercase;color:var(--gold);margin-bottom:14px}
  .daat-yomi-banner .dy-tag .dy-sub{color:rgba(255,255,255,.7);letter-spacing:2px}
  .daat-yomi-banner .dy-today{font-family:'Inter',sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,.6);margin-bottom:8px}
  .daat-yomi-banner .dy-day{font-family:'Cormorant Garamond',serif;font-size:42px;font-weight:600;color:#fff;margin-bottom:6px;line-height:1.1}
  .daat-yomi-banner .dy-day .dy-day-num{color:var(--gold)}
  .daat-yomi-banner .dy-siman{font-family:'Frank Ruhl Libre',serif;font-size:18px;color:var(--gold);margin-bottom:6px;letter-spacing:1px}
  .daat-yomi-banner .dy-seif{font-family:'Inter',sans-serif;font-size:13px;color:rgba(255,255,255,.78);letter-spacing:1px;text-transform:uppercase;margin-bottom:8px}
  .daat-yomi-banner .dy-title{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:22px;color:rgba(255,255,255,.92);margin-bottom:8px;max-width:720px;margin-left:auto;margin-right:auto}
  .daat-yomi-banner .dy-notice{font-family:'Cormorant Garamond',serif;font-style:italic;color:var(--gold);font-size:15px;margin-top:4px}
  .daat-yomi-banner .dy-cta{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:22px}
  .daat-yomi-banner .dy-btn{padding:14px 26px;text-decoration:none;font-family:'Inter',sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;border-radius:3px;transition:.2s;border:1px solid var(--gold)}
  .daat-yomi-banner .dy-btn-primary{background:var(--gold);color:var(--navy);font-weight:600}
  .daat-yomi-banner .dy-btn-primary:hover{background:#d9b66e}
  .daat-yomi-banner .dy-btn-secondary{color:#fff;background:transparent}
  .daat-yomi-banner .dy-btn-secondary:hover{background:rgba(197,165,90,.15)}
  @media (max-width:640px){
    .daat-yomi-banner{padding:36px 20px}
    .daat-yomi-banner .dy-day{font-size:32px}
    .daat-yomi-banner .dy-title{font-size:18px}
  }
</style>
<script>
(function(){
  var ENTRIES = ${JSON.stringify(compact)};
  var T = ${JSON.stringify(t)};
  var DAYS_FR = ${JSON.stringify(DAYS_FR)};
  var DAYS_EN = ${JSON.stringify(DAYS_EN)};
  var DAYS_HE = ${JSON.stringify(DAYS_HE)};
  var LANG = ${JSON.stringify(lang)};

  function parseISO(s){var p=s.split('-');return new Date(Date.UTC(+p[0],+p[1]-1,+p[2]));}
  function isStudyDay(d){var w=d.getUTCDay();return w>=0&&w<=4;}
  function todayUTC(){var n=new Date();return new Date(Date.UTC(n.getFullYear(),n.getMonth(),n.getDate()));}
  function fmtDate(d){
    var dow=d.getUTCDay(), day=d.getUTCDate(), m=d.getUTCMonth()+1;
    if(LANG==='en')return DAYS_EN[dow]+', '+m+'/'+day;
    if(LANG==='he')return 'יום '+DAYS_HE[dow]+', '+day+'/'+m;
    return DAYS_FR[dow]+' '+day+'/'+m;
  }
  function pad3(n){return ('00'+n).slice(-3);}
  function dayHref(num){
    var p=pad3(num);
    if(LANG==='fr')return '/limoud/jour-'+p+'.html';
    if(LANG==='en')return '/limoud/jour-'+p+'-en.html';
    return '/limoud/jour-'+p+'-he.html';
  }
  function getCurrentStudyDay(today, startDate){
    if(today < startDate) return 0;
    var dayNum=0;
    var cur=new Date(startDate.getTime());
    while(cur < today){ if(isStudyDay(cur)) dayNum++; cur.setUTCDate(cur.getUTCDate()+1); }
    if(isStudyDay(today)) dayNum++;
    return dayNum;
  }

  var banner=document.getElementById('daat-yomi-banner');
  if(!banner) return;
  var start=parseISO(banner.dataset.start);
  var total=parseInt(banner.dataset.total,10);
  var today=todayUTC();
  var container=document.getElementById('dy-content');
  var ctaLink=document.getElementById('dy-cta-link');

  if(today < start){
    container.innerHTML='<div class="dy-notice">'+T.beforeStart+'</div>';
    return;
  }

  var dow=today.getUTCDay();
  var dayNum;
  var notice='';

  if(dow===5){
    var sun=new Date(today.getTime()); sun.setUTCDate(sun.getUTCDate()+2);
    dayNum=getCurrentStudyDay(sun, start);
    notice=T.friday;
  } else if(dow===6){
    var sun=new Date(today.getTime()); sun.setUTCDate(sun.getUTCDate()+1);
    dayNum=getCurrentStudyDay(sun, start);
    notice=T.shabbat;
  } else {
    dayNum=getCurrentStudyDay(today, start);
  }

  if(dayNum > total){
    container.innerHTML='<div class="dy-day">'+T.finished+'</div>';
    return;
  }
  if(dayNum < 1){
    container.innerHTML='<div class="dy-notice">'+T.beforeStart+'</div>';
    return;
  }

  var e=ENTRIES[dayNum-1];
  // e = [dayNum, date, simanNum, numHe, title, seifStart, seifEnd, lotIndex, lotTotal]
  var seifStart=e[5], seifEnd=e[6], lotIdx=e[7], lotTot=e[8];
  var isSplit = lotTot > 1;

  var html='';
  if(notice){
    html+='<div class="dy-today">'+T.todayLabel+' · '+fmtDate(today)+'</div>';
    html+='<div class="dy-notice">'+notice+'</div>';
  } else {
    html+='<div class="dy-today">'+T.todayLabel+' · '+fmtDate(today)+'</div>';
  }
  html+='<div class="dy-day">'+T.jourLabel+' <span class="dy-day-num">'+e[0]+'</span> <span style="opacity:.55">/ '+total+'</span></div>';
  if(isSplit){
    var rangeStr = (seifStart===seifEnd) ? String(seifStart) : (seifStart+'-'+seifEnd);
    html+='<div class="dy-siman">'+T.simanLabel+' '+e[2]+' · '+e[3]+'</div>';
    html+='<div class="dy-seif">'+T.seifLabel+' '+rangeStr+' · ('+lotIdx+'/'+lotTot+')</div>';
  } else {
    html+='<div class="dy-siman">'+T.simanLabel+' '+e[2]+' · '+e[3]+'</div>';
  }
  html+='<div class="dy-title">'+e[4]+'</div>';
  container.innerHTML=html;
  ctaLink.href=dayHref(e[0]);
})();
</script>
<!-- ── /BANDEAU DAAT YOMI ───────────────────────────────────────── -->
`;
}

const SNIPPET_DIR = path.join(ROOT, 'data', '.banner-snippets');
fs.mkdirSync(SNIPPET_DIR, { recursive: true });
const snippetFR = bannerSnippet('fr');
const snippetEN = bannerSnippet('en');
const snippetHE = bannerSnippet('he');
fs.writeFileSync(path.join(SNIPPET_DIR, 'banner-fr.html'), snippetFR, 'utf8');
fs.writeFileSync(path.join(SNIPPET_DIR, 'banner-en.html'), snippetEN, 'utf8');
fs.writeFileSync(path.join(SNIPPET_DIR, 'banner-he.html'), snippetHE, 'utf8');

const MARK_BEGIN = '<!-- ── BANDEAU DAAT YOMI ──────────────────────────────────────────── -->';
const MARK_END = '<!-- ── /BANDEAU DAAT YOMI ───────────────────────────────────────── -->';

function injectBanner(filePath, snippet) {
  if (!fs.existsSync(filePath)) {
    console.warn('  ! page introuvable: ' + filePath);
    return;
  }
  let html = fs.readFileSync(filePath, 'utf8');

  const startIdx = html.indexOf(MARK_BEGIN);
  if (startIdx !== -1) {
    const endIdx = html.indexOf(MARK_END);
    if (endIdx !== -1) {
      const after = endIdx + MARK_END.length;
      html = html.slice(0, startIdx) + snippet.trim() + html.slice(after);
      fs.writeFileSync(filePath, html, 'utf8');
      console.log('  ↻ bandeau mis à jour dans ' + path.basename(filePath));
      return;
    }
  }

  const anchor = '<section class="social-proof">';
  const anchorPos = html.indexOf(anchor);
  if (anchorPos !== -1) {
    const closeRel = html.indexOf('</section>', anchorPos);
    if (closeRel !== -1) {
      const insertAt = closeRel + '</section>'.length;
      html = html.slice(0, insertAt) + '\n\n  ' + snippet.trim() + '\n' + html.slice(insertAt);
      fs.writeFileSync(filePath, html, 'utf8');
      console.log('  + bandeau inséré dans ' + path.basename(filePath));
      return;
    }
  }
  console.warn('  ! anchor introuvable dans ' + path.basename(filePath));
}

injectBanner(path.join(ROOT, 'index.html'), snippetFR);
injectBanner(path.join(ROOT, 'index-en.html'), snippetEN);
injectBanner(path.join(ROOT, 'index-he.html'), snippetHE);

// ─── Résumé final ──────────────────────────────────────────────────────────
console.log('\n──────── RÉSUMÉ ────────');
console.log('Date début : ' + planJSON.meta.startDate);
console.log('Date fin   : ' + planJSON.meta.endDate);
console.log('Total jours étude : ' + planJSON.meta.totalDays);
console.log('Total séifim      : ' + planJSON.meta.totalSeifim);
console.log('Total semaines    : ' + weeks.length);
console.log('\nÉchantillons :');
const samples = [1, 2, 5, 10, 47, 100, totalDays];
for (const n of samples) {
  if (n <= entries.length) {
    const e = entries[n-1];
    const dt = parseISODate(e.date);
    const seifInfo = e.lotTotal > 1
      ? ` · séif ${e.seifRange[0]}-${e.seifRange[1]} (${e.lotIndex}/${e.lotTotal})`
      : '';
    console.log(`  Jour ${String(n).padStart(3,' ')} → ${e.date} (${DAYS_FR[dt.getUTCDay()]}) · Siman ${e.siman.num}${seifInfo}`);
  }
}
