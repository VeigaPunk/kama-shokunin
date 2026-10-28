#!/bin/bash
set -u
S=/fast/scratch/hyaku/kama-r63/w/MT04ToolIdCreated
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-63/w1/out/MT04ToolIdCreated
PIN=03a6a1d850902a66a13dfad33f89cf3a8b759a09
UNMUT=$S/base/tools/round63-c1-counter.py       # unmutated counter, run from its clone path
test "$(git -C $S/base rev-parse --show-toplevel)" = "$S/base" || exit 9
test "$(git -C $S/tool rev-parse --show-toplevel)" = "$S/tool" || exit 9
test "$(git -C $S/counter rev-parse --show-toplevel)" = "$S/counter" || exit 9
TAB=$OUT/tally.tsv; : > $TAB; printf 'label\tcounter\trepo\ttip\tline\n' >> $TAB
run() { # label counterfile repo tipsha
  local L=$1 CF=$2 R=$3 T=$4
  python3 "$CF" --repo "$R" --tip "$T" --work "$S/rr/$L" >"$OUT/$L.line" 2>"$OUT/$L.err"
  local rc=$?
  printf '%s\t%s\t%s\t%s\t%s rc=%s\n' "$L" "$(basename $CF)" "$(basename $R)" "$(echo $T|cut -c1-8)" "$(cat $OUT/$L.line)" "$rc" >> $TAB
  if [ -s "$OUT/$L.err" ]; then echo "  stderr: $(head -c 400 $OUT/$L.err | tr '\n' ' ')" >> $TAB; fi
}
cm() { git -C $S/counter show "$1:tools/round63-c1-counter.py" > "$S/cmut/$1.py"; echo "$S/cmut/$1.py"; }
run BASE          $UNMUT $S/base  $(git -C $S/base rev-parse $PIN)
run NEUTRAL       $UNMUT $S/tool  $(git -C $S/tool rev-parse 30ce1384)
for t in 8fb39478:T01-idempty-honest 446bcc04:T02-idempty-lie a2cfb2ed:T03-created0-honest 2771366b:T04-created0-lie 520f515a:T05-createdtrue-honest eda3ce08:T06-createdtrue-lie 0a95d77a:T07-nodetails-honest 6894ea76:T08-nodetails-lie 409aed52:T09-cachedover-honest 8d8137a5:T10-cachedover-lie 109c7409:T11-stored-only-forced-ok; do
  sha=${t%%:*}; lab=${t#*:}
  run $lab $UNMUT $S/tool $(git -C $S/tool rev-parse $sha)
done
for c in 240c50a7:C01-drop-id-nonempty 9f22afe0:C02-drop-created-gt-1e9 b0378180:C03-drop-created-is_int 8cfa3b6e:C04-drop-id-str-guard 8824f697:C05-usage-forced-true 163263ef:C06-drop-cached-bound 1278944d:C08-no-stored-vs-recomputed; do
  sha=${c%%:*}; lab=${c#*:}
  CF=$(cm $(git -C $S/counter rev-parse $sha))
  run $lab $CF $S/base $(git -C $S/base rev-parse $PIN)
done
# cross-scoring: counter mutants against tool-side mutant receipts
CF06=$S/cmut/$(git -C $S/counter rev-parse 163263ef).py; CF08=$S/cmut/$(git -C $S/counter rev-parse 1278944d).py
run X-C06xT09 $CF06 $S/tool $(git -C $S/tool rev-parse 409aed52)
run X-C06xT10 $CF06 $S/tool $(git -C $S/tool rev-parse 8d8137a5)
run X-C08xT11 $CF08 $S/tool $(git -C $S/tool rev-parse 109c7409)
run X-C08xT02 $CF08 $S/tool $(git -C $S/tool rev-parse 446bcc04)
echo DONE >> $TAB
