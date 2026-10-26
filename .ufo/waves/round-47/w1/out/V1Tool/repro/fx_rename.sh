#!/usr/bin/env bash
# F2: rename of a declared file (--no-renames => delete+add on the old path).
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
    for i in range(30):
        fh.write(f"log line {i}\n")
PY
git -C "$D" add -A
git -C "$D" commit -qm c1
git -C "$D" mv LOG.md RENAMED.md
git -C "$D" commit -qm c2
echo "== numstat for the rename (no-renames) =="
git -C "$D" diff --numstat --no-renames HEAD~1 HEAD
echo "== tool run =="
python3 "$TOOL" --repo "$D" --to HEAD --files LOG.md,RENAMED.md --json
echo "exit=$?"
