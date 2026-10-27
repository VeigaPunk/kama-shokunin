#!/usr/bin/env bash
# Mutant M-B "superseded-wrong-replacement": the ledger row's evidence is re-pointed at a
# token that IS cited and resolves in the surface but is NOT the file the base citation
# was actually re-pointed to. SCORECARD.md is left untouched (the honest re-point to
# corpus/lessons/round-53-verifier-spotcheck.md stays in place).
#
# The `fixed` class is anchored to the base citation line (M15 fixture: "fixed replacement
# cited away from the base line is bad"). `superseded` has no such anchor, so a row whose
# evidence is an unrelated cited file is accepted (met=True, bad=0).
#
# Runs in the seat's own clone only; the lane is never written to.
set -euo pipefail
S=/fast/scratch/hyaku/kama-r55/w1/X2C2Rerun
CLONE="$S/lane"
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X2C2Rerun
TIP=9c60eae6f7ed84f7da93d219a406aadc30958c6c

cd "$CLONE"
[ "$(git rev-parse --show-toplevel)" = "$CLONE" ] || { echo "NOT the clone toplevel"; exit 1; }
git checkout -q -B mutant/superseded-wrong-replacement "$TIP"

python3 - <<'PY'
p = "registry/cited-path-corrections.tsv"
s = open(p).read()
old = "SCORECARD.md\tcorpus/lessons/round-52-verifier-spotcheck.md\tsuperseded\tcorpus/lessons/round-53-verifier-spotcheck.md"
new = "SCORECARD.md\tcorpus/lessons/round-52-verifier-spotcheck.md\tsuperseded\ttools/round41-scorecard-reconcile.py"
assert old in s
open(p, "w").write(s.replace(old, new))
PY
git add -A
git -c user.name=fx -c user.email=fx@invalid commit -q -m "mutant: superseded row names an unrelated cited token"
MTIP=$(git rev-parse HEAD)
echo "mutant tip: $MTIP"

export TMPDIR="$S"
set +e
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py \
  --repo "$CLONE" --tip "$MTIP" --fleet /home/vgpnk/Projects/shokunin \
  --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b --scratch "$S" \
  --out "$OUT/mutant-B-superseded-wrong-replacement.out" > "$OUT/mutant-B-run.log" 2>&1
echo "MUTANT-B EXIT=$?"
set -e
head -2 "$OUT/mutant-B-superseded-wrong-replacement.out"
grep -c "bad=0 stale=0 dropped=0 met=True" "$OUT/mutant-B-superseded-wrong-replacement.out" && echo "MUTANT B ACCEPTED (bad=0 stale=0 dropped=0 met=True)"
