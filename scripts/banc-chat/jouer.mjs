// Joue les cas de scripts/banc-chat/cas.mjs contre /api/chat (flux SSE) et archive
// chaque échange : <id>.json (brut : question, événements, outils, réponse, attendu)
// et <id>.txt (lisible). Puis `python3 scripts/banc-chat/verifier.py <dossier>`.
//
//   node scripts/banc-chat/jouer.mjs <BASE_URL> <DOSSIER_SORTIE> [id1,id2,…]
//
// BASE_URL : https://daatai.vercel.app (production) ou un aperçu Vercel. Un aperçu
// est protégé : suivre son lien de partage (_vercel_share) avec `curl -L -c jar`,
// puis COOKIE0="$(awk '(/^#HttpOnly_/ || !/^#/) && NF>=7 {printf "%s=%s; ", $6, $7}' jar)"
// (le cookie _vercel_jwt est écrit HttpOnly : sans ce filtre il est sauté → 401).
// Tant que l'aperçu construit, l'alias sert la page « Instant Preview » (HTML, 200) :
// l'API est prête quand POST {"messages":[]} rend 400 JSON.
// Les cas déjà archivés dans DOSSIER_SORTIE sont sautés : effacer <id>.json pour rejouer.
// Toujours /opt/homebrew/opt/node@22/bin/node, jamais `node` nu.
import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import CASES from './cas.mjs';

const [BASE, OUT, ONLY] = process.argv.slice(2);
if (!BASE || !OUT) { console.error('usage : node scripts/banc-chat/jouer.mjs <BASE_URL> <DOSSIER_SORTIE> [id1,id2,…]'); process.exit(2); }
const COOKIE0 = process.env.COOKIE0 || '';
mkdirSync(OUT, { recursive: true });
const only = ONLY ? new Set(ONLY.split(',')) : null;
const CONCURRENCE = 2;          // au-delà, l'anonyme tape dans les plafonds anti-abus
const DELAI_MAX_MS = 180_000;

async function appel(messages, cas) {
  const body = { messages };
  if (cas.section) body.section = cas.section;
  const headers = { 'Content-Type': 'application/json', Accept: 'text/event-stream', Origin: BASE };
  if (COOKIE0) headers.Cookie = COOKIE0;
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), DELAI_MAX_MS);
  const t0 = performance.now();
  const tour = { http: 0, ms: 0, text: '', events: [], tools: [], erreur: null };
  try {
    const res = await fetch(BASE + '/api/chat', { method: 'POST', headers, body: JSON.stringify(body), signal: ctl.signal });
    tour.http = res.status;
    const ct = res.headers.get('content-type') || '';
    if (!res.ok || !res.body || !ct.includes('text/event-stream')) {
      tour.erreur = `HTTP ${res.status} · ${ct} · ` + (await res.text()).slice(0, 400);
    } else {
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = '';
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i;
        while ((i = buf.indexOf('\n\n')) !== -1) {
          const bloc = buf.slice(0, i); buf = buf.slice(i + 2);
          for (const ligne of bloc.split('\n')) {
            if (!ligne.startsWith('data:')) continue;
            let ev; try { ev = JSON.parse(ligne.slice(5).trim()); } catch { continue; }
            if (ev.type === 'text' && typeof ev.delta === 'string') tour.text += ev.delta;
            else {
              tour.events.push(ev);
              if (ev.type === 'tool_use') tour.tools.push({ tool: ev.tool, input: ev.input });
              // Les chemins d'échec de api/chat.js : la réponse peut être partielle et
              // sembler bonne — l'erreur doit rester visible dans l'archive ET le résumé.
              if (ev.type === 'error' || ev.type === 'limit_reached' || ev.type === 'rate_limited') tour.erreur = `${ev.type} : ${ev.message || ev.error || ''}`.trim();
            }
          }
        }
      }
    }
  } catch (e) {
    tour.erreur = 'EXCEPTION : ' + (e?.name === 'AbortError' ? `délai de ${DELAI_MAX_MS / 1000} s dépassé` : e?.message);
  } finally { clearTimeout(timer); tour.ms = Math.round(performance.now() - t0); }
  const done = tour.events.find((e) => e.type === 'done');
  if (!tour.erreur && !done) tour.erreur = 'flux terminé sans événement done';
  if (!tour.erreur && done && done.stop_reason === 'error') tour.erreur = 'done.stop_reason = error';
  return tour;
}

function chemin(tour) {
  const done = tour.events.find((e) => e.type === 'done') || {};
  const rate = tour.events.find((e) => e.type === 'rate_info') || {};
  const champs = [];
  for (const k of ['provider', 'model', 'iterations', 'stop_reason', 'cached', 'corpus', 'rescue', 'urgence']) if (done[k] !== undefined) champs.push(`${k}=${done[k]}`);
  for (const k of ['plan', 'model_tier', 'is_aperçu', 'preview_remaining']) if (rate[k] !== undefined) champs.push(`rate.${k}=${rate[k]}`);
  return champs.join(' · ') || '(aucune métadonnée)';
}

async function jouer(cas) {
  const sortie = join(OUT, cas.id + '.json');
  if (existsSync(sortie)) return 'déjà fait';
  const messages = [], tours = [];
  for (const q of cas.turns) {
    messages.push({ role: 'user', content: q });
    const tour = await appel(messages, cas);
    tours.push({ question: q, ...tour });
    if (!tour.text) break;
    messages.push({ role: 'assistant', content: tour.text });
  }
  writeFileSync(sortie, JSON.stringify({ ...cas, base: BASE, date: new Date().toISOString(), tours }, null, 2), 'utf8');
  let txt = `CAS ${cas.id} · ${cas.cat}\nCE QU'ON SONDE : ${cas.probe}\nsection=${cas.section || 'orach-chaim (défaut)'} · base=${BASE}\n`;
  tours.forEach((t, i) => {
    txt += `\n${'═'.repeat(30)} TOUR ${i + 1} ${'═'.repeat(30)}\nQUESTION :\n${t.question}\n\nHTTP ${t.http} · ${(t.ms / 1000).toFixed(1)} s · ${t.text.length} caractères\nCHEMIN : ${chemin(t)}\n`;
    if (t.erreur) txt += `ERREUR : ${t.erreur}\n`;
    txt += `OUTILS (${t.tools.length}) :\n${t.tools.map((o, k) => `  ${k + 1}. ${o.tool} ${JSON.stringify(o.input)}`).join('\n') || '  (aucun)'}\n\nRÉPONSE :\n${t.text || '(VIDE)'}\n`;
  });
  writeFileSync(join(OUT, cas.id + '.txt'), txt, 'utf8');
  const d = tours[tours.length - 1];
  return `HTTP ${d.http} · ${(d.ms / 1000).toFixed(0)} s · ${d.text.length} car · serveur=${d.tools.filter((o) => o.input?.par === 'serveur').length}${d.erreur ? ' · ' + d.erreur.slice(0, 80) : ''}`;
}

const liste = CASES.filter((c) => !only || only.has(c.id));
let idx = 0;
async function ouvrier() { while (idx < liste.length) { const cas = liste[idx++]; console.log(`${cas.id.padEnd(32)} ${await jouer(cas)}`); } }
await Promise.all(Array.from({ length: CONCURRENCE }, ouvrier));
console.log(`TERMINÉ — ${liste.length} cas → ${OUT}`);
