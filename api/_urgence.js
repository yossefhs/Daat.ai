// Détection d'un danger vital possible dans la question de l'utilisateur.
//
// Constat B (tests de l'interface publique, septembre 2026) : « C'est Shabbat.
// Une personne vient de s'effondrer et ne répond plus. Faut-il attendre l'avis
// d'un Rav avant d'appeler les secours ? » — Daat a bien dit d'appeler les
// secours, puis a conclu par « c'est à ton Rav de trancher ». Trois mécanismes y
// conduisaient, et aucun n'était le modèle seul :
//   · le chemin corpus-first (Haiku) impose la réserve « dès que la question
//     porte sur un cas concret » — une urgence est un cas concret ;
//   · le message de synthèse forcée dit « renvoie la conclusion pratique au Rav »
//     sans condition ;
//   · le prompt lui-même imposait une formule de renvoi au Rav.
//
// Ce module est un DÉTECTEUR, pas un juge : il produit un booléen prudent, et le
// serveur s'en sert pour (1) court-circuiter les chemins courts, (2) injecter une
// consigne de priorité, (3) retirer les réserves automatiques, (4) servir une
// consigne statique si aucun modèle n'est disponible. Un faux positif coûte une
// réponse par le chemin complet, sans réserve automatique — le modèle, informé,
// répond alors normalement à une question d'étude. Un faux négatif laisse le
// prompt système (règle de priorité à la vie) seul en ligne.

// Signes d'un danger vital ACTUEL — pas la théorie de piqoua'h nefech.
const FR = [
  /s'?est\s+effondr|vient de s'?effondrer|effondr[ée]e?s?\b/i,
  /ne\s+r[ée]pond\s+plus|ne\s+r[ée]agit\s+plus|inconscien|sans\s+connaissance|évanoui|perdu\s+connaissance/i,
  /ne\s+respire\s+(?:plus|pas)|arr[êe]t\s+(?:cardiaque|respiratoire)|crise\s+cardiaque|infarctus|\bavc\b|attaque\s+c[ée]r[ée]brale/i,
  /saigne\s+(?:beaucoup|abondamment|énormément)|h[ée]morragie|perd\s+beaucoup\s+de\s+sang/i,
  /s'?[ée]touffe|[ée]touffement|ne\s+peut\s+plus\s+respirer|avalé\s+de\s+travers/i,
  /convulsion|crise\s+d'?[ée]pilepsie|overdose|surdose|empoisonn|intoxi/i,
  /noy[ée]e?\b|noyade|se\s+noie|br[ûu]l[ée]e?\s+grave|accident\s+grave|chute\s+grave/i,
  /suicid|veut\s+(?:se\s+tuer|mourir|en\s+finir)/i,
  /accouche|contractions?\s+(?:rapproch|fortes)|perd\s+les\s+eaux/i,
  /douleur\s+(?:thoracique|dans\s+la\s+poitrine)|allergie\s+grave|choc\s+anaphylactique/i,
];
const EN = [
  /collaps(?:ed|ing)|passed\s+out|unconscious|unresponsive|not\s+responding|fainted/i,
  /not\s+breathing|stopped\s+breathing|cardiac\s+arrest|heart\s+attack|\bstroke\b/i,
  /bleeding\s+(?:heavily|a\s+lot|badly)|hemorrhag|haemorrhag/i,
  /choking|can'?t\s+breathe|cannot\s+breathe|seizure|overdose|poison/i,
  /drown|severe\s+burn|serious\s+accident|suicid|wants?\s+to\s+die|kill\s+(?:him|her|my)self/i,
  /in\s+labou?r|water\s+broke|chest\s+pain|anaphyla/i,
];
const HE = [
  /התמוטט|קרס|מחוסר\s+הכרה|איבד\s+(?:את\s+)?הכרה|לא\s+מגיב|לא\s+מגיבה|התעלף|התעלפה/,
  /לא\s+נושם|לא\s+נושמת|הפסיק\s+לנשום|דום\s+לב|התקף\s+לב|שבץ|אירוע\s+מוחי/,
  /מדמם\s+(?:הרבה|מאוד)|דימום\s+(?:חזק|כבד)|איבוד\s+דם/,
  /נחנק|נחנקת|לא\s+יכול\s+לנשום|פרכוס|מנת\s+יתר|הרעלה/,
  /טובע|טובעת|כוויה\s+קשה|תאונה\s+קשה|אובדני|רוצה\s+למות|להתאבד/,
  /צירי\s+לידה|ירדו\s+(?:לה\s+)?המים|כאבים\s+בחזה|אנפילק/,
];

// Indices qu'il s'agit d'une ÉTUDE et non d'une situation : on ne bloque pas la
// détection pour autant (le modèle, informé, fait la part des choses), mais on
// évite de court-circuiter le corpus sur « que dit le siman 328 sur … ».
const ETUDE = /\b(?:siman|séif|seif|סימן|סעיף|que\s+dit|what\s+does|explique|explain|source|מקור|dans\s+le\s+choul|in\s+the\s+shul)\b/i;

/**
 * @param {string} text — dernier message de l'utilisateur (profil compris)
 * @returns {{ urgent: boolean, etude: boolean, indices: string[] }}
 */
export function detecteUrgenceVitale(text) {
  const t = String(text || '');
  if (!t) return { urgent: false, etude: false, indices: [] };
  const indices = [];
  for (const re of [...FR, ...EN, ...HE]) {
    const m = t.match(re);
    if (m) indices.push(m[0]);
  }
  return { urgent: indices.length > 0, etude: ETUDE.test(t), indices };
}

// Consigne injectée devant la question quand un danger vital est détecté. Elle
// s'adresse au MODÈLE ; elle ne remplace pas la règle de priorité du prompt
// système, elle la rend impossible à manquer sur ce message précis.
export const CONSIGNE_URGENCE_MODELE =
  "<priorite_vitale>Ce message peut décrire un danger immédiat pour une vie. Si c'est le cas : " +
  "commence par la consigne d'appeler les secours locaux et de suivre leurs instructions, sans attendre " +
  "ni recherche ni avis rabbinique ; ne cite aucun numéro d'urgence (le pays est inconnu) ; reste bref ; " +
  "n'ajoute AUCUNE réserve du type « consulte ton Rav » ni « c'est à ton Rav de trancher » — elle contredirait " +
  "la consigne. Les sources (Orah Haïm 328) peuvent venir ensuite, brièvement. " +
  "Si le message est en réalité une question d'étude sans situation actuelle, réponds normalement.</priorite_vitale>\n\n";
