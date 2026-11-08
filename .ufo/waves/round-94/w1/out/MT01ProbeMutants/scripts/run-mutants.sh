#!/usr/bin/env bash
# MT01ProbeMutants runner: one mutant at a time, 94 counter then 89 counter.
set -u
ROOT=/fast/scratch/hyaku/kama-r94/MT01ProbeMutants
REPO=/home/vgpnk/Projects/shokunin/kama-shokunin
REV=a27656a454b1a2364f8b6e55f42fbca8c2e86ee4
export TMPDIR="$ROOT/tmp"
mkdir -p "$TMPDIR" "$ROOT/logs" "$ROOT/w94" "$ROOT/w89"
for m in "$@"; do
  P="$ROOT/mutants/$m/kama-probe.sh"
  [ -f "$P" ] || { echo "$m MISSING"; continue; }
  echo "== $m start $(date -Is) load=$(cut -d' ' -f1 /proc/loadavg)"
  python3 "$REPO/tools/round94-router-budget.py" --repo "$REPO" --rev "$REV" \
    --work "$ROOT/w94/$m" --probe-file "$P" --burners 32 --runs 1 \
    > "$ROOT/logs/$m-94.out" 2>&1
  rc94=$?
  echo "## exit=$rc94 load=$(cut -d' ' -f1 /proc/loadavg)" >> "$ROOT/logs/$m-94.out"
  echo "-- $m 94 rc=$rc94 $(tail -2 "$ROOT/logs/$m-94.out" | tr '\n' '|')"
  python3 "$REPO/tools/round89-unloadable-cells.py" --repo "$REPO" --rev "$REV" \
    --work "$ROOT/w89/$m" --probe-file "$P" \
    > "$ROOT/logs/$m-89.out" 2>&1
  rc89=$?
  echo "## exit=$rc89 load=$(cut -d' ' -f1 /proc/loadavg)" >> "$ROOT/logs/$m-89.out"
  echo "-- $m 89 rc=$rc89 $(tail -2 "$ROOT/logs/$m-89.out" | tr '\n' '|')"
done
echo "ALL DONE $(date -Is)"
