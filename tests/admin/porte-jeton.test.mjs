// adminParJetonMemeSite (api/_admin-gate.js) : la session par courriel ouvre les
// API admin HORS de /api/admin/ (dédicaces, khavroutha, qonto-sync, signalement)
// — mais jamais pour une requête qu'un AUTRE SITE a déclenchée : le cookie est
// SameSite=None et part aussi sur une image, un lien ou un formulaire tiers.
import { test, before } from 'node:test';
import assert from 'node:assert/strict';

let porte, signer;
before(async () => {
  Object.assign(process.env, { JWT_SECRET: 'jwt-test-secret', ADMIN_EMAILS: 'admin@exemple.org' });
  ({ adminParJetonMemeSite: porte } = await import('../../api/_admin-gate.js'));
  ({ signSession: signer } = await import('../../api/_auth.js'));
});
const req = (email, entetes = {}) => ({ headers: { cookie: email ? 'daat_session=' + encodeURIComponent(signer({ email })) : '', ...entetes } });

test('session admin depuis la page /admin (même origine) → acceptée', () => {
  assert.equal(porte(req('admin@exemple.org', { 'sec-fetch-site': 'same-origin' })), 'admin@exemple.org');
  assert.equal(porte(req('admin@exemple.org')), 'admin@exemple.org'); // navigateur ancien, appel serveur
});

test('session d\'une adresse non administratrice, ou aucune → refusée', () => {
  assert.equal(porte(req('intrus@exemple.org', { 'sec-fetch-site': 'same-origin' })), null);
  assert.equal(porte(req(null, { 'sec-fetch-site': 'same-origin' })), null);
});

test('requête déclenchée par un autre site → refusée, même avec le bon cookie', () => {
  assert.equal(porte(req('admin@exemple.org', { 'sec-fetch-site': 'cross-site' })), null);
  assert.equal(porte(req('admin@exemple.org', { origin: 'https://mechant.example' })), null);
});
