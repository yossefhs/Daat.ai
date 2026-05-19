#!/bin/bash
# SessionStart hook — prépare l'environnement Claude Code (web).
#
# 1. Installe les dépendances npm (fonctions serverless api/ + scripts de build)
#    afin que les commandes de build fonctionnent dès le début de la session.
# 2. Affiche l'audit de l'état des simanim de Hilkhot Shabbat
#    (scripts/audit-simanim.py) : boilerplate non réécrit, fichiers absents,
#    TOC désynchronisée. Garde-fou pour ne pas considérer « complété » un
#    siman encore générique.
#
# Le hook ne tourne qu'en environnement distant (Claude Code on the web) ;
# en local l'environnement de développement est déjà configuré.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# --- Dépendances npm ---------------------------------------------------------
# `npm install` (et non `npm ci`) : idempotent et tire parti du cache du
# conteneur entre les sessions.
echo "session-start : installation des dépendances npm…"
npm install --no-audit --no-fund

# --- Audit Hilkhot Shabbat (informationnel) ----------------------------------
if command -v python3 >/dev/null 2>&1; then
  echo ""
  echo "=== Audit Hilkhot Shabbat — scripts/audit-simanim.py ==="
  python3 scripts/audit-simanim.py --quiet || true
  echo "Détail complet : python3 scripts/audit-simanim.py"
  echo "Manifeste      : PROGRESS.md"
else
  echo "session-start : python3 introuvable, audit des simanim ignoré."
fi
