#!/bin/bash
S=/fast/scratch/hyaku/kama-r64/b/MT09ReceiptTamper; D=$S/clone
FREEZE=f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
test "$(git -C $D rev-parse --show-toplevel)" = "$D" || { echo "host guard failed"; exit 9; }
for p in "$@"; do
  n=$(basename $p .patch); tag=$(date +%s%N)
  git -C $D reset -q --hard $FREEZE && git -C $D apply --unidiff-zero --recount "$p" || { echo "== $n APPLY-FAIL"; continue; }
  git -C $D add -A && git -C $D -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "mutant $n fresh"
  T=$(git -C $D rev-parse HEAD)
  ( cd $S && python3 $D/tools/round64-c1-counter.py --repo $D --tip $T --work $S/wf-$n-$tag > $S/out/fresh-$n.out 2> $S/out/fresh-$n.err ); rc=$?
  echo "== fresh $n tip=${T:0:12} rc=$rc"; cut -c1-200 $S/out/fresh-$n.out; grep -E '^error: live' $S/out/fresh-$n.err | head -2
done
git -C $D reset -q --hard $FREEZE; echo DONE
