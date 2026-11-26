#!/bin/bash
# Portes de publication de 394-397 (et 393, dont les liens changent), une à la fois.
cd /home/user/Daat.ai
P=/tmp/claude-0/-home-user-Daat-ai/7d493fdf-7647-52e4-bf6b-12b6742d003b/scratchpad/oh366/publi8
R="$P/portes.txt"; : > "$R"
run() { nom=$1; shift; "$@" > "$P/$nom.txt" 2>&1; c=$?; echo "=== $nom"; echo "exit $c — $(tail -3 "$P/$nom.txt" | tr '\n' ' ' | cut -c1-260)"; }
{
run chabbat python3 scripts/verify-chabbat-source.py 393 394 395 396 397
run apercus python3 scripts/verifier-apercus.py 393 394 395 396 397
for n in 393 394 395 396 397; do
  run align$n python3 scripts/verifier-alignement.py --siman $n --section shabbat
  run encadres$n python3 scripts/verifier-encadres.py --siman $n
  run cit$n python3 scripts/verifier-citations.py --path sources/shabbat/siman-$n --langues fr,he,en
  run tronc$n python3 scripts/verifier-troncatures.py --path sources/shabbat/siman-$n
  run denomb$n python3 scripts/verifier-denombrements.py --path sources/shabbat/siman-$n
done
run etiq python3 scripts/verifier-etiquettes.py 393 394 395 396 397
run ancrage python3 scripts/verifier-ancrage.py 393 394 395 396 397
run couverture python3 scripts/verifier-couverture-encadres.py --section shabbat --bref 393 394 395 396 397
run langues python3 scripts/verifier-langues.py
run urllang python3 scripts/verifier-url-langue.py --path sources/shabbat
run liens python3 scripts/verifier-liens.py
run lienslang python3 scripts/verifier-liens-langue.py --path sources
run balises python3 scripts/verifier-balises.py --path sources
run classes python3 scripts/verifier-classes.py --path sources/shabbat
run planlimoud python3 scripts/verifier-plan-limoud.py --bref
run audit python3 scripts/audit-simanim.py --quiet
run rendu python3 scripts/verify-oh-source.py 393 394 395 396 397 --rendu
} >> "$R"
echo FIN >> "$R"
