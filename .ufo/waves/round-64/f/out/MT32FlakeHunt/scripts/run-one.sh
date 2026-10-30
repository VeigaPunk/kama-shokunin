#!/bin/bash
# usage: run-one.sh <label> <workdir>
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT32FlakeHunt
D=$S/clone
OUT=$S/out
LABEL=$1
WORK=$2
mkdir -p "$OUT" "$WORK"
cd "$D/tools" || exit 9
start=$(date +%s.%N)
python3 round64-c1-counter.py --repo "$D" --tip 23b3fdb1a925129a9961cf551f6d40bf251602cb --work "$WORK" \
  >"$OUT/$LABEL.out" 2>"$OUT/$LABEL.err"
rc=$?
end=$(date +%s.%N)
wall=$(python3 -c "print(f'{$end-$start:.2f}')")
echo "rc=$rc wall=$wall label=$LABEL" > "$OUT/$LABEL.meta"
echo "=== $LABEL rc=$rc wall=${wall}s"
cat "$OUT/$LABEL.out"
if [ -s "$OUT/$LABEL.err" ]; then echo "--- stderr:"; cat "$OUT/$LABEL.err"; fi
exit 0
