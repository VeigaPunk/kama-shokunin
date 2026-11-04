#!/usr/bin/env bash
# Run by L1 after integration, not during the editing wave.
# Usage: bash verify.sh [absolute-path-to-EX01-harness.patch]
# With no harness patch, base r41 run-fact failures are intentionally NOT hidden.
set -euo pipefail
L=/home/vgpnk/Projects/shokunin/kama-shokunin
O=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/w1/out/EX03RecordRepair
BASE=6035e952c2521999e192d6f236331f265ac98392
ROOT=/fast/scratch/hyaku/kama-r70/EX03RecordRepair
mkdir -p "$ROOT"
S=$(mktemp -d "$ROOT/verify.XXXXXX")
trap 'rm -rf -- "$S"' EXIT
mkdir -p "$S/tmp"
export TMPDIR="$S/tmp"
FX="$S/fx"
# All fixture mutations below are guarded; no lane checkout/index is mutated.
git clone --quiet --shared --no-checkout "$L" "$FX"
test "$(git -C "$FX" rev-parse --show-toplevel)" = "$FX"
git -C "$FX" update-ref --no-deref HEAD "$BASE"
git -C "$FX" read-tree --reset -u HEAD
git -C "$FX" apply "$O/record-repair.patch"
cat "$O/round70-sections.md" >> "$FX/SCORECARD.md"
if [[ $# -gt 0 ]]; then
    test "$#" -eq 1
    case "$1" in /*) ;; *) printf '%s\n' 'Harness patch must have an absolute path' >&2; exit 2 ;; esac
    git -C "$FX" apply "$1"
fi
NAME=$(git -C "$L" config --get user.name)
EMAIL=$(git -C "$L" config --get user.email)
test -n "$NAME" && test -n "$EMAIL"
test "$(git -C "$FX" rev-parse --show-toplevel)" = "$FX"
git -C "$FX" add -- SCORECARD.md PROVINCE.md tools/round41-scorecard-reconcile.py tools/round42-selfdesc-reconcile.py
git -C "$FX" -c user.name="$NAME" -c user.email="$EMAIL" -c core.hooksPath=/dev/null commit --quiet -m 'Round 70 record-repair isolated fixture'
TIP=$(git -C "$FX" rev-parse HEAD)
printf 'FIXTURE_TIP=%s\n' "$TIP"
set +e
python3 "$FX/tools/round42-selfdesc-reconcile.py" --repo "$FX" --tip "$TIP"
RC=$?
set -e
printf 'RECONCILER_EXIT=%s\n' "$RC"
exit "$RC"
