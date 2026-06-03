# Connecter OmniSocials à Claude

**OmniSocials** (https://omnisocials.com) — gestion sociale « AI-friendly ».
- **Prix** : 10 $/mo (annuel) / 12 $/mo (mensuel). Essai 14 j sans CB.
- **10 plateformes** : Instagram, Facebook, LinkedIn, YouTube, TikTok, X, Pinterest,
  Bluesky, Threads, Mastodon.
- **Ce que Claude peut faire** : rédiger, éditer, **programmer** et **publier** sur
  toute combinaison de plateformes en un message ; analytics ; audits hebdo/mensuels.
- MCP + Agent Skill = **open-source (MIT)**.

## 3 façons de connecter (choisir une)

### A. MCP local (Claude Desktop / Claude Code / Cursor / Windsurf)
```
claude mcp add omnisocials -- npx -y @omnisocials/mcp-server
```

### B. Remote MCP (claude.ai, connecteurs)
- URL du serveur : `mcp.omnisocials.com`
- Dans OmniSocials : **Settings → Integrations → Claude**, cliquer **Connect**.
- Auth **OAuth** (pas de copier-coller de clé).

### C. Agent Skill (CLI — tout agent : Claude Code, Codex, Gemini CLI…)
- Approche en ligne de commande, MIT. Voir la doc OmniSocials.

## Étapes
1. Créer un compte OmniSocials (essai gratuit).
2. **Connecter les comptes sociaux** DAAT (commencer par LinkedIn — la page « DAAT דעת »
   existe déjà — puis Instagram, Facebook, X).
3. Connecter Claude via A, B ou C ci-dessus.
4. Tester : « Programme ce post LinkedIn pour mardi 9h. »

## Sécurité
- Donner à OmniSocials l'accès **uniquement** aux comptes DAAT.
- Garder la **validation humaine** active au début (le skill `daat-social` la prévoit).

## Liens
- Intégration Claude : https://omnisocials.com/integrations/claude
- Toutes intégrations : https://omnisocials.com/integrations
- Tarifs : https://omnisocials.com/pricing
