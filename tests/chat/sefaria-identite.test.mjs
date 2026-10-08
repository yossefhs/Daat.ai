// Tests A (identité de l'ouvrage) et F (source indisponible) — fetch SIMULÉ.
// Sefaria n'est pas appelé : les réponses sont celles observées le 28/09/2026
// (champs indexTitle / ref / heRef / versions) pour 317:4 dans les deux ouvrages.
import { test, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { executeSefariaTool, describeWork, indexTitleFromRef, toUrlRef } from '../../api/_sefaria.js';

const KARO_317_4 = {
  title: 'Shulchan Arukh, Orach Chayim 317', indexTitle: 'Shulchan Arukh, Orach Chayim',
  ref: 'Shulchan Arukh, Orach Chayim 317:4', heRef: 'שולחן ערוך, אורח חיים שי״ז:ד׳',
  versions: [
    { language: 'he', versionTitle: 'Wikisource', text: 'קושרין דלי במשיחה או באבנט וכיוצא בו אבל לא בחבל' },
    { language: 'en', versionTitle: 'Sefaria Community Translation', text: 'One may tie a bucket with a belt…' },
  ],
};
const HARAV_317_4 = {
  title: 'Shulchan Arukh HaRav, Orach Chayim 317', indexTitle: 'Shulchan Arukh HaRav',
  ref: 'Shulchan Arukh HaRav, Orach Chayim 317:4', heRef: 'שולחן ערוך הרב, אורח חיים שי״ז:ד׳',
  versions: [{ language: 'he', versionTitle: 'Kehot Publication Society', text: 'קֶשֶׁר שֶׁאֵינוֹ נִקְרָא שֶׁל קַיָּמָא מִן הַתּוֹרָה אֶלָּא מִדִּבְרֵי סוֹפְרִים' }],
};

let realFetch;
beforeEach(() => { realFetch = globalThis.fetch; });
afterEach(() => { globalThis.fetch = realFetch; });

function mockFetch(map) {
  globalThis.fetch = async (url) => {
    const u = decodeURIComponent(String(url));
    for (const [key, val] of Object.entries(map)) {
      if (u.includes(key)) {
        if (val === 404) return { ok: false, status: 404, json: async () => ({ error: `We have no text for ${key}.` }) };
        return { ok: true, status: 200, json: async () => val };
      }
    }
    return { ok: false, status: 500, json: async () => ({}) };
  };
}

test('A — Shulchan_Arukh,_Orach_Chayim.317.4 est identifié comme Karo, avec la note qui exclut le HaRav', async () => {
  mockFetch({ 'Shulchan_Arukh,_Orach_Chayim.317.4': KARO_317_4 });
  const out = JSON.parse(await executeSefariaTool('sefaria_get_text', { ref: 'Shulchan_Arukh,_Orach_Chayim.317.4' }));
  assert.ok(!out.error, out.error);
  assert.match(out.work, /Shulchan Arukh, Orach Chayim/);
  assert.match(out.author, /Karo/);
  assert.match(out.attribution_note, /NON le Choul'han Aroukh HaRav/);
  assert.equal(out.url, 'https://www.sefaria.org/Shulchan_Arukh,_Orach_Chayim.317.4');
  assert.equal(out.english_is_translation, true);
  assert.ok(out.versions.some(v => v.language === 'en' && /Community/.test(v.versionTitle)));
  assert.match(out.hebrew, /קושרין דלי/);
});

test('A — Shulchan_Arukh_HaRav,_Orach_Chayim.317.4 est identifié comme Admour HaZaken (nœuds, pas salaire de Shabbat)', async () => {
  mockFetch({ 'Shulchan_Arukh_HaRav,_Orach_Chayim.317.4': HARAV_317_4 });
  const out = JSON.parse(await executeSefariaTool('sefaria_get_text', { ref: 'Shulchan_Arukh_HaRav,_Orach_Chayim.317.4' }));
  assert.match(out.work, /Shulchan Arukh HaRav/);
  assert.match(out.author, /Admour HaZaken/);
  assert.match(out.attribution_note, /NON le Choul'han Aroukh de R\. Yossef Karo/);
  assert.equal(out.work_he, 'שולחן ערוך הרב, אורח חיים שי״ז:ד׳');
  assert.equal(out.url, 'https://www.sefaria.org/Shulchan_Arukh_HaRav,_Orach_Chayim.317.4');
  assert.match(out.hebrew, /קֶשֶׁר/);
  assert.ok(!/שכר שבת/.test(out.hebrew), 'le 317:4 ne parle pas du salaire de Shabbat');
});

test('A — le préfixe le plus long gagne : « Shulchan Arukh HaRav » n\'est jamais lu comme « Shulchan Arukh »', () => {
  const w = describeWork('Shulchan_Arukh_HaRav,_Orach_Chayim.319.4-5', null);
  assert.match(w.author, /Admour/);
  assert.equal(indexTitleFromRef('Shulchan_Arukh_HaRav,_Orach_Chayim.319.4-5'), 'Shulchan Arukh HaRav, Orach Chayim');
  assert.equal(indexTitleFromRef('Shabbat.19a'), 'Shabbat');
  assert.equal(indexTitleFromRef('Mishneh_Torah,_Sabbath.6.16'), 'Mishneh Torah, Sabbath');
  assert.equal(toUrlRef('Shulchan Arukh HaRav, Orach Chayim 317:4'), 'Shulchan_Arukh_HaRav,_Orach_Chayim.317.4');
});

test('A — un ouvrage non répertorié reçoit une note qui demande d\'identifier l\'auteur avant d\'attribuer', () => {
  const w = describeWork('Sefer_HaChinukh.1', null);
  assert.equal(w.author, null);
  assert.match(w.attribution_note, /identifie l'auteur/);
});

test('F — référence inexistante : erreur explicite, ouvrage DEMANDÉ nommé, interdiction de substituer', async () => {
  mockFetch({ 'Shulchan_Arukh_HaRav,_Orach_Chayim.317.99': 404 });
  const out = JSON.parse(await executeSefariaTool('sefaria_get_text', { ref: 'Shulchan_Arukh_HaRav,_Orach_Chayim.317.99' }));
  assert.ok(out.error);
  assert.match(out.error, /Ne cite PAS/);
  assert.match(out.work_requested, /Shulchan Arukh HaRav/);
  assert.match(out.note, /ne le remplace pas silencieusement/);
  assert.equal(out.hebrew, undefined);
});

test('F — 200 sans aucun texte : erreur, jamais un résultat d\'apparence valide', async () => {
  mockFetch({ 'Tanya,_Part_I.999': { indexTitle: 'Tanya', ref: 'Tanya, Part I 999', versions: [] } });
  const out = JSON.parse(await executeSefariaTool('sefaria_get_text', { ref: 'Tanya,_Part_I.999' }));
  assert.ok(out.error);
  assert.match(out.error, /aucun texte/);
});

test('la description de l\'outil nomme les identifiants distincts et interdit la substitution', async () => {
  const { SEFARIA_TOOLS } = await import('../../api/_sefaria.js');
  const d = SEFARIA_TOOLS.find(t => t.name === 'sefaria_get_text').description;
  assert.ok(d.includes('Shulchan_Arukh,_Orach_Chayim.N.M'));
  assert.ok(d.includes('Shulchan_Arukh_HaRav,_Orach_Chayim.N.M'));
  assert.ok(/ne les substitue jamais/.test(d));
  assert.ok(/prouve que la référence existe, pas qu'elle soutient/.test(d));
});
