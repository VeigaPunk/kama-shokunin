#!/bin/bash
# MT01 final driver: unmutated (frozen) counter, fresh --work per mode, fresh old helper for O3/O4.
set -u
S=/fast/scratch/hyaku/kama-r64/b/MT01DumpableHide
D=$S/clone
T=$(cat $S/forge-tip.txt)
cd "$S" || exit 2
run_mode() {
  local mode="$1"
  rm -rf "$S/work-final-$mode"
  rm -f "$S/forge/forge-mode.txt" "$S/forge/served.log" "$S/forge/state.log"
  local helper_pid=""
  if [ "$mode" = "O3" ] || [ "$mode" = "O4" ]; then
    rm -f "$S/forge/ctl-$mode.sock"
    setsid python3 "$S/forge/helper.py" "$S/forge/ctl-$mode.sock" >"$S/forge/helper-$mode-final.log" 2>&1 </dev/null &
    helper_pid=$!
    for _ in $(seq 1 50); do [ -S "$S/forge/ctl-$mode.sock" ] && break; sleep 0.1; done
    echo "final old helper $mode pid=$helper_pid uid=$(awk '/^Uid/{print $2}' /proc/$helper_pid/status)" >>"$S/run-final-log.txt"
  fi
  echo "$mode" > "$S/forge/forge-mode.txt"
  python3 "$S/wrap.py" "$S/genuine-counter.py" --repo "$D" --tip "$T" --work "$S/work-final-$mode" \
    > "$S/out-final-$mode.txt" 2> "$S/err-final-$mode.txt"
  echo "final $mode counter_exit=$?" >>"$S/run-final-log.txt"
  [ -n "$helper_pid" ] && kill "$helper_pid" 2>/dev/null
  cp -f "$S/forge/served.log" "$S/served-final-$mode.log" 2>/dev/null
  cp -f "$S/forge/state.log" "$S/state-final-$mode.log" 2>/dev/null
  true
}
for m in T1 O3 O4; do run_mode "$m"; done
echo DONE >>"$S/run-final-log.txt"
