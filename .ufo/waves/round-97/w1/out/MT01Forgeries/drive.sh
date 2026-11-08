#!/usr/bin/env bash
# MT01 round-97 w1: drive both counters over the pristine probe and my five mutants.
# Control/natural-only paths: no burners are raised by this driver.
set -u
S=/fast/scratch/hyaku/kama-r97/MT01Forgeries
REV=9e605d41
R=$S/receipts
mkdir -p "$R" "$S/work97" "$S/work96"
probe() { case "$1" in P) echo "$S/pristine/kama-probe.sh";; *) echo "$S/mut/$1/kama-probe.sh";; esac; }

run97() { # label cells expect
  local lab=$1 cells=$2 exp=$3
  {
    python3 "$S/lane/tools/round97-router-budget.py" --repo "$S/lane" --rev "$REV" \
      --work "$S/work97/r97-$lab-$cells" --cells "$cells" --control --expect "$exp" \
      --probe-file "$(probe "$lab")"
    echo "exit=$?"
  } > "$R/r97-$lab-$cells.out" 2>&1
}

run96() { # label
  local lab=$1
  {
    python3 "$S/lane/tools/round96-router-budget.py" --repo "$S/lane" --rev "$REV" \
      --work "$S/work96/r96-$lab" --runs 1 --slow-files 40 --burners 0 --allow-clock --skip-load \
      --probe-file "$(probe "$lab")"
    echo "exit=$?"
  } > "$R/r96-$lab.out" 2>&1
}

one() { # label : all three instruments
  local lab=$1
  run97 "$lab" legacy survived &
  run97 "$lab" new survived &
  run96 "$lab" &
  wait
  echo "DONE $lab"
}

wave() { for l in "$@"; do one "$l" & done; wait; }

wave P A B
wave C D E
echo ALL_DONE
