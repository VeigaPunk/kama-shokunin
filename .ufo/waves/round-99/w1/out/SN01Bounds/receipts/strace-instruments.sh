#!/usr/bin/env bash
# SN01Bounds: strace every instrument for write-mode opens, mkdir, unlink, bind.
set -uo pipefail
S=/fast/scratch/hyaku/kama-r99/SN01Bounds
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
T="$S/strace"; rm -rf "$T"; mkdir -p "$T/c1" "$T/c2" "$T/c3"

TRACE=(strace -f -qq -s 300 -e trace=openat,open,creat,mkdir,mkdirat,unlink,unlinkat,rename,renameat,renameat2,socket,bind)

echo "### C3 autoload-states"
"${TRACE[@]}" -o "$T/c3.trace" python3 "$LANE/tools/round99-autoload-states.py" \
  --repo "$LANE" --rev f6e7ccc285e0c1207378f73c394acbfda58bff23 \
  --probe-file "$LANE/.ufo/waves/round-99/candidates/kama-probe.r99.sh" \
  --work "$T/c3/w" > "$T/c3.out" 2> "$T/c3.err"
echo "c3 rc=$?"

echo "### C2 record-audit (committed rev)"
"${TRACE[@]}" -o "$T/c2.trace" python3 "$LANE/tools/round99-record-audit.py" \
  --repo "$LANE" --rev f6e7ccc285e0c1207378f73c394acbfda58bff23 \
  --work "$T/c2/w" > "$T/c2.out" 2> "$T/c2.err"
echo "c2 rc=$?"

echo "### C1 control-population"
"${TRACE[@]}" -o "$T/c1.trace" python3 "$LANE/tools/round99-control-population.py" \
  --repo "$LANE" --rev f6e7ccc285e0c1207378f73c394acbfda58bff23 \
  --counter tools/round99-router-budget.py --work "$T/c1/w" > "$T/c1.out" 2> "$T/c1.err"
echo "c1 rc=$?"

echo "### leftovers under each --work"
find "$T" -mindepth 1 -maxdepth 3 -type d | sort
echo "### kama-probe temp dirs in /tmp"
ls -d /tmp/kama-probe.* 2>/dev/null || echo none
