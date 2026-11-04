#!/bin/sh
# kama r76 C1 control input: fence-blind vs fence-stripped vs all-stripped populations.
# Runs only in a scratch shared clone (never the lane) and prints the frozen base tool's verdict
# for each reading. Usage: fence-dryrun.sh <lane> <scratch>
set -u
LANE=$1; SCRATCH=$2
for mode in fences all; do
  d="$SCRATCH/$mode"; rm -rf "$d"
  git clone -q --shared "$LANE" "$d"
  ( cd "$d" && python3 "$LANE/.ufo/waves/round-76/controls/fence-dryrun.py" "$mode" \
    && git -c user.name=kama-shokunin -c user.email=kama@shokunin.local commit -aqm "scratch: $mode record view" >/dev/null )
  ( cd "$d" && python3 tools/round72-receipt-tip-binding.py --repo . --round 75 --tip HEAD >"$d/base.out" 2>&1; rc=$?
    echo "mode=$mode"; tail -9 "$d/base.out"; echo "mode=$mode exit=$rc" )
done
