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
//   niveau déclaré Lamdan / Talmid Hakham  ET  un siman nommé dans la question.
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

import { namedSimanInQuestion } from './_corpus-search.js';
import { fetchSefariaText } from './_sefaria.js';

// Plafond du texte chargé d'office. Mesuré le 18/10/2026 sur le Mehaber d'Orah
// Haïm : 253 → 5 451 caractères, 328 → 8 018, 301 (51 séifim, le plus long de
// Hilkhot Shabbat) → 11 032. À 12 000, aucun siman de Shabbat n'est coupé ; les
// 4 000 de sefaria_get_text (pensés pour un résultat d'outil) auraient tronqué
// le 253 au milieu du séif 4. Au-delà, le bloc l'annonce et renvoie aux séifim.
const MAX_PRIMAIRE = 12000;

// Libellés réellement envoyés par le widget (assets/js/chat-widget.js) :
// « • Niveau : Lamdan / Talmid Hakham — pilpoul approfondi ». On accepte aussi
// la forme sans puce, et « Talmid Hakham » seul.
const LAMDAN_RE = /niveau\s*:[^\n]*?(?:lamdan|talmid\s*(?:[ḥh]akham|chacham))/i;

export function demandeLamdan(texte) {
  return LAMDAN_RE.test(String(texte || ''));
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
  const profil = [...messagesUtilisateur, question].join('\n');
  if (!demandeLamdan(profil)) return null;
  // Le widget préfixe CHAQUE message du profil et d'une ligne « je consulte
  // actuellement le Siman N » (la page ouverte). Si la question elle-même nomme
  // un autre siman, c'est elle qui compte ; sinon la page.
  const partieQuestion = String(question).split(/\[Ma question\]/i).pop();
  const siman = namedSimanInQuestion(partieQuestion) ?? namedSimanInQuestion(question);
  if (siman == null) return null;
  const ref = refMehaber(siman, section);
  if (!ref) return null;
  try {
    const d = await fetchSefariaText(ref);
    if (!d || d.error || !d.hebrew || !String(d.hebrew).trim()) return null;
    const hebrew = String(d.hebrew);
    return {
      siman,
      ref,
      texte: blocTextePrimaire(ref, {
        siman,
        hebrew: hebrew.slice(0, MAX_PRIMAIRE),
        truncated: hebrew.length > MAX_PRIMAIRE,
        url: 'https://www.sefaria.org/' + ref,
      }, section),
    };
  } catch {
    return null;
  }
}
