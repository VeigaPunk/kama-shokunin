#!/bin/bash
# usage: run-batch.sh <prefix> <n> ; runs n concurrent counter runs, fresh --work each
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT32FlakeHunt
PREFIX=$1
N=$2
for i in $(seq 1 "$N"); do
  bash "$S/run-one.sh" "${PREFIX}${i}" "$S/work-${PREFIX}${i}" > "$S/out/${PREFIX}${i}.log" 2>&1 &
done
wait
for i in $(seq 1 "$N"); do
  echo "########## ${PREFIX}${i}"
  cat "$S/out/${PREFIX}${i}.meta"
  cat "$S/out/${PREFIX}${i}.out"
  if [ -s "$S/out/${PREFIX}${i}.err" ]; then echo "--- stderr:"; cat "$S/out/${PREFIX}${i}.err"; fi
done
