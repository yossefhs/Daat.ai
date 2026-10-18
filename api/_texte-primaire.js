// Texte primaire OBLIGATOIRE avant une analyse de niveau lamdan sur un siman nommé.
//
// Constat (18 octobre 2026, siman 253 / רנ״ג). À un lamdan 'Habad qui demandait
// « un résumé clair avec l'idée des opinions », le chat a inversé l'ORDRE des
// opinions du Mehaber en 253:1 (il ouvre par Rif/Rambam, stricts ; la lénienté
// « מאכל בן דרוסאי » vient ensuite en יש אומרים), écrit « תישוי » pour חיתוי avec
// une étymologie inventée, prêté au séif י״ד une raison (« bâtir le foyer ») qui
// n'y est pas, et coupé la réserve du séif כ״ט (« ואם הישראל חפץ באותן המים… אסור »).
//
// Cause, vérifiée : le chemin agentique a lu la rubrique Daat HaRav du site —
// 29 extraits sur le 253, UN seul en hébreu — c'est-à-dire des traductions. Il a
// raisonné sur elles, puis RECONSTRUIT l'hébreu de mémoire pour faire lamdan. Une
// seule lecture du Mehaber sur Sefaria aurait suffi ; il ne l'a pas faite, parce
// que le site lui paraissait suffisant. Le prompt interdit déjà « pas d'hébreu
// cité sans texte ouvert » ; une consigne ne tient pas quand le modèle croit
// avoir lu. Ici, le serveur lit à sa place : le texte du Mehaber est chargé et
// placé dans la conversation AVANT que le modèle n'écrive un mot. Ce n'est pas
// une consigne, c'est un fait de contexte.
//
// Périmètre volontairement étroit — ce que le Rav a demandé (« point 1 ») :
//   niveau déclaré Lamdan / Talmid Hakham  ET  un siman nommé dans la question
//   (en chiffres ou en lettres hébraïques), dans la partie nommée ou, à défaut,
//   celle de la requête.
// Un visiteur sans profil ou d'un autre niveau n'est pas concerné : le coût est
// nul pour lui. Élargir à toute question sur un siman nommé tient en une ligne
// (demandeLamdan → true) ; mesurer d'abord.
//
// Deux limites, assumées :
//  - le texte est plafonné (MAX_PRIMAIRE) : sur un siman hors norme, le début du
//    Mehaber est garanti, la fin ne l'est pas — le bloc le dit et renvoie le modèle
//    aux séifim suivants ;
//  - seul le Mehaber est chargé d'office. Le Choul'han Aroukh HaRav (29 séifim sur
//    le 253) dépasserait la troncature ; le bloc impose de l'ouvrir séif par séif
//    avant de le citer.

// ── Point 1b (18/10/2026) : le Beit Yossef, parce que le Mehaber ne nomme personne ──
// Banc de 14 réponses réelles après le point 1 : ordre, mots, séifim du Mehaber
// désormais justes — mais 5 réponses sur 7 sur le 253 attribuaient de MÉMOIRE :
// Rambam et Rif rangés côté indulgent alors qu'ils sont stricts (Hil. Shabbat 3:4 ;
// Beit Yossef 253), « R. Yehuda » inventé pour l'opinion stricte. Le Mehaber écrit
// « יש אומרים » ; les noms sont dans le Beit Yossef, que le modèle n'a ouvert dans
// aucun cas. Quand la question demande les opinions (ou nomme un Richon), le
// serveur charge aussi le DÉBUT du Beit Yossef du siman. Sur Sefaria ses
// paragraphes suivent le Tour, pas les séifim du Choul'han Aroukh (253 : 22
// paragraphes, le premier — 5 197 caractères — porte toute la sougya de la שהייה),
// et aucun lien ne les rattache aux séifim : on charge le début jusqu'au plafond,
// coupé à une frontière de paragraphe, et on dit comment ouvrir la suite.

import { namedSimanInQuestion } from './_corpus-search.js';
import { fetchSefariaText, fetchSefariaSegments } from './_sefaria.js';

// Plafond du texte chargé d'office. Mesuré le 18/10/2026 sur le Mehaber d'Orah
// Haïm : 253 → 5 451 caractères, 328 → 8 018, 301 (51 séifim, le plus long de
// Hilkhot Shabbat) → 11 032. À 12 000, aucun siman de Shabbat n'est coupé ; les
// 4 000 de sefaria_get_text (pensés pour un résultat d'outil) auraient tronqué
// le 253 au milieu du séif 4. Au-delà, le bloc l'annonce et renvoie aux séifim.
const MAX_PRIMAIRE = 12000;

// Plafond du Beit Yossef chargé d'office (≈ 3 000 à 4 000 jetons) : 253 → les 7
// premiers paragraphes (7 364 car.) ; Yoreh De'ah 100 → les 7 en entier (5 377).
const MAX_BEIT_YOSEF = 8000;

// La question demande-t-elle « qui tient quoi » ? Mots des trois langues du site ;
// un faux positif coûte un chargement, un faux négatif laisse le modèle attribuer
// de mémoire — le motif est donc large.
const OPINIONS_RE = /\b(?:opinions?|avis|positions?|shit[ao]t?|chit[ao]t?|ma[’'h]?[hḥ]?loket|machloket|mahloket|divergences?|d[ée]saccord|richonim|rishonim|a[’'h]?[hḥ]aronim|rambam|rif|ro?sh|ran|rachi|rashi|toss?afot|rabb?[ée]i?nou\s+tam|rabbeinu\s+tam|ra[cs]hba|beit\s+yoss?ef|tour|qui\s+(?:dit|soutient|tient|tranche|pense)|selon\s+(?:qui|quel)|views?|dispute|who\s+(?:holds|says|rules|maintains))\b|דעות|דעת ה|שיטות|שיטת|מחלוקת|מי סובר|מאן דאמר|ראשונים|אחרונים|רמב[״"]ם|רי[״"]ף|רא[״"]ש|ר[״"]ן|רש[״"]י|תוספות|ר[״"]ת|בית יוסף|הטור|רשב[״"]א/i;
export function demandeOpinions(texte) {
  return OPINIONS_RE.test(String(texte || ''));
}

export function refBeitYosef(siman, partie) {
  const n = parseInt(siman, 10);
  if (!Number.isFinite(n) || n < 1) return null;
  return partie === 'yoreh-deah' ? `Beit_Yosef,_Yoreh_De'ah.${n}` : `Beit_Yosef,_Orach_Chayim.${n}`;
}

// Libellés réellement émis par les quatre clients du site :
//   widget (assets/js/chat-widget.js)  « • Niveau : Lamdan / Talmid Hakham — pilpoul approfondi »
//   chat.html                           « - Niveau : Lamdan »
//   chat-en.html                        « - Level: Lamdan »
//   chat-he.html                        « - רמה: Lamdan »  (ou « למדן / תלמיד חכם » si la valeur
//                                       localisée est un jour envoyée)
// Relecture Codex du 18/10 : la première version n'acceptait que « niveau », donc
// aucun lamdan des chats anglais et hébreu n'était couvert.
const LAMDAN_RE = /(?:niveau|level|רמה)\s*:[^\n]*?(?:lamdan|talmid\s*(?:[ḥh]akham|chacham)|למדן|תלמיד\s*חכם)/i;

export function demandeLamdan(texte) {
  return LAMDAN_RE.test(String(texte || ''));
}

// ── Numéro de siman en lettres hébraïques ─────────────────────────────────────
// Les questions rapides des pages de chat disent « Siman רמ״ב », un lamdan écrit
// « סימן ש״א » ou « סי' ק׳ » ; namedSimanInQuestion ne lit que des chiffres.
// On exige la ponctuation d'usage (״ ou " avant la dernière lettre ; ׳ ou ' après
// une lettre seule) : sans elle, « סימן זה » vaudrait 12.
const GEMATRIA = { א: 1, ב: 2, ג: 3, ד: 4, ה: 5, ו: 6, ז: 7, ח: 8, ט: 9, י: 10, כ: 20, ך: 20, ל: 30, מ: 40, ם: 40, נ: 50, ן: 50, ס: 60, ע: 70, פ: 80, ף: 80, צ: 90, ץ: 90, ק: 100, ר: 200, ש: 300, ת: 400 };
export function gematriaVersNombre(s) {
  const lettres = String(s || '').replace(/[״"׳'\s]/g, '');
  if (!lettres || !/^[א-ת]+$/.test(lettres)) return null;
  let n = 0;
  for (const c of lettres) n += GEMATRIA[c] || 0;
  return n >= 1 && n <= 1714 ? n : null;
}
const SIMAN_HE_RE = /(?:\bsimane?\b|סימן|סי['׳])\s*((?:[א-ת]{1,3}[״"][א-ת])|(?:[א-ת][׳']))(?![א-ת])/i;

// Le siman nommé dans un texte : chiffres (namedSimanInQuestion) ou lettres.
export function simanNomme(texte) {
  const t = String(texte || '');
  const n = namedSimanInQuestion(t);
  if (n != null) return n;
  const m = t.match(SIMAN_HE_RE);
  return m ? gematriaVersNombre(m[1]) : null;
}

// ── Partie du Choul'han Aroukh nommée dans un texte ───────────────────────────
// chat.html / chat-en.html / chat-he.html envoient section = 'orach-chaim' par
// défaut (URLSearchParams … || 'orach-chaim'). Un lecteur qui demande « le siman
// 100 de Yoreh De'ah » depuis la page générale recevrait donc Orah Haïm 100,
// étiqueté texte primaire — un faux texte avec autorité. La partie NOMMÉE dans
// la question prime sur la section de la requête ; une autre partie (Even
// HaEzer, Hoshen Michpat) interdit l'injection, le site ne les couvre pas.
const PARTIES = [
  ['yoreh-deah',  /yor[eé]h?\s*d[eé][’'`]?ah|יורה\s*דעה|יו[״"]ד/i],
  ['orach-chaim', /ora[hḥ]?\s*[hḥ]a[iïy]{1,2}m|orach\s*cha[iy]{1,2}m|אורח\s*חיים|או[״"]ח/i],
  ['autre',       /even\s*ha[’'`]?ezer|אבן\s*העזר|אה[״"]ע|[ck]?[hḥ]oshen\s*mishpat|חושן\s*משפט|חו[״"]מ/i],
];
export function partieNommee(texte) {
  const t = String(texte || '');
  let meilleur = null;
  for (const [partie, re] of PARTIES) {
    const m = t.match(re);
    if (m && (meilleur === null || m.index < meilleur.index)) meilleur = { partie, index: m.index };
  }
  return meilleur ? meilleur.partie : null;
}

// Dernier siman de chaque partie (Choul'han Aroukh) : au-delà, rien à charger.
const DERNIER_SIMAN = { 'orach-chaim': 697, 'yoreh-deah': 403 };

// La partie « question » d'un message : les clients préfixent le profil et le
// séparent de la question par un marqueur ; sans marqueur, tout le message.
const MARQUEURS_QUESTION = /\[Ma question\]|\[My question\]|\[השאלה שלי\]/i;
function partieQuestion(question) {
  return String(question || '').split(MARQUEURS_QUESTION).pop();
}

// La CIBLE, sans réseau : { siman, partie, ref } ou null. Sert aussi au routage
// dans chat.js (une question lamdan sur un siman nommé ne doit jamais prendre le
// chemin court corpus-first, où ce texte n'existe pas — relecture Codex du 18/10).
export function cibleTextePrimaire({ messagesUtilisateur = [], question = '', section = 'orach-chaim' } = {}) {
  const profil = [...messagesUtilisateur, question].join('\n');
  if (!demandeLamdan(profil)) return null;
  const q = partieQuestion(question);
  // Le siman de la question prime sur celui de la ligne « je consulte actuellement
  // le Siman N » que le widget préfixe à chaque message (la page ouverte).
  const siman = simanNomme(q) ?? simanNomme(question);
  if (siman == null) return null;
  const partie = partieNommee(q) ?? partieNommee(question) ?? section;
  if (!(partie in DERNIER_SIMAN) || siman > DERNIER_SIMAN[partie]) return null;
  const ref = refMehaber(siman, partie);
  if (!ref) return null;
  const beitYosef = demandeOpinions(q) ? refBeitYosef(siman, partie) : null;
  return { siman, partie, ref, beitYosef };
}

// Le bloc Beit Yossef : paragraphes entiers jusqu'au plafond, et la suite indiquée.
export function blocBeitYosef(ref, segments, siman, partie) {
  const nomPartie = partie === 'yoreh-deah' ? "Yoreh De'ah" : 'Orah Haïm';
  const paragraphes = (Array.isArray(segments) ? segments : String(segments || '').split(/\n+/)).map((x) => String(x).trim()).filter(Boolean);
  const hebrew = paragraphes.join('\n');
  const gardes = [];
  let total = 0;
  for (const par of paragraphes) {
    if (gardes.length && total + par.length > MAX_BEIT_YOSEF) break;
    gardes.push(par.length > MAX_BEIT_YOSEF ? par.slice(0, MAX_BEIT_YOSEF) + ' […]' : par);
    total += par.length;
    if (total >= MAX_BEIT_YOSEF) break;
  }
  const k = gardes.length, K = paragraphes.length;
  const etendue = K > 1
    ? (k < K ? `(paragraphes 1-${k} sur ${K} ; les suivants : sefaria_get_text, ref ${ref}.${k + 1}-${K})` : `(les ${K} paragraphes)`)
    : (hebrew.length > MAX_BEIT_YOSEF ? `(début, tronqué à ${MAX_BEIT_YOSEF} caractères ; la suite : sefaria_get_text, ref ${ref})` : '');
  return [
    '',
    '---',
    '[Beit Yossef chargé par le serveur — même règle : tu n\'as pas à le redemander]',
    `Beit Yossef, ${nomPartie}, siman ${siman} · réf. Sefaria ${ref} · https://www.sefaria.org/${ref}`,
    etendue,
    '',
    gardes.join('\n\n'),
    '',
    'C\'est ICI que sont les noms. Toute attribution d\'une opinion à un Richon ou à un décisionnaire (Rif, Rambam, Roch, Ran, Rachi, Tossafot, Rabbénou Tam, Rachba, Tour…) doit s\'appuyer sur ce texte ou sur un texte que tu as ouvert avec sefaria_get_text ; un nom que ces textes ne portent pas sur ce point n\'a pas sa place dans ta réponse — écris alors « יש אומרים », comme le Mehaber.',
    '---',
  ].filter((l, i, a) => !(l === '' && a[i - 1] === '')).join('\n');
}

// Référence Sefaria du Mehaber pour un siman, selon la partie du Choul'han Aroukh.
// Format URL attendu par sefaria_get_text (underscores, virgule, point).
export function refMehaber(siman, section) {
  const n = parseInt(siman, 10);
  if (!Number.isFinite(n) || n < 1) return null;
  return section === 'yoreh-deah'
    ? `Shulchan_Arukh,_Yoreh_De'ah.${n}`
    : `Shulchan_Arukh,_Orach_Chayim.${n}`;
}

// Le bloc ajouté au dernier message de l'utilisateur. Étiqueté comme venant du
// SERVEUR : le modèle ne doit pas croire que l'utilisateur l'a collé, ni le
// redemander. Hébreu seul (le lamdan le lit ; l'anglais doublerait le coût).
export function blocTextePrimaire(ref, d, section) {
  const partie = section === 'yoreh-deah' ? "Yoreh De'ah" : 'Orah Haïm';
  const lignes = [
    '',
    '---',
    '[Texte primaire chargé par le serveur avant ta réponse — tu n\'as pas à le redemander]',
    `Choul'han Aroukh (Mehaber), ${partie}, siman ${d.siman} · réf. Sefaria ${ref}` + (d.url ? ` · ${d.url}` : ''),
    '',
    d.hebrew,
    '',
  ];
  if (d.truncated) {
    lignes.push(`(Texte tronqué à ${MAX_PRIMAIRE} caractères : les séifim suivants sont à ouvrir avec sefaria_get_text, ref ${ref}.<séif>.)`);
  }
  lignes.push(
    'Pour toute citation ou attribution sur ce siman — ordre des opinions, conditions, mots exacts — appuie-toi sur CE texte, pas sur ta mémoire ni sur une traduction du site. ' +
    (section === 'yoreh-deah'
      ? 'Les commentateurs (Chakh, Taz) et le Choul\'han Aroukh HaRav sur la niddah sont à ouvrir avec sefaria_get_text avant d\'être cités.'
      : `Le Choul'han Aroukh HaRav est à ouvrir séif par séif avec sefaria_get_text (Shulchan_Arukh_HaRav,_Orach_Chayim.${d.siman}.<séif>) avant d'être cité.`),
    '---',
  );
  return lignes.join('\n');
}

// Charge le texte, ou rend null — JAMAIS d'exception : un échec de Sefaria ne doit
// pas priver l'utilisateur de réponse, il le prive seulement de ce filet.
export async function chargerTextePrimaire({ messagesUtilisateur = [], question = '', section = 'orach-chaim', urgent = false } = {}) {
  if (urgent) return null;                                   // le danger vital court-circuite tout
  const cible = cibleTextePrimaire({ messagesUtilisateur, question, section });
  if (!cible) return null;
  const { siman, partie, ref, beitYosef } = cible;
  try {
    // Les deux lectures partent ensemble : le Beit Yossef n'ajoute pas de latence.
    const [d, b] = await Promise.all([
      fetchSefariaText(ref),
      beitYosef ? fetchSefariaSegments(beitYosef).catch(() => null) : Promise.resolve(null),
    ]);
    if (!d || d.error || !d.hebrew || !String(d.hebrew).trim()) return null;
    const hebrew = String(d.hebrew);
    let texte = blocTextePrimaire(ref, {
      siman,
      hebrew: hebrew.slice(0, MAX_PRIMAIRE),
      truncated: hebrew.length > MAX_PRIMAIRE,
      url: 'https://www.sefaria.org/' + ref,
    }, partie);
    const complements = [];
    if (beitYosef && b && !b.error && Array.isArray(b.segments) && b.segments.length) {
      texte += '\n' + blocBeitYosef(beitYosef, b.segments, siman, partie);
      complements.push({ ref: beitYosef, type: 'beit-yosef' });
    }
    return { siman, partie, ref, texte, complements };
  } catch {
    return null;
  }
}
