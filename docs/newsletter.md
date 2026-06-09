# Newsletter DAAT — fonctionnement

## Ce qui est en place
1. **Inscription** : formulaire d'accueil → `POST /api/newsletter` → stocke l'email (KV) + envoie l'email de bienvenue (J0).
2. **Séquence d'accueil** : 5 emails sur 14 jours (J0, J3, J7, J10, J14) — `api/_email-sequence.js`.
3. **Broadcast hebdomadaire « le siman du dimanche »** *(nouveau)* : chaque **dimanche**, le cron envoie à **tous les abonnés confirmés** le siman de la semaine (ordre **242 → 365**), avec lien d'étude `/oh/N/` et — si l'article existe — un lien vers le blog. Module : `api/_newsletter-weekly.js`.

Le cron Vercel (`vercel.json`, `0 9 * * *`, quotidien 09:00 UTC) fait avancer la séquence **et**, le dimanche, déclenche le broadcast (idempotent : un seul envoi par jour).

## Variables d'environnement requises (Vercel)
- `RESEND_API_KEY` — clé Resend (obligatoire pour tout envoi).
- `RESEND_FROM_EMAIL` — ex. `bonjour@daattorah.com` (défaut `noreply@daattorah.com`). **Le domaine doit être vérifié dans Resend** (SPF/DKIM) sinon les emails partent en spam / sont rejetés.
- `CRON_SECRET` — secret partagé ; Vercel l'envoie en `Authorization: Bearer …` sur le cron, et il sert aussi à déclencher les actions admin ci-dessous.

## Vérifier / tester (avant la 1re diffusion)
Remplace `SECRET` par la valeur de `CRON_SECRET`. Origine API : `https://daattorah.com` (ou `https://daatai.vercel.app`).

- **Prévisualiser** l'email (HTML, dans le navigateur), sans rien envoyer :
  `https://daattorah.com/api/newsletter?action=weekly-preview&secret=SECRET`
- **Envoi de test** à une seule adresse (n'avance pas le curseur) :
  `https://daattorah.com/api/newsletter?action=weekly-test&to=toi@exemple.com&secret=SECRET`
- **Forcer** la 1re diffusion réelle maintenant (à tous, avance le curseur) :
  `https://daattorah.com/api/newsletter?action=weekly-force&secret=SECRET`

> Une fois validé, **rien d'autre à faire** : le cron envoie automatiquement chaque dimanche, en avançant de siman en siman.

## État stocké (Vercel KV)
- `newsletter:{email}` → `{ email, subscribedAt, confirmed, sentSteps[] }`
- `newsletter:list` → liste des emails
- `newsletter:weekly:cursor` → prochain siman à envoyer (défaut 242)
- `newsletter:weekly:lastSentDate` → `YYYY-MM-DD` du dernier broadcast (anti-doublon)

## Notes
- **Single opt-in** pour l'instant (`confirmed: true` à l'inscription).
- Pour repartir d'un autre siman : poser `newsletter:weekly:cursor` à la valeur voulue dans KV.
- Après le siman 365, le broadcast s'arrête (série terminée) — à faire évoluer si on étend le corpus.
