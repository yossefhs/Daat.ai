/*
 * pwa.js — Daat Torah
 *   1. Enregistre le service worker (/sw.js).
 *   2. Affiche un bandeau « Installer l'application » :
 *        - Android/Chrome : capture beforeinstallprompt → bouton d'installation natif.
 *        - iOS/Safari : pas de beforeinstallprompt → instructions « Partager → Sur l'écran d'accueil ».
 *   Trilingue (fr/he/en d'après <html lang>), RTL en hébreu, et silencieux si déjà
 *   installé ou récemment ignoré (localStorage, 30 jours).
 */
(function () {
  'use strict';

  // 1) Service worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(function () {/* silencieux */});
    });
  }

  // --- Helpers d'état ---
  var DISMISS_KEY = 'daat_pwa_dismissed';
  var DISMISS_DAYS = 30;

  function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }
  function recentlyDismissed() {
    try {
      var t = parseInt(localStorage.getItem(DISMISS_KEY) || '0', 10);
      return t && (Date.now() - t) < DISMISS_DAYS * 864e5;
    } catch (e) { return false; }
  }
  function markDismissed() {
    try { localStorage.setItem(DISMISS_KEY, String(Date.now())); } catch (e) {}
  }
  function isIOS() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent) ||
           // iPadOS se fait passer pour un Mac mais a un écran tactile :
           (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  }

  if (isStandalone() || recentlyDismissed()) return;

  // --- Textes ---
  var L = (document.documentElement.lang || 'fr').slice(0, 2).toLowerCase();
  if (L !== 'he' && L !== 'en') L = 'fr';
  var T = {
    fr: { title: 'Installer Daat Torah', body: "Ajoutez l'app à votre écran d'accueil pour une étude plus rapide, même hors connexion.",
          install: 'Installer', later: 'Plus tard',
          ios: 'Appuyez sur  Partager  puis « Sur l’écran d’accueil ».', close: 'Fermer' },
    he: { title: 'התקנת דעת תורה', body: 'הוסיפו את האפליקציה למסך הבית ללימוד מהיר, גם ללא חיבור לאינטרנט.',
          install: 'התקנה', later: 'אחר כך',
          ios: 'הקישו על  שיתוף  ואז על «הוספה למסך הבית».', close: 'סגירה' },
    en: { title: 'Install Daat Torah', body: 'Add the app to your home screen for faster study, even offline.',
          install: 'Install', later: 'Later',
          ios: 'Tap  Share  then “Add to Home Screen”.', close: 'Close' }
  }[L];
  var RTL = (L === 'he');

  // --- Styles (injectés une fois) ---
  var css = '' +
    '#daat-pwa{position:fixed;left:50%;bottom:18px;transform:translateX(-50%) translateY(140%);' +
    'width:min(440px,calc(100vw - 24px));background:#1A1F3A;color:#FAF6EE;border:1px solid rgba(197,165,90,.45);' +
    'border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.45);padding:16px 18px;z-index:2147483000;' +
    'font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;transition:transform .35s cubic-bezier(.22,1,.36,1);}' +
    '#daat-pwa.show{transform:translateX(-50%) translateY(0);}' +
    '#daat-pwa[dir=rtl]{direction:rtl;}' +
    '#daat-pwa .pwa-row{display:flex;align-items:center;gap:13px;}' +
    '#daat-pwa .pwa-ic{flex:0 0 46px;width:46px;height:46px;border-radius:11px;}' +
    '#daat-pwa h3{margin:0 0 3px;font-size:15.5px;font-weight:600;color:#C5A55A;}' +
    '#daat-pwa p{margin:0;font-size:13px;line-height:1.45;opacity:.9;}' +
    '#daat-pwa .pwa-actions{display:flex;gap:9px;margin-top:13px;justify-content:flex-end;}' +
    '#daat-pwa button{font:inherit;font-size:13.5px;font-weight:600;border-radius:999px;padding:9px 18px;cursor:pointer;border:0;}' +
    '#daat-pwa .pwa-install{background:#C5A55A;color:#1A1F3A;}' +
    '#daat-pwa .pwa-later{background:transparent;color:#FAF6EE;opacity:.75;}' +
    '#daat-pwa .pwa-later:hover{opacity:1;}' +
    '#daat-pwa .pwa-ios{margin-top:11px;font-size:12.5px;background:rgba(197,165,90,.12);border-radius:10px;padding:9px 11px;line-height:1.5;}' +
    '#daat-pwa .pwa-ios b{color:#C5A55A;}';
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var ICON = '<svg class="pwa-ic" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
    '<rect width="512" height="512" rx="96" fill="#1A1F3A"/>' +
    '<circle cx="256" cy="256" r="150" fill="none" stroke="#EEE6D6" stroke-width="13"/>' +
    '<text x="256" y="301" font-family="Frank Ruhl Libre,serif" font-size="122" font-weight="700" text-anchor="middle" fill="#C5A55A">דעת</text></svg>';

  var deferredPrompt = null;
  var banner = null;

  function buildBanner(mode) {
    if (banner) return;
    banner = document.createElement('div');
    banner.id = 'daat-pwa';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', T.title);
    if (RTL) banner.setAttribute('dir', 'rtl');

    var html = '<div class="pwa-row">' + ICON +
      '<div><h3>' + T.title + '</h3><p>' + T.body + '</p></div></div>';
    if (mode === 'ios') {
      html += '<div class="pwa-ios">' + iosShareSvg() + ' ' + T.ios + '</div>' +
        '<div class="pwa-actions"><button class="pwa-later" data-act="later">' + T.close + '</button></div>';
    } else {
      html += '<div class="pwa-actions">' +
        '<button class="pwa-later" data-act="later">' + T.later + '</button>' +
        '<button class="pwa-install" data-act="install">' + T.install + '</button></div>';
    }
    banner.innerHTML = html;
    document.body.appendChild(banner);

    banner.addEventListener('click', function (e) {
      var act = e.target && e.target.getAttribute('data-act');
      if (act === 'later') { markDismissed(); hide(); }
      else if (act === 'install') { doInstall(); }
    });
    requestAnimationFrame(function () { banner.classList.add('show'); });
  }

  function iosShareSvg() {
    return '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C5A55A" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px">' +
      '<path d="M12 16V4M12 4l-4 4M12 4l4 4"/><path d="M5 12v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/></svg>';
  }

  function hide() {
    if (!banner) return;
    banner.classList.remove('show');
    setTimeout(function () { if (banner && banner.parentNode) banner.parentNode.removeChild(banner); banner = null; }, 400);
  }

  function doInstall() {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then(function () { deferredPrompt = null; hide(); });
  }

  // Android / Chromium
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    setTimeout(function () { if (!isStandalone()) buildBanner('prompt'); }, 2500);
  });

  window.addEventListener('appinstalled', function () { markDismissed(); hide(); });

  // iOS / Safari : pas d'événement → on propose les instructions.
  if (isIOS() && /safari/i.test(navigator.userAgent) && !/crios|fxios/i.test(navigator.userAgent)) {
    window.addEventListener('load', function () {
      setTimeout(function () { if (!isStandalone()) buildBanner('ios'); }, 3000);
    });
  }
})();
