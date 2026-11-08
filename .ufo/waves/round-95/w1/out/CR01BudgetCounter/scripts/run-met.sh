#!/bin/bash
# CR01BudgetCounter met-candidate driver: full two-pass default load for cell-equivalent mutants.
set -u
L=/home/vgpnk/Projects/shokunin/kama-shokunin
OUT=$L/.ufo/waves/round-95/w1/out/CR01BudgetCounter
S=/fast/scratch/hyaku/kama-r95/CR01BudgetCounter
export TMPDIR=$S/tmp
cd "$L" || exit 9
REV=f6325660
COUNTER=tools/round95-router-budget.py
STATUS=$OUT/logs/met-status.txt
: > "$STATUS"

run() { # $1 name, rest = python3 args
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

run F4_no_maxmeta "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F4" --probe-file "$OUT/probes/probe-F4.sh" --runs 1

run F6_unreadable_invalid "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F6" --probe-file "$OUT/probes/probe-F6.sh" --runs 1

run F7_tensorcount_shortcut "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F7" --probe-file "$OUT/probes/probe-F7.sh" --runs 1

run F1b_shared600s "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-F1b" --probe-file "$OUT/probes/probe-F1b.sh" --runs 1

run G1_burners0 "$COUNTER" --repo . --rev "$REV" \
  --work "$S/work-G1" --probe-file "$OUT/probes/probe-M1.sh" --burners 0 --runs 1

echo "MET_BATCH_DONE"
