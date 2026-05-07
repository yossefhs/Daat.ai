# DAAT דעת — Plateforme d'étude halakhique

> דעת התורה לעומקה — La connaissance profonde de la Torah, du débutant au Talmid Chakham.

Initiée par le **Rav Yossef Haim Samama** — YH Community Manager.

## Structure du projet

```
daat-ai/
├── index.html                              ← Homepage
├── sources/
│   └── shabbat/
│       └── siman-246/
│           ├── index.html                  ← Siman 246 — vue d'ensemble
│           ├── niveau-1-base.html          ← Niveau 1 : Initiation (texte + traduction + explication)
│           ├── niveau-3-lamdan.html        ← Niveau 3 : Lamdan (pilpoul 13 sections)
│           ├── niveau-4-synthese.html      ← Niveau 4 : Synthèse Magistrale
│           └── pdfs/
│               ├── Siman_246_Seif_Alef_Hilkhot_Shabbat.pdf
│               ├── Siman_246_Seif_Alef_Pilpoul_Lamdan.pdf
│               └── Synthese_Magistrale_Siman_246_Seif_Alef.pdf
└── assets/
    └── css/
```

## Déploiement — Vercel

Le site est déployé sur Vercel et accessible à : `https://daattorah.com`

Configuration DNS requise chez le registrar du domaine :

```
A      @     76.76.21.21
CNAME  www   cname.vercel-dns.com
```

GitHub Pages doit rester désactivé (Settings → Pages → Source : None) pour éviter tout conflit DNS / SSL avec Vercel.

## Contenu disponible

- **Orah Haïm, Siman 246, Seif Alef** — Hilkhot Shabbat : דיני השאלה והשכרה לגוי בשבת
  - Niveau 1 : Initiation (Base accessible)
  - Niveau 3 : Lamdan (Pilpoul complet)
  - Niveau 4 : Synthèse Magistrale

## Palette graphique

- Navy : `#1A1F3A`
- Or : `#C5A55A`
- Crème : `#FAF6EE`
- Fonts : Frank Ruhl Libre + Cormorant Garamond

---

© 5786 / 2026 — DAAT.AI
