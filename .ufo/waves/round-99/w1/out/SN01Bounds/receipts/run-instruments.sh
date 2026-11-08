#!/usr/bin/env bash
# SN01Bounds: run the three round-99 instruments once each from an empty scratch dir and
# record every file they create outside it.
set -uo pipefail

S=/fast/scratch/hyaku/kama-r99/SN01Bounds
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
FLEET=/home/vgpnk/Projects/shokunin
OUT=$S/logs
mkdir -p "$OUT"

STAMP=/fast/scratch/hyaku/kama-r99/SN01Bounds/.stamp
touch "$STAMP"

snapshot() {
  local tag=$1
  {
    echo "### lane tree"
    find "$LANE" -xdev -newer "$STAMP" -not -path '*/.git/*' -not -path '*/.ufo/waves/round-99/w1/*' 2>/dev/null
    echo "### fleet root (top + scripts)"
    find "$FLEET" -maxdepth 2 -xdev -newer "$STAMP" -not -path "$LANE*" 2>/dev/null
    echo "### /tmp"
    find /tmp -xdev -newer "$STAMP" -maxdepth 3 2>/dev/null
    echo "### /home/vgpnk (maxdepth 3)"
    find /home/vgpnk -maxdepth 3 -xdev -newer "$STAMP" -not -path '/home/vgpnk/Projects/*' 2>/dev/null
  } > "$OUT/outside-$tag.txt"
}

run() { # name cmd...
  local name=$1; shift
  echo "=== $name ===" | tee "$OUT/$name.log"
  local t0=$SECONDS
  ( "$@" ) > "$OUT/$name.out" 2> "$OUT/$name.err"
  local rc=$?
  echo "exit=$rc seconds=$((SECONDS - t0))" | tee -a "$OUT/$name.log"
  tail -n 25 "$OUT/$name.out" | tee -a "$OUT/$name.log"
  return $rc
}

# --- C3: autoload states (candidate probe) ---
WORK3="$S/work c3"; mkdir -p "$WORK3"
( cd "$S" && TMPDIR=/tmp python3 "$LANE/tools/round99-autoload-states.py" \
    --repo "$LANE" --rev f6e7ccc285e0c1207378f73c394acbfda58bff23 \
    --probe-file "$LANE/.ufo/waves/round-99/candidates/kama-probe.r99.sh" \
    --work "$WORK3" ) > "$OUT/c3.out" 2> "$OUT/c3.err"
echo "c3 exit=$?" >> "$OUT/c3.log"
snapshot c3

# --- C2: record audit, committed bytes ---
WORK2="$S/work c2"; mkdir -p "$WORK2"
( cd "$S" && python3 "$LANE/tools/round99-record-audit.py" \
    --repo "$LANE" --rev f6e7ccc285e0c1207378f73c394acbfda58bff23 \
    --work "$WORK2" ) > "$OUT/c2-rev.out" 2> "$OUT/c2-rev.err"
echo "c2-rev exit=$?" >> "$OUT/c2.log"

# --- C2: record audit, in-flight tree (--tree) ---
TREE="$S/tree-m2"; mkdir -p "$TREE/.ufo/waves/round-98/measured" "$TREE/corpus/lessons" "$TREE/.ufo/waves/round-98"
cp "$LANE/SCORECARD.md" "$TREE/SCORECARD.md"
cp "$LANE/LOG.md" "$TREE/LOG.md"
cp "$LANE/corpus/lessons/round-98.md" "$TREE/corpus/lessons/round-98.md"
cp "$LANE/corpus/lessons/round-99.md" "$TREE/corpus/lessons/round-99.md"
cp "$LANE/.ufo/waves/round-98/w1-results.json" "$TREE/.ufo/waves/round-98/w1-results.json"
cp "$LANE/.ufo/waves/round-98/measured/pre-report-gate.out" "$TREE/.ufo/waves/round-98/measured/pre-report-gate.out"
WORK2T="$S/work c2 tree"; mkdir -p "$WORK2T"
( cd "$S" && python3 "$LANE/tools/round99-record-audit.py" \
    --repo "$LANE" --tree "$TREE" --work "$WORK2T" ) > "$OUT/c2-tree.out" 2> "$OUT/c2-tree.err"
echo "c2-tree exit=$?" >> "$OUT/c2.log"
snapshot c2

# --- C1: control population ---
WORK1="$S/work c1"; mkdir -p "$WORK1"
( cd "$S" && python3 "$LANE/tools/round99-control-population.py" \
    --repo "$LANE" --rev f6e7ccc285e0c1207378f73c394acbfda58bff23 \
    --counter tools/round99-router-budget.py --work "$WORK1" ) > "$OUT/c1.out" 2> "$OUT/c1.err"
echo "c1 exit=$?" >> "$OUT/c1.log"
snapshot c1

echo "=== ALL DONE ==="
