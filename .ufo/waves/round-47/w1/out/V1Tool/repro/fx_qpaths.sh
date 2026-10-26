#!/usr/bin/env bash
# F5: contract expansion over paths with spaces (unquoted -> works) and
# non-ASCII / tab (quoted by ls-tree and numstat -> pathspec mismatch -> silent
# miss of the deletion event).
set -u
S=/fast/scratch/hyaku/kama-r47/V1Tool
TOOL=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py
D=$(mktemp -d -p "$S")
git -C "$D" init -q
git -C "$D" config user.name fx
git -C "$D" config user.email fx@fx
mkdir -p "$D/corpus/lessons" "$D/registry"
printf 'lessons are append-only\n' > "$D/AGENTS.md"
printf 'path\trule\tdeclared_at\tnote\ncorpus/lessons/*.md\tA-corr\tAGENTS.md:1\tx\n' > "$D/registry/append-only-contract.tsv"
python3 - "$D" <<'PY'
import sys, os
D = sys.argv[1]
base = os.path.join(D, "corpus", "lessons")
names = ["my file.md", "caf\xc3\xa9.md", "tab\tfile.md"]
for n in names:
    with open(os.path.join(base, n), "w") as fh:
        for i in range(30):
            fh.write(f"line {i}\n")
PY
git -C "$D" add -A
git -C "$D" commit -qm c1
python3 - "$D" <<'PY'
import sys, os
D = sys.argv[1]
base = os.path.join(D, "corpus", "lessons")
names = ["my file.md", "caf\xc3\xa9.md", "tab\tfile.md"]
for n in names:
    with open(os.path.join(base, n), "w") as fh:
        for i in range(5):
            fh.write(f"line {i}\n")   # 25 deleted each
PY
git -C "$D" add -A
git -C "$D" commit -qm c2
echo "== ls-tree name-only at tip =="
git -C "$D" ls-tree -r --name-only HEAD
echo "== numstat for c2 =="
git -C "$D" diff --numstat --no-renames HEAD~1 HEAD
echo "== tool run (contract at tip) =="
python3 "$TOOL" --repo "$D" --to HEAD --json
echo "exit=$?"
