// api/_daily-post-checks.js — Contrôles bloquants du post quotidien.
//
// Règle : mieux vaut ne rien envoyer qu'un Daat Yomi faux. Deux familles :
//   BLOQUANT : le pack n'est pas préparé ; un email d'anomalie part à la place.
//   AVERTISSEMENT : le pack part, l'anomalie est affichée en tête de l'email et
//                   de la page de validation.
//
// 1. auditCalendar : le jour du plan est confronté (a) au nombre RÉEL de séifim
//    du siman, lu en direct sur Sefaria ; (b) aux autres journées du même siman
//    dans le plan — séifim 1..N couverts une fois et une seule, ≤ 5 par jour ;
//    (c) à la page du calendrier réellement publiée sur daattorah.com ;
//    (d) à la cohérence interne du plan (total annoncé = journées réelles).
// 2. checkTexts : après rédaction, les textes reprennent-ils exactement le
//    jour, le total, le siman, les séifim et le lien ?

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { loadPlan } from './_daily-limoud.js';

const here = dirname(fileURLToPath(import.meta.url));
const SITE = 'https://daattorah.com';

function seifimCountFile() {
  try {
    const d = JSON.parse(readFileSync(join(here, '..', 'data', 'seifim-count.json'), 'utf-8'));
    return d['orach-chayim'] || {};
  } catch { return {}; }
}

// Siman entier sur Sefaria : le nombre de séifim ET leur texte.
export async function fetchSiman(num) {
  const r = await fetch(`https://www.sefaria.org/api/v3/texts/Shulchan_Arukh,_Orach_Chayim.${num}?version=hebrew`, {
    headers: { Accept: 'application/json' },
  });
  if (!r.ok) throw new Error(`Sefaria siman ${num} → HTTP ${r.status}`);
  const d = await r.json();
  const t = d?.versions?.[0]?.text;
  if (!Array.isArray(t) || !t.length) throw new Error(`Sefaria siman ${num} → texte vide`);
  return t.map((s) => String(Array.isArray(s) ? s.join(' ') : s || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim());
}

export async function auditCalendar(entry, sefariaSeifim) {
  const bloquant = [];
  const avertissement = [];
  const plan = loadPlan();
  const num = entry.siman.num;
  const [a, b] = entry.seifRange;
  const reel = sefariaSeifim.length;

  // (a) nombre réel de séifim
  const fichier = Number(seifimCountFile()[String(num)]) || null;
  if (fichier && fichier !== reel) {
    bloquant.push(`Siman ${num} : Sefaria donne ${reel} séifim, data/seifim-count.json en annonce ${fichier}.`);
  }
  if (a < 1 || b > reel || a > b) {
    bloquant.push(`Siman ${num} : le plan programme les séifim ${a}–${b}, mais le siman n'en compte que ${reel}.`);
  }
  if (b - a + 1 > 5) bloquant.push(`Jour ${entry.dayNumber} : ${b - a + 1} séifim programmés (maximum 5).`);
  for (let n = a; n <= b; n++) {
    if (!sefariaSeifim[n - 1]) bloquant.push(`Siman ${num}, séif ${n} : texte absent sur Sefaria.`);
  }

  // (b) toutes les journées du même siman
  const lots = (plan.entries || []).filter((e) => e.siman?.num === num)
    .sort((x, y) => x.seifRange[0] - y.seifRange[0]);
  const vus = new Map();
  for (const l of lots) {
    for (let n = l.seifRange[0]; n <= l.seifRange[1]; n++) vus.set(n, (vus.get(n) || 0) + 1);
    if (l.seifRange[1] - l.seifRange[0] + 1 > 5) bloquant.push(`Jour ${l.dayNumber} (siman ${num}) : plus de 5 séifim.`);
  }
  const manquants = []; const doubles = [];
  for (let n = 1; n <= reel; n++) {
    if (!vus.has(n)) manquants.push(n); else if (vus.get(n) > 1) doubles.push(n);
  }
  if (manquants.length) bloquant.push(`Siman ${num} : séifim jamais programmés → ${manquants.join(', ')}.`);
  if (doubles.length) bloquant.push(`Siman ${num} : séifim programmés deux fois → ${doubles.join(', ')}.`);

  // Étiquette de partie vraie : rang du lot du jour parmi ceux du siman.
  const rang = lots.findIndex((l) => l.dayNumber === entry.dayNumber) + 1;
  const partie = { index: rang || entry.lotIndex, total: lots.length || entry.lotTotal };
  if (rang && (entry.lotIndex !== rang || entry.lotTotal !== lots.length)) {
    avertissement.push(`Le plan indique la partie ${entry.lotIndex}/${entry.lotTotal}, mais ce siman compte ${lots.length} journées et celle-ci est la ${rang}e : le post affiche ${rang}/${lots.length}.`);
  }
  const jours = lots.map((l) => l.dayNumber);
  if (jours.some((d, i) => i && d !== jours[i - 1] + 1)) {
    avertissement.push(`Le siman ${num} n'est pas étudié sur des journées consécutives (journées ${jours.join(', ')}) : rattrapage de séifim omis lors d'un premier passage.`);
  }

  // (d) cohérence interne du plan
  const total = plan.meta?.totalDays;
  const entrees = (plan.entries || []).length;
  if (total !== entrees) bloquant.push(`Le plan annonce ${total} journées mais en contient ${entrees}.`);

  // (c) page du calendrier réellement publiée
  try {
    const pad = String(entry.dayNumber).padStart(3, '0');
    const r = await fetch(`${SITE}/limoud/jour-${pad}.html`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const html = await r.text();
    // Deux formes de titre : « Jour 82 — Siman 299 (séif 6-10 / 10) » pour une partie,
    // « Jour 83 — Siman 300 · » quand la journée couvre le siman entier.
    const m = html.match(/Jour (\d+) — Siman (\d+) \(séif (\d+)-(\d+) \/ (\d+)\)/);
    const entier = !m && html.match(/Jour (\d+) — Siman (\d+) ·/);
    if (!m && !entier) {
      avertissement.push(`Page publiée du jour ${entry.dayNumber} : format non reconnu, confrontation impossible.`);
    } else {
      const [, j, s, pa, pb, pn] = m ? m.map(Number) : [0, Number(entier[1]), Number(entier[2]), 1, reel, reel];
      if (j !== entry.dayNumber || s !== num || pa !== a || pb !== b) {
        bloquant.push(`La page publiée /limoud/jour-${pad} annonce « Jour ${j}, siman ${s}, séifim ${pa}-${pb} » alors que le plan dit « Jour ${entry.dayNumber}, siman ${num}, séifim ${a}-${b} ».`);
      }
      if (pn !== reel) bloquant.push(`La page publiée annonce ${pn} séifim pour le siman ${num} ; Sefaria en compte ${reel}.`);
    }
  } catch (e) {
    bloquant.push(`Page du calendrier publiée injoignable (/limoud/jour-${String(entry.dayNumber).padStart(3, '0')}.html) : ${e.message}.`);
  }

  return { bloquant, avertissement, partie, seifimReels: reel, totalDays: total };
}

// Les textes reprennent-ils exactement les données verrouillées ?
export function checkTexts(info, post) {
  const out = [];
  const [a, b] = info.seifRange;
  const cartes = (post.seifim || []).map((s) => s.n);
  const attendues = []; for (let n = a; n <= b; n++) attendues.push(n);
  if (cartes.join(',') !== attendues.join(',')) {
    out.push({ ou: 'visuel', statut: 'faux', affirmation: `cartes des séifim ${cartes.join(', ')}`, explication: `le jour porte sur les séifim ${a} à ${b}.` });
  }
  const p = post.posts || {};
  const jour = `${info.dayNumber}/${info.totalDays}`;
  if (!(p.whatsapp || '').includes(jour)) out.push({ ou: 'whatsapp', statut: 'imprécis', affirmation: 'en-tête', explication: `« Jour ${jour} » absent de l'en-tête.` });
  for (const k of ['whatsapp', 'facebook', 'instagram', 'linkedin', 'x']) {
    const t = p[k] || '';
    if (!t.includes(String(info.siman.num))) out.push({ ou: k, statut: 'imprécis', affirmation: 'siman', explication: `le numéro du siman ${info.siman.num} n'apparaît pas.` });
    const autreJour = t.match(/[Jj][Oo][Uu][Rr] (\d+) ?\/ ?(\d+)/);
    if (autreJour && `${autreJour[1]}/${autreJour[2]}` !== jour) out.push({ ou: k, statut: 'faux', affirmation: autreJour[0], explication: `le jour est ${jour}.` });
  }
  for (const k of ['whatsapp', 'facebook', 'linkedin', 'x']) {
    if (!(p[k] || '').includes(`/oh/${info.siman.num}`)) out.push({ ou: k, statut: 'imprécis', affirmation: 'lien', explication: `le lien ${info.studyUrl} manque.` });
  }
  if ((p.x || '').length > 280) out.push({ ou: 'x', statut: 'imprécis', affirmation: `${p.x.length} caractères`, explication: 'X limite à 280.' });
  return out;
}
