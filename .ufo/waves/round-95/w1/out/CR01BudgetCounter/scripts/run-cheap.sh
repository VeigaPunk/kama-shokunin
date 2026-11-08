#!/bin/bash
# CR01BudgetCounter cheap forgery batch: red/exit-2 paths and counter-level G2/G3.
set -u
L=/home/vgpnk/Projects/shokunin/kama-shokunin
OUT=$L/.ufo/waves/round-95/w1/out/CR01BudgetCounter
S=/fast/scratch/hyaku/kama-r95/CR01BudgetCounter
export TMPDIR=$S/tmp
cd "$L" || exit 9
REV=f6325660
COUNTER=tools/round95-router-budget.py
STATUS=$OUT/logs/cheap-status.txt
: > "$STATUS"

run() { # $1 name, rest = command after python3
  local name=$1; shift
  local log=$OUT/logs/$name.log
  local t0=$SECONDS
  python3 "$@" > "$log" 2>&1
  local rc=$?
  local dt=$((SECONDS - t0))
  printf '%s EXIT=%s wall=%ss\n' "$name" "$rc" "$dt" | tee -a "$STATUS"
  grep -E '^(ROUTER_BUDGET95|ROUTER_BUDGET95_UNSTABLE)' "$log" | tail -3 | tee -a "$STATUS"
  echo "---" >> "$STATUS"
  return 0
}

run F1a_shared4s_allowclock_skipload "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F1a" --probe-file "$OUT/probes/probe-F1a.sh" \
  --allow-clock --skip-load --runs 1

run G2_counter_impossible_expectation "$OUT/round95-router-budget-G2.py" --repo . --rev "$REV" \
  --work "$S/work-G2" --probe-file "$OUT/probes/probe-M1.sh" \
  --allow-clock --skip-load --runs 1 --slow-files 8

run G3_skipload_receipt "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-G3" --probe-file "$OUT/probes/probe-M1.sh" \
  --allow-clock --skip-load --runs 1 --slow-files 8

run F3_maxsteps_default "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F3d" --probe-file "$OUT/probes/probe-F3.sh" --runs 1

run F3_maxsteps_graded "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F3g" --probe-file "$OUT/probes/probe-F3.sh" \
  --allow-clock --skip-load --runs 1 --slow-files 8

run F5_const60_default "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F5d" --probe-file "$OUT/probes/probe-F5.sh" --runs 1

run F5_const60_graded "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F5g" --probe-file "$OUT/probes/probe-F5.sh" \
  --allow-clock --skip-load --runs 1 --slow-files 40

run F2_noctime "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F2" --probe-file "$OUT/probes/probe-F2.sh" \
  --allow-clock --skip-load --runs 1

echo "CHEAP_BATCH_DONE"
