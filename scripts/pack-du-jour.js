#!/usr/bin/env node
// scripts/pack-du-jour.js — CLI du « Pack du jour » DAAT.
//
// Fine couche au-dessus de api/_pack.js (même moteur que /api/daily-pack en prod) :
// génère le lot de posts du jour, prêt à copier-coller, ancré dans la source réelle
// (titre du siman, numéro hébreu, sous-titre et concepts du corpus, liens canoniques).
// On ne crée pas de halakha ; tout cas pratique renvoie « consulte ton Rav ».
//
// Usage :
//   node scripts/pack-du-jour.js                 # siman 242, angle du jour = aujourd'hui
//   node scripts/pack-du-jour.js --siman 253     # un siman précis
//   node scripts/pack-du-jour.js --siman 253 --day 3   # forcer l'angle (0=dim … 6=sam)
//   node scripts/pack-du-jour.js --siman 253 --html pack.html   # + page avec boutons « Copier »
//
// En production, la même chose sans session ni Node local :
//   https://daattorah.com/api/daily-pack?secret=CRON_SECRET[&siman=N][&day=D]

import { writeFileSync } from 'node:fs';
import { buildPack, renderPackHtml, JOURS, LINKS } from '../api/_pack.js';

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}
const num = Number(arg('siman', '242'));
const dayOverride = arg('day', null);
const htmlOut = arg('html', null);
const day = dayOverride != null ? Number(dayOverride) : new Date().getDay();

const pack = buildPack(num, day);
if (!pack) {
  console.error(`✗ Siman ${num} introuvable dans data/. Vérifie le numéro (242→365).`);
  process.exit(1);
}

const sep = '\n' + '─'.repeat(64) + '\n';
const marks = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧'];

const out = [
  `\n╔══════════════════════════════════════════════════════════════╗`,
  `   דעת · PACK DU JOUR — ${JOURS[pack.day]}`,
  `   Siman ${pack.num} ${pack.numHe ? '(' + pack.numHe + ')' : ''} — ${pack.title}`,
  `   Angle du jour : ${pack.angle.label}`,
  `╚══════════════════════════════════════════════════════════════╝`,
  ``,
  `Liens : étude ${pack.links.study} · vue ${pack.links.overview}`,
  pack.links.blog ? `Article de blog : ${pack.links.blog}` : `(pas encore d'article de blog pour ce siman)`,
  pack.links.image ? `Visuel OG : ${pack.links.image}` : ``,
  pack.subtitle ? `Sous-titre (corpus) : ${pack.subtitle}` : ``,
  pack.concepts.length ? `Concepts : ${pack.concepts.join(' · ')}` : ``,
  ...pack.blocks.flatMap((b, i) => [sep, `${marks[i]} ${b.title.toUpperCase()}\n`, b.text]),
  sep,
  `Groupe WhatsApp : ${LINKS.whatsapp}\nCanal Telegram : ${LINKS.telegram}`,
  ``,
  `Rappel : on ne tranche pas de halakha. Toujours « consulte ton Rav ».`,
  ``,
].filter((l) => l !== '').join('\n');

console.log(out);

if (htmlOut) {
  writeFileSync(htmlOut, renderPackHtml(pack));
  console.log(`\n📄 Page HTML avec boutons « Copier » écrite : ${htmlOut}`);
}
