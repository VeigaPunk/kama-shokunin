#!/usr/bin/env bash
# Run the gate selftest (tests/llamacpp-live/check-receipt.py --selftest) at
# each REV in its own detached worktree of CLONE_DIR, a throwaway clone (never
# the lane). Records the gate blob, porcelain status before/after, stdout,
# stderr and exit per revision, then removes the worktree.
#
# Usage: gate-selftest-by-rev.sh CLONE_DIR WT_ROOT OUT_FILE REV [REV ...]
set -u
if [ "$#" -lt 4 ]; then
  echo "usage: $0 CLONE_DIR WT_ROOT OUT_FILE REV [REV ...]" >&2
  exit 2
fi
clone=$1
wtroot=$2
out=$3
shift 3
if [ -e "$out" ]; then
  echo "refusing to overwrite $out" >&2
  exit 2
fi
gate=tests/llamacpp-live/check-receipt.py
status=0
{
  echo "python3=$(command -v python3) $(python3 --version 2>&1)"
  for rev in "$@"; do
    full=$(git -C "$clone" rev-parse --verify "$rev^{commit}") || exit 2
    wt="$wtroot/wt-${full:0:12}"
    git -C "$clone" worktree add -q --detach "$wt" "$full" || exit 2
    echo "=== rev=$rev commit=$full ==="
    echo "gate_blob=$(git -C "$wt" rev-parse "HEAD:$gate")"
    echo "status_porcelain_before_lines=$(git -C "$wt" status --porcelain | wc -l)"
    (cd "$wt" && python3 "$gate" --selftest) >"$wt.stdout" 2>"$wt.stderr"
    rc=$?
    echo "--- stdout ---"
    cat "$wt.stdout"
    echo "--- stderr ---"
    cat "$wt.stderr"
    echo "exit=$rc"
    echo "status_porcelain_after_lines=$(git -C "$wt" status --porcelain | wc -l)"
    [ "$rc" -eq 0 ] || status=1
    rm -f "$wt.stdout" "$wt.stderr"
    git -C "$clone" worktree remove --force "$wt" || status=2
  done
} >"$out"
exit "$status"
