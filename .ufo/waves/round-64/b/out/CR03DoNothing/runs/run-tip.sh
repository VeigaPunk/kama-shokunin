#!/bin/bash
# usage: run-tip.sh NAME TIP -- scores TIP with the unmutated counter from the freeze checkout
set -u
S=/fast/scratch/hyaku/kama-r64/b/CR03DoNothing
D=$S/clone
N=$1; T=$(git -C $D rev-parse "$2")
test "$(git -C $D rev-parse --show-toplevel)" = "$D" || { echo "not clone"; exit 3; }
mkdir -p $S/work-$N
cd $S
python3 $D/tools/round64-c1-counter.py --repo $D --tip $T --work $S/work-$N > $S/out-$N.txt 2> $S/err-$N.txt
echo "rc=$? tip=$T"; cat $S/out-$N.txt; head -c 800 $S/err-$N.txt
