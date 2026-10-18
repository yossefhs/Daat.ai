// Garde-fous du CHEMIN COURT (corpus-first : un extrait du corpus reformulé par
// Haiku). Deux fonctions pures, sans dépendance ni variable d'environnement :
// elles s'importent et se testent seules (tests/chat/garde-corpus.test.mjs).
//
// POURQUOI. Mesuré en production le 30 septembre 2026, siman 89 de Yoré Déa
// (פ״ט) : à une question sur le fromage après la viande, le chemin court a servi
// l'extrait yd-base-siman-89-s3-b2 — un paragraphe de CONTEXTE qui ne porte
// aucune règle — et Haiku a répondu « tu peux recommencer aussitôt, à condition
// de bien te nettoyer… Source : Siman 89 ». C'est l'inverse du séif 1 (« לא יאכל
// גבינה אחריו עד שישהה שש שעות ») : la permission du séif 2, qui porte sur le cas
// INVERSE (fromage puis viande). La réponse a été mise en cache pour 30 jours.
//
// Le texte du site était juste. Deux défaillances l'ont rendu faux :
//  1. la recherche par mots-clés ne voit pas l'ORDRE viande/lait, dont dépend
//     le sens du séif — l'extrait des six heures arrivait 5ᵉ, 8ᵉ ou 14ᵉ, jamais
//     dans ce que le chemin court transmet au modèle ;
//  2. le prompt interdisait déjà « N'invente AUCUNE halakha » et « JAMAIS
//     d'autorisation personnelle », et rien ne faisait respecter ces règles.
// Une consigne de prompt a déjà été mesurée INEFFICACE sur ce chemin (voir la
// réserve écrite par le serveur dans api/chat.js) : la vérification se fait ici,
// dans le code, sur le texte produit.

function normaliser(texte) {
  return String(texte || '')
    .toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '')   // accents latins seulement
    .replace(/[’`]/g, "'")
    .replace(/\s+/g, ' ');
}

// ── 1. La question demande-t-elle une PERMISSION ou un DÉLAI ? ──────────────
// En Yoré Déa (cacherout), ces questions ne passent plus par le chemin court :
// le sens d'un séif s'y inverse selon l'ordre (viande puis lait / lait puis
// viande), et un seul extrait choisi par mots-clés ne le voit pas. Le chemin
// complet, lui, ouvre le séif. Un faux positif ne coûte qu'un appel plus cher ;
// un faux négatif peut servir une permission inversée.
const PERMISSION_FR = new RegExp('(?:^|[^a-z])(?:' + [
  'puis[- ]je', 'peut[- ]on', 'peux[- ]tu', 'pouvons[- ]nous', 'pourrais[- ]je',
  'je peux', 'on peut', 'je pourrais', "est[- ]ce que je peux", "est[- ]ce qu'on peut",
  'ai[- ]je le droit', 'a[- ]t[- ]on le droit', 'avons[- ]nous le droit', 'le droit de',
  'est[- ]il permis', 'est[- ]ce permis', "c'est permis", 'permis de', 'est[- ]il interdit',
  "est[- ]ce interdit", "c'est interdit", 'autorise', 'faut[- ]il', 'doit[- ]on', 'dois[- ]je',
  'combien de temps', "combien d'heures", 'attendre', 'delai', 'tout de suite', 'aussitot',
  'immediatement', 'directement apres', 'juste apres',
].join('|') + ')(?:[^a-z]|$)');
const PERMISSION_EN = new RegExp('(?:^|[^a-z])(?:' + [
  'can i', 'may i', 'can we', 'may we', 'can one', 'could i', 'am i allowed', 'are we allowed',
  'is it (?:permitted|allowed|forbidden|prohibited|ok|okay)', 'must i', 'do i (?:have|need) to',
  'how long', 'wait', 'right away', 'immediately', 'straight after', 'right after',
].join('|') + ')(?:[^a-z]|$)');
// Hébreu : pas de \b en JavaScript (il ne connaît que [A-Za-z0-9_]) — on cherche
// les formes comme sous-chaînes, préfixes de conjonction compris (ומותר, האם מותר).
const PERMISSION_HE = /(?:מותר|אסור|אפשר|כמה זמן|להמתין|לחכות|מיד)/;

export function questionDePermission(question) {
  const t = normaliser(question);
  return PERMISSION_FR.test(t) || PERMISSION_EN.test(t) || PERMISSION_HE.test(String(question || ''));
}

// ── 2. La réponse donne-t-elle un FEU VERT PERSONNEL au lecteur ? ───────────
// « Tu peux recommencer aussitôt » est exactement ce que le prompt interdit :
// rapporter une source (« le Rav écrit que … est permis lorsque … ») est permis,
// la convertir en permission pour cette personne ne l'est pas. Les tournures
// qui ORIENTENT sans permettre restent libres : « tu peux consulter ton Rav »,
// « tu peux reposer la question en mode étendu ». Rend le passage fautif, ou null.
const VERBES_ORIENTATION_FR = '(?:poser|reposer|consulter|demander|redemander|lire|relire|etudier|voir|revoir|approfondir|retrouver|ouvrir|cliquer|te referer|vous referer|contacter|en parler|interroger|preciser|reformuler|t\'adresser|vous adresser|te reporter|vous reporter|suivre|continuer)';
const AUTORISATION_FR = new RegExp(
  "(?:^|[^a-z])(tu peux|vous pouvez|tu as le droit|vous avez le droit|tu es autorise|vous etes autorise|"
  + "rien ne t'empeche|rien ne vous empeche|pas de probleme pour toi|pas de souci pour toi|"
  + "n'hesite pas a|libre a toi|c'est bon pour toi)"
  + "(?![a-z])(?!\\s+(?:aussi\\s+|egalement\\s+|toujours\\s+)?" + VERBES_ORIENTATION_FR + ")",
);
const VERBES_ORIENTATION_EN = '(?:ask|re-ask|consult|read|reread|check|see|study|open|refer|contact|rephrase|clarify|look)';
const AUTORISATION_EN = new RegExp(
  "(?:^|[^a-z])(you can|you may|you're allowed|you are allowed|you're permitted|you are permitted|feel free to|go ahead)"
  + "(?![a-z])(?!\\s+(?:also\\s+|always\\s+)?" + VERBES_ORIENTATION_EN + ")",
);
const AUTORISATION_HE = /(מותר לך|מותר לכם|מותר לכן|אתה יכול|את יכולה|אתם יכולים|אין בעיה)(?!\s+(?:לשאול|לפנות|לעיין|לקרוא|ללמוד|להתייעץ))/;

export function autorisationPersonnelle(reponse) {
  const brut = String(reponse || '');
  const t = normaliser(brut);
  const m = t.match(AUTORISATION_FR) || t.match(AUTORISATION_EN);
  if (m) return m[1];
  const h = brut.match(AUTORISATION_HE);
  return h ? h[1] : null;
}
