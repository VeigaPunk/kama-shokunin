#!/usr/bin/env bash
# Mutant M-A "superseded-unanchored-drop" against the REAL lane tree, in the seat's own
# clone only (/fast/scratch/.../lane). The lane itself is never written to.
#
# Mutation: in SCORECARD.md at the landed tip, DELETE the calibration row's
# "latest outside closure" pointer entirely (no re-point at all) and re-point the
# ledger's `superseded` row's evidence at a different token that happens to be cited
# elsewhere in the same surface.
#
# Claim under test (preregistration.json claims.C2.predicate): "`superseded` rows
# disclosing a LIVE BASE CITATION RE-POINTED to a cited, resolving replacement" and
# "no citation dropped on any of the three surfaces since the base".
#
# The `fixed` class IS anchored to the base citation line (M15 fixture). If `superseded`
# is not anchored, deleting a live base citation (rather than re-pointing it) would
# still print met=True with dropped=0.
set -euo pipefail
S=/fast/scratch/hyaku/kama-r55/w1/X2C2Rerun
CLONE="$S/lane"
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X2C2Rerun
TIP=9c60eae6f7ed84f7da93d219a406aadc30958c6c

cd "$CLONE"
[ "$(git rev-parse --show-toplevel)" = "$CLONE" ] || { echo "NOT the clone toplevel"; exit 1; }
git checkout -q -B mutant/superseded-unanchored "$TIP"

python3 - <<'PY'
import re
p = "SCORECARD.md"
s = open(p).read()
before = s
# 1) delete the closure pointer from the calibration row (the base-cited live token
#    corpus/lessons/round-52-verifier-spotcheck.md is already absent at tip; the row
#    currently points at corpus/lessons/round-53-verifier-spotcheck.md).
s = s.replace("latest outside closure `corpus/lessons/round-53-verifier-spotcheck.md` (rejected; re-anchored round 54)",
              "latest outside closure (pointer deleted by mutant)")
assert s != before, "closure pointer text not found"
open(p, "w").write(s)
PY

# 2) re-point the ledger's superseded row at a token that IS cited elsewhere in
#    SCORECARD.md and resolves in the lane tree: tools/round41-scorecard-reconcile.py
python3 - <<'PY'
p = "registry/cited-path-corrections.tsv"
s = open(p).read()
old = "SCORECARD.md\tcorpus/lessons/round-52-verifier-spotcheck.md\tsuperseded\tcorpus/lessons/round-53-verifier-spotcheck.md"
new = "SCORECARD.md\tcorpus/lessons/round-52-verifier-spotcheck.md\tsuperseded\ttools/round41-scorecard-reconcile.py"
assert old in s, "superseded row not found"
open(p, "w").write(s.replace(old, new))
PY

git add -A
git -c user.name=fx -c user.email=fx@invalid commit -q -m "mutant: superseded row unanchored; closure pointer deleted"
MTIP=$(git rev-parse HEAD)
echo "mutant tip: $MTIP"
git --no-pager log --oneline -1

echo "=== does SCORECARD.md still cite round-53 spotcheck anywhere? ==="
grep -c "corpus/lessons/round-53-verifier-spotcheck.md" SCORECARD.md || echo 0
echo "=== is tools/round41-scorecard-reconcile.py cited in SCORECARD.md? ==="
grep -c "tools/round41-scorecard-reconcile.py" SCORECARD.md || echo 0

export TMPDIR="$S"
echo "=== run the FROZEN counter at the MUTANT tip ==="
set +e
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py \
  --repo "$CLONE" --tip "$MTIP" --fleet /home/vgpnk/Projects/shokunin \
  --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b --scratch "$S" \
  --out "$OUT/mutant-A-superseded-unanchored.out"
echo "MUTANT EXIT=$?"
set -e
echo "=== unmutated control at the same ledger/surface state is the landed tip ==="
