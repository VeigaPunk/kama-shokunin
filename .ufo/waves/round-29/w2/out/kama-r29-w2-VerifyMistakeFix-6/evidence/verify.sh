#!/bin/bash
REPO=/tmp/kama-w2-VerifyMistakeFix/clone
P=$REPO/tools/prereg-time-check.py
O=/tmp/kama-w2-VerifyMistakeFix/tree-75b78bb4/tools/prereg-time-check.py
M=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/mined
cd /tmp/kama-w2-VerifyMistakeFix || exit 9

gen() { # tool rev path outfile
  o=$(python3 "$1" --repo "$REPO" --path "$3" --rev "$2" --strict 2>&1); rc=$?
  { echo "$o"; echo "exit=$rc"; } > "$4"
}

gen "$P" 75b78bb4 .ufo/waves/round-28/preregistration.json r1.out
gen "$P" d8bf1804 .ufo/waves/round-28/preregistration.json r2.out
gen "$O" 75b78bb4 .ufo/waves/round-28/preregistration.json r3.out
gen "$P" 513eba3b .ufo/waves/round-28/preregistration.json r4.out
gen "$P" 513eba3b .ufo/waves/round-29/preregistration.json r5.out

for pair in "patched-75b78bb4.out r1.out" "patched-d8bf1804.out r2.out" "orig-75b78bb4.out r3.out"; do
  set -- $pair
  d=$(diff "$M/$1" "$2" 2>&1); drc=$?
  if [ $drc -eq 0 ]; then echo "IDENTICAL: $1 == $2"; else echo "DIFFERS($drc): $1 vs $2"; echo "$d"; fi
done
echo "=== NEW: patched at 513eba3b on round-28 prereg (no receipt in mined/) ==="
cat r4.out
echo "=== NEW: patched at 513eba3b on round-29 prereg (no receipt in mined/) ==="
cat r5.out
echo "SCRIPT_DONE"
