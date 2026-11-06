#!/usr/bin/env bash
set -u
fails=0
for s in abc 'Zz~ ' 'é' $'\xc2\x85' $'\xe2\x80\xa8' $'\xe2\x80\xae' $'\xc2\x9b' $'\xf0\x9f\x98\x80' $'\x01' $'\x1f' $'\x20' $'\x7f' $'\x0a' $'\x80' $'\xff'; do
  hex=$(printf '%s' "$s" | od -An -v -tx1 | tr -d ' \n')
  if [[ $s == *[$'\x01'-$'\x1f'$'\x7f']* ]]; then r=FIRE; else r=no; fi
  printf '%-10s %s\n' "$r" "$hex"
done
# cost: 20000 pre-check tests on a 200-char ASCII string and on a 200-char non-ASCII string
a=$(printf 'x%.0s' {1..200}); n=$(printf 'é%.0s' {1..100})
for name in a n; do
  eval "v=\$$name"
  s=$(date +%s%N)
  for ((k=0;k<20000;k++)); do [[ $v == *[$'\x01'-$'\x1f'$'\x7f']* ]]; done
  e=$(date +%s%N); echo "precheck_20k $name ms=$(( (e-s)/1000000 ))"
done
