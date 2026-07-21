# Chiourim — fichiers de travail

Sauvegarde des fichiers de production des chiourim vidéo du Rav Yossef Haim Samama
(sous-titres, transcriptions, textes de publication, scripts de génération).

Ces fichiers vivaient uniquement dans une copie locale non sauvegardée : ils ne
figuraient dans aucun dépôt git. Cette sauvegarde les met à l'abri.

| Dossier | Contenu |
|---|---|
| `soustitres/` | `.srt` et `.vtt` français, prêts pour YouTube |
| `transcriptions/` | sources hébraïques et sorties brutes de transcription (fichiers intermédiaires) |
| `publication/` | descriptions YouTube et posts WhatsApp |
| `scripts/` | scripts Python qui génèrent les `.srt`/`.vtt` (les sous-titres y sont codés en dur, horodatage + texte) |
| `resumes/` | résumés de cours rédigés |

## Notes

- **Contenu non révisé** : ce sont des fichiers de travail, pas des pages publiées du site.
  Ils ne sont pas passés par l'audit du dépôt (`scripts/audit-simanim.py`), qui ne
  couvre que `sources/shabbat` et `sources/yoreh-deah`.
- **Hors du site** : `.vercelignore` exclut `chiourim/` du déploiement. Ces fichiers
  sont versionnés sur GitHub (donc sauvegardés) mais **ne sont pas servis** par
  daattorah.com. `robots.txt` conserve un `Disallow: /chiourim/` en second rideau.
  Raison : les transcriptions sont des sorties brutes de reconnaissance vocale,
  fautives sur les termes halakhiques (« הלכות בורך » pour « בורר »). Servies
  depuis le domaine du Rav, elles seraient lues comme son enseignement.
- **Aucun secret** : vérifié avant publication — pas de clé d'API, pas de donnée
  personnelle, pas de numéro de téléphone ni d'adresse e-mail.
