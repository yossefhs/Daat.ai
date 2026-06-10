/*!
 * intra-links.js — Navigation intra-page DAAT
 * Intercepte les clics sur `a.intra-ref` : scroll smooth vers la cible
 * (#anchor) et flash 1.4 s. Respecte prefers-reduced-motion.
 */
(function () {
  'use strict';

  function flash(el) {
    el.classList.remove('intra-flash'); // reset si déjà appliqué
    // force un reflow pour rejouer l'animation
    void el.offsetWidth;
    el.classList.add('intra-flash');
    // Nettoie la classe après l'animation pour permettre re-flash
    setTimeout(function () {
      el.classList.remove('intra-flash');
    }, 1500);
  }

  function scrollToTarget(target) {
    var reduced =
      window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    try {
      target.scrollIntoView({
        behavior: reduced ? 'auto' : 'smooth',
        block: 'center',
      });
    } catch (e) {
      target.scrollIntoView();
    }
    // Met le focus pour l'accessibilité clavier/AT
    if (typeof target.focus === 'function') {
      // tabindex temporaire si l'élément n'est pas focusable nativement
      var hadTabindex = target.hasAttribute('tabindex');
      if (!hadTabindex) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      if (!hadTabindex) {
        // Retire le tabindex après pour ne pas polluer la tab order
        setTimeout(function () {
          target.removeAttribute('tabindex');
        }, 200);
      }
    }
  }

  function handleClick(ev) {
    var a = ev.target.closest('a.intra-ref');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (!href.startsWith('#')) return;
    var id = href.slice(1);
    if (!id) return;
    var target = document.getElementById(id);
    if (!target) return;
    ev.preventDefault();
    scrollToTarget(target);
    flash(target);
    // Met à jour l'URL pour le partage (sans recharger)
    if (history && history.replaceState) {
      history.replaceState(null, '', '#' + id);
    }
  }

  // Au chargement : si l'URL contient déjà un hash, flash la cible une fois
  function flashOnHashLoad() {
    var hash = window.location.hash;
    if (!hash || hash.length < 2) return;
    var target = document.getElementById(hash.slice(1));
    if (!target) return;
    // attend un tick pour que le navigateur ait fini son scroll natif
    setTimeout(function () {
      flash(target);
    }, 250);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      document.addEventListener('click', handleClick);
      flashOnHashLoad();
    });
  } else {
    document.addEventListener('click', handleClick);
    flashOnHashLoad();
  }

  // Réagit aussi aux changements de hash (navigation arrière/avant)
  window.addEventListener('hashchange', flashOnHashLoad);
})();
