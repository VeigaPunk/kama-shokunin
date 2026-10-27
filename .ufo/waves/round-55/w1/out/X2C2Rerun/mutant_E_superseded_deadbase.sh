#!/usr/bin/env bash
# Mutant M-E "superseded on a base-DEAD citation": take a token that was cited at the
# frozen BASE but did NOT resolve there (a dead base citation) and give it a `superseded`
# row naming a cited, resolving replacement. The `fixed` class owns that case ("fixed
# token was not an unresolved citation of this surface at base"); `superseded` must
# refuse it.
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
git checkout -q -B mutant/me "$TIP"

python3 - <<'PY'
p="SCORECARD.md"; s=open(p).read()
# .ufo/waves/round-999/count-c999.py is cited at BASE but dead there (never row 17).
# Remove every tip citation of it and re-point the line to a resolving file.
old="- §Round 31 C2 row cites `.ufo/waves/round-31/c2/c2-tip.json`, which does not exist; the receipts are"
assert old in s
s = s.replace("`.ufo/waves/round-999/count-c999.py`", "`.ufo/round-10/audit/stale-anchors.tsv`")
open(p,"w").write(s)
p="registry/cited-path-corrections.tsv"; s=open(p).read()
old="SCORECARD.md\t.ufo/waves/round-999/count-c999.py\tnever\t-\t"
assert old in s
s = s.replace(old, "SCORECARD.md\t.ufo/waves/round-999/count-c999.py\tsuperseded\t.ufo/round-10/audit/stale-anchors.tsv\t")
open(p,"w").write(s)
PY
git add -A
git -c user.name=fx -c user.email=fx@invalid commit -q -m "mutant M-E: superseded row on a base-dead citation"
ME=$(git rev-parse HEAD)
echo "M-E tip: $ME"
export TMPDIR="$S"
for which in frozen fixed; do
  c="$COUNTER"; [ "$which" = fixed ] && c="$FIXED"
  out="$OUT/ME-$which.out"
  set +e
  python3 "$c" --repo "$CLONE" --tip "$ME" --fleet /home/vgpnk/Projects/shokunin \
    --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b --scratch "$S" --out "$out" >/dev/null 2>&1
  rc=$?; set -e
  echo "M-E/$which exit=$rc :: $(sed -n 2p "$out")"
  grep -E "bad ledger line|dropped citation" "$out" | sed 's/^/      /' || true
done
