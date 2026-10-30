#!/bin/bash
# Score one forged tool against the UNMUTATED counter, in a given clone.
# usage: score-fg2.sh <clone> <label> <forged-tool-file>
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT32FlakeHunt
D=$1; LABEL=$2; FORGED=$3
OUT=$S/out
cp "$D/tools/kama-completion-live.py" "$S/pristine-$LABEL.py"
cp "$FORGED" "$D/tools/kama-completion-live.py"
git -C "$D" add -A
git -C "$D" -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "forgery $LABEL"
T=$(git -C "$D" rev-parse HEAD)
echo "=== $LABEL commit $T (clone $D)"
cd "$D/tools" || exit 9
python3 round64-c1-counter.py --repo "$D" --tip "$T" --work "$S/work-fg-$LABEL" \
  >"$OUT/fg-$LABEL.out" 2>"$OUT/fg-$LABEL.err"
echo "rc=$?"
cat "$OUT/fg-$LABEL.out"
if [ -s "$OUT/fg-$LABEL.err" ]; then echo "--- stderr:"; cat "$OUT/fg-$LABEL.err"; fi
cp "$S/pristine-$LABEL.py" "$D/tools/kama-completion-live.py"
git -C "$D" add -A
git -C "$D" -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "restore after $LABEL"
echo "restored to $(git -C "$D" rev-parse HEAD)"
exit 0
