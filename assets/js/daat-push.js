// assets/js/daat-push.js — abonnement aux notifications « Daat Yomi ».
//
// Transforme tout élément [data-daat-push] en bouton d'abonnement :
//   <button data-daat-push>🔔 Recevoir le Daat Yomi chaque jour</button>
// États gérés : non supporté (bouton masqué), permission refusée, abonné
// (le bouton devient « Notifications activées ✓ » et re-cliquer désabonne).
// L'API est servie par daatai.vercel.app (même convention que la newsletter).
(function () {
  'use strict';
  var API = (window.DAAT_CHAT_API_URL ? String(window.DAAT_CHAT_API_URL).replace(/\/api\/chat.*/, '') : 'https://daatai.vercel.app') + '/api/push';

  var TXT = {
    fr: { on: '🔔 Recevoir le Daat Yomi chaque jour', ok: '🔕 Notifications activées ✓ (toucher pour arrêter)', denied: 'Notifications bloquées par le navigateur', ios: "Installe d'abord l'app : Partager → « Sur l'écran d'accueil »" },
    he: { on: '🔔 לקבל את הדעת יומי מדי יום', ok: '🔕 התראות פעילות ✓ (לחץ לביטול)', denied: 'ההתראות חסומות בדפדפן', ios: 'התקן תחילה את האפליקציה: שיתוף ← « אל מסך הבית »' },
    en: { on: '🔔 Get the daily Daat Yomi', ok: '🔕 Notifications on ✓ (tap to stop)', denied: 'Notifications blocked by the browser', ios: 'Install the app first: Share → "Add to Home Screen"' },
  };
  function lang() {
    var l = (document.documentElement.lang || 'fr').slice(0, 2);
    return TXT[l] ? l : 'fr';
  }
  function b64ToU8(b64) {
    var pad = '='.repeat((4 - (b64.length % 4)) % 4);
    var raw = atob((b64 + pad).replace(/-/g, '+').replace(/_/g, '/'));
    var arr = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
    return arr;
  }
  function supported() {
    return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
  }
  // iOS Safari : le push n'existe que dans la PWA installée (standalone).
  function iosNeedsInstall() {
    var ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
    var standalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    return ios && !standalone;
  }

  async function getSub() {
    var reg = await navigator.serviceWorker.ready;
    return reg.pushManager.getSubscription();
  }
  async function enable() {
    var perm = await Notification.requestPermission();
    if (perm !== 'granted') throw new Error('denied');
    var keyRes = await fetch(API + '?action=key');
    var publicKey = (await keyRes.json()).publicKey;
    var reg = await navigator.serviceWorker.ready;
    var sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64ToU8(publicKey) });
    await fetch(API, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'subscribe', subscription: sub.toJSON(), lang: lang() }),
    });
    return sub;
  }
  async function disable() {
    var sub = await getSub();
    if (!sub) return;
    await fetch(API, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'unsubscribe', endpoint: sub.endpoint }),
    }).catch(function () {});
    await sub.unsubscribe();
  }

  async function paint(btn) {
    var t = TXT[lang()];
    var compact = btn.getAttribute('data-daat-push') === 'compact';
    if (!supported()) {
      if (iosNeedsInstall() && !compact) { btn.textContent = t.ios; btn.disabled = true; return; }
      btn.style.display = 'none'; return;
    }
    if (Notification.permission === 'denied') {
      if (compact) { btn.style.display = 'none'; return; }
      btn.textContent = t.denied; btn.disabled = true; return;
    }
    var sub = null;
    try { sub = await getSub(); } catch (_) {}
    if (compact) {
      btn.textContent = sub ? '🔕' : '🔔';
      btn.title = sub ? t.ok : t.on;
    } else {
      btn.textContent = sub ? t.ok : t.on;
    }
    btn.disabled = false;
    btn.dataset.state = sub ? 'on' : 'off';
  }

  function wire(btn) {
    paint(btn);
    btn.addEventListener('click', async function () {
      var t = TXT[lang()];
      btn.disabled = true;
      try {
        if (btn.dataset.state === 'on') await disable();
        else await enable();
      } catch (e) {
        if (String(e && e.message) === 'denied') { btn.textContent = t.denied; return; }
      }
      paint(btn);
    });
  }

  window.daatPush = { enable: enable, disable: disable, supported: supported };
  function init() { document.querySelectorAll('[data-daat-push]').forEach(wire); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
