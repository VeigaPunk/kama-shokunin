#!/usr/bin/env bash
# Reproduce the CR01 held-out receipts (holdout.out). Read-only against the lane; all writes go to
# the scratch dir named by the caller (TMPDIR must point there).
# Usage: run-holdouts.sh <lane> <scratch> <out-dir>
set -uo pipefail
lane=$1 scratch=$2 out=$3
C="$lane/tools/round92-linear-paths.py"
H="$out/holdout.py"
cd "$scratch" || exit 2
export TMPDIR=$scratch
uptime
run() { # cell probe label kill
  python3 "$H" --counter "$C" --work "$scratch/hw" --cell "$1" --probe "$2" --label "$3" --kill "${4:-240}"
}
for n in 400000 800000 1600000; do
  run "H1-mixed-$n" "$scratch/m2-probe.sh" m2 300
  run "H1-mixed-$n" "$out/forgeries/FG1-jstr-mixed.sh" FG1 300
done
run H2-router-90001 "$scratch/m2-probe.sh" m2
run H2-router-90001 "$out/forgeries/FG2-router-cap-85k.sh" FG2
for spec in "base:$scratch/base-probe.sh" "m2:$scratch/m2-probe.sh" "FG3:$out/forgeries/FG3-served-persist-m-only.sh"; do
  run H3-deep-12 "${spec#*:}" "${spec%%:*}"
done
run H3-deep-20000 "$scratch/m2-probe.sh" m2
run H3-deep-20000 "$out/forgeries/FG3-served-persist-m-only.sh" FG3
run H5-snap-30000 "$scratch/m2-probe.sh" m2
run H5-snap-30000 "$out/forgeries/FG5-served-persist-cap-20k.sh" FG5
for spec in "base:$scratch/base-probe.sh" "m2:$scratch/m2-probe.sh" "FG4:$out/forgeries/FG4-served-ids-rstrip.sh"; do
  run H4-trailing-space "${spec#*:}" "${spec%%:*}"
done
uptime
