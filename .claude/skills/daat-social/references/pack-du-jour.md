# Pack du jour — playbook (stratégie de croissance DAAT)

Objectif : faire connaître daattorah.com **au maximum**, sous ses meilleurs angles, et
faire rentrer de quoi payer l'infrastructure (tokens IA, hébergement) — sans jamais
trahir la rigueur (on ne tranche pas de halakha ; toujours « consulte ton Rav »).

Le moteur est `api/_pack.js` (déterministe, enrichi du corpus — zéro token IA), servi
par **`/api/daily-pack`** en production (page mobile, boutons « Copier », protégée par
CRON_SECRET) et par `scripts/pack-du-jour.js` en local. Ce document dit **comment s'en
servir intelligemment** et **comment aller plus loin**.

---

## 1. Les 7 angles (un par jour, jamais lassant)

Le même siman présenté différemment chaque jour. Le script choisit l'angle par le jour
de la semaine ; on peut forcer avec `--day 0..6`.

| # | Angle | Ce qu'on montre | Réseau fort |
|---|-------|-----------------|-------------|
| 0 dim | La question concrète | un cas du vendredi après-midi | IG / FB |
| 1 lun | Le mot juste | définir un terme de halakha | LinkedIn |
| 2 mar | D'où ça vient | Talmud → Choulhan Aroukh | LinkedIn / X |
| 3 mer | La nuance qui change tout | 2 cas proches, 1 différence | X / IG |
| 4 jeu | Cas pratique | application moderne | FB / IG |
| 5 ven | Les 4 niveaux | la profondeur unique du site | tous (avant Shabbat) |
| 6 sam→motzei | La chitah de l'Admour HaZaken | le niveau 4 (Daat HaRav) | LinkedIn / Telegram |

**Enrichir (le vrai travail de qualité)** : le script met une accroche générique.
Pour un post qui *donne envie*, remplacer par le concept réel du siman, lu dans
`sources/shabbat/siman-{N}/niveau-1-base.html` (cas pratiques, terme hébreu clé,
mahloket). Règle absolue : **citer la source, jamais inventer de din.**

---

## 2. La monétisation qui tourne (⑦)

Le pack finit toujours par UN appel, choisi en rotation (par `siman + jour`) pour ne
jamais spammer le même message. Les 5 offres, toutes réelles sur le site :

1. **Dédicace** — dédier l'étude (לעילוי נשמת / refoua / hatzlacha). Le nom paraît sur
   la page. → `soutenir.html` · le plus puissant dans une communauté Torah.
2. **Don 18 €** = « une semaine d'étude offerte à tous ». → HelloAsso formulaire 9.
3. **Mécénat 36 €/mois** — fait vivre la plateforme + l'IA gratuite. → `soutenir.html`.
4. **Chat Da'at** (gratuit) — capte l'usage, crée l'attachement avant de demander. → `chat.html`.
5. **Newsletter** — « le siman du dimanche », audience possédée. → bas de `daattorah.com`.

Principe marketing : **80 % valeur, 20 % demande.** On donne (enseignement, chat gratuit)
bien plus qu'on ne demande. La dédicace convertit mieux qu'un don sec parce qu'elle
répond à un besoin réel (mémoire d'un proche, refoua).

---

## 3. Le rythme de la semaine (1 siman, 6 sorties)

Étaler UN siman sur la semaine, un réseau par jour — cohérent avec l'autopilot (mardi)
et la newsletter (dimanche) :

- **Dim** — newsletter (auto) + accroche « question » en story.
- **Lun** — LinkedIn (angle « mot juste »).
- **Mar** — autopilot social (auto) ; renforcer avec le fil X/Bluesky.
- **Mer** — Instagram carrousel (angle « nuance »).
- **Jeu** — Facebook (angle « cas pratique »).
- **Ven** — message communauté WhatsApp/Telegram **avant Shabbat** + rappel « 4 niveaux ».
- **Motzei Shabbat** — angle « Daat HaRav » (public lamdan).

Générer les 6 en une session le dimanche (`--day` 0→6), programmer/coller au fil.

---

## 4. Faire connaître le site « sous ses meilleurs angles »

Ce qui distingue DAAT — à marteler dans les posts :
- **4 niveaux** du même texte (base → lamdan → synthèse → Daat HaRav) : personne d'autre.
- **Trilingue** FR / HE / EN — élargir à trois publics.
- **Chat IA sourcé** sur le corpus du Rav : essayer gratuitement = accrocher.
- **Le blog** répond aux vraies questions Google (« réchauffer un plat Shabbat », « borer »…) :
  c'est la porte d'entrée SEO. Toujours lier l'article quand il existe (le script le fait).
- Voix : sérieuse, jamais putaclic ; on respecte l'intelligence du lecteur.

## 5. Boucle de croissance (le stratagème)

`Contenu utile (SEO/social) → visite → chat gratuit / newsletter → habitude →
dédicace/soutien → finance les tokens → plus de contenu`.
Chaque pack alimente au moins deux points de cette boucle : la **découverte** (post) et
la **capture** (newsletter/chat) ou la **monétisation** (⑦). Ne jamais poster sans au
moins un lien de capture ou de soutien.

---

## 6. Checklist avant publication (garde-fous)
- [ ] Aucun psak tranché ; « consulte ton Rav » présent sur tout cas pratique.
- [ ] Lien de capture OU de soutien présent (jamais un post « cul-de-sac »).
- [ ] Une variante par réseau (pas de copié-collé inter-plateformes).
- [ ] Concept ancré dans la source si on a enrichi (pas d'invention).
- [ ] Niveau 4 présenté comme la *chitah de l'Admour HaZaken*, pas comme obligation.
