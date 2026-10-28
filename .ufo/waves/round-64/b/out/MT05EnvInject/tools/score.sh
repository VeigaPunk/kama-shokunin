#!/bin/bash
# usage: score.sh <variant>  -- builds the variant commit in the clone and scores it with the unmutated counter (fresh --work)
set -u
S=/fast/scratch/hyaku/kama-r64/b/MT05EnvInject; D=$S/clone; v=$1
sha=$(python3 $S/forge.py $D $v) || { echo "forge failed $v"; exit 1; }
rm -rf $S/work/$v; mkdir -p $S/work/$v
python3 $D/tools/round64-c1-counter.py --repo $D --tip $sha --work $S/work/$v > $S/out/$v.out 2> $S/out/$v.err
echo "rc=$? tip=$sha"
cat $S/out/$v.out
