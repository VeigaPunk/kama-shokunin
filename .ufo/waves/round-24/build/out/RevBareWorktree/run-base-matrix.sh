#!/usr/bin/env bash
# Run the BASE (r23) audit tool over every layout fixture and record
# exit code + verdict summary. Read-only against the tool; fixtures live
# under the lane scratch dir.
set -u
ROOT=/fast/scratch/hyaku/kama-r24/RevBareWorktree/fixtures2
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
run() { # label lane fleet
  local label=$1 lane=$2 fleet=$3
  out=$(python3 "$TOOL" --lane-repo "$lane" --fleet-repo "$fleet" \
        --branch master --lane kama --rounds 1 --no-errata 2>&1)
  rc=$?
  printf '### %-28s rc=%s\n' "$label" "$rc"
  printf '%s\n' "$out" | sed 's/^/    /'
  echo
}
run plain            "$ROOT/plain/lane"           "$ROOT/plain/fleet"
run bare             "$ROOT/bare/lane"            "$ROOT/bare/fleet"
run linked-main      "$ROOT/linked/lane"         "$ROOT/linked/fleet"
run linked-worktree  "$ROOT/linked/lane-wt"      "$ROOT/linked/fleet-wt"
run promisor         "$ROOT/promisor/lane"       "$ROOT/promisor/fleet"
run promisor-bare    "$ROOT/promisor-bare/lane"  "$ROOT/promisor-bare/fleet"
run promisor-linked-wt "$ROOT/promisor-linked/lane-wt" "$ROOT/promisor-linked/fleet-wt"
