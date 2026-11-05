#!/usr/bin/env bash
# SC01SourceOpen — census conformance check for the proposed SOURCES row S580.
#
# Read-only against the lane: it copies corpus/SOURCES.md into a scratch tree
# (the lane tree is never written), appends the candidate row, and runs the
# fleet's own scripts/sources-census.sh in `validate` and `census` mode.
#
# Usage: bash census-check.sh <lane-repo> <scratch-dir>
set -u
LANE=$1
SCRATCH=$2
CENSUS=/home/vgpnk/Projects/shokunin/scripts/sources-census.sh
TODAY=2026-11-05

rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/lane"
for e in "$LANE"/*; do
  b=$(basename "$e")
  [ "$b" = corpus ] && continue
  ln -s "$e" "$SCRATCH/lane/$b"
done
ln -s "$LANE/.ufo" "$SCRATCH/lane/.ufo"
mkdir -p "$SCRATCH/lane/corpus"
for e in "$LANE"/corpus/*; do
  b=$(basename "$e")
  [ "$b" = SOURCES.md ] && continue
  ln -s "$e" "$SCRATCH/lane/corpus/$b"
done

append_row() { # $1 = used-by value
  cp "$LANE/corpus/SOURCES.md" "$SCRATCH/lane/corpus/SOURCES.md"
  python3 - "$SCRATCH/lane/corpus/SOURCES.md" "$1" <<'PY'
import sys
path, usedby = sys.argv[1], sys.argv[2]
row = (
    "| S580 | CommonMark0.31.2 list items — https://spec.commonmark.org/0.31.2/#list-items"
    " | spec | A | List-item container rule in kama rendered-cell selection (round-87 C1 rule R1)"
    " | Version0.31.2 (2024-01-28), section5.2 List items, opening definition of list-item content,"
    " opened2026-11-05: \"A list item may contain any kind of block:\""
    " | The content of a list item is block content nested in that item, so a line beginning with a list"
    " marker is never a closing fence of an enclosing fenced block"
    f" | mined | 2026-11-05 | on-release | {usedby} |"
)
s = open(path, encoding="utf-8").read()
m = "\n## Paths"
assert m in s, "anchor '## Paths' not found"
open(path, "w", encoding="utf-8").write(s.replace(m, "\n" + row + m, 1))
PY
}

run() { # $1 = label, $2 = mode
  echo "--- $1 ($2 mode) ---"
  bash "$CENSUS" "$2" --file "$SCRATCH/lane/corpus/SOURCES.md" --today "$TODAY" \
    | grep -E "S580|	E[0-9]+	|FLEET	(rows|tier\.A|status\.mined)" || true
  bash "$CENSUS" "$2" --file "$SCRATCH/lane/corpus/SOURCES.md" --today "$TODAY" >/dev/null 2>&1
  echo "exit=$?"
}

echo "=== lane: $LANE ==="
cp "$LANE/corpus/SOURCES.md" "$SCRATCH/lane/corpus/SOURCES.md"
run "baseline (no S580)" validate
run "baseline (no S580)" census

append_row "round-87 C1"
run "S580 used-by=round-87 C1" validate
run "S580 used-by=round-87 C1" census

append_row "corpus/lessons/round-87.md"
# The lesson file the round-87 obligation creates must exist for E11.  Replace the
# lessons symlink with a real copy FIRST, so nothing can be written through the
# symlink back into the lane tree.
rm -f "$SCRATCH/lane/corpus/lessons"
cp -rL "$LANE/corpus/lessons" "$SCRATCH/lane/corpus/lessons"
printf '# round 87\n\nplaceholder: the used-by path must exist for E11\n' \
  > "$SCRATCH/lane/corpus/lessons/round-87.md"
run "S580 used-by=corpus/lessons/round-87.md" validate
run "S580 used-by=corpus/lessons/round-87.md" census
