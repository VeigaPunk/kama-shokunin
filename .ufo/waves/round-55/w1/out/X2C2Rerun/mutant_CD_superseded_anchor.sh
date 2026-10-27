#!/usr/bin/env bash
# Mutants M-C (delete-the-pointer) and M-D (wrong-replacement, cited away from the base
# citation line) against the REAL lane tree, in the seat's own clone only.
#
# The `fixed` class is anchored to the base citation line (M15 fixture: "fixed replacement
# cited away from the base line is bad"). The `superseded` class has no such anchor.
#
# M-C: delete the calibration row's "latest outside closure" pointer entirely (a live
#      base citation DELETED, not re-pointed) and point the superseded row's evidence at
#      an unrelated cited+resolving token.
# M-D: leave SCORECARD.md untouched (the honest re-point to round-53 stays) but point the
#      superseded row's evidence at a token that resolves but is cited at line 249, not
#      at the base citation line 18.
#
# Runs in the seat's own clone only; the lane is never written to.
set -euo pipefail
S=/fast/scratch/hyaku/kama-r55/w1/X2C2Rerun
CLONE="$S/lane"
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X2C2Rerun
TIP=9c60eae6f7ed84f7da93d219a406aadc30958c6c
COUNTER=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py
FIXED="$S/fix/tools/round54-cited-path-check.py"

cd "$CLONE"
[ "$(git rev-parse --show-toplevel)" = "$CLONE" ] || { echo "NOT the clone toplevel"; exit 1; }

# ---- M-C -------------------------------------------------------------
git checkout -q -B mutant/mc "$TIP"
python3 - <<'PY'
p="SCORECARD.md"; s=open(p).read()
old="latest outside closure `corpus/lessons/round-53-verifier-spotcheck.md` (rejected; re-anchored round 54)"
new="latest outside closure (pointer deleted by mutant M-C)"
assert old in s
open(p,"w").write(s.replace(old,new))
p="registry/cited-path-corrections.tsv"; s=open(p).read()
old="SCORECARD.md\tcorpus/lessons/round-52-verifier-spotcheck.md\tsuperseded\tcorpus/lessons/round-53-verifier-spotcheck.md"
new="SCORECARD.md\tcorpus/lessons/round-52-verifier-spotcheck.md\tsuperseded\t.ufo/round-10/audit/stale-anchors.tsv"
assert old in s
open(p,"w").write(s.replace(old,new))
PY
git add -A
git -c user.name=fx -c user.email=fx@invalid commit -q -m "mutant M-C: closure pointer deleted; superseded row names an unrelated token"
MC=$(git rev-parse HEAD)
echo "M-C tip: $MC"

# ---- M-D -------------------------------------------------------------
git checkout -q -B mutant/md "$TIP"
python3 - <<'PY'
p="registry/cited-path-corrections.tsv"; s=open(p).read()
old="SCORECARD.md\tcorpus/lessons/round-52-verifier-spotcheck.md\tsuperseded\tcorpus/lessons/round-53-verifier-spotcheck.md"
new="SCORECARD.md\tcorpus/lessons/round-52-verifier-spotcheck.md\tsuperseded\t.ufo/round-10/audit/stale-anchors.tsv"
assert old in s
open(p,"w").write(s.replace(old,new))
PY
git add -A
git -c user.name=fx -c user.email=fx@invalid commit -q -m "mutant M-D: superseded row names a replacement cited away from the base line"
MD=$(git rev-parse HEAD)
echo "M-D tip: $MD"

export TMPDIR="$S"
for pair in "MC:$MC" "MD:$MD"; do
  name="${pair%%:*}"; tip="${pair##*:}"
  for which in frozen fixed; do
    c="$COUNTER"; [ "$which" = fixed ] && c="$FIXED"
    out="$OUT/${name}-${which}.out"
    set +e
    python3 "$c" --repo "$CLONE" --tip "$tip" --fleet /home/vgpnk/Projects/shokunin \
      --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b --scratch "$S" --out "$out" >/dev/null 2>&1
    rc=$?
    set -e
    echo "$name/$which exit=$rc :: $(sed -n 2p "$out")"
    grep -E "bad ledger line|dropped citation" "$out" | sed 's/^/      /' || true
  done
done
