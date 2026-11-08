#!/usr/bin/env bash
# 94-only runner (the round-89 harm counter runs later, in run89.sh, to avoid port races).
set -u
ROOT=/fast/scratch/hyaku/kama-r94/MT01ProbeMutants
REPO=/home/vgpnk/Projects/shokunin/kama-shokunin
REV=a27656a454b1a2364f8b6e55f42fbca8c2e86ee4
export TMPDIR="$ROOT/tmp"
mkdir -p "$TMPDIR" "$ROOT/logs" "$ROOT/w94"
for m in "$@"; do
  P="$ROOT/mutants/$m/kama-probe.sh"
  for attempt in 1 2 3; do
    python3 "$REPO/tools/round94-router-budget.py" --repo "$REPO" --rev "$REV" \
      --work "$ROOT/w94/$m-$attempt" --probe-file "$P" --burners 32 --runs 1 \
      > "$ROOT/logs/$m-94-try$attempt.out" 2>&1
    rc=$?
    echo "## exit=$rc attempt=$attempt load=$(cut -d' ' -f1 /proc/loadavg)" >> "$ROOT/logs/$m-94-try$attempt.out"
    echo "-- $m 94 try$attempt rc=$rc $(tail -2 "$ROOT/logs/$m-94-try$attempt.out" | tr '\n' '|')"
    [ "$rc" != 2 ] && break
    sleep 20
  done
done
echo "ALL DONE $(date -Is)"
