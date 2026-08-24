/*!
 * chat-loader.js — Mini-bootstrap pour le chat DAAT (Core Web Vitals / INP 2026)
 *
 * Objectif : ne pas exécuter les ~36 KB minifiés de chat-widget.min.js
 * au chargement initial de la page. À la place :
 *   1. On crée immédiatement un FAB statique (clone CSS du vrai bouton).
 *   2. On déclenche le chargement du vrai widget sur le premier signal
 *      d'engagement utilisateur : pointer/touch sur le FAB, scroll proche,
 *      ou idle après quelques secondes (pour préserver la sync auth des
 *      utilisateurs connectés).
 *   3. Une fois le vrai widget chargé, il auto-init et remplace le FAB
 *      provisoire (le vrai bouton porte la même classe `.daat-chat-button`).
 *
 * Coût total au boot : <1 KB minifié, zéro DOM mutation lourde, zéro
 * localStorage, zéro fetch. Devrait économiser ~30-60 ms de scripting
 * sur les pages siman (mesure indicative — dépend de l'appareil).
 *
 * Note : pour les utilisateurs connectés, la synchronisation des
 * conversations (chat-widget.js _bindAuthSyncHook) est déclenchée par
 * le chargement du widget réel. On force donc le chargement après
 * 4 s d'idle pour ne pas casser ce flux.
 */
(function () {
  'use strict';

  if (window.__daatChatLoaderActive) return;
  window.__daatChatLoaderActive = true;

  // Si le vrai widget est déjà chargé (cas peu probable mais propre), on sort.
  if (window.daatChatWidget) return;

  // Résolution du path du vrai widget : on prend le src de NOTRE propre
  // <script>, on remplace 'chat-loader' par 'chat-widget.min'. Ça gère
  // automatiquement les chemins relatifs (`/assets/...`, `../../../assets/...`).
  var WIDGET_SRC = (function () {
    try {
      var scripts = document.getElementsByTagName('script');
      for (var i = scripts.length - 1; i >= 0; i--) {
        var src = scripts[i].src || '';
        if (src.indexOf('chat-loader') !== -1) {
          return src.replace(/chat-loader(\.min)?\.js.*$/, 'chat-widget.min.js');
        }
      }
    } catch (e) {}
    // Fallback (devrait jamais arriver) : path absolu
    return '/assets/js/chat-widget.min.js';
  })();

  var loaded = false;
  var fab = null;
  var pendingOpen = false;

  function buildPlaceholderFab() {
    // Clone visuel du vrai bouton (mêmes classes CSS → même rendu, zéro flash).
    var b = document.createElement('button');
    b.className = 'daat-chat-button';
    b.type = 'button';
    // Titre contextuel : si on est sur une page siman, le bouton le dit déjà
    // (le vrai widget affinera à son chargement — même détection).
    var simanMatch = location.pathname.match(/^\/(?:oh|yd|oh-quotidien)\/(\d+)/) ||
                     location.pathname.match(/\/siman-(\d+)/);
    var fabLabel = simanMatch ? ('Poser une question sur le Siman ' + simanMatch[1]) : 'Ouvrir le chat avec Daat';
    b.setAttribute('aria-label', fabLabel);
    b.title = fabLabel;
    b.innerHTML =
      '<span class="daat-chat-button-icon">דעת</span>' +
      '<span class="daat-chat-button-pulse"></span>';
    return b;
  }

  function loadWidget(openAfter) {
    if (loaded) {
      if (openAfter) tryOpenWhenReady();
      return;
    }
    loaded = true;
    pendingOpen = !!openAfter;

    // On laisse le placeholder en place pendant le download — il sera
    // retiré dès que le vrai widget s'attache au DOM (cf. tryOpenWhenReady).
    // Évite un "trou" visuel sans FAB pendant la latence réseau.

    var s = document.createElement('script');
    s.src = WIDGET_SRC;
    s.async = true;
    s.onload = function () {
      tryOpenWhenReady();
    };
    s.onerror = function () {
      // Échec réseau : on garde le placeholder fonctionnel (clic = retry).
      loaded = false;
      console.warn('[daat-chat-loader] Failed to load', WIDGET_SRC);
    };
    document.head.appendChild(s);
  }

  function removePlaceholder() {
    if (fab && fab.parentNode) {
      fab.parentNode.removeChild(fab);
      fab = null;
    }
  }

  function tryOpenWhenReady() {
    // Le vrai widget s'auto-init sur DOMContentLoaded OU immédiatement
    // si readyState != 'loading'. On poll jusqu'à ce qu'il existe, puis
    // on retire notre placeholder (évite le double-FAB) et on ouvre si demandé.
    var attempts = 0;
    (function poll() {
      if (window.daatChatWidget && typeof window.daatChatWidget.toggle === 'function') {
        removePlaceholder();
        if (pendingOpen && !window.daatChatWidget.isOpen) {
          window.daatChatWidget.toggle();
        }
        pendingOpen = false;
        return;
      }
      if (++attempts < 40) setTimeout(poll, 25); // ~1 s max
    })();
  }

  function onFabClick(ev) {
    ev.preventDefault();
    loadWidget(true);
  }

  // ======================================================================
  // Triggers d'engagement
  // ======================================================================

  function onAnyEngagement() {
    if (loaded) return;
    loadWidget(false);
  }

  function attachIdleFallback() {
    // Pour ne PAS casser la sync auth des utilisateurs connectés et
    // garder le bouton interactif pour les screen readers/clavier,
    // on charge le widget après un délai d'idle.
    var schedule = window.requestIdleCallback || function (cb) { return setTimeout(cb, 1); };
    schedule(function () {
      // Délai supplémentaire : on laisse passer LCP/INP du premier paint.
      setTimeout(onAnyEngagement, 4000);
    }, { timeout: 6000 });
  }

  function attachEngagementListeners() {
    // 1. Click sur le FAB → chargement + ouverture
    fab.addEventListener('click', onFabClick, { passive: false });

    // 2. Pointer hover/touchstart sur le FAB → préchargement (sans ouverture)
    var preloadOnHover = function () {
      fab.removeEventListener('mouseenter', preloadOnHover);
      fab.removeEventListener('focusin', preloadOnHover);
      onAnyEngagement();
    };
    fab.addEventListener('mouseenter', preloadOnHover, { passive: true });
    fab.addEventListener('focusin', preloadOnHover, { passive: true });

    // 3. Scroll significatif → préchargement
    var scrollHandler = function () {
      if (window.scrollY > 600) {
        window.removeEventListener('scroll', scrollHandler);
        onAnyEngagement();
      }
    };
    window.addEventListener('scroll', scrollHandler, { passive: true });

    // 4. Idle fallback
    attachIdleFallback();
  }

  function init() {
    fab = buildPlaceholderFab();
    document.body.appendChild(fab);
    attachEngagementListeners();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
