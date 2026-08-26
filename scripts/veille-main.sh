#!/bin/bash
# Veille sur `main` — détecte en une seconde qu'une autre session a écrasé du
# contenu publié.
#
# Trois fois, un commit poussé depuis une copie périmée du dépôt a supprimé des
# dizaines de simanim en ligne sans que son message n'en dise rien (7ed67012,
# a1311630, f80641ad), la troisième fois en emportant les garde-fous eux-mêmes.
# Un workflow CI ne peut rien contre cela : supprimé dans le push qu'il devait
# contrôler, il ne s'exécute pas. Seule une protection de branche côté GitHub
# l'empêcherait vraiment ; à défaut, ce script permet de s'en apercevoir tout
# de suite plutôt qu'au lot suivant.
#
#     bash scripts/veille-main.sh     # depuis une branche à jour
#
# Sortie non nulle = régression sur main. Les seuils sont ceux de l'état
# vérifié au 26 août 2026 : 415 simanim, 4 garde-fous, 482 vignettes.
cd /home/user/Daat.ai || exit 1
git fetch origin main -q 2>/dev/null
ref=origin/main
compte () { git ls-tree -d -r --name-only "$1" sources/ 2>/dev/null | grep -cE 'siman-[0-9]+$'; }
m=$(compte "$ref"); b=$(compte HEAD)
gf=$(git ls-tree --name-only "$ref" .github/workflows/ scripts/ 2>/dev/null | grep -cE 'anti-regression|verifier-integrite|heb-nums|fix-jsonld')
im=$(git ls-tree --name-only "$ref" assets/img/og/ 2>/dev/null | grep -c '\-oh\.')
printf 'main=%s  simanim main=%s  branche=%s  garde-fous=%s/4  vignettes=%s\n' \
  "$(git log --oneline "$ref" -1 | cut -c1-9)" "$m" "$b" "$gf" "$im"
alerte=0
[ "$m" -lt "$b" ] && { echo "ALERTE: main a $((b-m)) siman(im) de moins que la branche"; alerte=1; }
[ "$gf" -lt 4 ]   && { echo "ALERTE: garde-fous incomplets sur main ($gf/4)"; alerte=1; }
[ "$im" -lt 482 ] && { echo "ALERTE: vignettes manquantes sur main ($im au lieu de 482)"; alerte=1; }
[ "$alerte" = 0 ] && echo "RAS — main est intact."
exit $alerte
