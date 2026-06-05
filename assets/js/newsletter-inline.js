/* DAAT — inscription newsletter inline (auto-initialisé).
   Branche tout <form data-daat-newsletter> de la page sur l'API newsletter.
   Aucune dépendance. */
(function () {
  var API = 'https://daatai.vercel.app/api/newsletter';

  function wire(form) {
    if (form.__daatWired) return;
    form.__daatWired = true;
    var msg = form.parentNode.querySelector('.newsletter-box-msg');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type="email"]');
      var btn = form.querySelector('button');
      var email = (input && input.value || '').trim();
      if (!email) return;
      if (btn) { btn.disabled = true; }
      var ok = (form.getAttribute('data-ok-text')) || 'Merci ! Tu es inscrit. À dimanche 🕯️';
      var ko = (form.getAttribute('data-ko-text')) || 'Une erreur est survenue. Réessaie.';
      fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, source: form.getAttribute('data-source') || 'blog' }),
      })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { return { status: r.status, d: d }; }); })
        .then(function (res) {
          if (res.status >= 200 && res.status < 300) {
            if (msg) { msg.textContent = ok; msg.style.color = '#2E7D52'; }
            form.reset();
          } else {
            if (msg) { msg.textContent = (res.d && res.d.error) || ko; msg.style.color = '#B23A48'; }
            if (btn) btn.disabled = false;
          }
        })
        .catch(function () {
          if (msg) { msg.textContent = ko; msg.style.color = '#B23A48'; }
          if (btn) btn.disabled = false;
        });
    });
  }

  function init() {
    var forms = document.querySelectorAll('form[data-daat-newsletter]');
    for (var i = 0; i < forms.length; i++) wire(forms[i]);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
