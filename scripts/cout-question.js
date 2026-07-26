#!/usr/bin/env node
// Calculateur de coût par question du chat Daat — et marge par plan.
//
// POURQUOI CE SCRIPT
// Les plafonds mensuels de chaque plan (MONTHLY_LIMITS dans api/chat.js) ont été
// calibrés à la main sur une estimation de « ~0,55 €/question Opus ». Cette
// estimation reposait sur un tarif Opus erroné ET ignorait les tokens de cache
// (corrigé en 07/2026). Plutôt que de figer un nouveau chiffre dans un
// commentaire — qui redeviendra faux au prochain changement de tarif — ce script
// recalcule tout à partir des constantes RÉELLES du code.
//
// USAGE
//   node scripts/cout-question.js               # tarifs et plafonds actuels
//   node scripts/cout-question.js --eur 1.08    # taux de change €→$ (défaut 1.08)
//
// À RELANCER : après tout changement de tarif Anthropic, de modèle, de plafond
// (MONTHLY_LIMITS), ou de taille du prompt système.
//
// ⚠️ Les coûts sont en DOLLARS (les tarifs Anthropic le sont, et le champ KV
// s'appelle cost_usd). Les recettes des plans sont en EUROS. La comparaison
// passe donc par un taux de change explicite — c'est le seul endroit du projet
// où les deux unités se rencontrent.

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

// ── Lecture des constantes réelles depuis api/chat.js ──────────────────────
// On extrait les littéraux plutôt que de les recopier : le script ne peut donc
// pas diverger du code qu'il mesure.
const chatSrc = readFileSync(join(ROOT, 'api', 'chat.js'), 'utf-8');

async function evalLiteral(name, source) {
  const m = source.match(new RegExp(`const ${name} = (\\{[\\s\\S]*?\\n\\});`));
  if (!m) throw new Error(`Constante introuvable dans api/chat.js : ${name}`);
  const mod = await import(
    'data:text/javascript,' + encodeURIComponent(`export const v = ${m[1]};`)
  );
  return mod.v;
}

// Deux formes coexistent dans chat.js :
//   const X = 4096;
//   const X = parseInt(process.env.X || '7', 10);   ← la valeur est le défaut
// Dans la seconde, le dernier nombre de la ligne est le radix (10), pas la
// valeur : on cherche donc d'abord le défaut après « || ».
function evalNumber(name, source, fallback) {
  const ligne = source.match(new RegExp(`const ${name}\\s*=\\s*(.+)`));
  if (!ligne) return fallback;
  const defaut = ligne[1].match(/\|\|\s*'?([\d.]+)'?/);
  if (defaut) return parseFloat(defaut[1]);
  const direct = ligne[1].match(/^([\d.]+)/);
  return direct ? parseFloat(direct[1]) : fallback;
}

const MODELS = await evalLiteral('MODELS', chatSrc);
const MONTHLY_LIMITS = await evalLiteral('MONTHLY_LIMITS', chatSrc);
const CACHE_READ_MULT = evalNumber('CACHE_READ_MULT', chatSrc, 0.1);
const CACHE_WRITE_MULT = evalNumber('CACHE_WRITE_MULT', chatSrc, 2.0);
const MAX_ITER_HALAKHA = evalNumber('MAX_TOOL_ITERATIONS_HALAKHA', chatSrc, 7);
const MAX_CALLS_HALAKHA = evalNumber('MAX_TOOL_CALLS_HALAKHA', chatSrc, 12);
const MAX_TOKENS_OUTPUT = evalNumber('MAX_TOKENS_OUTPUT', chatSrc, 4096);

// Taille réelle du prompt système. ~3,5 caractères par token : le prompt mêle
// français, hébreu et balises XML, donc c'est une ESTIMATION — pas un compte
// exact. Pour un compte exact, utiliser l'endpoint count_tokens d'Anthropic.
const { buildSystemPrompt } = await import(join(ROOT, 'api', '_system-prompt.js'));
const CHARS_PER_TOKEN = 3.5;
const PROMPT_TOKENS = Math.round(buildSystemPrompt('orach-chaim').length / CHARS_PER_TOKEN);

// Recettes mensuelles par plan, en EUROS (source : /soutenir).
const REVENUE_EUR = {
  khavroutha: 8,
  beit_midrash: 25,
  beit_midrash_plus: 50,
  yeshiva: 100,
};

const eurArg = process.argv.indexOf('--eur');
const EUR_USD = eurArg > -1 ? parseFloat(process.argv[eurArg + 1]) : 1.08;

// ── Modèle de coût ─────────────────────────────────────────────────────────
// Reproduit exactement la formule de api/chat.js (bloc « Coût Claude »).
function cost({ model, uncachedIn = 0, cacheRead = 0, cacheWrite = 0, out = 0 }) {
  return (
    uncachedIn * model.in +
    cacheRead * model.in * CACHE_READ_MULT +
    cacheWrite * model.in * CACHE_WRITE_MULT +
    out * model.out
  ) / 1000;
}

// Une requête agentique de N itérations : le prompt système est écrit en cache à
// la 1re itération puis relu aux N-1 suivantes. Chaque itération renvoie aussi
// les résultats d'outils accumulés, dont une part échappe au cache incrémental.
function agentic({ model, iterations, toolCalls, out, coldCache }) {
  const TOKENS_PER_TOOL_RESULT = 1200; // extraits corpus (700) + Sefaria + marge
  const uncachedIn = toolCalls * TOKENS_PER_TOOL_RESULT + iterations * 400;
  return cost({
    model,
    uncachedIn,
    cacheWrite: coldCache ? PROMPT_TOKENS : 0,
    cacheRead: (coldCache ? iterations - 1 : iterations) * PROMPT_TOKENS,
    out,
  });
}

const SCENARIOS = [
  {
    nom: 'Corpus-first (Haiku)',
    note: 'chemin court : 1 extrait reformulé, pas de prompt système long',
    calc: () => cost({ model: MODELS.haiku, uncachedIn: 2000, out: 800 }),
  },
  {
    nom: 'Sonnet — question standard',
    note: '2 itérations, 2 appels d\'outils, cache chaud',
    calc: () => agentic({ model: MODELS.sonnet, iterations: 2, toolCalls: 2, out: 900, coldCache: false }),
  },
  {
    nom: 'Opus — question typique',
    note: '3 itérations, 4 appels d\'outils, cache chaud',
    calc: () => agentic({ model: MODELS.opus, iterations: 3, toolCalls: 4, out: 1200, coldCache: false }),
  },
  {
    nom: 'Opus — cache froid',
    note: 'idem, mais 1re requête après un déploiement ou > 1 h d\'inactivité',
    calc: () => agentic({ model: MODELS.opus, iterations: 3, toolCalls: 4, out: 1200, coldCache: true }),
  },
  {
    nom: 'Opus — PIRE CAS',
    note: `${MAX_ITER_HALAKHA} itérations, ${MAX_CALLS_HALAKHA} outils, sortie max, cache froid`,
    calc: () => agentic({
      model: MODELS.opus,
      iterations: MAX_ITER_HALAKHA,
      toolCalls: MAX_CALLS_HALAKHA,
      out: MAX_TOKENS_OUTPUT + (MAX_ITER_HALAKHA - 1) * 500,
      coldCache: true,
    }),
  },
];

// ── Sortie ─────────────────────────────────────────────────────────────────
const usd = (n) => '$' + n.toFixed(4);
const eur = (n) => (n).toFixed(2) + ' €';

console.log('\n=== Paramètres lus dans le code ===');
console.log(`  Prompt système      : ${PROMPT_TOKENS} tokens (estimation, ${CHARS_PER_TOKEN} car./token)`);
console.log(`  Cache               : lecture ×${CACHE_READ_MULT} · écriture ×${CACHE_WRITE_MULT}`);
for (const [k, m] of Object.entries(MODELS)) {
  console.log(`  ${k.padEnd(19)} : $${(m.in * 1000).toFixed(0)} / $${(m.out * 1000).toFixed(0)} par million (${m.id})`);
}
console.log(`  Budget halakha      : ${MAX_ITER_HALAKHA} itérations · ${MAX_CALLS_HALAKHA} outils · ${MAX_TOKENS_OUTPUT} tokens de sortie`);
console.log(`  Taux de change      : 1 € = $${EUR_USD}`);

console.log('\n=== Coût par question ===');
const couts = {};
for (const s of SCENARIOS) {
  const c = s.calc();
  couts[s.nom] = c;
  console.log(`  ${usd(c).padStart(9)}  ${s.nom}`);
  console.log(`             ${' '.repeat(0)}└─ ${s.note}`);
}

const pireCas = couts['Opus — PIRE CAS'];
const pireCasEur = pireCas / EUR_USD;

console.log('\n=== Marge par plan (hypothèse la plus défavorable) ===');
console.log(`  Toutes les questions du mois au PIRE CAS : ${usd(pireCas)} = ${eur(pireCasEur)}\n`);
console.log('  Plan                  Recette   Quota   Coût max      Marge');
console.log('  ' + '─'.repeat(58));
let alerte = false;
for (const [plan, recette] of Object.entries(REVENUE_EUR)) {
  const quota = MONTHLY_LIMITS[plan];
  const coutMax = quota * pireCasEur;
  const marge = recette - coutMax;
  // !(marge >= 0) et non (marge < 0) : NaN doit déclencher l'alerte, pas passer
  // silencieusement pour un plan bénéficiaire.
  if (!(marge >= 0)) alerte = true;
  console.log(
    '  ' + plan.padEnd(20) +
    (recette + ' €').padStart(8) +
    String(quota).padStart(8) +
    eur(coutMax).padStart(12) +
    (marge >= 0 ? eur(marge) : '⚠ ' + eur(marge)).padStart(12)
  );
}
console.log('  ' + '─'.repeat(58));
console.log(alerte
  ? '\n  ⚠️  Au moins un plan est déficitaire dans l\'hypothèse la plus défavorable.'
  : '\n  ✓ Tous les plans restent bénéficiaires même au pire cas.');

console.log('\n  Rappel : ce pire cas suppose que 100 % des questions consomment le');
console.log('  budget maximal ET repartent d\'un cache froid — ce qui n\'arrive jamais.');
console.log('  Le coût réel est dans /admin, champ cost_usd, désormais correct.\n');
