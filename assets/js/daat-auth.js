// DAAT Auth — client OTP par email
// Expose window.daatAuth { openLogin, logout, getUser, refresh, onChange }
// Injecte automatiquement le bouton "Se connecter / Mon compte" dans le <header>

(function () {
  'use strict';

  const STORAGE_KEY = 'daat-auth-user-v1';
  const listeners = new Set();
  let currentUser = null;

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
    m.innerHTML = `
      <div class="daat-auth-overlay" data-close></div>
      <div class="daat-auth-dialog" role="dialog" aria-modal="true" aria-label="Connexion DAAT">
        <button class="daat-auth-close" data-close aria-label="Fermer">×</button>
        <div class="daat-auth-header">
          <span class="daat-auth-logo">דעת</span>
          <span class="daat-auth-title">Se connecter à DAAT</span>
        </div>
        <div class="daat-auth-body">
          <div class="daat-auth-step is-active" data-step="email">
            <p class="daat-auth-text">Entre ton email — on t'envoie un code à 6 chiffres pour te connecter. <strong>Pas de mot de passe.</strong></p>
            <label class="daat-auth-label" for="daat-auth-email">Adresse email</label>
            <input type="email" class="daat-auth-input" id="daat-auth-email" placeholder="ton-email@example.com" autocomplete="email" />
            <button class="daat-auth-submit" id="daat-auth-send">Recevoir un code →</button>
            <div class="daat-auth-error" id="daat-auth-err1" aria-live="polite"></div>
          </div>
          <div class="daat-auth-step" data-step="code">
            <p class="daat-auth-text">Code envoyé à <strong id="daat-auth-email-recap"></strong>. Vérifie ta boîte mail (et les spams).</p>
            <label class="daat-auth-label" for="daat-auth-code">Code à 6 chiffres</label>
            <input type="text" class="daat-auth-input daat-auth-code-input" id="daat-auth-code" placeholder="——————" maxlength="6" inputmode="numeric" pattern="\\d{6}" autocomplete="one-time-code" />
            <button class="daat-auth-submit" id="daat-auth-verify">Vérifier →</button>
            <button class="daat-auth-link" id="daat-auth-resend">↻ Renvoyer un code</button>
            <button class="daat-auth-link" id="daat-auth-back">← Changer d'email</button>
            <div class="daat-auth-error" id="daat-auth-err2" aria-live="polite"></div>
          </div>
        </div>
        <div class="daat-auth-footer">
          🔒 On ne stocke que ton email. Pas de mot de passe, pas de tracking.
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
      if (!email) { $err1.textContent = 'Entre ton email.'; return; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        $err1.textContent = 'Adresse email invalide.';
        return;
      }
      $sendBtn.disabled = true;
      const originalText = $sendBtn.textContent;
      $sendBtn.textContent = 'Envoi…';
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
        $err2.textContent = 'Le code doit faire 6 chiffres.';
        return;
      }
      $verifyBtn.disabled = true;
      const originalText = $verifyBtn.textContent;
      $verifyBtn.textContent = 'Vérification…';
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
          <button class="daat-auth-logout-btn" title="Se déconnecter" aria-label="Se déconnecter">↪</button>
        `;
        const logoutBtn = container.querySelector('.daat-auth-logout-btn');
        if (logoutBtn) logoutBtn.addEventListener('click', () => {
          if (confirm('Se déconnecter de DAAT ?')) logout();
        });
      } else {
        container.innerHTML = `
          <button class="daat-auth-login-btn">🔑 Se connecter</button>
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
