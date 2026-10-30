#!/bin/bash
# usage: run-seq.sh <prefix> <first-index> <last-index>
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT32FlakeHunt
P=$1; A=$2; B=$3
for i in $(seq "$A" "$B"); do
  bash "$S/run-one.sh" "${P}${i}" "$S/work-${P}${i}" > "$S/out/${P}${i}.log" 2>&1
  echo "########## ${P}${i}"
  cat "$S/out/${P}${i}.meta"
  cat "$S/out/${P}${i}.out"
  if [ -s "$S/out/${P}${i}.err" ]; then echo "--- stderr:"; cat "$S/out/${P}${i}.err"; fi
done
exit 0
