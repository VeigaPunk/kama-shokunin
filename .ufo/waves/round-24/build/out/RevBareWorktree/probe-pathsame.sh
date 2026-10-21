#!/usr/bin/env bash
# Probe 6: the SAME repository reached through two different paths must
# give the SAME verdict. Measure the base tool's path-dependent promisor
# detection (worktree-scoped config vs sibling worktree scope).
set -u
ROOT=/fast/scratch/hyaku/kama-r24/RevBareWorktree/fixtures2
W=/fast/scratch/hyaku/kama-r24/RevBareWorktree/probe6
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
rm -rf "$W"; mkdir -p "$W"
for v in $(env | sed -n 's/^\(GIT_[A-Za-z_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

git clone -q "$ROOT/src/lane" "$W/lane"
git clone -q "$ROOT/src/fleet" "$W/fleet"
git -C "$W/lane" worktree add -q --detach "$W/lane-wt" HEAD
git -C "$W/fleet" worktree add -q --detach "$W/fleet-wt" HEAD

# promisor marking ONLY in the linked worktree's own config scope
git -C "$W/lane" config extensions.worktreeConfig true
git -C "$W/lane-wt" config --worktree remote.origin.promisor true
git -C "$W/lane-wt" config --worktree remote.origin.partialclonefilter blob:none

echo "marking lives in: $(git -C "$W/lane-wt" rev-parse --git-path config.worktree)"
echo "  (file: $(cat "$W/lane/.git/worktrees/lane-wt/config.worktree" 2>/dev/null | tr '\n' ' '))"
echo
echo "-- config --list seen through the LINKED worktree:"
git -C "$W/lane-wt" config --null --list 2>/dev/null | tr '\0' '\n' | grep -i promisor | sed 's/^/     /'
echo "-- config --list seen through the MAIN worktree:"
git -C "$W/lane" config --null --list 2>/dev/null | tr '\0' '\n' | grep -i promisor | sed 's/^/     /' || echo "     (none)"

audit() { # label lane fleet
  out=$(python3 "$TOOL" --lane-repo "$2" --fleet-repo "$3" --branch master \
        --lane kama --rounds 1 --no-errata 2>&1); rc=$?
  printf '  %-34s rc=%s  %s\n' "$1" "$rc" "$(printf '%s' "$out" | tail -1)"
}
echo
echo "audit through the MARKED path (linked worktree):"
audit "lane-wt (marked scope)" "$W/lane-wt" "$W/fleet"
echo "audit through the UNMARKED path (main worktree):"
audit "lane (sibling scope)"   "$W/lane"    "$W/fleet"
echo
echo "same repository, two paths -> the verdicts must agree."
