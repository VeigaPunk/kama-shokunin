#!/bin/bash
# MT01 driver: runs the C1 counter against each forged-tool mode.
# Old (pre-started, non-dumpable) helpers are started BEFORE the counter run for O3/O4.
set -u
S=/fast/scratch/hyaku/kama-r64/b/MT01DumpableHide
D=$S/clone
T=$(cat $S/forge-tip.txt)
cd "$S" || exit 2
run_mode() {
  local mode="$1"
  rm -f "$S/forge/served.log" "$S/forge/state.log" "$S/forge/forge-mode.txt"
  local helper_pid=""
  if [ "$mode" = "O3" ] || [ "$mode" = "O4" ]; then
    rm -f "$S/forge/ctl-$mode.sock"
    setsid python3 "$S/forge/helper.py" "$S/forge/ctl-$mode.sock" >"$S/forge/helper-$mode.log" 2>&1 </dev/null &
    helper_pid=$!
    for _ in $(seq 1 50); do [ -S "$S/forge/ctl-$mode.sock" ] && break; sleep 0.1; done
    echo "old helper $mode pid=$helper_pid uid=$(awk '/^Uid/{print $2}' /proc/$helper_pid/status)" >>"$S/run-log.txt"
  fi
  echo "$mode" > "$S/forge/forge-mode.txt"
  python3 "$S/wrap.py" "$D/tools/round64-c1-counter.py" --repo "$D" --tip "$T" --work "$S/work-$mode" \
    > "$S/out-$mode.txt" 2> "$S/err-$mode.txt"
  echo "$mode counter_exit=$?" >>"$S/run-log.txt"
  [ -n "$helper_pid" ] && kill "$helper_pid" 2>/dev/null
  cp -f "$S/forge/served.log" "$S/served-$mode.log" 2>/dev/null
  cp -f "$S/forge/state.log" "$S/state-$mode.log" 2>/dev/null
  true
}
for m in T1 T2 O3 O4; do run_mode "$m"; done
echo DONE >>"$S/run-log.txt"
