// Session par courriel dans les pages /admin.
//
// La connexion se fait sur /connexion-admin.html (code reçu par courriel) ; le
// middleware laisse alors entrer dans /admin sans mot de passe. Ce petit script
// permet à chaque page d'en faire autant pour SES appels : si la session ouverte
// est celle d'une adresse de ADMIN_EMAILS, la page se connecte seule, et ses API
// acceptent le cookie de session — plus de mot de passe à taper.
//
// Le statut est demandé à /api/auth/me, JAMAIS à une API admin : là, une requête
// sans identifiants compte comme un échec de mot de passe (5 par IP en 15 min).
// Le mot de passe reste possible partout, exactement comme avant.
(function () {
  var S = window.DaatAdminSession = {
    active: false,
    email: '',
    // Rend une promesse : true si la session est celle d'un administrateur.
    estAdmin: function () {
      return fetch('/api/auth/me', { credentials: 'same-origin' })
        .then(function (r) { return r.ok ? r.json() : {}; })
        .then(function (j) {
          S.active = j.admin === true;
          S.email = S.active && j.user ? String(j.user.email || '') : '';
          return S.active;
        })
        .catch(function () { return false; });
    },
    // Déconnexion : ferme AUSSI la session par courriel. Sans cela, la page se
    // reconnecterait seule au rechargement. Le middleware renvoie ensuite vers
    // la page de connexion (sauf mot de passe déjà donné au navigateur).
    quitter: function () {
      var fin = function () { location.reload(); };
      try { localStorage.removeItem('daat_admin_mode'); } catch (_) {}
      fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' }).then(fin, fin);
    },
  };
})();
