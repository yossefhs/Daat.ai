// DAAT Auth — client OTP par email
// Expose window.daatAuth { openLogin, logout, getUser, refresh, onChange }
// Injecte automatiquement le bouton "Se connecter / Mon compte" dans le <header>

(function () {
  'use strict';

  const STORAGE_KEY = 'daat-auth-user-v1';
  const listeners = new Set();
  let currentUser = null;

  // === i18n ===
  // Detecte la langue via <html lang="..."> (fallback : fr)
  const LANG = (function () {
    const l = (document.documentElement.lang || 'fr').toLowerCase();
    if (l.startsWith('he')) return 'he';
    if (l.startsWith('en')) return 'en';
    return 'fr';
  })();

  const I18N = {
    fr: {
      loginBtn: '🔑 Se connecter',
      logoutBtn: 'Se déconnecter',
      logoutConfirm: 'Se déconnecter de DAAT ?',
      dialogLabel: 'Connexion DAAT',
      closeLabel: 'Fermer',
      title: 'Se connecter à DAAT',
      step1Text: "Entre ton email — on t'envoie un code à 6 chiffres pour te connecter. <strong>Pas de mot de passe.</strong>",
      emailLabel: 'Adresse email',
      emailPlaceholder: 'ton-email@example.com',
      sendBtn: 'Recevoir un code →',
      sendingBtn: 'Envoi…',
      step2Text: 'Code envoyé à <strong id="daat-auth-email-recap"></strong>. Vérifie ta boîte mail (et les spams).',
      codeLabel: 'Code à 6 chiffres',
      codePlaceholder: '——————',
      verifyBtn: 'Vérifier →',
      verifyingBtn: 'Vérification…',
      resendBtn: '↻ Renvoyer un code',
      backBtn: "← Changer d'email",
      footer: '🔒 On ne stocke que ton email. Pas de mot de passe, pas de tracking.',
      errEmpty: 'Entre ton email.',
      errInvalid: 'Adresse email invalide.',
      err6Digits: 'Le code doit faire 6 chiffres.',
    },
    he: {
      loginBtn: '🔑 התחבר',
      logoutBtn: 'התנתק',
      logoutConfirm: 'להתנתק מדעת?',
      dialogLabel: 'התחברות דעת',
      closeLabel: 'סגור',
      title: 'התחבר לדעת',
      step1Text: 'הזן את האימייל שלך — נשלח אליך קוד בן 6 ספרות לכניסה. <strong>בלי סיסמה.</strong>',
      emailLabel: 'כתובת אימייל',
      emailPlaceholder: 'your-email@example.com',
      sendBtn: 'קבל קוד →',
      sendingBtn: 'שולח…',
      step2Text: 'הקוד נשלח אל <strong id="daat-auth-email-recap"></strong>. בדוק את תיבת הדואר (וגם בספאם).',
      codeLabel: 'קוד בן 6 ספרות',
      codePlaceholder: '——————',
      verifyBtn: 'אמת →',
      verifyingBtn: 'מאמת…',
      resendBtn: '↻ שלח קוד מחדש',
      backBtn: '← שנה אימייל',
      footer: '🔒 שומרים רק את האימייל. בלי סיסמה, בלי מעקב.',
      errEmpty: 'הזן את האימייל שלך.',
      errInvalid: 'כתובת אימייל לא תקינה.',
      err6Digits: 'הקוד חייב להיות בן 6 ספרות.',
    },
    en: {
      loginBtn: '🔑 Sign in',
      logoutBtn: 'Sign out',
      logoutConfirm: 'Sign out of DAAT?',
      dialogLabel: 'DAAT sign-in',
      closeLabel: 'Close',
      title: 'Sign in to DAAT',
      step1Text: "Enter your email — we'll send you a 6-digit code to sign in. <strong>No password.</strong>",
      emailLabel: 'Email address',
      emailPlaceholder: 'your-email@example.com',
      sendBtn: 'Send code →',
      sendingBtn: 'Sending…',
      step2Text: 'Code sent to <strong id="daat-auth-email-recap"></strong>. Check your inbox (and spam).',
      codeLabel: '6-digit code',
      codePlaceholder: '——————',
      verifyBtn: 'Verify →',
      verifyingBtn: 'Verifying…',
      resendBtn: '↻ Resend code',
      backBtn: '← Change email',
      footer: '🔒 We only store your email. No password, no tracking.',
      errEmpty: 'Enter your email.',
      errInvalid: 'Invalid email address.',
      err6Digits: 'Code must be 6 digits.',
    },
  };
  const T = I18N[LANG] || I18N.fr;

  // Hydrate cache
  try {
    const cached = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
    if (cached && cached.email) currentUser = cached;
  } catch (_) {}

  function notify() {
    listeners.forEach(cb => {
      try { cb(currentUser); } catch (_) {}
    });
  }

  function setUser(user) {
    currentUser = user || null;
    if (user) {
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(user)); } catch (_) {}
    } else {
      try { localStorage.removeItem(STORAGE_KEY); } catch (_) {}
    }
    notify();
  }

  async function refresh() {
    try {
      const res = await fetch('https://daatai.vercel.app/api/auth/me', { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
      } else if (res.status === 401) {
        setUser(null);
      }
    } catch (_) {
      // Network error — keep cached user (offline-friendly)
    }
  }

  async function logout() {
    try {
      await fetch('https://daatai.vercel.app/api/auth/logout', { method: 'POST', credentials: 'include' });
    } catch (_) {}
    setUser(null);
  }

  // === MODAL ===

  function buildModal() {
    if (document.getElementById('daat-auth-modal')) return;
    const m = document.createElement('div');
    m.id = 'daat-auth-modal';
    m.className = 'daat-auth-modal';
    const dir = LANG === 'he' ? 'rtl' : 'ltr';
    m.innerHTML = `
      <div class="daat-auth-overlay" data-close></div>
      <div class="daat-auth-dialog" role="dialog" aria-modal="true" aria-label="${T.dialogLabel}" dir="${dir}">
        <button class="daat-auth-close" data-close aria-label="${T.closeLabel}">×</button>
        <div class="daat-auth-header">
          <span class="daat-auth-logo">דעת</span>
          <span class="daat-auth-title">${T.title}</span>
        </div>
        <div class="daat-auth-body">
          <div class="daat-auth-step is-active" data-step="email">
            <p class="daat-auth-text">${T.step1Text}</p>
            <label class="daat-auth-label" for="daat-auth-email">${T.emailLabel}</label>
            <input type="email" class="daat-auth-input" id="daat-auth-email" placeholder="${T.emailPlaceholder}" autocomplete="email" />
            <button class="daat-auth-submit" id="daat-auth-send">${T.sendBtn}</button>
            <div class="daat-auth-error" id="daat-auth-err1" aria-live="polite"></div>
          </div>
          <div class="daat-auth-step" data-step="code">
            <p class="daat-auth-text">${T.step2Text}</p>
            <label class="daat-auth-label" for="daat-auth-code">${T.codeLabel}</label>
            <input type="text" class="daat-auth-input daat-auth-code-input" id="daat-auth-code" placeholder="${T.codePlaceholder}" maxlength="6" inputmode="numeric" pattern="\\d{6}" autocomplete="one-time-code" />
            <button class="daat-auth-submit" id="daat-auth-verify">${T.verifyBtn}</button>
            <button class="daat-auth-link" id="daat-auth-resend">${T.resendBtn}</button>
            <button class="daat-auth-link" id="daat-auth-back">${T.backBtn}</button>
            <div class="daat-auth-error" id="daat-auth-err2" aria-live="polite"></div>
          </div>
        </div>
        <div class="daat-auth-footer">
          ${T.footer}
        </div>
      </div>
    `;
    document.body.appendChild(m);

    m.querySelectorAll('[data-close]').forEach(el => {
      el.addEventListener('click', closeModal);
    });

    // Step 1 — Send code
    const $emailInput = document.getElementById('daat-auth-email');
    const $sendBtn = document.getElementById('daat-auth-send');
    const $err1 = document.getElementById('daat-auth-err1');

    async function sendCode() {
      const email = $emailInput.value.trim().toLowerCase();
      $err1.textContent = '';
      if (!email) { $err1.textContent = T.errEmpty; return; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        $err1.textContent = T.errInvalid;
        return;
      }
      $sendBtn.disabled = true;
      const originalText = $sendBtn.textContent;
      $sendBtn.textContent = T.sendingBtn;
      try {
        const res = await fetch('https://daatai.vercel.app/api/auth/send-code', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
        // Move to step 2
        const $recap = document.getElementById('daat-auth-email-recap');
        $recap.textContent = email;
        $recap.dataset.email = email;
        document.querySelector('[data-step="email"]').classList.remove('is-active');
        document.querySelector('[data-step="code"]').classList.add('is-active');
        setTimeout(() => document.getElementById('daat-auth-code').focus(), 100);
      } catch (err) {
        $err1.textContent = err.message;
      } finally {
        $sendBtn.disabled = false;
        $sendBtn.textContent = originalText;
      }
    }

    $sendBtn.addEventListener('click', sendCode);
    $emailInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') sendCode();
    });

    // Step 2 — Verify code
    const $codeInput = document.getElementById('daat-auth-code');
    const $verifyBtn = document.getElementById('daat-auth-verify');
    const $err2 = document.getElementById('daat-auth-err2');

    async function verifyCode() {
      const email = document.getElementById('daat-auth-email-recap').dataset.email;
      const code = $codeInput.value.trim();
      $err2.textContent = '';
      if (!/^\d{6}$/.test(code)) {
        $err2.textContent = T.err6Digits;
        return;
      }
      $verifyBtn.disabled = true;
      const originalText = $verifyBtn.textContent;
      $verifyBtn.textContent = T.verifyingBtn;
      try {
        const res = await fetch('https://daatai.vercel.app/api/auth/verify-code', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email, code }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
        setUser(data.user);
        closeModal();
      } catch (err) {
        $err2.textContent = err.message;
      } finally {
        $verifyBtn.disabled = false;
        $verifyBtn.textContent = originalText;
      }
    }

    $verifyBtn.addEventListener('click', verifyCode);
    $codeInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') verifyCode();
    });
    // Auto-format : keep only digits
    $codeInput.addEventListener('input', () => {
      $codeInput.value = $codeInput.value.replace(/\D/g, '').slice(0, 6);
    });

    // Resend
    document.getElementById('daat-auth-resend').addEventListener('click', () => {
      const email = document.getElementById('daat-auth-email-recap').dataset.email;
      if (email) {
        $emailInput.value = email;
        document.querySelector('[data-step="code"]').classList.remove('is-active');
        document.querySelector('[data-step="email"]').classList.add('is-active');
        sendCode();
      }
    });

    // Back to email step
    document.getElementById('daat-auth-back').addEventListener('click', () => {
      $codeInput.value = '';
      $err2.textContent = '';
      document.querySelector('[data-step="code"]').classList.remove('is-active');
      document.querySelector('[data-step="email"]').classList.add('is-active');
      setTimeout(() => $emailInput.focus(), 100);
    });

    // Close on Escape
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && m.classList.contains('is-open')) closeModal();
    });
  }

  function openModal() {
    buildModal();
    const m = document.getElementById('daat-auth-modal');
    m.classList.add('is-open');
    setTimeout(() => {
      const inp = document.getElementById('daat-auth-email');
      if (inp) inp.focus();
    }, 100);
  }

  function closeModal() {
    const m = document.getElementById('daat-auth-modal');
    if (m) m.classList.remove('is-open');
  }

  // === HEADER BUTTON ===

  function injectAuthButton() {
    // Trouve un parent dans le header de la page (pas le widget chat)
    const candidates = [
      'header nav',
      'header .header-actions',
    ];
    let target = null;
    for (const sel of candidates) {
      const el = document.querySelector(sel);
      if (el) { target = el; break; }
    }
    if (!target) return;

    if (target.querySelector('.daat-auth-btn-container')) return;

    const container = document.createElement('span');
    container.className = 'daat-auth-btn-container';
    target.appendChild(container);

    function render() {
      if (currentUser && currentUser.email) {
        const initial = currentUser.email[0].toUpperCase();
        const username = currentUser.email.split('@')[0];
        container.innerHTML = `
          <span class="daat-auth-user-info" title="${currentUser.email}">
            <span class="daat-auth-user-avatar">${initial}</span>
            <span class="daat-auth-user-email">${username}</span>
          </span>
          <button class="daat-auth-logout-btn" title="${T.logoutBtn}" aria-label="${T.logoutBtn}">↪</button>
        `;
        const logoutBtn = container.querySelector('.daat-auth-logout-btn');
        if (logoutBtn) logoutBtn.addEventListener('click', () => {
          if (confirm(T.logoutConfirm)) logout();
        });
      } else {
        container.innerHTML = `
          <button class="daat-auth-login-btn">${T.loginBtn}</button>
        `;
        const btn = container.querySelector('.daat-auth-login-btn');
        if (btn) btn.addEventListener('click', openModal);
      }
    }
    render();
    listeners.add(render);
  }

  // === PUBLIC API ===

  window.daatAuth = {
    openLogin: openModal,
    logout,
    getUser: () => currentUser,
    refresh,
    onChange: cb => listeners.add(cb),
  };

  // === INIT ===

  function init() {
    injectAuthButton();
    refresh();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
