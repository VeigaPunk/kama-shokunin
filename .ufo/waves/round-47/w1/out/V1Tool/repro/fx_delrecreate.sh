#!/usr/bin/env bash
# F3: declared file deleted entirely (event), then recreated fully (restored),
# then half-trimmed again (window max must keep it restored).
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
with open(os.path.join(D, "SCORECARD.md"), "w") as fh:
    for i in range(40):
        fh.write(f"score line {i}\n")
PY
git -C "$D" add -A
git -C "$D" commit -qm c1
git -C "$D" rm -q SCORECARD.md
git -C "$D" commit -qm c2-delete
python3 - "$D" <<'PY'
import sys, os
D = sys.argv[1]
with open(os.path.join(D, "SCORECARD.md"), "w") as fh:
    for i in range(40):
        fh.write(f"score line {i}\n")
PY
git -C "$D" add -A
git -C "$D" commit -qm c3-recreate
python3 - "$D" <<'PY'
import sys, os
D = sys.argv[1]
with open(os.path.join(D, "SCORECARD.md"), "w") as fh:
    for i in range(20):
        fh.write(f"score line {i}\n")
PY
git -C "$D" add -A
git -C "$D" commit -qm c4-trim
echo "== tool run =="
python3 "$TOOL" --repo "$D" --to HEAD --files SCORECARD.md --json
echo "exit=$?"
