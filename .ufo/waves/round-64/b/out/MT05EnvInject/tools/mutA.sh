#!/bin/bash
S=/fast/scratch/hyaku/kama-r64/b/MT05EnvInject; D=$S/clone
for pair in "$@"; do
  v=${pair%%:*}; t=${pair#*:}
  rm -rf $S/work/mutA-$v; mkdir -p $S/work/mutA-$v
  timeout 200 python3 $D/tools/round64-c1-counter.py --repo $D --tip $t --work $S/work/mutA-$v > $S/out/mutA-$v.out 2> $S/out/mutA-$v.err
  echo "== mutant-counter vs $v rc=$?"
  cut -c1-150 $S/out/mutA-$v.out
  grep '^error' $S/out/mutA-$v.err | head -2 | cut -c1-200
done
