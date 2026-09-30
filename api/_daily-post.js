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
import { fetchSiman, auditCalendar, checkTexts } from './_daily-post-checks.js';

export const SITE = 'https://daattorah.com';
const TTL = 10 * 24 * 3600;
const env = (k) => (process.env[k] || '').trim();

// Modèle de rédaction : le plus récent par défaut, repli sur celui déjà
// éprouvé en production par le chat si le premier n'est pas disponible.
const MODELS = [env('DAILY_POST_MODEL') || 'claude-sonnet-5-5', 'claude-sonnet-4-6'];

// ---------- dates & plan ----------

// Date civile du jour à Jérusalem (fuseau du programme d'étude).
export function studyToday() {
  return new Intl.DateTimeFormat('fr-CA', {
    timeZone: 'Asia/Jerusalem', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(new Date());
}
export const parisToday = studyToday;

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
- Séifim ${info.seifRange[0]}–${info.seifRange[1]}${lot} (le siman en compte ${info.seifimReels})
- Lien d'étude : ${info.studyUrl}

TEXTE EXACT DES SÉIFIM DU JOUR (Sefaria). La glose du Rama commence par « הגה » ; tout le reste est le Mehaber.
${seifim.map((s) => `[séif ${s.n} · ${s.lettre}] ${s.he}`).join('\n')}

PAGE D'ÉTUDE DU SITE (niveau 1, traduction et explications du Rav ; ne traite QUE les séifim ${info.seifRange[0]} à ${info.seifRange[1]}) :
<<<
${page}
>>>

RÈGLES DE FOND — non négociables :
1. N'écris que ce que dit le texte source ci-dessus. Aucune halakha ajoutée, aucun commentaire (Michna Beroura, etc.) sauf s'il figure dans la page du site. Les explications de la page sont la pédagogie de DAAT : ne les présente jamais comme le texte du Choul'han Aroukh.
2. Attribution exacte : n'attribue au Rama que ce qui suit « הגה ». « יש אומרים / יש מי שאומר » = « une opinion » / « certains disent », jamais « le Rama ».
3. Ne tranche pas là où le texte rapporte une discussion : présente les opinions. Jamais une opinion secondaire en règle unique, une mahloket en décision unanime, un minhag en obligation générale.
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

export class BlockedError extends Error {
  constructor(reasons) { super(reasons.join(' · ')); this.reasons = reasons; }
}

export async function writePost(date) {
  const info = dayInfo(date);
  if (!info) return null;
  const entry = getEntryForDate(date);

  // Verrouillage : rien n'est rédigé tant que le jour n'est pas confronté au
  // nombre réel de séifim, au reste du plan et à la page publiée.
  let simanTexte, page;
  try {
    [simanTexte, page] = await Promise.all([fetchSiman(info.siman.num), fetchStudyPage(info.siman.num)]);
  } catch (e) {
    throw new BlockedError([`Source injoignable : ${e.message}`]);
  }
  const audit = await auditCalendar(entry, simanTexte);
  if (audit.bloquant.length) {
    await kv.set(`dailypost:${date}:blocked`, { info, audit, at: new Date().toISOString() }, { ex: TTL });
    await logEvent({ date, event: 'bloqué', reasons: audit.bloquant });
    throw new BlockedError(audit.bloquant);
  }
  info.lotIndex = audit.partie.index;
  info.lotTotal = audit.partie.total;
  info.seifimReels = audit.seifimReels;
  const seifim = [];
  for (let n = info.seifRange[0]; n <= info.seifRange[1]; n++) {
    seifim.push({ n, lettre: HEB[n] || String(n), he: simanTexte[n - 1] });
  }
  const { res, model } = await callClaude({
    max_tokens: 6000,
    tools: [POST_TOOL],
    tool_choice: { type: 'tool', name: 'post_du_jour' },
    messages: [{ role: 'user', content: writerPrompt(info, seifim, page) }],
  });
  const post = toolInput(res, 'post_du_jour');
  const record = { info, seifim, post, model, usage: res.usage, anomalies: audit.avertissement, createdAt: new Date().toISOString() };
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
  // Contrôles mécaniques : jour, total, siman, séifim et lien repris à l'identique.
  const meca = checkTexts(rec.info, rec.post);
  if (meca.length) {
    verdict.points = [...meca, ...(verdict.points || [])];
    if (meca.some((m) => m.statut === 'faux')) verdict.global = 'rouge';
    else if (verdict.global === 'vert') verdict.global = 'orange';
  }
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

export async function generateImage(date, slot, { force = false, retried = false } = {}) {
  const key = `dailypost:${date}:img:${slot}`;
  if (!force) {
    const cached = await kv.get(key);
    if (cached) return cached;
  }
  const rec = await kv.get(`dailypost:${date}`);
  if (!rec) throw new Error('post introuvable');
  const def = imageSlots(rec).find((s) => s.slot === slot);
  if (!def) throw new Error(`illustration inconnue : ${slot}`);
  def.retried = retried;
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
  const controle = await inspectImage(b64, def.prompt);
  if (!controle.ok) {
    await logEvent({ date, event: `image ${slot} rejetée`, raison: controle.raison });
    if (!force && !def.retried) return generateImage(date, slot, { force: true, retried: true });
    return null; // deuxième refus : fond sobre plutôt qu'une image douteuse
  }
  await kv.set(key, dataUrl, { ex: TTL });
  await logEvent({ date, event: `image ${slot}`, quality: def.quality, size: def.size });
  return dataUrl;
}

// L'illustration contient-elle du texte, des personnes, un symbole religieux
// étranger, ou est-elle sans rapport avec le sujet ? (vision Claude, ~0,3 c).
async function inspectImage(b64, attendu) {
  try {
    const { res } = await callClaude({
      max_tokens: 300,
      tools: [{ name: 'controle', description: 'Résultat du contrôle', input_schema: { type: 'object', required: ['ok', 'raison'], properties: {
        ok: { type: 'boolean' }, raison: { type: 'string' } } } }],
      tool_choice: { type: 'tool', name: 'controle' },
      messages: [{ role: 'user', content: [
        { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: b64 } },
        { type: 'text', text: `Illustration d'un post d'étude juive (halakha de Chabbat). Attendu : ${attendu}. Refuse (ok=false) si tu vois : du texte, des lettres ou chiffres lisibles, des personnes ou des mains, une croix ou tout symbole d'une autre religion, ou une scène sans rapport avec l'attendu. Sinon ok=true.` },
      ] }],
    });
    return toolInput(res, 'controle');
  } catch (e) {
    return { ok: true, raison: `contrôle indisponible : ${e.message}` };
  }
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

// Destinataires : DAILY_POST_EMAIL (liste séparée par des virgules), sinon
// l'administrateur et la boîte de l'association.
function recipients() {
  const list = (env('DAILY_POST_EMAIL') || [env('ADMIN_EMAIL') || 'yossefhs@gmail.com', 'daattorah.com@gmail.com'].join(','))
    .split(',').map((x) => x.trim().toLowerCase()).filter(Boolean);
  return [...new Set(list)];
}

async function send(subject, html, date, label) {
  const to = recipients();
  if (!to.length || !env('RESEND_API_KEY')) {
    await logEvent({ date, event: `EMAIL NON ENVOYÉ (${label})`, error: 'destinataire ou RESEND_API_KEY absent' });
    return { ok: false, error: 'destinataire ou RESEND_API_KEY absent' };
  }
  const resend = new Resend(env('RESEND_API_KEY'));
  const from = env('RESEND_FROM_EMAIL') || 'noreply@daattorah.com';
  // Comme les emails du site qui arrivent (plan, newsletter) : UN destinataire par
  // envoi et une version texte. L'envoi groupé à deux adresses, sans texte, était
  // donné « delivered » par Resend le 30/09 et n'est arrivé dans aucune boîte.
  const text = html.replace(/<(br|\/p|\/h[12]|\/li|\/tr|\/div)[^>]*>/gi, '\n').replace(/<a [^>]*href="([^"]+)"[^>]*>([^<]*)<\/a>/gi, '$2 : $1')
    .replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\n\s*\n+/g, '\n\n').trim();
  const each = await Promise.all(to.map(async (d) => {
    try {
      const r = await resend.emails.send({ from: `DAAT <${from}>`, to: d, subject, html, text });
      // Seule la réponse de Resend (un identifiant) atteste l'envoi.
      if (r.error || !r.data?.id) return { to: d, error: r.error?.message || JSON.stringify(r.error || 'aucun identifiant renvoyé') };
      return { to: d, id: r.data.id };
    } catch (e) { return { to: d, error: e?.message || String(e) }; }
  }));
  const ok = each.filter((x) => x.id);
  if (!ok.length) {
    const error = each.map((x) => `${x.to} : ${x.error}`).join(' · ');
    await logEvent({ date, event: `EMAIL NON ENVOYÉ (${label})`, error });
    return { ok: false, error };
  }
  const id = ok.map((x) => x.id).join(',');
  const sentTo = ok.map((x) => x.to);
  await kv.set(`dailypost:${date}:emailed:${label}`, { at: new Date().toISOString(), id, to: sentTo, envois: each }, { ex: TTL });
  await logEvent({ date, event: `email ${label} envoyé`, envois: each });
  return { ok: true, id, to: sentTo, envois: each };
}

const box = (inner) => `<div style="font-family:Georgia,serif;background:#FAF6EE;padding:20px;color:#1A1F3A"><div style="max-width:640px;margin:auto;background:#fff;border:1px solid #E6DDC9;border-radius:10px;padding:24px">${inner}</div></div>`;
const h2 = (t) => `<h2 style="margin:22px 0 8px;font:700 13px Arial;letter-spacing:.14em;color:#A8883E;text-transform:uppercase">${t}</h2>`;
const pre = (t) => `<div style="white-space:pre-wrap;font:14.5px/1.55 Arial;background:#FFFDF8;border:1px solid #EFE6D2;border-radius:8px;padding:12px">${esc(t)}</div>`;

export async function sendReviewEmail(date) {
  const rec = await kv.get(`dailypost:${date}`);
  if (!rec) return { ok: false, error: 'post introuvable' };
  const verdict = await kv.get(`dailypost:${date}:verify`);
  const { info, post } = rec;
  const total = info.totalDays ? `/${info.totalDays}` : '';
  const partie = info.lotTotal > 1 ? ` (${info.lotIndex}/${info.lotTotal})` : '';
  const flag = verdict?.global === 'rouge' ? '⛔ À corriger' : verdict?.global === 'orange' ? '⚠️ À relire' : verdict?.global === 'vert' ? '✅ Vérifié' : '⏳ Vérification en cours';
  const anomalies = [...(rec.anomalies || []), ...(verdict?.points || []).map((p) => `${p.ou} · ${p.statut} — « ${p.affirmation} » : ${p.explication}`)];
  const p = post.posts || {};
  const html = box(`
<p style="margin:0 0 4px;color:#A8883E;font:600 12px Arial;letter-spacing:.14em">DAAT YOMI · ${flag}</p>
<h1 style="margin:0 0 6px;font-size:24px">${esc(post.titre)}</h1>
<p style="text-align:center;margin:18px 0"><a href="${reviewUrl(date)}" style="display:inline-block;background:#C5A55A;color:#1A1F3A;text-decoration:none;font:700 16px Arial;padding:14px 26px;border-radius:8px">Voir le visuel, corriger et publier</a></p>
${anomalies.length ? `${h2('⚠️ Anomalies détectées')}<ul style="font:14px/1.5 Arial;margin:0;padding-left:18px">${anomalies.map((a) => `<li>${esc(a)}</li>`).join('')}</ul>` : ''}
${h2('1. Données vérifiées')}
<table style="font:14px/1.6 Arial;border-collapse:collapse">
<tr><td style="padding-right:14px;color:#5B6078">Date</td><td>${esc(info.dateFr)}</td></tr>
<tr><td style="padding-right:14px;color:#5B6078">Semaine</td><td>${info.semaine}</td></tr>
<tr><td style="padding-right:14px;color:#5B6078">Jour</td><td>${info.dayNumber}${total}</td></tr>
<tr><td style="padding-right:14px;color:#5B6078">Siman</td><td>${info.siman.num} · ${esc(info.siman.numHe)} — ${esc(info.siman.titleHe)}</td></tr>
<tr><td style="padding-right:14px;color:#5B6078">Séifim</td><td>${info.seifRange[0]}–${info.seifRange[1]}${partie} · le siman en compte ${info.seifimReels} (Sefaria)</td></tr>
<tr><td style="padding-right:14px;color:#5B6078">Vérification</td><td>${flag}${verdict?.nb_affirmations_verifiees ? ` · ${verdict.nb_affirmations_verifiees} affirmations confrontées au Choul'han Aroukh` : ''}</td></tr>
</table>
${h2('2. WhatsApp')}${pre(p.whatsapp)}
${h2('3. Facebook')}${pre(p.facebook)}
${h2('4. Instagram')}${pre(p.instagram)}
${h2('5. LinkedIn')}${pre(p.linkedin)}
${h2('6. X')}${pre(p.x)}
${h2('7. Hashtags')}${pre((post.hashtags || []).join(' '))}
${h2('8. Lien de l\'étude')}<p style="font:14px Arial"><a href="${info.studyUrl}">${info.studyUrl}</a></p>
<p style="font:13px/1.5 Arial;color:#5B6078;margin-top:20px">Rien n'est publié tant que tu n'as pas cliqué sur « Publier partout » dans la page. Le visuel se télécharge et se partage sur WhatsApp depuis la même page.</p>`);
  return send(`Daat Yomi — ${info.dateCourte} — Jour ${info.dayNumber}${total} — Siman ${info.siman.num} · ${flag}`, html, date, 'pack');
}

// Blocage : aucun pack, seulement l'explication de ce qui n'a pas pu être vérifié.
// Email minimal, envoyé EN PLUS de l'email complet : quelques lignes et un lien
// court. Le 30/09, l'email complet a été donné « delivered » par Resend sans
// jamais paraître dans Gmail, quand les codes de connexion du même expéditeur
// arrivent en secondes : celui-ci dit, par comparaison, si c'est le contenu.
export function shortReviewUrl(date) {
  return `${SITE}/valider/${date}/${tokenFor(date)}`;
}

export async function sendLinkEmail(date) {
  const rec = await kv.get(`dailypost:${date}`);
  if (!rec) return { ok: false, error: 'post introuvable' };
  const { info } = rec;
  const url = shortReviewUrl(date);
  const total = info.totalDays ? `/${info.totalDays}` : '';
  const html = `<p>Bonjour,</p><p>Le post Daat Yomi du ${esc(info.dateFr)} est prêt : jour ${info.dayNumber}${total}, siman ${info.siman.num}.</p><p><a href="${url}">Ouvrir le post</a></p><p>${url}</p>`;
  return send(`Daat Yomi ${info.dateCourte} : le post du jour est prêt`, html, date, 'lien');
}

export async function sendBlockedEmail(date, reasons) {
  const info = dayInfo(date);
  const titre = info ? `Jour ${info.dayNumber}${info.totalDays ? '/' + info.totalDays : ''} — Siman ${info.siman.num} — séifim ${info.seifRange[0]}–${info.seifRange[1]}` : date;
  const html = box(`
<p style="margin:0 0 4px;color:#9B2F2F;font:700 12px Arial;letter-spacing:.14em">DAAT YOMI · PACK NON PRÉPARÉ</p>
<h1 style="margin:0 0 10px;font-size:22px">${esc(titre)}</h1>
<p style="font:15px/1.55 Arial">Le post du jour n'a pas été rédigé : une donnée essentielle n'a pas pu être vérifiée. Rien n'a été inventé et rien ne sera publié.</p>
${h2('Ce qui bloque')}<ul style="font:14px/1.55 Arial;padding-left:18px">${reasons.map((r) => `<li>${esc(r)}</li>`).join('')}</ul>
<p style="font:13px/1.5 Arial;color:#5B6078">Après correction, relancer : <code>/api/daily-post?date=${date}&amp;force=1</code> (avec le CRON_SECRET).</p>`);
  return send(`Daat Yomi — ${info?.dateCourte || date} — PACK NON PRÉPARÉ ⛔`, html, date, 'd\'anomalie');
}

// ---------- journal ----------

export async function logEvent(e) {
  // Aussi dans les logs Vercel : le journal KV n'est lisible qu'avec le secret.
  console.log('[daily-post]', JSON.stringify(e).slice(0, 1500));
  try {
    await kv.lpush('dailypost:log', JSON.stringify({ at: new Date().toISOString(), ...e }));
    await kv.ltrim('dailypost:log', 0, 29);
  } catch { /* journal best effort */ }
}
