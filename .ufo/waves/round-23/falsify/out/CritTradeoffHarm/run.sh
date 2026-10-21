#!/usr/bin/env bash
# CritTradeoffHarm: real-workflow repo layouts vs frozen (4fe9339f) and current (245a37f6) audit.
set -u
REAL_LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
REAL_FLEET=/home/vgpnk/Projects/shokunin
CLONE=/tmp/kama-r23w2/CritTradeoffHarm
FX=/tmp/kama-r23w2/CritTradeoffHarm-fx
G() { GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git "$@"; }
rm -rf "$FX/w"; mkdir -p "$FX/w" "$FX/arms"
G -C "$CLONE" show 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py > "$FX/arms/frozen.py"
G -C "$CLONE" show 245a37f69628c2c6bb29bbf17897d8fb5946c857:tools/report-landing-audit.py > "$FX/arms/current.py"
sha256sum "$FX/arms/"*.py
W="$FX/w"
cell() { # name lane fleet [extra args...]
  local name=$1 lane=$2 fleet=$3; shift 3
  for arm in frozen current; do
    local out; out=$(cd /tmp && timeout 120 python3 "$FX/arms/$arm.py" --lane-repo "$lane" ${fleet:+--fleet-repo "$fleet"} --rounds 10-22 "$@" 2>&1)
    local rc=$?
    printf '%-34s %-7s rc=%s  %s\n' "$name" "$arm" "$rc" "$(printf '%s' "$out" | tail -1 | cut -c1-170)"
  done
}
cell_default() { # name dir: arm copied to dir/tools, run with default --lane-repo/--fleet-repo
  local name=$1 dir=$2
  for arm in frozen current; do
    cp "$FX/arms/$arm.py" "$dir/tools/report-landing-audit.py"
    local out; out=$(cd /tmp && timeout 120 python3 "$dir/tools/report-landing-audit.py" --rounds 10-22 2>&1)
    local rc=$?
    printf '%-34s %-7s rc=%s  %s\n' "$name" "$arm" "$rc" "$(printf '%s' "$out" | tail -1 | cut -c1-170)"
  done
}
# R0 real lane + real fleet (read-only)
cell R0-real-lane-real-fleet "$REAL_LANE" "$REAL_FLEET"
# R1 seat clone --no-hardlinks (wave contract) + real fleet
G clone -q --no-hardlinks "$REAL_LANE" "$W/r1"
cell R1-noHardlinks-seat "$W/r1" "$REAL_FLEET"
# R2 --shared lane + --shared fleet (rounds 20-22 seat recipe)
G clone -q --shared "$REAL_LANE" "$W/r2lane"; G clone -q --shared --no-checkout "$REAL_FLEET" "$W/r2fleet"
cell R2-shared-lane-shared-fleet "$W/r2lane" "$W/r2fleet"
# R3 bare lane + mirror fleet (round-21 LessonPointers recipe)
G clone -q --bare "$REAL_LANE" "$W/r3lane.git"; G clone -q --mirror "$REAL_FLEET" "$W/r3fleet.git"
cell R3-bare-lane-mirror-fleet "$W/r3lane.git" "$W/r3fleet.git"
# R4 lane as git worktree (tower layout) nested under a fleet clone, default --fleet-repo
G clone -q --no-hardlinks "$REAL_FLEET" "$W/r4fleet"
mkdir -p "$W/r4fleet/.tower/worktrees/kaika"
G -C "$W/r1" worktree add -q --detach "$W/r4fleet/.tower/worktrees/kaika/kama-shokunin" master
cell R4b-tower-worktree-explicit-fleet "$W/r4fleet/.tower/worktrees/kaika/kama-shokunin" "$W/r4fleet"
cell_default R4-tower-worktree-default-fleet "$W/r4fleet/.tower/worktrees/kaika/kama-shokunin"
# R4c full lane clone nested in fleet clone (real layout), defaults
G clone -q --no-hardlinks "$REAL_LANE" "$W/r4fleet/kama-shokunin"
cell_default R4c-nested-lane-clone-defaults "$W/r4fleet/kama-shokunin"
# R5 default invocation from a seat clone (fleet = parent dir, not a repo)
cell_default R5-seat-default-fleet "$W/r1"
# R6 depth-limited lane clone deep enough for every round (CI-style --depth)
G clone -q --depth 400 "file://$REAL_LANE" "$W/r6lane"
echo "r6 shallow=$(G -C "$W/r6lane" rev-parse --is-shallow-repository) commits=$(G -C "$W/r6lane" rev-list --count HEAD) full=$(G -C "$REAL_LANE" rev-list --count refs/heads/master)"
cell R6-depth-lane-covering-all "$W/r6lane" "$REAL_FLEET"
# R7 shallow fleet clone, depth 1 (single-commit fleet history)
G clone -q --depth 1 --no-checkout "file://$REAL_FLEET" "$W/r7fleet"
cell R7-depth1-fleet "$REAL_LANE" "$W/r7fleet"
# R8 blobless fleet via file:// promisor (T01 on real data)
G -c uploadpack.allowFilter=true -c protocol.file.allow=always clone -q --no-checkout --filter=blob:none "file://$REAL_FLEET" "$W/r8fleet" 2>&1 | tail -1
echo "r8 promisor=$(G -C "$W/r8fleet" config --get remote.origin.promisor)"
cell R8-blobless-fleet "$REAL_LANE" "$W/r8fleet"
# R9 treeless lane clone
G -c uploadpack.allowFilter=true -c protocol.file.allow=always clone -q --no-checkout --filter=tree:0 "file://$REAL_LANE" "$W/r9lane" 2>&1 | tail -1
cell R9-treeless-lane "$W/r9lane" "$REAL_FLEET"
