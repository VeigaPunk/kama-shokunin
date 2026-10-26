#!/usr/bin/env bash
# F4: merges are judged against the first parent only.
#  - m1 on main deletes 30 LOG.md lines (event); side branch keeps them.
#  - merge side into main: first-parent diff of the merge adds them back -> no
#    NEW event at the merge; m1 gets restored_by = merge commit.
set -u
S=/fast/scratch/hyaku/kama-r47/V1Tool
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py
D=$(mktemp -d -p "$S")
git -C "$D" init -q
git -C "$D" config user.name fx
git -C "$D" config user.email fx@fx
python3 - "$D" <<'PY'
import sys, os
D = sys.argv[1]
with open(os.path.join(D, "LOG.md"), "w") as fh:
    for i in range(40):
        fh.write(f"log line {i}\n")
PY
git -C "$D" add -A
git -C "$D" commit -qm root
git -C "$D" checkout -qb side
printf 'side file\n' > "$D/side.txt"
git -C "$D" add -A
git -C "$D" commit -qm s1
git -C "$D" checkout -q main
python3 - "$D" <<'PY'
import sys, os
D = sys.argv[1]
with open(os.path.join(D, "LOG.md"), "w") as fh:
    for i in range(10):
        fh.write(f"log line {i}\n")
PY
git -C "$D" add -A
git -C "$D" commit -qm m1-delete30
git -C "$D" merge -q --no-edit side
M=$(git -C "$D" rev-parse HEAD)
echo "== merge commit $M parents =="
git -C "$D" log -1 --format='%p' "$M"
echo "== first-parent diff numstat (merge vs parent1) =="
git -C "$D" diff --numstat --no-renames "$M^1" "$M"
echo "== tool run =="
python3 "$TOOL" --repo "$D" --to HEAD --files LOG.md --json
echo "exit=$?"
