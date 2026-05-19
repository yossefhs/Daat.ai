/* DAAT — suivi du parcours d'étude.
 *
 * Inclus dans chaque page de niveau (base / lamdan / synthèse / daat-harav).
 * À l'ouverture de la page, enregistre le niveau étudié dans localStorage.
 * La page d'index /oh/ relit ces données pour afficher la progression.
 *
 * Format : localStorage['daat-progress-v2'] = { "357": ["base","lamdan"], ... }
 */
(function () {
  'use strict';

  var KEY = 'daat-progress-v2';
  var path = window.location.pathname;

  // Numéro du siman — URL « propre » /oh/357/... ou chemin brut .../siman-357/...
  var mSiman = path.match(/\/oh\/(\d+)/) || path.match(/siman-(\d+)/);
  if (!mSiman) return;
  var siman = mSiman[1];

  // Niveau étudié — gère les deux formes d'URL.
  var level = null;
  if (/\/base(\/|$)/.test(path) || /niveau-1-base/.test(path)) level = 'base';
  else if (/\/lamdan(\/|$)/.test(path) || /niveau-2-lamdan/.test(path)) level = 'lamdan';
  else if (/\/synthese(\/|$)/.test(path) || /niveau-3-synthese/.test(path)) level = 'synthese';
  else if (/\/daat-harav(\/|$)/.test(path) || /niveau-4-daat-harav/.test(path)) level = 'daat-harav';
  if (!level) return;

  try {
    var data = JSON.parse(localStorage.getItem(KEY) || '{}');
    var done = Array.isArray(data[siman]) ? data[siman] : [];
    if (done.indexOf(level) === -1) {
      done.push(level);
      data[siman] = done;
      localStorage.setItem(KEY, JSON.stringify(data));
    }
  } catch (e) {
    /* localStorage indisponible (navigation privée, quota…) — sans gravité */
  }
})();
