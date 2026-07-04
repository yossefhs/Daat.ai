// api/_social-content.js — Génère les posts sociaux du « siman de la semaine ».
//
// Réutilise les données de _newsletter-weekly.js (siman + article de blog éventuel)
// et produit un texte adapté par plateforme. Aucun psak : on présente le sujet et
// on renvoie à l'étude + « pour la pratique, consulte ton Rav ».

import { getSiman, BLOG_BY_SIMAN } from './_newsletter-weekly.js';

const SITE = 'https://daattorah.com';

function linksFor(num) {
  const slug = BLOG_BY_SIMAN[num];
  return {
    study: `${SITE}/oh/${num}/`,
    blog: slug ? `${SITE}/blog/${slug}.html` : null,
    image: `${SITE}/assets/img/og/siman-${num}.png`,
  };
}

// Le meilleur lien public à mettre en avant (article si dispo, sinon page d'étude).
function mainLink(num) {
  const { study, blog } = linksFor(num);
  return blog || study;
}

const DISCLAIMER = 'Pour la pratique, consulte ton Rav.';
const TAGS = '#Halakha #Torah #ChoulhanAroukh #Shabbat #DaatTorah';

// Construit tous les posts pour un siman. Retourne null si siman inconnu.
export function buildSocialPosts(num) {
  const siman = getSiman(num);
  if (!siman) return null;
  const he = siman.numHe || '';
  const title = siman.title || `Siman ${num}`;
  const { study, blog, image } = linksFor(num);
  const link = mainLink(num);

  const linkedin =
    `📖 Le siman de la semaine — ${he ? he + ' · ' : ''}${title}\n\n` +
    `Chaque semaine, DAAT étudie un siman du Choulhan Aroukh (Orah Haïm, Hilkhot Shabbat) ` +
    `en plusieurs niveaux : texte hébreu du Mehaber avec traduction française, pilpoul des Rishonim ` +
    `et Acharonim, synthèse, et la chitah de l'Admour HaZaken (Daat HaRav).\n\n` +
    (blog ? `➡️ La question concrète du quotidien, traitée à partir de ce siman : ${blog}\n` : '') +
    `➡️ Étudier le siman : ${study}\n\n` +
    `${DISCLAIMER}\n\n${TAGS}`;

  const facebook =
    `🕯️ Le siman de la semaine : ${he ? he + ' — ' : ''}${title}.\n\n` +
    `On l'étudie en profondeur sur daattorah.com — du débutant au talmid hakham (4 niveaux, ` +
    `texte hébreu + traduction française).\n` +
    `👉 ${link}\n\n${DISCLAIMER} 🙏`;

  // X : rester court (l'URL compte ~23 caractères).
  let x =
    `📖 Siman de la semaine — ${he ? he + ' · ' : ''}${title}.\n` +
    `Étude complète (texte, traduction, pilpoul, Daat HaRav) 👉 ${link}\n` +
    `${DISCLAIMER} #Halakha #Shabbat`;
  if (x.length > 275) {
    x =
      `📖 Siman de la semaine — ${he || num}.\n` +
      `Étude complète 👉 ${link}\n` +
      `${DISCLAIMER} #Halakha #Shabbat`;
  }

  const telegram =
    `🕯️ Le siman de la semaine — ${he ? he + ' · ' : ''}${title}\n` +
    (blog ? `📰 Article : ${blog}\n` : '') +
    `📖 Étude (4 niveaux) : ${study}\n` +
    `${DISCLAIMER}`;

  const instagram =
    `🕯️ Le siman de la semaine : ${he ? he + ' — ' : ''}${title}.\n` +
    `Étude complète sur daattorah.com (lien en bio) — texte hébreu, traduction, pilpoul, Daat HaRav.\n` +
    `${DISCLAIMER}\n` +
    `#Halakha #Torah #Shabbat #ChoulhanAroukh #Judaisme #DaatTorah #Limoud`;

  return { num, numHe: he, title, link, study, blog, image, linkedin, facebook, x, telegram, instagram };
}
