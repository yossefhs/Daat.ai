# Rav Abichid Content Engine

Fondation privée et **sans publication** pour proposer un pack éditorial traçable à partir du corpus du Rav.

## Installation locale

Copier les noms de variables de `.env.example` dans l’environnement local, avec deux chemins privés hors Git : `RAVQA_DB_PATH` et `RAV_CONTENT_REGISTRY_PATH`.

```bash
npm run rav:weekly-pack
npm run rav:review
npm run test:rav
```

`rav:weekly-pack` ouvre la base source SQLite en lecture seule et n’examine que les résultats ciblés. Il ne lance aucune publication et ne traite pas le corpus média en masse. `rav:review` ouvre une interface locale de validation ; les décisions sont enregistrées dans le registre privé.

## Fiabilité et confidentialité

- GREEN : preuve audio vérifiée ou texte directement validé.
- ORANGE : transcription corrigée à valider.
- RED : source absente, brute, ambiguë ou `needs_review`; elle est bloquée.

Les questions sont anonymisées avant toute génération éditoriale. Les données sensibles identifiables sont bloquées. Ne jamais ajouter `ravqa.db`, son chemin réel, ni une donnée WhatsApp au dépôt.

## Score et anti-doublon

Le score combine calendrier (20), intérêt pratique (20), hook (15), audio (15), fiabilité (20) et fraîcheur (10). Un doublon au-delà de 80 ou une source RED obtient zéro et ne peut pas être approuvé.
