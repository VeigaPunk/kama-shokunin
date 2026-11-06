#!/bin/bash
# Harm sweep runner: one revision per invocation.
# usage: run-harm.sh <rev> <label>
set -u
rev="$1"; label="$2"
S=/fast/scratch/hyaku/kama-r88/EX01HarmSweep
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-88/w1/out/EX01HarmSweep
WT="$S/wt"
mkdir -p "$OUT/$label"
export TMPDIR="$S/tmp-$label"; mkdir -p "$TMPDIR"
cd "$WT" || exit 9
git checkout --detach "$rev" > "$OUT/$label/checkout.out" 2>&1 || exit 9
git rev-parse HEAD > "$OUT/$label/head.txt"
: > "$OUT/$label/summary.tsv"

run() {
  id="$1"; shift
  log="$OUT/$label/$id.out"
  timeout 600 "$@" > "$log" 2>&1
  rc=$?
  printf '%s\t%s\t%s\n' "$id" "$rc" "$(tail -n 1 "$log" | tr '\t' ' ')" >> "$OUT/$label/summary.tsv"
}

run check              python3 tests/probe-verdicts/check.py
run check-selftest     python3 tests/probe-verdicts/check.py --selftest
run snapshot           bash tools/test-snapshot.sh
run census-selftest    python3 tools/round79-unregistered-census.py --selftest --work "$TMPDIR/census"
run live-reconcile-selftest python3 tools/round78-live-reconcile.py --selftest
run pin-watch-selftest python3 tools/pin-watch.py selftest
run r77-citation-baseline-selftest python3 tools/round77-citation-baseline.py --selftest
run r77-append-registers-selftest  python3 tools/round77-append-registers.py --selftest
run r77-selfrecord-round76-selftest python3 tools/round77-selfrecord-round76.py --selftest
run r78-selfrecord-round77-selftest python3 tools/round78-selfrecord-round77.py --selftest
run r78-append-registers-selftest  python3 tools/round78-append-registers.py --selftest
run r81-append-debt-selftest       python3 tools/round81-append-debt.py --selftest
run r82-selfrecord-round81-selftest python3 tools/round82-selfrecord-round81.py --selftest
run r82-late-delta-selftest        python3 tools/round82-late-delta.py --selftest
run r83-pending-falls-selftest     python3 tools/round83-pending-falls.py --selftest
run r83-pin-rechecks-selftest      python3 tools/round83-pin-rechecks.py --selftest
run r86-rendered-cells-selftest    python3 tools/round86-rendered-cells.py --selftest
run r86-mutant-owners-selftest     python3 tools/round86-mutant-owners.py --selftest
run r86-pin-origin-selftest        python3 tools/round86-pin-origin.py --selftest

git status --porcelain -uall > "$OUT/$label/worktree-dirty.txt" 2>&1
echo "done $label"
