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

/* =====================================================================
 * CAPTURE EMAIL « Garde ta progression » — au pic d'engagement.
 *
 * Affiché à la fin d'une page de niveau si :
 *   - l'utilisateur N'EST PAS connecté (GET /api/auth/me → 401)
 *   - il a déjà étudié ≥ 3 niveaux au total (investissement réel)
 *   - il n'a pas fermé le bloc dans les 14 derniers jours
 *
 * Réutilise l'OTP existant (send-code / verify-code) en inline, sans
 * dépendre de daat-auth.js (non chargé sur les pages de niveau). À la
 * connexion réussie, la progression localStorage est poussée vers KV.
 * ===================================================================== */
(function () {
  'use strict';

  var KEY = 'daat-progress-v2';
  var DISMISS_KEY = 'daat-save-cta-dismissed';
  var DISMISS_DAYS = 14;
  var MIN_LEVELS = 3;
  var API_BASE = (window.DAAT_CHAT_API_URL || '').replace(/\/api\/chat\/?$/, '');
  if (!API_BASE) return;

  // N'afficher que sur une page de niveau
  var path = window.location.pathname;
  var isLevelPage = /\/(base|lamdan|synthese|daat-harav)(\/|$)/.test(path) ||
                    /niveau-[1-4]-/.test(path);
  if (!isLevelPage) return;

  // Récemment fermé ?
  try {
    var t = parseInt(localStorage.getItem(DISMISS_KEY) || '0', 10);
    if (t && (Date.now() - t) < DISMISS_DAYS * 864e5) return;
  } catch (e) {}

  // Compter les niveaux étudiés
  var totalLevels = 0, progressData = {};
  try {
    progressData = JSON.parse(localStorage.getItem(KEY) || '{}');
    for (var s in progressData) {
      if (Array.isArray(progressData[s])) totalLevels += progressData[s].length;
    }
  } catch (e) {}
  if (totalLevels < MIN_LEVELS) return;

  // i18n
  var L = (document.documentElement.lang || 'fr').slice(0, 2).toLowerCase();
  if (L !== 'he' && L !== 'en') L = 'fr';
  var T = {
    fr: {
      title: '✓ Tu as déjà étudié ' + totalLevels + ' niveaux',
      body: 'Crée ton compte en 10 secondes pour retrouver ta progression sur tous tes appareils — et recevoir le Daat Yomi chaque matin (optionnel).',
      placeholder: 'ton@email.com',
      send: 'Sauvegarder ma progression',
      sending: 'Envoi…',
      codeBody: 'Entre le code à 6 chiffres reçu par email :',
      codePlaceholder: '123456',
      verify: 'Valider',
      verifying: 'Vérification…',
      success: '✓ Progression sauvegardée sur ton compte. Tu la retrouveras partout.',
      errInvalid: 'Adresse email invalide.',
      err6: 'Le code doit faire 6 chiffres.',
      dismiss: 'Plus tard',
    },
    he: {
      title: '✓ כבר למדת ' + totalLevels + ' רמות',
      body: 'צור חשבון ב-10 שניות כדי לשמור את ההתקדמות שלך בכל המכשירים — ולקבל את הדעת יומי בכל בוקר (אופציונלי).',
      placeholder: 'your@email.com',
      send: 'שמור את ההתקדמות שלי',
      sending: 'שולח…',
      codeBody: 'הזן את הקוד בן 6 הספרות שקיבלת במייל:',
      codePlaceholder: '123456',
      verify: 'אישור',
      verifying: 'מאמת…',
      success: '✓ ההתקדמות נשמרה בחשבונך. תמצא אותה בכל מקום.',
      errInvalid: 'כתובת אימייל לא תקינה.',
      err6: 'הקוד צריך להיות בן 6 ספרות.',
      dismiss: 'אחר כך',
    },
    en: {
      title: '✓ You\'ve already studied ' + totalLevels + ' levels',
      body: 'Create your account in 10 seconds to keep your progress across all your devices — and receive the Daat Yomi every morning (optional).',
      placeholder: 'your@email.com',
      send: 'Save my progress',
      sending: 'Sending…',
      codeBody: 'Enter the 6-digit code sent to your email:',
      codePlaceholder: '123456',
      verify: 'Verify',
      verifying: 'Verifying…',
      success: '✓ Progress saved to your account. You\'ll find it everywhere.',
      errInvalid: 'Invalid email address.',
      err6: 'The code must be 6 digits.',
      dismiss: 'Later',
    },
  }[L];

  var isRTL = (L === 'he');

  // Vérifier l'état de connexion avant d'afficher quoi que ce soit
  fetch(API_BASE + '/api/auth/me', { credentials: 'include' })
    .then(function (r) {
      if (r.ok) return null;        // déjà connecté → ne rien afficher
      if (r.status === 401) return 'anon';
      return null;
    })
    .then(function (state) {
      if (state === 'anon') injectBlock();
    })
    .catch(function () { /* offline — silence */ });

  function injectBlock() {
    var box = document.createElement('div');
    box.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
    box.style.cssText =
      'max-width:640px;margin:32px auto;padding:24px 28px;border:1px solid #C5A55A;' +
      'border-radius:8px;background:linear-gradient(135deg,#FBF7EF,#FFF8E5);' +
      'font-family:Inter,system-ui,sans-serif;text-align:' + (isRTL ? 'right' : 'left') +
      ';box-shadow:0 2px 12px rgba(26,31,58,0.08);';

    box.innerHTML =
      '<div style="font-size:17px;font-weight:600;color:#1A1F3A;margin-bottom:8px;">' + T.title + '</div>' +
      '<div style="font-size:14px;color:#5a5a5a;line-height:1.6;margin-bottom:16px;">' + T.body + '</div>' +
      '<div data-step="email">' +
        '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
          '<input type="email" inputmode="email" autocomplete="email" placeholder="' + T.placeholder + '" ' +
            'style="flex:1;min-width:180px;padding:11px 14px;border:1px solid #d8cdb0;border-radius:5px;font-size:15px;font-family:inherit;">' +
          '<button type="button" style="padding:11px 20px;background:#1A1F3A;color:#C5A55A;border:none;border-radius:5px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;white-space:nowrap;">' + T.send + '</button>' +
        '</div>' +
        '<div class="cta-err" style="color:#a33;font-size:13px;margin-top:8px;min-height:1px;"></div>' +
      '</div>' +
      '<div data-step="code" style="display:none;">' +
        '<div style="font-size:14px;color:#5a5a5a;margin-bottom:10px;">' + T.codeBody + '</div>' +
        '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
          '<input type="text" inputmode="numeric" maxlength="6" placeholder="' + T.codePlaceholder + '" ' +
            'style="flex:1;min-width:120px;padding:11px 14px;border:1px solid #d8cdb0;border-radius:5px;font-size:18px;letter-spacing:3px;font-family:inherit;text-align:center;">' +
          '<button type="button" style="padding:11px 20px;background:#1A1F3A;color:#C5A55A;border:none;border-radius:5px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;white-space:nowrap;">' + T.verify + '</button>' +
        '</div>' +
        '<div class="cta-err" style="color:#a33;font-size:13px;margin-top:8px;min-height:1px;"></div>' +
      '</div>' +
      '<div data-step="done" style="display:none;font-size:15px;color:#2a7;font-weight:600;"></div>' +
      '<button type="button" class="cta-dismiss" style="margin-top:12px;background:none;border:none;color:#998;font-size:12px;cursor:pointer;text-decoration:underline;font-family:inherit;padding:0;">' + T.dismiss + '</button>';

    // Point d'insertion : avant le watermark, sinon avant le next-siman-nav,
    // sinon dans <main>, sinon fin de <body>.
    var anchor = document.querySelector('.yh-watermark') ||
                 document.querySelector('.next-siman-nav') ||
                 document.querySelector('main');
    if (anchor && anchor.parentNode && anchor.className !== 'yh-watermark' && !anchor.classList.contains('next-siman-nav')) {
      anchor.appendChild(box); // dans <main>
    } else if (anchor && anchor.parentNode) {
      anchor.parentNode.insertBefore(box, anchor); // avant watermark/nav
    } else {
      document.body.appendChild(box);
    }

    var emailStep = box.querySelector('[data-step="email"]');
    var codeStep = box.querySelector('[data-step="code"]');
    var doneStep = box.querySelector('[data-step="done"]');
    var emailInput = emailStep.querySelector('input');
    var emailBtn = emailStep.querySelector('button');
    var emailErr = emailStep.querySelector('.cta-err');
    var codeInput = codeStep.querySelector('input');
    var codeBtn = codeStep.querySelector('button');
    var codeErr = codeStep.querySelector('.cta-err');
    var currentEmail = '';

    box.querySelector('.cta-dismiss').addEventListener('click', function () {
      try { localStorage.setItem(DISMISS_KEY, String(Date.now())); } catch (e) {}
      box.remove();
    });

    function sendCode() {
      var email = (emailInput.value || '').trim().toLowerCase();
      emailErr.textContent = '';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { emailErr.textContent = T.errInvalid; return; }
      emailBtn.disabled = true; var orig = emailBtn.textContent; emailBtn.textContent = T.sending;
      fetch(API_BASE + '/api/auth/send-code', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.d.error || 'Erreur');
        currentEmail = email;
        emailStep.style.display = 'none';
        codeStep.style.display = '';
        setTimeout(function () { codeInput.focus(); }, 80);
      })
      .catch(function (err) { emailErr.textContent = err.message; })
      .finally(function () { emailBtn.disabled = false; emailBtn.textContent = orig; });
    }

    function verifyCode() {
      var code = (codeInput.value || '').trim();
      codeErr.textContent = '';
      if (!/^\d{6}$/.test(code)) { codeErr.textContent = T.err6; return; }
      codeBtn.disabled = true; var orig = codeBtn.textContent; codeBtn.textContent = T.verifying;
      fetch(API_BASE + '/api/auth/verify-code', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: currentEmail, code: code }),
      })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.d.error || 'Erreur');
        // Connecté → pousser toute la progression locale vers KV
        try {
          fetch(API_BASE + '/api/progress', {
            method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ progress: progressData }),
          }).catch(function () {});
        } catch (e) {}
        emailStep.style.display = 'none';
        codeStep.style.display = 'none';
        doneStep.style.display = '';
        doneStep.textContent = T.success;
      })
      .catch(function (err) { codeErr.textContent = err.message; })
      .finally(function () { codeBtn.disabled = false; codeBtn.textContent = orig; });
    }

    emailBtn.addEventListener('click', sendCode);
    emailInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') sendCode(); });
    codeBtn.addEventListener('click', verifyCode);
    codeInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') verifyCode(); });
  }
})();
