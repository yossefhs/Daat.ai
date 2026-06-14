/* DAAT — suivi du parcours d'étude (offline-first + sync KV si connecté).
 *
 * Inclus dans chaque page de niveau (base / lamdan / synthèse / daat-harav).
 * À l'ouverture de la page :
 *   1. Enregistre le niveau étudié dans localStorage (offline-first, instantané)
 *   2. Si l'utilisateur est connecté (cookie daat_session) : pousse la mise à
 *      jour vers /api/progress (fire-and-forget — l'utilisateur n'attend pas).
 *      Si pas de session, le serveur répond 401 et on ignore silencieusement.
 *
 * La page d'index /oh/ relit localStorage pour afficher la grille de progression.
 * Si l'utilisateur est connecté, elle GET /api/progress et merge avec localStorage
 * (union — jamais de perte de niveau étudié).
 *
 * Format localStorage : { "357": ["base","lamdan"], ... }
 *
 * Endpoint API : POST /api/progress { progress: {...} }
 * Côté serveur : union avec ce qui existait déjà.
 */
(function () {
  'use strict';

  var KEY = 'daat-progress-v2';
  // Origine de l'API (cross-site daatai.vercel.app). Permet à daattorah.com
  // d'écrire dans la KV via la même surface que /api/chat.
  var API_BASE = (window.DAAT_CHAT_API_URL || '').replace(/\/api\/chat\/?$/, '');
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

  // 1) Écriture locale (offline-first) — instantanée, aucune attente réseau.
  var dirty = false;
  try {
    var data = JSON.parse(localStorage.getItem(KEY) || '{}');
    var done = Array.isArray(data[siman]) ? data[siman] : [];
    if (done.indexOf(level) === -1) {
      done.push(level);
      data[siman] = done;
      localStorage.setItem(KEY, JSON.stringify(data));
      dirty = true; // → on va aussi pousser vers le serveur ci-dessous
    }
  } catch (e) {
    /* localStorage indisponible (navigation privée, quota…) — sans gravité */
  }

  // 2) Sync KV (fire-and-forget) — seulement si :
  //    - on a un nouveau niveau étudié (dirty)
  //    - on connaît l'URL de l'API (window.DAAT_CHAT_API_URL est posée sur les pages)
  //
  // On ne tente pas de détecter si l'user est connecté côté client (le cookie
  // de session est HttpOnly et illisible en JS). On POST avec credentials: 'include'.
  // Si pas de session, le serveur répond 401 et on ignore silencieusement.
  if (dirty && API_BASE) {
    var payload = {};
    payload[siman] = [level];
    try {
      fetch(API_BASE + '/api/progress', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ progress: payload }),
        keepalive: true, // survit à un changement de page rapide (navigation)
      }).catch(function () { /* offline ou non connecté — silence */ });
    } catch (e) { /* fetch indisponible — silence */ }
  }
})();
