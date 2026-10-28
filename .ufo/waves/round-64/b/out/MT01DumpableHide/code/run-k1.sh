#!/bin/bash
# MT01 driver: K1 counter mutant (status-Uid owner, no start-time gate) against
# the forged tip. NONE = honest genuine-tool control (mode file absent).
set -u
S=/fast/scratch/hyaku/kama-r64/b/MT01DumpableHide
D=$S/clone
T=$(cat $S/forge-tip.txt)
cd "$S" || exit 2
run_mode() {
  local mode="$1"
  rm -f "$S/forge/forge-mode.txt" "$S/forge/served.log" "$S/forge/state.log"
  local helper_pid=""
  if [ "$mode" = "O3" ] || [ "$mode" = "O4" ]; then
    rm -f "$S/forge/ctl-$mode.sock"
    setsid python3 "$S/forge/helper.py" "$S/forge/ctl-$mode.sock" >"$S/forge/helper-$mode-k1.log" 2>&1 </dev/null &
    helper_pid=$!
    for _ in $(seq 1 50); do [ -S "$S/forge/ctl-$mode.sock" ] && break; sleep 0.1; done
    echo "k1 old helper $mode pid=$helper_pid" >>"$S/run-k1-log.txt"
  fi
  if [ "$mode" != "NONE" ]; then echo "$mode" > "$S/forge/forge-mode.txt"; fi
  python3 "$S/wrap.py" "$D/tools/round64-c1-counter.py" --repo "$D" --tip "$T" --work "$S/work-k1-$mode" \
    > "$S/out-k1-$mode.txt" 2> "$S/err-k1-$mode.txt"
  echo "k1 $mode counter_exit=$?" >>"$S/run-k1-log.txt"
  [ -n "$helper_pid" ] && kill "$helper_pid" 2>/dev/null
  cp -f "$S/forge/served.log" "$S/served-k1-$mode.log" 2>/dev/null
  true
}
for m in NONE T1 O3 O4; do run_mode "$m"; done
echo DONE >>"$S/run-k1-log.txt"
