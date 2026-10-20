// Réponses d'accueil ÉCRITES, non générées.
//
// Constat (30 septembre 2026) : à « Bonjour », le chat répondait « Shalom ! Rav de
// te retrouver ici. » — « Rav » pour « Ravi ». La phrase était produite par le
// petit modèle chargé des messages conversationnels (DeepSeek), puis figée 14
// jours dans le cache : chaque visiteur qui commençait par « Bonjour » la
// recevait. Lue littéralement, elle fait dire à Daat qu'il est « Rav » — la
// première chose que voit un nouveau venu, et l'exact contraire de ce que le
// prompt système s'emploie à garantir (ni smikha, ni qualité de posek).
//
// Une salutation n'a pas besoin d'un modèle. Un texte fixe ne peut pas déraper,
// ne coûte rien, répond en quelques millisecondes — et la présentation de Daat
// (« qui es-tu ? ») est trop sensible pour être confiée à un modèle qui ne reçoit
// pas le prompt système. Ce module couvre TOUTES les familles de la liste blanche
// META_PATTERNS de api/chat.js ; un message qui n'entre dans aucune famille rend
// null et suit le chemin existant.
//
// Deuxième défaut corrigé au passage : la consigne du modèle méta imposait de
// répondre « en français » — « hello » recevait une réponse française. Ici la
// langue suit le mot lui-même quand il est sans ambiguïté, sinon la page d'où
// vient la question.

// Même normalisation que isConversationalMeta() dans api/chat.js : minuscules,
// sans accents, tout ce qui n'est pas [a-z0-9 -] devient une espace.
function normaliser(text) {
  return String(text || '')
    .toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9 -]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// Les familles reprennent une à une les alternatives de META_PATTERNS.
const FAMILLES = [
  ['salutation', /^(?:(?:re)?bonjour(?: daat)?|bonsoir|bonne (?:journee|soiree|nuit)|salut(?: daat)?|coucou|hello|hi|hey|(?:shalom|chalom|sholom)(?: aleikhem)?|(?:shabbat|chabbat) (?:shalom|chalom)|boker tov|erev tov)$/],
  ['remerciement', /^(?:merci(?: beaucoup| bien| infiniment| a toi)?|todah?(?: raba)?|thanks|thank you|yasher koah|yaacher koah)$/],
  ['identite', /^(?:qui (?:es|est)[- ]?tu|(?:tu es|t es|vous etes) qui|tu es quoi|c est quoi (?:daat|daat torah|ce site|ce chat)|presente[- ]toi|tu sers a quoi|que sais[- ]?tu faire|qu est[- ]?ce que tu sais faire|tu fais quoi|qui te supervise|tu es une ia|tu es un robot)$/],
  ['fonctionnement', /^(?:comment (?:ca|cela) (?:marche|fonctionne)|(?:ca|cela) (?:marche|fonctionne) comment|comment (?:t|tu) utilise[rs]?|comment utiliser|comment ca se passe)$/],
  ['politesse', /^(?:comment (?:ca va|vas[- ]?tu|allez[- ]?vous)|ca va(?: bien)?|ca roule)$/],
  ['acquiescement', /^(?:ok(?:ay)?|d ?accord|super|parfait|genial|bravo|top|nickel|oui|non|tres bien|compris)$/],
  ['fin', /^(?:au revoir|a bientot|bonne continuation|bye)$/],
  ['test', /^(?:test|essai)$/],
];

// Mots qui désignent eux-mêmes leur langue.
const MOTS_ANGLAIS = /^(?:hello|hi|hey|thanks|thank you|bye)$/;
// Mots employés tels quels dans les trois langues du site : ils ne disent rien
// de la langue du visiteur — c'est la page qui tranche.
const MOTS_NEUTRES = /^(?:(?:shalom|chalom|sholom)(?: aleikhem)?|(?:shabbat|chabbat) (?:shalom|chalom)|boker tov|erev tov|todah?(?: raba)?|yasher koah|yaacher koah|ok(?:ay)?|super|top|bravo|test)$/;

const TEXTES = {
  fr: {
    salutation: "Shalom et bienvenue ! Je suis Daat, l'assistant d'étude du projet DAAT. Pose-moi ta question — un siman, un concept, un sujet à approfondir — et nous l'étudierons ensemble, sources à l'appui.",
    remerciement: "Avec plaisir ! Si un point reste à éclaircir, je suis là.",
    identite: "Je suis Daat (דעת), l'assistant d'étude de la Torah du projet DAAT, créé par le Rav Yossef Haim Samama. Je suis une intelligence artificielle : je t'aide à comprendre les textes et à retrouver les sources, mais je ne suis pas un Rav et je ne rends pas de psak — pour l'application à ton cas, c'est ton Rav qui tranche.",
    fonctionnement: "Pose ta question en langage courant : je cherche d'abord dans les contenus du site (Choul'han Aroukh, Orah Haïm et Yoreh De'ah), puis dans les textes disponibles sur Sefaria, et je te réponds avec les sources. Tu peux préciser ton niveau et ton minhag pour une réponse mieux adaptée.",
    politesse: "Tout va bien, merci ! Sur quel sujet veux-tu étudier ?",
    acquiescement: "Très bien. Quelle est ta question ?",
    fin: "À bientôt, et bonne étude !",
    test: "Je suis bien là. Pose-moi ta question d'étude.",
  },
  he: {
    salutation: 'שלום וברוך הבא! אני דעת, עוזר הלימוד של פרויקט DAAT. שאל את שאלתך — סימן, מושג או נושא לעיון — ונלמד יחד מתוך המקורות.',
    remerciement: 'בשמחה! אם נשארה נקודה לא ברורה — אני כאן.',
    identite: 'אני דעת, עוזר לימוד התורה של פרויקט DAAT, שהוקם על ידי הרב יוסף חיים סממה. אני בינה מלאכותית: אני מסייע להבין את הטקסטים ולמצוא את המקורות, אך אינני רב ואינני פוסק הלכה — למעשה יש לפנות לרב.',
    fonctionnement: 'שאל בלשון רגילה: אני מחפש תחילה בתכני האתר (שולחן ערוך, אורח חיים ויורה דעה), אחר כך בטקסטים הזמינים בספריא, ומשיב עם המקורות. אפשר לציין רמה ומנהג כדי לקבל תשובה מותאמת.',
    politesse: 'הכול טוב, תודה! באיזה נושא תרצה ללמוד?',
    acquiescement: 'טוב מאוד. מה השאלה שלך?',
    fin: 'להתראות, ולימוד פורה!',
    test: 'אני כאן. שאל את שאלתך.',
  },
  en: {
    salutation: "Shalom and welcome! I'm Daat, the study assistant of the DAAT project. Ask your question — a siman, a concept, a topic to explore — and we'll study it together from the sources.",
    remerciement: "With pleasure! If anything is still unclear, I'm here.",
    identite: "I'm Daat (דעת), the Torah study assistant of the DAAT project, created by Rav Yossef Haim Samama. I'm an artificial intelligence: I help you understand the texts and find the sources, but I am not a rabbi and I do not issue halakhic rulings — for practical application, consult your rabbi.",
    fonctionnement: "Ask in plain language: I first search the site's content (Shulchan Arukh, Orach Chaim and Yoreh De'ah), then the texts available on Sefaria, and I answer with sources. You can mention your level and custom for a better-adapted answer.",
    politesse: 'All good, thank you! What would you like to study?',
    acquiescement: 'Very well. What is your question?',
    fin: 'Goodbye, and good learning!',
    test: "I'm here. Ask your question.",
  },
};

// Langue de la page d'où vient la question, d'après le Referer : le widget
// n'envoie pas de champ « lang ». Convention du site : X-he.html / …/he pour
// l'hébreu, X-en.html / …/en pour l'anglais, le reste en français.
export function langueDeLaPage(referer) {
  let chemin = '';
  try { chemin = new URL(String(referer || '')).pathname; } catch { return null; }
  if (/[-/]he(?:\.html)?\/?$/.test(chemin)) return 'he';
  if (/[-/]en(?:\.html)?\/?$/.test(chemin)) return 'en';
  return null;
}

export function familleAccueil(text) {
  const n = normaliser(text);
  if (!n) return null;
  for (const [nom, re] of FAMILLES) if (re.test(n)) return nom;
  return null;
}

// Rend { texte, famille, lang } ou null si le message n'est pas un message
// d'accueil reconnu. `declared` = langue explicitement transmise, si un client
// en envoie une un jour (req.body.lang) ; elle prime alors sur tout le reste.
export function reponseAccueil(text, { declared = null, referer = null } = {}) {
  const famille = familleAccueil(text);
  if (!famille) return null;
  const n = normaliser(text);
  const d = String(declared || '').toLowerCase().slice(0, 2);
  let lang;
  if (d === 'fr' || d === 'he' || d === 'en') lang = d;
  else if (MOTS_ANGLAIS.test(n)) lang = 'en';
  else if (MOTS_NEUTRES.test(n)) lang = langueDeLaPage(referer) || 'fr';
  else lang = 'fr'; // le mot est français (bonjour, merci, d'accord…)
  return { texte: TEXTES[lang][famille], famille, lang };
}
