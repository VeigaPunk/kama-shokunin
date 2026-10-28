#!/bin/bash
# usage: run.sh <label> [mutant.py]  -- installs mutant (if given) at clone counter path, runs with a FRESH work dir, restores
S=/fast/scratch/hyaku/kama-r64/b/MT10CopyModes; D=${REPO:-$S/clone}; T=${TIP:-f6a4ea9a8b5a876d685b08e7e582ec0723412a4a}
L=$1; M=${2:-}; mkdir -p $S/out/$L
if [ -n "$M" ]; then cp "$M" $D/tools/round64-c1-counter.py; fi
W=$S/work/$L-$(date +%s%N); mkdir -p $W
cp $D/tools/round64-c1-counter.py $S/out/$L/counter.py
python3 $D/tools/round64-c1-counter.py --repo $D --tip $T --work $W >$S/out/$L/stdout.txt 2>$S/out/$L/stderr.txt
rc=$?
echo "exit=$rc"; cat $S/out/$L/stdout.txt; echo "stderr-error-lines=$(grep -c '^error:' $S/out/$L/stderr.txt)"
git -C $D checkout -q -- tools/round64-c1-counter.py
git -C $D status --short
