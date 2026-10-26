#!/usr/bin/env bash
# Micro-checks: cat-file --batch-check parsing edges + numstat -z layout.
set -u
S=/fast/scratch/hyaku/kama-r47/V1Tool
D=$(mktemp -d -p "$S")
git -C "$D" init -q
git -C "$D" config user.name fx
git -C "$D" config user.email fx@fx
printf 'a\nb\nc\n' > "$D/x.md"
git -C "$D" add -A
git -C "$D" commit -qm c1
echo "== batch-check with missing + tree + blob specs =="
printf 'HEAD:x.md\nHEAD:y.md\nHEAD:\nHEAD\n' | git -C "$D" cat-file --batch-check='%(objectname) %(objecttype)'
echo "== diff --numstat -z layout (fix probe) =="
printf 'new\n' >> "$D/x.md"
printf 'caf\xc3\xa9.md\n' > "$D/y.md"
git -C "$D" add -A
git -C "$D" commit -qm c2
git -C "$D" diff --numstat -z HEAD~1 HEAD | od -An -c | head -8
echo "== raw (non -z) numstat =="
git -C "$D" diff --numstat --no-renames HEAD~1 HEAD
