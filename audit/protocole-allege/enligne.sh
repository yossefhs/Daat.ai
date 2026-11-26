#!/bin/bash
cd /home/user/Daat.ai
want=$(md5sum < sitemap.xml | cut -c1-32)
for i in $(seq 1 90); do
  got=$(curl -s --max-time 30 https://daattorah.com/sitemap.xml | md5sum | cut -c1-32)
  [ "$got" = "$want" ] && break
  sleep 30
done
echo "déploiement vu : $(date -u +%H:%M:%S) (essai $i)"
ok=0; ko=0
chk() { url=$1; f=$2; a=$(curl -sL --max-time 30 "https://daattorah.com$url" | md5sum | cut -c1-32); b=$(md5sum < "$f" | cut -c1-32); if [ "$a" = "$b" ]; then ok=$((ok+1)); else ko=$((ko+1)); echo "DIFFÉRENT $url ($f)"; fi; }
for n in 393 394 395 396 397; do
  for L in "" he en; do
    s=${L:+-$L}; u=${L:+/$L}
    chk "/oh/$n$u" sources/shabbat/siman-$n/index$s.html
    chk "/oh/$n/base$u" sources/shabbat/siman-$n/niveau-1-base$s.html
    chk "/oh/$n/lamdan$u" sources/shabbat/siman-$n/niveau-2-lamdan$s.html
    chk "/oh/$n/synthese$u" sources/shabbat/siman-$n/niveau-3-synthese$s.html
    chk "/oh/$n/daat-harav$u" sources/shabbat/siman-$n/niveau-4-daat-harav$s.html
  done
done
chk /oh/ sources/shabbat/index.html
chk /oh/he sources/shabbat/index-he.html
chk /oh/en sources/shabbat/index-en.html
chk /llms.txt llms.txt
chk /assets/js/siman-nav.js assets/js/siman-nav.js
chk /assets/img/og/siman-396.png assets/img/og/siman-396.png
chk /sitemap.xml sitemap.xml
chk /oh/396/index.md sources/shabbat/siman-396/index.md
chk /index-he.html index-he.html
chk /index-en.html index-en.html
chk / index.html
echo "IDENTIQUES $ok · DIFFÉRENTS $ko"
