// api/_daily-post.js — Le post quotidien du Daat Yomi : rédaction, vérification,
// illustrations, email de validation.
//
// Chaîne (déclenchée par le cron de /api/daily-post, dimanche → jeudi) :
//   1. l'entrée du jour vient du plan (data/limoud-plan.json) : jour, total,
//      siman, séifim — jamais recopiés à la main ;
//   2. Claude rédige le post à partir de DEUX sources : le texte exact des
//      séifim du jour (Sefaria, Mehaber + gloses du Rama) et la page d'étude
//      du site (niveau 1). Sortie structurée (outil forcé), pas de texte libre ;
//   3. un second appel confronte chaque affirmation au texte source et rend un
//      verdict (vert / orange / rouge) ;
//   4. OpenAI génère les illustrations — SANS AUCUN TEXTE : tous les mots du
//      visuel (titres, hébreu, lien) sont posés par la page, jamais par l'IA
//      d'image, qui écrit mal l'hébreu ;
//   5. un email part vers l'administrateur avec le lien de validation.
// Rien n'est publié sans un clic sur « Publier partout » (voir /api/daily-post).
//
// État en KV, une clé par date (TTL 10 jours) :
//   dailypost:{date}            → le post rédigé + métadonnées
//   dailypost:{date}:verify     → le verdict de vérification
//   dailypost:{date}:img:{slot} → une illustration (data URL JPEG)
//   dailypost:{date}:final      → le visuel composé et publié (base64 JPEG)
//   dailypost:{date}:published  → résultat par réseau
//   dailypost:log               → journal (30 derniers événements)

import { createHmac, timingSafeEqual } from 'node:crypto';
import Anthropic from '@anthropic-ai/sdk';
import { Resend } from 'resend';
import { kv } from './_kv.js';
import { getEntryForDate, loadPlan } from './_daily-limoud.js';

export const SITE = 'https://daattorah.com';
const TTL = 10 * 24 * 3600;
const env = (k) => (process.env[k] || '').trim();

// Modèle de rédaction : le plus récent par défaut, repli sur celui déjà
// éprouvé en production par le chat si le premier n'est pas disponible.
const MODELS = [env('DAILY_POST_MODEL') || 'claude-sonnet-5-5', 'claude-sonnet-4-6'];

// ---------- dates & plan ----------

export function parisToday() {
  return new Intl.DateTimeFormat('fr-CA', {
    timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(new Date());
}

export function dayInfo(date) {
  const entry = getEntryForDate(date);
  if (!entry) return null;
  let totalDays = null;
  try { totalDays = loadPlan()?.meta?.totalDays || null; } catch { /* plan illisible */ }
  const [y, m, d] = date.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d, 12));
  const dateFr = new Intl.DateTimeFormat('fr-FR', {
    timeZone: 'UTC', weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  }).format(dt);
  const dateCourte = new Intl.DateTimeFormat('fr-FR', {
    timeZone: 'UTC', day: '2-digit', month: '2-digit', year: 'numeric',
  }).format(dt);
  const jourSemaine = new Intl.DateTimeFormat('fr-FR', { timeZone: 'UTC', weekday: 'long' }).format(dt);
  return {
    date,
    dateFr,
    dateCourte,
    jourSemaine,
    dayNumber: entry.dayNumber,
    totalDays,
    semaine: Math.ceil(entry.dayNumber / 5),
    siman: entry.siman,
    seifRange: entry.seifRange,
    lotIndex: entry.lotIndex,
    lotTotal: entry.lotTotal,
    studyUrl: `${SITE}/oh/${entry.siman.num}/base`,
  };
}

// ---------- jeton de validation ----------
// Un jeton par date, dérivé de CRON_SECRET : le lien de l'email n'ouvre que le
// post de ce jour-là, et le secret lui-même ne circule jamais.

export function tokenFor(date) {
  const secret = env('CRON_SECRET');
  if (!secret) return null;
  return createHmac('sha256', secret).update(`dailypost:${date}`).digest('hex').slice(0, 32);
}

export function tokenOk(date, token) {
  const good = tokenFor(date);
  if (!good || typeof token !== 'string' || token.length !== good.length) return false;
  return timingSafeEqual(Buffer.from(good), Buffer.from(token));
}

// ---------- sources ----------

const HEB = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'יא', 'יב', 'יג', 'יד', 'טו', 'טז', 'יז', 'יח', 'יט', 'כ'];

// Texte exact des séifim du jour (Mehaber + gloses du Rama marquées « הגה »).
export async function fetchSeifim(num, from, to) {
  const out = [];
  for (let n = from; n <= to; n++) {
    const url = `https://www.sefaria.org/api/v3/texts/Shulchan_Arukh,_Orach_Chayim.${num}.${n}?version=hebrew`;
    const r = await fetch(url, { headers: { Accept: 'application/json' } });
    if (!r.ok) throw new Error(`Sefaria ${num}:${n} → HTTP ${r.status}`);
    const d = await r.json();
    let t = d?.versions?.[0]?.text;
    if (Array.isArray(t)) t = t.join(' ');
    t = String(t || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
    if (!t) throw new Error(`Sefaria ${num}:${n} → texte vide`);
    out.push({ n, lettre: HEB[n] || String(n), he: t });
  }
  return out;
}

// Texte de la page d'étude (niveau 1), servi par le site public.
export async function fetchStudyPage(num) {
  const r = await fetch(`${SITE}/sources/shabbat/siman-${num}/niveau-1-base.html`);
  if (!r.ok) throw new Error(`page du siman ${num} → HTTP ${r.status}`);
  const html = await r.text();
  const body = (html.match(/<body[^>]*>([\s\S]*)<\/body>/i) || [, html])[1];
  return body
    .replace(/<(script|style|nav|header|footer)[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<\/(p|div|li|h\d|tr|blockquote)>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/[ \t]+/g, ' ').replace(/\n\s*\n+/g, '\n').trim()
    .slice(0, 60000);
}

// ---------- rédaction (Claude) ----------

const POST_TOOL = {
  name: 'post_du_jour',
  description: 'Le post Daat Yomi du jour, prêt pour le visuel et pour chaque réseau.',
  input_schema: {
    type: 'object',
    required: ['titre', 'sous_titre', 'seifim', 'a_retenir', 'illustration_principale', 'posts', 'hashtags'],
    properties: {
      titre: { type: 'string', description: 'Titre du visuel, accrocheur, ≤ 45 caractères. Ex. « Havdala — jusqu\'à quand ? »' },
      sous_titre: { type: 'string', description: 'Deuxième ligne du titre, ≤ 55 caractères.' },
      seifim: {
        type: 'array',
        description: 'Un élément par séif du jour, dans l\'ordre du Choul\'han Aroukh.',
        items: {
          type: 'object',
          required: ['n', 'titre', 'points', 'illustration'],
          properties: {
            n: { type: 'integer' },
            titre: { type: 'string', description: 'Titre de la carte, ≤ 40 caractères.' },
            points: { type: 'array', items: { type: 'string' }, description: '1 ou 2 phrases, chacune ≤ 110 caractères. Entoure de **…** un ou deux mots-clés par phrase (ex. « jusqu\'à la fin de **mardi** »).' },
            illustration: { type: 'string', description: 'En anglais : décrire UNE photo d\'objet ou de scène qui illustre ce séif (ex. « a silver kiddush cup beside a vintage alarm clock »). Aucune personne, aucun texte, aucune lettre.' },
          },
        },
      },
      a_retenir: {
        type: 'array',
        description: '3 ou 4 mémos très courts.',
        items: {
          type: 'object',
          required: ['label', 'texte', 'icone'],
          properties: {
            label: { type: 'string', description: '≤ 20 caractères, ex. « Oubli : »' },
            texte: { type: 'string', description: '≤ 38 caractères.' },
            icone: { type: 'string', enum: ['clock', 'candle', 'bread', 'gear', 'wine', 'water', 'plate', 'book', 'alert', 'check'], description: 'Pictogramme le plus proche du mémo.' },
          },
        },
      },
      illustration_principale: { type: 'string', description: 'En anglais : la scène de l\'en-tête (objets de la halakha du jour, ambiance chaude, nuit, Jérusalem floue en fond). Aucune personne, aucun texte.' },
      posts: {
        type: 'object',
        required: ['whatsapp', 'facebook', 'instagram', 'linkedin', 'x'],
        properties: {
          whatsapp: { type: 'string' },
          facebook: { type: 'string' },
          instagram: { type: 'string' },
          linkedin: { type: 'string' },
          x: { type: 'string', description: '≤ 260 caractères, lien compris.' },
        },
      },
      hashtags: { type: 'array', items: { type: 'string' } },
    },
  },
};

function writerPrompt(info, seifim, page) {
  const lot = info.lotTotal > 1 ? ` (${info.lotIndex}/${info.lotTotal})` : '';
  const total = info.totalDays ? `/${info.totalDays}` : '';
  return `Tu rédiges le post quotidien du Daat Yomi de DAAT (daattorah.com), l'étude quotidienne des lois de Chabbat du Choul'han Aroukh, pour un public francophone.

DONNÉES DU JOUR (à reprendre telles quelles, ne jamais les recalculer) :
- ${info.jourSemaine} ${info.dateCourte} · Semaine ${info.semaine} · Jour ${info.dayNumber}${total}
- Siman ${info.siman.num} · ${info.siman.numHe} — ${info.siman.titleHe}
- Séifim ${info.seifRange[0]}–${info.seifRange[1]}${lot}
- Lien d'étude : ${info.studyUrl}

TEXTE EXACT DES SÉIFIM DU JOUR (Sefaria). La glose du Rama commence par « הגה » ; tout le reste est le Mehaber.
${seifim.map((s) => `[séif ${s.n} · ${s.lettre}] ${s.he}`).join('\n')}

PAGE D'ÉTUDE DU SITE (niveau 1, traduction et explications du Rav ; ne traite QUE les séifim ${info.seifRange[0]} à ${info.seifRange[1]}) :
<<<
${page}
>>>

RÈGLES DE FOND — non négociables :
1. N'écris que ce que dit le texte source ci-dessus. Aucune halakha ajoutée, aucun commentaire (Michna Beroura, etc.) sauf s'il figure dans la page du site.
2. Attribution exacte : n'attribue au Rama que ce qui suit « הגה ». « יש אומרים / יש מי שאומר » = « une opinion » / « certains disent », jamais « le Rama ».
3. Ne tranche pas là où le texte rapporte une discussion : présente les opinions.
4. Termes en translittération usuelle (Havdala, berakha, melakha, Birkat Hamazon, bessamim…). Hébreu seulement s'il est cité mot pour mot du texte source.
5. Pas de psak personnel. Termine WhatsApp, Facebook et LinkedIn par : « Pour la pratique, consulte ton Rav. »

FORME :
- Visuel : titre ≤ 45 car., sous-titre ≤ 55, une carte par séif (titre ≤ 40, 1-2 phrases ≤ 110 car., un ou deux mots-clés en **gras** par phrase), 3-4 mémos « À retenir » très courts, chacun avec son pictogramme.
- WhatsApp : en-tête « 📖 DAAT YOMI — JOUR ${info.dayNumber}${total} », date, semaine, siman, séifim, titre en capitales ; puis un bloc par séif numéroté en émoji (${info.seifRange[0]}️⃣…) avec un titre-question et des phrases courtes ; « 💡 À RETENIR » ; lien d'étude.
- Facebook : un paragraphe d'accroche (question), l'essentiel en prose, le lien.
- Instagram : lignes courtes, émojis sobres, le lien (sera dans la bio aussi).
- LinkedIn : ton posé, 3 paragraphes, le lien.
- X : ≤ 260 caractères, lien compris.
- Hashtags : 8 à 12, sans espaces, dont #DaatYomi et #DaatTorah.
- Illustrations : décris des objets réels (coupe de kiddouch en argent, bougie de Havdala tressée, boîte à bessamim, hallot, siddour fermé, horloge…) en situation, photographie chaleureuse, fond sombre bleu nuit et doré. Jamais de personne, jamais de texte ni de lettre, jamais de scène qui contredirait la halakha du jour.

Réponds uniquement en appelant l'outil post_du_jour.`;
}

async function callClaude(params) {
  const client = new Anthropic();
  let lastErr;
  for (const model of MODELS) {
    try {
      const res = await client.messages.create({ ...params, model });
      return { res, model };
    } catch (e) {
      lastErr = e;
      const notFound = e?.status === 404 || /model/i.test(String(e?.message || ''));
      if (!notFound) throw e;
    }
  }
  throw lastErr;
}

function toolInput(res, name) {
  const block = (res.content || []).find((b) => b.type === 'tool_use' && b.name === name);
  if (!block) throw new Error(`réponse sans appel à l'outil ${name}`);
  return block.input;
}

export async function writePost(date) {
  const info = dayInfo(date);
  if (!info) return null;
  const [seifim, page] = await Promise.all([
    fetchSeifim(info.siman.num, info.seifRange[0], info.seifRange[1]),
    fetchStudyPage(info.siman.num),
  ]);
  const { res, model } = await callClaude({
    max_tokens: 6000,
    tools: [POST_TOOL],
    tool_choice: { type: 'tool', name: 'post_du_jour' },
    messages: [{ role: 'user', content: writerPrompt(info, seifim, page) }],
  });
  const post = toolInput(res, 'post_du_jour');
  const record = { info, seifim, post, model, usage: res.usage, createdAt: new Date().toISOString() };
  await kv.set(`dailypost:${date}`, record, { ex: TTL });
  await kv.del(`dailypost:${date}:verify`);
  await logEvent({ date, event: 'rédigé', model, usage: res.usage });
  return record;
}

// ---------- vérification (Claude contre la source) ----------

const VERIFY_TOOL = {
  name: 'verdict',
  description: 'Verdict de fidélité du post au texte source.',
  input_schema: {
    type: 'object',
    required: ['global', 'points'],
    properties: {
      global: { type: 'string', enum: ['vert', 'orange', 'rouge'], description: 'vert : tout est fidèle. orange : imprécisions sans erreur de fond. rouge : au moins une affirmation fausse ou mal attribuée.' },
      points: {
        type: 'array',
        description: 'Chaque affirmation qui n\'est PAS pleinement conforme. Liste vide si tout est conforme.',
        items: {
          type: 'object',
          required: ['ou', 'affirmation', 'statut', 'explication'],
          properties: {
            ou: { type: 'string', description: 'visuel · séif N, ou le nom du réseau' },
            affirmation: { type: 'string' },
            statut: { type: 'string', enum: ['imprécis', 'faux', 'mal attribué'] },
            explication: { type: 'string', description: 'Ce que dit réellement le texte, en une ou deux phrases.' },
          },
        },
      },
      nb_affirmations_verifiees: { type: 'integer' },
    },
  },
};

export async function verifyPost(date) {
  const rec = await kv.get(`dailypost:${date}`);
  if (!rec) return null;
  const prompt = `Tu es le relecteur halakhique de DAAT. Confronte CHAQUE affirmation du post ci-dessous au texte exact du Choul'han Aroukh. La glose du Rama commence par « הגה » ; tout le reste est le Mehaber ; « יש אומרים » n'est pas le Rama.

TEXTE SOURCE :
${rec.seifim.map((s) => `[séif ${s.n}] ${s.he}`).join('\n')}

POST À VÉRIFIER (JSON) :
${JSON.stringify(rec.post, null, 1)}

Signale : toute affirmation absente du texte, toute attribution fausse (Rama / Mehaber / opinion), tout psak que le texte ne donne pas, toute inversion d'une condition. Ne signale pas le style ni les simplifications fidèles. Réponds uniquement en appelant l'outil verdict.`;
  const { res, model } = await callClaude({
    max_tokens: 3000,
    tools: [VERIFY_TOOL],
    tool_choice: { type: 'tool', name: 'verdict' },
    messages: [{ role: 'user', content: prompt }],
  });
  const verdict = { ...toolInput(res, 'verdict'), model, usage: res.usage, at: new Date().toISOString() };
  await kv.set(`dailypost:${date}:verify`, verdict, { ex: TTL });
  await logEvent({ date, event: `vérifié : ${verdict.global}`, model, usage: res.usage });
  return verdict;
}

// ---------- illustrations (OpenAI, sans texte) ----------

const STYLE = 'Photorealistic editorial still life, warm candlelight, deep navy blue and gold palette, shallow depth of field, elegant and serene. Absolutely no text, no letters, no writing, no Hebrew characters, no logos, no people, no hands.';

export function imageSlots(rec) {
  const slots = [{ slot: 'hero', size: '1536x1024', quality: env('DAILY_POST_HERO_QUALITY') || 'medium', prompt: rec.post.illustration_principale }];
  for (const s of rec.post.seifim || []) {
    slots.push({ slot: `s${s.n}`, size: '1024x1024', quality: env('DAILY_POST_THUMB_QUALITY') || 'low', prompt: s.illustration });
  }
  return slots;
}

export async function generateImage(date, slot, { force = false } = {}) {
  const key = `dailypost:${date}:img:${slot}`;
  if (!force) {
    const cached = await kv.get(key);
    if (cached) return cached;
  }
  const rec = await kv.get(`dailypost:${date}`);
  if (!rec) throw new Error('post introuvable');
  const def = imageSlots(rec).find((s) => s.slot === slot);
  if (!def) throw new Error(`illustration inconnue : ${slot}`);
  const apiKey = env('OPENAI_API_KEY');
  if (!apiKey) return null; // pas de clé : le visuel utilise un fond sobre
  const r = await fetch('https://api.openai.com/v1/images/generations', {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: env('OPENAI_IMAGE_MODEL') || 'gpt-image-1',
      prompt: `${def.prompt}. ${STYLE}`,
      size: def.size,
      quality: def.quality,
      output_format: 'jpeg',
      output_compression: 72,
      n: 1,
    }),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d?.error?.message || `OpenAI HTTP ${r.status}`);
  const b64 = d?.data?.[0]?.b64_json;
  if (!b64) throw new Error('OpenAI : image absente de la réponse');
  const dataUrl = `data:image/jpeg;base64,${b64}`;
  await kv.set(key, dataUrl, { ex: TTL });
  await logEvent({ date, event: `image ${slot}`, quality: def.quality, size: def.size });
  return dataUrl;
}

export async function generateAllImages(date) {
  const rec = await kv.get(`dailypost:${date}`);
  if (!rec || !env('OPENAI_API_KEY')) return [];
  const results = await Promise.allSettled(imageSlots(rec).map((s) => generateImage(date, s.slot)));
  return results.map((r, i) => ({ slot: imageSlots(rec)[i].slot, ok: r.status === 'fulfilled' && !!r.value, error: r.reason?.message }));
}

// ---------- email de validation ----------

export function reviewUrl(date) {
  return `${SITE}/api/daily-post?action=review&date=${date}&t=${tokenFor(date)}`;
}

function esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export async function sendReviewEmail(date) {
  const rec = await kv.get(`dailypost:${date}`);
  if (!rec) return { ok: false, error: 'post introuvable' };
  const verdict = await kv.get(`dailypost:${date}:verify`);
  const to = env('DAILY_POST_EMAIL') || env('ADMIN_EMAIL');
  if (!to || !env('RESEND_API_KEY')) return { ok: false, error: 'destinataire ou RESEND_API_KEY absent' };
  const { info, post } = rec;
  const flag = verdict?.global === 'rouge' ? '⛔ À corriger' : verdict?.global === 'orange' ? '⚠️ À relire' : verdict?.global === 'vert' ? '✅ Vérifié' : '⏳ Vérification en cours';
  const url = reviewUrl(date);
  const html = `<div style="font-family:Georgia,serif;background:#FAF6EE;padding:24px;color:#1A1F3A">
<div style="max-width:560px;margin:auto;background:#fff;border:1px solid #E6DDC9;border-radius:10px;padding:26px">
<p style="margin:0 0 4px;color:#A8883E;font:600 12px Arial;letter-spacing:.14em">DAAT YOMI · JOUR ${info.dayNumber}${info.totalDays ? '/' + info.totalDays : ''} · ${esc(info.dateFr.toUpperCase())}</p>
<h1 style="margin:0 0 6px;font-size:24px">${esc(post.titre)}</h1>
<p style="margin:0 0 14px;color:#5B6078">Siman ${info.siman.num} · ${esc(info.siman.numHe)} · séifim ${info.seifRange[0]}–${info.seifRange[1]}</p>
<p style="margin:0 0 16px;font:600 14px Arial">${flag}${verdict?.points?.length ? ` — ${verdict.points.length} point(s) signalé(s)` : ''}</p>
<ol style="margin:0 0 20px;padding-left:20px;font:15px/1.5 Arial">${post.seifim.map((s) => `<li value="${s.n}"><strong>${esc(s.titre)}</strong></li>`).join('')}</ol>
<p style="text-align:center;margin:0 0 20px"><a href="${url}" style="display:inline-block;background:#C5A55A;color:#1A1F3A;text-decoration:none;font:700 16px Arial;padding:14px 26px;border-radius:8px">Voir le visuel et publier</a></p>
<p style="font:13px/1.5 Arial;color:#5B6078;margin:0">Rien n'est publié tant que tu n'as pas cliqué sur « Publier partout » dans la page. Le texte WhatsApp et l'image à partager s'y trouvent aussi.</p>
</div></div>`;
  const resend = new Resend(env('RESEND_API_KEY'));
  const from = env('RESEND_FROM_EMAIL') || 'noreply@daattorah.com';
  const r = await resend.emails.send({
    from: `DAAT <${from}>`,
    to,
    subject: `${flag} · Daat Yomi du ${info.dateCourte} — ${post.titre}`,
    html,
  });
  if (r.error) return { ok: false, error: r.error.message || String(r.error) };
  await logEvent({ date, event: 'email envoyé' });
  return { ok: true, id: r.data?.id };
}

// ---------- journal ----------

export async function logEvent(e) {
  try {
    await kv.lpush('dailypost:log', JSON.stringify({ at: new Date().toISOString(), ...e }));
    await kv.ltrim('dailypost:log', 0, 29);
  } catch { /* journal best effort */ }
}
