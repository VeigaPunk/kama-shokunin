#!/usr/bin/env bash
# SN01Bounds: boundary/edge tests for the three graders.
set -uo pipefail
S=/fast/scratch/hyaku/kama-r99/SN01Bounds
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
E="$S/edge"; rm -rf "$E"; mkdir -p "$E"
REV=f6e7ccc285e0c1207378f73c394acbfda58bff23

echo "########## A. control-population: --work with a space"
mkdir -p "$E/space dir"
( cd "$S" && python3 "$LANE/tools/round99-control-population.py" --repo "$LANE" --rev "$REV" \
    --counter tools/round99-router-budget.py --work "$E/space dir" ) 2>&1 | tail -2
echo "A rc=${PIPESTATUS[0]}"
find "$E/space dir" -mindepth 1 | head -5
echo "A leftovers=$(find "$E/space dir" -mindepth 1 | wc -l)"

echo "########## B. control-population: --work under a read-only dir"
mkdir -p "$E/ro"; chmod 500 "$E/ro"
( cd "$S" && python3 "$LANE/tools/round99-control-population.py" --repo "$LANE" --rev "$REV" \
    --counter tools/round99-router-budget.py --work "$E/ro/sub" ) > "$E/ro.out" 2> "$E/ro.err"
echo "B rc=$? stdout=$(wc -c < "$E/ro.out")B"
echo "B stderr tail:"; tail -4 "$E/ro.err"
chmod 700 "$E/ro"

echo "########## C. control-population: --counter is any committed blob (README.md)"
( cd "$S" && python3 "$LANE/tools/round99-control-population.py" --repo "$LANE" --rev "$REV" \
    --counter README.md --work "$E/readme" ) > "$E/readme.out" 2> "$E/readme.err"
echo "C rc=$?"; tail -3 "$E/readme.out"; tail -3 "$E/readme.err"

echo "########## D. control-population: --counter path outside the repo"
( cd "$S" && python3 "$LANE/tools/round99-control-population.py" --repo "$LANE" --rev "$REV" \
    --counter ../../../../etc/passwd --work "$E/outside" ) > "$E/outside.out" 2> "$E/outside.err"
echo "D rc=$?"; tail -2 "$E/outside.out" "$E/outside.err"

echo "########## E. autoload-states: missing --probe-file"
mkdir -p "$E/c3a"
python3 "$LANE/tools/round99-autoload-states.py" --repo "$LANE" --rev "$REV" \
  --probe-file "$E/does-not-exist.sh" --work "$E/c3a" > "$E/c3a.out" 2> "$E/c3a.err"
echo "E rc=$?"; tail -3 "$E/c3a.out"; tail -3 "$E/c3a.err"
echo "E leftovers under work: $(find "$E/c3a" -mindepth 1 | wc -l)"

echo "########## F. autoload-states: --work under a read-only dir"
mkdir -p "$E/ro3"; chmod 500 "$E/ro3"
python3 "$LANE/tools/round99-autoload-states.py" --repo "$LANE" --rev "$REV" \
  --work "$E/ro3/sub" > "$E/ro3.out" 2> "$E/ro3.err"
echo "F rc=$?"; tail -3 "$E/ro3.err"
chmod 700 "$E/ro3"

echo "########## G. record-audit: missing --work parent chain + bad rev"
python3 "$LANE/tools/round99-record-audit.py" --repo "$LANE" --rev deadbeef --work "$E/c2" \
  > "$E/c2.out" 2> "$E/c2.err"
echo "G rc=$?"; cat "$E/c2.out"

echo "########## H. record-audit: --tree is not written (mtime of every file before/after)"
T="$S/tree-m2"
before=$(find "$T" -type f -printf '%T@ %p\n' | sort | md5sum)
python3 "$LANE/tools/round99-record-audit.py" --repo "$LANE" --tree "$T" --work "$E/c2t" \
  > "$E/c2t.out" 2> "$E/c2t.err"
echo "H rc=$?"; tail -1 "$E/c2t.out"
after=$(find "$T" -type f -printf '%T@ %p\n' | sort | md5sum)
[ "$before" = "$after" ] && echo "H tree unchanged" || echo "H TREE CHANGED"

echo DONE
