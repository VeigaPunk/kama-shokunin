#!/usr/bin/env bash
# F1: binary change on a declared file -> numstat prints '-', no event, no crash.
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
os.makedirs(os.path.join(D, "corpus", "lessons"))
with open(os.path.join(D, "corpus", "lessons", "r1.md"), "w") as fh:
    for i in range(30):
        fh.write(f"binary line {i}\n")
PY
git -C "$D" add -A
git -C "$D" commit -qm c1
python3 - "$D" <<'PY'
import sys, os
D = sys.argv[1]
with open(os.path.join(D, "corpus", "lessons", "r1.md"), "wb") as fh:
    fh.write(b"\x00\x01\x02" * 50)   # binary blob
PY
git -C "$D" add -A
git -C "$D" commit -qm c2
echo "== numstat for the binary change =="
git -C "$D" diff --numstat --no-renames HEAD~1 HEAD
echo "== tool run =="
python3 "$TOOL" --repo "$D" --to HEAD --files corpus/lessons/r1.md --json
echo "exit=$?"
echo "== counter recompute parity =="
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-append-audit-v2-check.py --repo "$D" --tip HEAD --scratch "$S" 2>&1 | head -4
