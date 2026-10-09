// Protection de /admin (middleware.js) : session par courriel, mot de passe,
// et renvoi vers la page de connexion. Le middleware est appelé tel quel, avec
// les Request/Response standard de Node — les mêmes API que l'Edge Runtime.
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import jwt from 'jsonwebtoken';

const SECRET = 'secret-de-test-assez-long-pour-hs256';
let middleware;

before(async () => {
  process.env.JWT_SECRET = SECRET;
  process.env.ADMIN_PASSWORD = 'mot-de-passe-test';
  process.env.ADMIN_EMAILS = 'admin@exemple.org, second@exemple.org';
  ({ default: middleware } = await import('../../middleware.js'));
});

const jeton = (charge, secret = SECRET, options = { expiresIn: '30d' }) => jwt.sign(charge, secret, options);
function requete(chemin = '/admin/', { cookie, basic } = {}) {
  const h = new Headers();
  if (cookie) h.set('cookie', cookie);
  if (basic !== undefined) h.set('authorization', 'Basic ' + btoa(basic));
  return new Request('https://daattorah.com' + chemin, { headers: h });
}
const session = (t) => `autre=1; daat_session=${encodeURIComponent(t)}; x=2`;
const versConnexion = (r) => r && r.status === 302 && new URL(r.headers.get('location')).pathname === '/connexion-admin.html';

test('session courriel d\'une adresse administratrice → laisse passer', async () => {
  assert.equal(await middleware(requete('/admin/', { cookie: session(jeton({ email: 'Admin@Exemple.org' })) })), undefined);
  assert.equal(await middleware(requete('/admin/feedback.html', { cookie: session(jeton({ email: 'second@exemple.org' })) })), undefined);
});

test('session valide mais adresse NON administratrice → page de connexion', async () => {
  assert.ok(versConnexion(await middleware(requete('/admin/', { cookie: session(jeton({ email: 'intrus@exemple.org' })) }))));
});

test('session expirée, signature fausse, autre secret, alg « none » → refusées', async () => {
  const expire = jeton({ email: 'admin@exemple.org', exp: Math.floor(Date.now() / 1000) - 10 }, SECRET, {});
  const bon = jeton({ email: 'admin@exemple.org' });
  const [h, , s] = bon.split('.');
  const chargeForgee = Buffer.from(JSON.stringify({ email: 'admin@exemple.org', exp: 9999999999 })).toString('base64url');
  const aucun = jwt.sign({ email: 'admin@exemple.org' }, '', { algorithm: 'none' });
  for (const t of [expire, `${h}.${chargeForgee}.${s}`, jeton({ email: 'admin@exemple.org' }, 'un-autre-secret'), aucun, 'pas.un.jeton', 'n%E0importe']) {
    assert.ok(versConnexion(await middleware(requete('/admin/', { cookie: session(t) }))), t.slice(0, 30));
  }
});

test('sans ADMIN_EMAILS, la session ne suffit pas — le mot de passe reste seul juge', async () => {
  const sauve = process.env.ADMIN_EMAILS; delete process.env.ADMIN_EMAILS;
  try {
    assert.ok(versConnexion(await middleware(requete('/admin/', { cookie: session(jeton({ email: 'admin@exemple.org' })) }))));
  } finally { process.env.ADMIN_EMAILS = sauve; }
});

test('mot de passe : bon → passe ; faux → 401 avec fenêtre du navigateur', async () => {
  assert.equal(await middleware(requete('/admin/', { basic: 'admin:mot-de-passe-test' })), undefined);
  assert.equal(await middleware(requete('/admin/', { basic: 'nimporte:mot-de-passe-test' })), undefined);
  const r = await middleware(requete('/admin/', { basic: 'admin:faux' }));
  assert.equal(r.status, 401);
  assert.match(r.headers.get('www-authenticate') || '', /^Basic /);
});

test('aucune identification → page de connexion, avec le chemin de retour', async () => {
  const r = await middleware(requete('/admin/feedback.html?onglet=2'));
  assert.ok(versConnexion(r));
  assert.equal(new URL(r.headers.get('location')).searchParams.get('retour'), '/admin/feedback.html?onglet=2');
});

test('?motdepasse → la fenêtre du mot de passe, comme avant', async () => {
  const r = await middleware(requete('/admin/?motdepasse'));
  assert.equal(r.status, 401);
  assert.match(r.headers.get('www-authenticate') || '', /^Basic /);
});

test('ADMIN_PASSWORD absent et aucune session → 500, comme avant (fermé)', async () => {
  const sauve = process.env.ADMIN_PASSWORD; delete process.env.ADMIN_PASSWORD;
  try {
    assert.equal((await middleware(requete('/admin/'))).status, 500);
  } finally { process.env.ADMIN_PASSWORD = sauve; }
});
