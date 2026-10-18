#!/bin/bash
# SessionStart hook — prépare l'environnement Claude Code (web).
#
# 1. Installe les dépendances npm (fonctions serverless api/ + scripts de build)
#    afin que les commandes de build fonctionnent dès le début de la session.
# 2. Installe openpyxl, seule dépendance Python hors bibliothèque standard
#    (scripts/reste-a-corriger.py) ; toutes les autres portes sont en stdlib.
# 3. Reconstruit le corpus du chat s'il manque (clone frais) : voir plus bas.
# 4. Affiche l'audit de l'état des simanim de Hilkhot Shabbat
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

# --- Dépendance Python -------------------------------------------------------
# Un échec ici ne doit pas empêcher la session de démarrer : un seul script
# en dépend.
if command -v python3 >/dev/null 2>&1 && ! python3 -c "import openpyxl" 2>/dev/null; then
  echo "session-start : installation d'openpyxl…"
  python3 -m pip install --quiet openpyxl 2>/dev/null \
    || echo "session-start : openpyxl NON installé (seul scripts/reste-a-corriger.py en a besoin)."
fi

# --- Corpus du chat (sortie de build non versionnée) -------------------------
# data/corpus-shabbat.json et data/corpus-index.br sont ignorés par git
# (plusieurs dizaines de Mio, régénérés par vercel-build) : après un clone
# frais, ils MANQUENT, et tout script local qui lit le corpus échoue ou lit
# un corpus vide. On les reconstruit avec extract-corpus.js SEUL — il n'écrit
# que ces deux fichiers ignorés. `npm run build` réécrirait aussi des fichiers
# versionnés (dates du catalogue et des index de section) et salirait l'arbre
# à chaque ouverture de session.
if [ ! -s data/corpus-shabbat.json ] || [ ! -s data/corpus-index.br ]; then
  echo "session-start : corpus du chat absent (clone frais), extraction…"
  if node scripts/extract-corpus.js >/tmp/session-start-corpus.log 2>&1; then
    grep -E "Index précalculé|Par section" /tmp/session-start-corpus.log || true
  else
    echo "session-start : ⚠️ extraction du corpus en échec — voir /tmp/session-start-corpus.log, puis npm run build."
  fi
fi

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
