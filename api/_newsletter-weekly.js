// api/_newsletter-weekly.js — Broadcast hebdomadaire « le siman du dimanche ».
//
// Envoyé chaque dimanche à tous les abonnés confirmés : le siman de la semaine
// (Choulhan Aroukh, Orah Haïm), dans l'ordre 242 → 365, avec un lien d'étude et —
// quand il existe — un lien vers l'article de blog correspondant.
//
// État Vercel KV :
//   newsletter:weekly:cursor        → prochain numéro de siman à envoyer (défaut 242)
//   newsletter:weekly:lastSentDate  → 'YYYY-MM-DD' du dernier envoi (anti-doublon)

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SITE = 'https://daattorah.com';
const FIRST_SIMAN = 242;
const LAST_SIMAN = 365;

// Simanim qui ont déjà un article de blog (FR). Slug = fichier dans /blog/.
export const BLOG_BY_SIMAN = {
  242: 'honorer-shabbat-kavod-oneg',
  243: 'louer-bien-non-juif-shabbat',
  244: 'travaux-non-juif-pour-juif-shabbat',
  245: 'association-juif-non-juif-shabbat',
  246: 'pret-location-non-juif-shabbat',
  247: 'livraison-colis-shabbat',
  248: 'voyage-bateau-caravane-avant-shabbat',
  249: 'regles-vendredi-erev-shabbat',
  250: 'preparer-repas-shabbat-vendredi',
  251: 'melakha-vendredi-apres-minha',
  252: 'travaux-commences-avant-shabbat',
  253: 'shabbat-plata-rechauffer-marmites',
  254: 'plats-mijotes-erev-shabbat',
  255: 'allumer-feu-avant-shabbat',
  256: 'sonneries-shofar-entree-shabbat',
  257: 'hatmana-envelopper-plats-chauds-shabbat',
  261: 'bougies-shabbat-horaire-allumage',
  308: 'muktse-telephone-argent-shabbat',
  312: 'papier-toilette-shabbat',
  318: 'rechauffer-plat-shabbat',
  319: 'trier-aliments-borer-shabbat',
  326: 'se-doucher-laver-shabbat',
  327: 'cremes-cosmetiques-shabbat',
};

let _simanim = null;
function loadSimanim() {
  if (_simanim) return _simanim;
  try {
    const raw = readFileSync(join(__dirname, '..', 'data', 'simanim-disponibles.json'), 'utf-8');
    const data = JSON.parse(raw);
    const list = Array.isArray(data) ? data : data.simanim || [];
    _simanim = new Map(list.map((s) => [Number(s.num), s]));
  } catch (e) {
    console.warn('[newsletter-weekly] load simanim failed:', e?.message);
    _simanim = new Map();
  }
  return _simanim;
}

const _details = new Map();
// Détail fiable par siman (data/simanim/siman-N.json : titleFr complet + numberHe),
// car simanim-disponibles.json (dérivé des <h1>) peut être tronqué pour certains simanim.
function loadDetail(num) {
  if (_details.has(num)) return _details.get(num);
  let d = null;
  try {
    d = JSON.parse(readFileSync(join(__dirname, '..', 'data', 'simanim', `siman-${num}.json`), 'utf-8'));
  } catch { /* absent → fallback index */ }
  _details.set(num, d);
  return d;
}

export function getSiman(num) {
  const n = Number(num);
  const base = loadSimanim().get(n);
  if (!base) return null;
  const detail = loadDetail(n);
  const numHe = (detail?.numberHe && /[֐-׿]/.test(detail.numberHe) && detail.numberHe)
    || (/[֐-׿]/.test(base.numHe || '') ? base.numHe : '');
  const title = detail?.titleFr || base.title || `Siman ${n}`;
  return { ...base, num: n, numHe, title };
}

// Renvoie le prochain numéro de siman valide ≥ from (borné à LAST_SIMAN).
export function nextValidSiman(from) {
  const map = loadSimanim();
  for (let n = Math.max(FIRST_SIMAN, Number(from) || FIRST_SIMAN); n <= LAST_SIMAN; n++) {
    if (map.has(n)) return n;
  }
  return null; // série terminée
}

function shell(title, bodyHtml, ctas) {
  const ctaHtml = (ctas || [])
    .map((c) => {
      const primary = c.primary !== false;
      const style = primary
        ? 'background:#C5A55A;color:#1A1F3A;'
        : 'background:#fff;color:#1A1F3A;border:1px solid #C5A55A;';
      return `<a href="${c.href}" style="display:inline-block;margin:4px 6px;${style}padding:13px 24px;text-decoration:none;font-family:'Inter',-apple-system,sans-serif;font-size:14px;font-weight:600;letter-spacing:0.5px;border-radius:3px;">${c.label}</a>`;
    })
    .join('');
  return `<!DOCTYPE html>
<html><body style="font-family:Georgia,'Times New Roman',serif;background:#FAF6EE;margin:0;padding:24px;color:#1A1F3A;">
  <div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #E4DDD0;border-radius:8px;padding:32px;">
    <div style="display:flex;align-items:baseline;gap:12px;padding-bottom:16px;border-bottom:2px solid #C5A55A;margin-bottom:24px;">
      <span style="font-family:'Frank Ruhl Libre',serif;font-size:32px;font-weight:700;color:#C5A55A;">דעת</span>
      <span style="font-family:'Inter',-apple-system,sans-serif;font-size:13px;font-weight:600;color:#1A1F3A;letter-spacing:4px;">DAAT · LE SIMAN DU DIMANCHE</span>
    </div>
    <h1 style="font-family:Georgia,serif;color:#1A1F3A;font-size:22px;margin:0 0 16px;line-height:1.3;">${title}</h1>
    <div style="color:#3D4266;font-size:15px;line-height:1.75;">${bodyHtml}</div>
    <div style="text-align:center;margin:28px 0 8px;">${ctaHtml}</div>
    <p style="color:#3D4266;font-size:13px;line-height:1.7;margin-top:24px;padding-top:16px;border-top:1px solid #E4DDD0;text-align:center;font-style:italic;">
      Pour la pratique de la halakha, consulte toujours ton Rav.
    </p>
    <p style="color:#aaa;font-size:11px;line-height:1.6;margin-top:12px;text-align:center;">
      דעת DAAT · <a href="${SITE}/" style="color:#C5A55A;">daattorah.com</a> · initié par le Rav Yossef Haim Samama<br>
      Tu reçois cet email car tu es inscrit à la newsletter Daat.
    </p>
  </div>
</body></html>`.trim();
}

// Construit l'email du siman de la semaine. `siman` = objet {num, numHe, title}.
export function buildWeeklyEmail(siman) {
  const num = Number(siman.num);
  const he = siman.numHe || '';
  const title = siman.title || `Siman ${num}`;
  const studyUrl = `${SITE}/oh/${num}/`;
  const blogSlug = BLOG_BY_SIMAN[num];
  const blogUrl = blogSlug ? `${SITE}/blog/${blogSlug}.html` : null;

  const subject = `Le siman du dimanche — ${he ? he + ' · ' : ''}${title}`;

  const blogBlock = blogUrl
    ? `<p style="background:#FAF6EE;border-left:3px solid #C5A55A;padding:14px 18px;margin:18px 0;">
         📖 <strong>Version article</strong> — une question concrète du quotidien, traitée à partir de ce siman, à lire et à partager :
         <br><a href="${blogUrl}" style="color:#8C6F1E;">${blogUrl.replace('https://', '')}</a>
       </p>`
    : '';

  const body = `
    <p>Le siman de cette semaine : <strong>${he ? he + ' — ' : ''}${title}</strong>.</p>
    <p>Il est étudié sur <strong>daattorah.com</strong> en plusieurs niveaux — du texte hébreu du Mehaber avec traduction française (Base), jusqu'au pilpoul et à la chitah de l'Admour HaZaken (Daat HaRav).</p>
    ${blogBlock}
    <p>Bonne étude, et חזק וברוך. 🕯️</p>
  `;

  const ctas = [{ href: studyUrl, label: `Étudier le Siman ${num} →` }];
  if (blogUrl) ctas.push({ href: blogUrl, label: 'Lire la version article', primary: false });

  const text =
    `Le siman du dimanche — ${he ? he + ' · ' : ''}${title}\n\n` +
    `Étudier : ${studyUrl}\n` +
    (blogUrl ? `Version article : ${blogUrl}\n` : '') +
    `\nPour la pratique, consulte ton Rav.\n— DAAT דעת · daattorah.com`;

  return { subject, html: shell(`Siman ${num} · ${title}`, body, ctas), text };
}

export const WEEKLY_DEFAULTS = { FIRST_SIMAN, LAST_SIMAN };
