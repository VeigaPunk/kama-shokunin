#!/usr/bin/env bash
# Probe 5:
#  (1) worktree-scoped promisor config: visible in the scope that declares
#      it, invisible to the sibling worktree of the same repository;
#  (2) end-to-end audit of a lane+fleet pair where BOTH are linked worktrees
#      of BARE repositories (bare + linked combined);
#  (3) end-to-end audit of the same pair with a worktree-scoped promisor
#      marking (does the audit still see it?).
set -u
ROOT=/fast/scratch/hyaku/kama-r24/RevBareWorktree/fixtures2
W=/fast/scratch/hyaku/kama-r24/RevBareWorktree/probe5
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
rm -rf "$W"; mkdir -p "$W"
for v in $(env | sed -n 's/^\(GIT_[A-Za-z_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

echo "=== (1) worktree-scoped promisor config"
git clone -q "$ROOT/src/lane" "$W/lane"
git -C "$W/lane" worktree add -q --detach "$W/lane-wt" HEAD
git -C "$W/lane" config extensions.worktreeConfig true
git -C "$W/lane-wt" config --worktree remote.origin.promisor true
git -C "$W/lane-wt" config --worktree remote.origin.partialclonefilter blob:none
echo "  --worktree config file(s):"
find "$W/lane/.git" -name 'config.worktree' | sed 's/^/    /'
echo "  linked worktree scope:"
git -C "$W/lane-wt" config --null --list 2>/dev/null | tr '\0' '\n' | grep -i -E 'promisor|partialclone|repositoryformat' | sed 's/^/    /'
echo "  main worktree scope:"
git -C "$W/lane" config --null --list 2>/dev/null | tr '\0' '\n' | grep -i -E 'promisor|partialclone|repositoryformat' | sed 's/^/    /' || echo "    (none)"

echo
echo "=== (2) audit: lane+fleet as linked worktrees of BARE repositories"
git clone -q --bare "$ROOT/src/lane" "$W/bare-lane"
git clone -q --bare "$ROOT/src/fleet" "$W/bare-fleet"
git -C "$W/bare-lane" worktree add -q --detach "$W/wt-lane" HEAD
git -C "$W/bare-fleet" worktree add -q --detach "$W/wt-fleet" HEAD
out=$(python3 "$TOOL" --lane-repo "$W/wt-lane" --fleet-repo "$W/wt-fleet" \
      --branch master --lane kama --rounds 1 --no-errata 2>&1); rc=$?
echo "  rc=$rc"; printf '%s\n' "$out" | sed 's/^/    /'

echo
echo "=== (3) audit: same bare+linked pair, promisor marking in the worktree scope"
git -C "$W/bare-lane" config extensions.worktreeConfig true
git -C "$W/wt-lane" config --worktree remote.origin.promisor true
git -C "$W/wt-lane" config --worktree remote.origin.partialclonefilter blob:none
out=$(python3 "$TOOL" --lane-repo "$W/wt-lane" --fleet-repo "$W/wt-fleet" \
      --branch master --lane kama --rounds 1 --no-errata 2>&1); rc=$?
echo "  rc=$rc"; printf '%s\n' "$out" | sed 's/^/    /'
echo "  (base r23 refuses promisor repos: rc=2 with 'partial clone (...)')"

echo
echo "=== (4) same, but the marking lives in the SIBLING worktree scope only"
git -C "$W/wt-lane" config --unset-all remote.origin.promisor 2>/dev/null || true
git -C "$W/wt-lane" config --unset-all remote.origin.partialclonefilter 2>/dev/null || true
git -C "$W/bare-lane" config --worktree remote.origin.promisor true
git -C "$W/bare-lane" config --worktree remote.origin.partialclonefilter blob:none
echo "  sibling scope:"
git -C "$W/bare-lane" config --null --list 2>/dev/null | tr '\0' '\n' | grep -i promisor | sed 's/^/    /'
echo "  audited path scope:"
git -C "$W/wt-lane" config --null --list 2>/dev/null | tr '\0' '\n' | grep -i promisor | sed 's/^/    /' || echo "    (none visible)"
out=$(python3 "$TOOL" --lane-repo "$W/wt-lane" --fleet-repo "$W/wt-fleet" \
      --branch master --lane kama --rounds 1 --no-errata 2>&1); rc=$?
echo "  audit rc=$rc"; printf '%s\n' "$out" | sed 's/^/    /'
