#!/bin/sh
# round-73 after-measurements. Run at the instrument tip T with the worktree clean.
# Every receipt starts with `# rev=<T>` so the receipt-tip binding can grade it.
set -u
L=/home/vgpnk/Projects/shokunin/kama-shokunin
W="$L/.ufo/waves/round-73"
OUT=/fast/scratch/hyaku/kama-r73/L1-measurements
mkdir -p "$OUT" "$OUT/tmp"
export TMPDIR="$OUT/tmp"
TIP=$(git -C "$L" rev-parse master)
export PYTHONDONTWRITEBYTECODE=1
run() {
  name=$1; shift
  { echo "# rev=$TIP round=73"; echo "# cwd=$L"; echo "# command: $*"; "$@"; echo "# exit=$?"; } \
    > "$OUT/$name.out" 2>&1
}
cd "$L" || exit 1
run score-survivors python3 "$W/controls/score-survivors.py"
run round-scope-v2-live python3 tools/round73-round-scope-cases.py --repo . --round 73 --tip master
run province-host-drift-live python3 tools/round73-province-host-drift.py --repo .
run pre-report-gate python3 tools/pre-report-gate.py --repo . --round 73 --tip master
run selfdesc python3 tools/round42-selfdesc-reconcile.py --repo . --tip master
run newest-closure python3 tools/round69-newest-closure-counter.py --repo . --rev master --since-round 63
run receipt-audit python3 tools/round68-receipt-pointer-audit.py --repo . --rev master
run worktree-landing python3 tools/round67-worktree-landing-check.py --repo .
run gate-registry python3 tools/gate-registry-check.py --repo .
run province-host-claims python3 tools/round71-province-host-claims.py --repo . --base "$TIP"
run sources-census /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
run round72-round-scope-selftest python3 tools/round72-round-scope.py --selftest
run round72-binding-selftest python3 tools/round72-receipt-tip-binding.py --selftest
run round73-scope-selftest python3 tools/round73-round-scope-cases.py --selftest
run round73-claim-selftest python3 tools/round73-receipt-claim-binding.py --selftest
run round73-drift-selftest python3 tools/round73-province-host-drift.py --selftest
run pre-report-selftest python3 tools/pre-report-gate.py --selftest
run f3-replay bash "$W/w1/CRT01ClaimCritic/replay-f3.sh"
cp "$OUT/"*.out "$W/measured/after/"
echo "WROTE $OUT at rev $TIP"
