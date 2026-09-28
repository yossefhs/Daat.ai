#!/usr/bin/env node
// Parcours RÉEL dans un navigateur (Chromium via Playwright) sur un déploiement :
//   1. page de chat plein écran : choisir niveau + minhag, « Commencer » → accueil
//      STATIQUE sans aucun appel à /api/chat ; poser une question de tableau +
//      citation → la réponse contient <table> et <blockquote>, pas de « | » ni
//      de « > » en texte brut ;
//   2. widget sur une page de siman : question saisie AVANT le choix du profil,
//      « Commencer » → elle part avec le profil, sans être écrasée.
//
//   DAAT_BASE_URL=https://<deploiement> DAAT_VERCEL_JWT=<_vercel_jwt> node tests/chat/navigateur.mjs
//
// Consomme deux questions réelles (quota d'un visiteur anonyme).
import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'node:fs';

const BASE = process.env.DAAT_BASE_URL;
const JWT = process.env.DAAT_VERCEL_JWT || '';
if (!BASE) { console.error('DAAT_BASE_URL manquant'); process.exit(2); }
const host = new URL(BASE).hostname;

const rapport = [];
const ok = (cond, msg) => { rapport.push(`${cond ? '✓' : '✗'} ${msg}`); console.log(`  ${cond ? '✓' : '✗'} ${msg}`); return cond; };
let tout = true;

// Chromium pré-installé de l'environnement si sa version ne correspond pas au paquet.
const browser = await chromium.launch({
  ...(process.env.DAAT_CHROMIUM ? { executablePath: process.env.DAAT_CHROMIUM } : {}),
  // Chromium ne lit pas HTTPS_PROXY tout seul : on le lui passe explicitement.
  ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY, bypass: process.env.NO_PROXY || '' } } : {}),
});
// DAAT_IGNORE_TLS=1 uniquement derrière un proxy d'entreprise qui réécrit le
// certificat (environnement de session) — jamais pour juger le site lui-même.
const ctx = await browser.newContext({ viewport: { width: 1200, height: 900 }, ignoreHTTPSErrors: process.env.DAAT_IGNORE_TLS === '1' });
if (JWT) await ctx.addCookies([{ name: '_vercel_jwt', value: JWT, domain: host, path: '/', httpOnly: true, secure: true, sameSite: 'Lax' }]);
const page = await ctx.newPage();
const apiCalls = [];
page.on('request', (r) => { if (/\/api\/chat(\?|$)/.test(r.url()) && r.method() === 'POST') apiCalls.push(r.url()); });

// ⚠️ Les pages fixent window.DAAT_CHAT_API_URL sur l'API de PRODUCTION
// (daatai.vercel.app), dont la liste d'origines CORS ne connaît pas un
// déploiement de prévisualisation : depuis la prévisualisation, l'appel échoue
// (« Failed to fetch »). Pour juger le déploiement lui-même, on réachemine tout
// POST /api/chat vers SON API, avec le cookie d'accès, et on rend la réponse au
// navigateur avec les en-têtes CORS de l'origine de la page. Le flux SSE est
// alors livré d'un bloc (route.fulfill) — le widget le lit tel quel.
await page.route(/\/api\/chat(\?|$)/, async (route) => {
  const req = route.request();
  if (req.method() !== 'POST') return route.continue();
  const origin = new URL(page.url()).origin;
  try {
    const resp = await ctx.request.post(`${BASE}/api/chat`, {
      data: req.postData() || '',
      headers: { 'Content-Type': 'application/json', ...(JWT ? { Cookie: `_vercel_jwt=${JWT}` } : {}) },
      timeout: 280000,
    });
    const body = await resp.body();
    const ct = resp.headers()['content-type'] || 'text/event-stream; charset=utf-8';
    await route.fulfill({
      status: resp.status(), body,
      headers: { 'Content-Type': ct, 'Access-Control-Allow-Origin': origin, 'Access-Control-Allow-Credentials': 'true' },
    });
  } catch (e) {
    await route.fulfill({ status: 502, body: String(e), headers: { 'Access-Control-Allow-Origin': origin } });
  }
});
mkdirSync('audit/captures', { recursive: true });

// ── 1. chat.html ──────────────────────────────────────────────────────────
console.log('\n=== chat.html');
// Le proxy de session rend parfois ERR_TOO_MANY_RETRIES au premier essai : on réessaie.
async function aller(url, opts) { let err; for (let i = 0; i < 3; i++) { try { return await page.goto(url, opts); } catch (e) { err = e; await page.waitForTimeout(3000); } } throw err; }
await aller(`${BASE}/chat.html`, { waitUntil: 'networkidle' });
// Pas de widget en double sur la page de chat ; on cible l'écran d'accueil.
await page.locator('#niveau-chips .chip').first().click();
await page.locator('#minhag-chips .chip').first().click();
await page.locator('#start-btn').click();
await page.waitForTimeout(1500);
tout &= ok(apiCalls.length === 0, `« Commencer » ne fait aucun appel à /api/chat (${apiCalls.length} appel)`);
const accueil = await page.locator('.bubble-assistant').first().innerText().catch(() => '');
tout &= ok(/Sur quel sujet|niveau/i.test(accueil), `accueil statique affiché : « ${accueil.slice(0, 60)}… »`);

const q = "Fais-moi un tableau comparant Mehaber et Rama sur Orah Haïm 246:1, avec la citation hébraïque en bloc et un lien vers la source.";
await page.locator('#input, textarea').first().fill(q);
await page.keyboard.press('Enter');
// La barre de retour n'est posée qu'APRÈS la fin du flux : c'est le seul signal
// fiable de fin de réponse (le texte, lui, arrive mot à mot).
await page.waitForFunction(() => document.querySelectorAll('.feedback-bar').length >= 1, null, { timeout: 280000 }).catch(() => {});
await page.waitForTimeout(1500);
const bulles = page.locator('.bubble-assistant');
const html = await bulles.last().innerHTML().catch(() => '');
const texte = await bulles.last().innerText().catch(() => '');
console.log(`  (réponse : ${texte.length} car.)`);
tout &= ok(apiCalls.length === 1, `la question déclenche exactement un appel (${apiCalls.length})`);
tout &= ok(/<table/.test(html), 'tableau rendu en <table>');
tout &= ok(/<blockquote/.test(html), 'citation rendue en <blockquote>');
tout &= ok(!/^\s*\|/m.test(texte) && !/^\s*>\s/m.test(texte), 'aucune barre « | » ni « > » en texte brut');
tout &= ok(/<a href="https:\/\/www\.sefaria\.org/.test(html), 'lien Sefaria cliquable');
await page.screenshot({ path: 'audit/captures/chat-html-tableau.png', fullPage: true });

// ── 2. widget sur une page de siman ───────────────────────────────────────
console.log('\n=== widget /oh/319/base');
apiCalls.length = 0;
await aller(`${BASE}/oh/319/base`, { waitUntil: 'domcontentloaded' });
await page.waitForSelector('.daat-chat-button', { timeout: 60000 });
await page.locator('.daat-chat-button').click();
// L'écran d'accueil existe dans le DOM même panneau FERMÉ : c'est l'ouverture
// du panneau qu'il faut attendre, pas la présence de l'accueil.
await page.waitForSelector('.daat-chat-panel.is-open', { timeout: 15000 });
await page.waitForTimeout(600); // fin de la transition d'ouverture
const brouillon = "C'est quoi le mouktsé ?";
await page.locator('.daat-chat-panel.is-open .daat-chat-input').first().fill(brouillon);
// Clics par événement DOM (pas par coordonnées) : pendant la transition, un
// élément de la page peut recouvrir le point visé et détourner un clic réel.
await page.locator('.daat-chat-chips[data-group="niveau"] .daat-chat-chip').first().dispatchEvent('click');
await page.locator('.daat-chat-chips[data-group="minhag"] .daat-chat-chip').first().dispatchEvent('click');
await page.waitForFunction(() => { const b = document.querySelector('#daat-chat-start'); return b && !b.disabled; }, null, { timeout: 5000 });
await page.locator('#daat-chat-start').dispatchEvent('click');
await page.waitForTimeout(1500);
const userMsg = await page.locator('.daat-chat-message.is-user').first().innerText().catch(() => '');
tout &= ok(userMsg.includes(brouillon), 'la question saisie avant le profil est envoyée, pas écrasée');
tout &= ok(/Niveau :/.test(userMsg), 'le profil est joint à la question');
tout &= ok(apiCalls.length === 1, `un seul appel à /api/chat (${apiCalls.length})`);
await page.waitForFunction(() => document.querySelector('.daat-chat-feedback'), null, { timeout: 280000 }).catch(() => {});
await page.waitForTimeout(1500);
// La bulle de réponse est l'élément qui PRÉCÈDE la barre de retour.
const rep = await page.evaluate(() => {
  const fb = document.querySelector('.daat-chat-feedback');
  const el = fb && fb.previousElementSibling;
  return el ? el.innerText : '';
});
console.log(`  (réponse : ${rep.length} car.)`);
tout &= ok(rep.length > 100, `réponse reçue (${rep.length} car.)`);
tout &= ok(!/ton niveau|ton minhag/i.test(rep), 'ne redemande pas le profil');
await page.screenshot({ path: 'audit/captures/widget-319.png', fullPage: false });

await browser.close();
writeFileSync('audit/navigateur-' + new Date().toISOString().slice(0, 10) + '.md',
  `# Parcours navigateur — ${BASE}\n\n${rapport.map(l => '- ' + l).join('\n')}\n\nCaptures : audit/captures/\n`);
console.log(tout ? '\nTout est vert.' : '\nAu moins un contrôle a échoué.');
process.exit(tout ? 0 : 1);
