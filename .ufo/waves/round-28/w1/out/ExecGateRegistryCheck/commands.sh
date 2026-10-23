#!/bin/sh
# Exact commands and outputs for the round-28 ExecGateRegistryCheck item.
# Every command ran under `timeout` on 2026-10-23; outputs are the *.out/*.err/*.exit
# files beside this script. No command writes to the lane repository.
set -eu
O=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecGateRegistryCheck
L=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/fast/scratch/hyaku/kama-r28/w1/ExecGateRegistryCheck
BASE=4179301f7516ad667509d54b5ebfe0a70a002d5b
TIP=5ebe7b1b2defa4d8109de8fcc9b28f13dd6fb5f6

# 1. Lane at the claim base 4179301f: exit 1 (two counters unregistered).
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" --repo "$L" --rev "$BASE" \
    > "$O/base-4179301.out" 2> "$O/base-4179301.err"; echo $? > "$O/base-4179301.exit"

# 2. Lane working tree at HEAD 5ebe7b1: exit 1 (three counters unregistered).
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" --repo "$L" \
    > "$O/worktree-head.out" 2> "$O/worktree-head.err"; echo $? > "$O/worktree-head.exit"

# 3. Lane at committed tip 5ebe7b1: exit 1, same three paths.
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" --repo "$L" --rev "$TIP" \
    > "$O/lane-HEAD-5ebe7b1.out" 2>&1; echo $? > "$O/lane-HEAD-5ebe7b1.exit"

# 4. Nonexistent revision: exit 2.
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" --repo "$L" --rev 0000000000000000000000000000000000000000 \
    > "$O/bad-rev.out" 2> "$O/bad-rev.err"; echo $? > "$O/bad-rev.exit"

# 5. Non-git directory: exit 2.
mkdir -p "$S/notgit"
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" --repo "$S/notgit" \
    > "$O/notgit.out" 2> "$O/notgit.err"; echo $? > "$O/notgit.exit"

# 6. Scratch clone at the base revision (hardlinks off, git env unset).
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE timeout 180 \
    git clone --no-hardlinks --quiet "$L" "$S/clone"
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE timeout 60 \
    git -C "$S/clone" checkout -q "$BASE"

# 7. Append the minimal registry mentions to clone/SKILL.md (edit applied by
#    hand; the appended block is quoted in the report), then commit.
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE timeout 60 \
    git -C "$S/clone" -c user.name='gate-registry-check scratch' \
    -c user.email='scratch@localhost' commit -q -am \
    'scratch: append round-28 gate-registry mentions (clone-only)'
# Clone commit: 18f62f891f0548f9430172d12231010d4d434143

# 8. Patched clone, working-tree mode from the clone root: exit 0.
cd "$S/clone"
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" \
    > "$O/scratch-worktree.out" 2> "$O/scratch-worktree.err"; echo $? > "$O/scratch-worktree.exit"

# 9. Patched clone at its commit: exit 0.
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" --rev HEAD \
    > "$O/scratch-rev-HEAD.out" 2> "$O/scratch-rev-HEAD.err"; echo $? > "$O/scratch-rev-HEAD.exit"

# 10. Same clone at the unpatched base revision: exit 1 (revision-only delta).
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" --rev "$BASE" \
    > "$O/scratch-rev-base.out" 2>&1; echo $? > "$O/scratch-rev-base.exit"

# 11. Untracked counter is not part of the population: exit 0.
mkdir -p "$S/clone/.ufo/waves/round-99"
printf '# untracked\n' > "$S/clone/.ufo/waves/round-99/count-x.py"
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" \
    > "$O/scratch-untracked.out" 2>&1; echo $? > "$O/scratch-untracked.exit"
rm -rf "$S/clone/.ufo/waves/round-99"

# 12. Default --repo from a subdirectory (clone/tools): exit 0.
cd "$S/clone/tools"
timeout 60 /usr/bin/python3 "$O/gate-registry-check.py" \
    > "$O/scratch-subdir.out" 2>&1; echo $? > "$O/scratch-subdir.exit"
