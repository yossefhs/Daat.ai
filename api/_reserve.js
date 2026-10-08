// La phrase de réserve UNIQUE du chat Daat, et la consigne d'urgence vitale.
//
// Pourquoi un module : mesuré le 28 septembre 2026, SIX formulations différentes
// de la même réserve coexistaient (prompt système ×3, chemin corpus-first de
// chat.js, chat-corpus.js, champ `disclaimer` de _mareh_mekomot.js), et le
// modèle en recopiait parfois deux dans une même réponse. Tout chemin de
// génération importe désormais la même phrase, dans la langue du lecteur.
//
// Deux règles que chaque consommateur doit respecter :
//   1. la réserve ne s'ajoute qu'à l'analyse d'un CAS PRATIQUE NON URGENT ;
//      jamais à une définition, une traduction ou une étude sans application
//      personnelle — et JAMAIS après une consigne d'urgence vitale (constat B :
//      « appelle les secours… c'est à ton Rav de trancher » est contradictoire) ;
//   2. elle ne répare pas une affirmation fausse ou non sourcée.

export const RESERVE = {
  fr: "Cette analyse présente les sources et leurs conditions ; elle ne tranche pas ton cas personnel. Pour l'application, consulte ton Rav.",
  he: 'הניתוח מציג את המקורות ותנאיהם, ואינו פסק למקרה האישי שלך. למעשה יש לפנות לרב.',
  en: 'This analysis presents the sources and their conditions; it does not decide your personal case. For practical application, consult your Rav.',
  es: 'Este análisis presenta las fuentes y sus condiciones; no resuelve tu caso personal. Para aplicarlo en la práctica, consulta a tu rabino.',
};

export function reserveFor(lang) {
  const l = String(lang || 'fr').toLowerCase().slice(0, 2);
  return RESERVE[l] || RESERVE.fr;
}

// Consigne d'urgence vitale — écrite par le SERVEUR, sans modèle, sans coût.
// Servie telle quelle quand un danger vital est détecté et qu'aucun modèle ne
// peut répondre (quota épuisé, budget IA épuisé, erreur avant le premier mot).
// Elle ne cite aucun numéro d'urgence : le pays de l'utilisateur est inconnu.
// Elle ne porte aucune réserve « consulte ton Rav » : c'est précisément la
// contradiction observée (constat B) qu'il s'agit d'empêcher.
export const URGENCE = {
  fr: "**Si une vie est en danger, appelle immédiatement les secours de ton pays et suis leurs instructions.** N'attends ni ma réponse ni l'avis d'un Rav : la halakha elle-même l'ordonne (Choul'han Aroukh, Orah Haïm 328:2 — celui qui agit vite est loué, celui qui s'attarde à demander est blâmé). Une fois la personne prise en charge, je pourrai t'expliquer les sources.",
  he: '**אם יש סכנת חיים, הזעק מיד את שירותי החירום במדינתך ופעל לפי הוראותיהם.** אל תמתין לא לתשובתי ולא לדעת רב: ההלכה עצמה מצווה כך (שולחן ערוך, אורח חיים שכ״ח:ב — הזריז הרי זה משובח, והשואל הרי זה שופך דמים). לאחר שהאדם מטופל, אוכל להסביר את המקורות.',
  en: "**If a life is in danger, call your country's emergency services immediately and follow their instructions.** Do not wait for my answer or for a Rav's opinion: halakha itself commands this (Shulchan Arukh, Orach Chayim 328:2 — one who acts quickly is praised, one who delays to ask is blamed). Once the person is being cared for, I can explain the sources.",
};

export function urgenceFor(lang) {
  const l = String(lang || 'fr').toLowerCase().slice(0, 2);
  return URGENCE[l] || URGENCE.fr;
}
