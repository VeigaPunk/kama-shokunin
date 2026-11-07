#!/bin/bash
# driver.sh <clone-dir> <mid...>  — mutant probe on one worker clone.
set -u
SC=/fast/scratch/hyaku/kama-r91/MT01ProbeMutants
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
CLONE=$(cd "$1" && pwd); shift
export TMPDIR=$SC/tmp/$CLONE
mkdir -p "$TMPDIR" "$SC/w/$CLONE" "$SC/receipts"
BASE=3decfa36b0eba7e5197c034dd1547146bca1568a
[ "$(git -C "$CLONE" rev-parse --show-toplevel)" = "$(cd "$CLONE" && pwd)" ] || { echo "TOPLEVEL-MISMATCH $CLONE"; exit 9; }

run_one() { # $1 mid or "baseline"
  local mid=$1 d=$SC/receipts/$1
  mkdir -p "$d"
  cp "$SC/pristine.sh" "$CLONE/tools/kama-probe.sh"
  if [ "$mid" != baseline ]; then
    python3 "$SC/muts.py" "$SC/pristine.sh" "$mid" "$CLONE/tools/kama-probe.sh" || { echo "$mid APPLY-FAIL"; return 1; }
  fi
  bash -n "$CLONE/tools/kama-probe.sh" 2>"$d/bash-n.err"; echo "bash_n_rc=$?" > "$d/bash-n.rc"
  sha256sum "$CLONE/tools/kama-probe.sh" | awk '{print $1}' > "$d/probe.sha256"
  if [ "$mid" != baseline ]; then
    git -C "$CLONE" diff HEAD -- tools/kama-probe.sh > "$d/probe.diff"
    git -C "$CLONE" -c user.name=mutant -c user.email=mutant@example.invalid -c commit.gpgsign=false \
      commit -q -m "mutant $mid" -- tools/kama-probe.sh || { echo "$mid COMMIT-FAIL"; return 1; }
  fi
  local rev; rev=$(git -C "$CLONE" rev-parse HEAD)
  echo "$rev" > "$d/rev"
  uptime > "$d/uptime.before"
  ( cd "$CLONE" && python3 "$LANE/tools/round91-answer-time.py" --repo "$CLONE" --rev "$rev" --work "$SC/w/$CLONE" ) \
     > "$d/counter.out" 2>&1; echo "counter_rc=$?" > "$d/counter.rc"
  uptime > "$d/uptime.after"
  ( cd "$CLONE" && python3 tests/probe-verdicts/check.py --json ) \
     > "$d/check.json" 2> "$d/check.err"; echo "check_rc=$?" > "$d/check.rc"
  # restore exact pristine bytes
  git -C "$CLONE" checkout -- tools/kama-probe.sh
  sha256sum "$CLONE/tools/kama-probe.sh" | awk '{print $1}' > "$d/restored.sha256"
  printf '%s %s %s %s\n' "$mid" "$rev" "$(cat "$d/counter.rc")" "$(cat "$d/check.rc")"
}

for m in "$@"; do run_one "$m"; done
