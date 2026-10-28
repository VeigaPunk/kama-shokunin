#!/bin/bash
S=/fast/scratch/hyaku/kama-r64/b/MT09ReceiptTamper; D=$S/clone
FREEZE=f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
test "$(git -C $D rev-parse --show-toplevel)" = "$D" || { echo "host guard failed"; exit 9; }
run_one() {
  name=$1; patch=$2
  git -C $D reset -q --hard $FREEZE
  if ! git -C $D apply --unidiff-zero --recount "$patch"; then echo "== $name APPLY-FAIL"; return; fi
  git -C $D add -A
  git -C $D -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "mutant $name" || { echo "== $name COMMIT-FAIL"; return; }
  T=$(git -C $D rev-parse HEAD)
  ( cd $S && python3 $D/tools/round64-c1-counter.py --repo $D --tip $T --work $S/w-$name > $S/out/$name.out 2> $S/out/$name.err ); rc=$?
  echo "== $name tip=${T:0:12} rc=$rc"
  cat $S/out/$name.out
  grep -E '^error: live|^error: relabel|^error: forge' $S/out/$name.err | cut -c1-300 | head -3
  git -C $D diff --stat HEAD~1 HEAD | tail -1
}
for p in "$@"; do n=$(basename $p .patch); run_one "$n" "$p"; done
git -C $D reset -q --hard $FREEZE
echo DONE
