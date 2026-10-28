#!/bin/bash
# MT22C2EnvLeak E1: real counters + per-row driver under clean / poison caller envs.
S="/fast/scratch/hyaku/kama-r63/w/MT22C2EnvLeak"; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; D="/fast/scratch/hyaku/kama-r63/w/MT22C2EnvLeak/clone"; T="58ba80d086cdb703eeac8c970c9a36c2c1e3c7b9"
P1="PYTHONPATH=$S/poison/json-shadow HTTP_PROXY=http://127.0.0.1:9 LD_PRELOAD=$S/poison/preload/mark.so"
P0="KAMA_PROBE_LEAK=1 LD_PRELOAD=$S/poison/preload/mark.so"
cd "$S/runs"
run_counter() { # name tool repo tip poison...
  local name=$1 tool=$2 repo=$3 tip=$4; shift 4
  env "$@" POISON_MARK="$S/marks/$name.txt" python3 "$tool" --repo "$repo" --tip "$tip" --work "$S/runs/work-$name" > "$S/runs/$name.out" 2> "$S/runs/$name.err"
  echo "rc=$?" >> "$S/runs/$name.out"
}
run_driver() { # name tool mode poison...
  local name=$1 tool=$2 mode=$3; shift 3
  env "$@" POISON_MARK="$S/marks/$name.txt" python3 "$S/driver/rowdiff.py" "$tool" "$mode" "$L" 03a6a1d850902a66a13dfad33f89cf3a8b759a09 "$S/runs/work-$name" > "$S/runs/$name.out" 2> "$S/runs/$name.err"
  echo "rc=$?" >> "$S/runs/$name.out"
}
run_counter U-P1 "$L/tools/round63-c2-counter.py" "$L" 03a6a1d850902a66a13dfad33f89cf3a8b759a09 PYTHONPATH="$S/poison/json-shadow" HTTP_PROXY=http://127.0.0.1:9 LD_PRELOAD="$S/poison/preload/mark.so"
run_counter M-clean "$D/tools/round63-c2-counter.py" "$D" "$T" PATH="$PATH" HOME="$HOME"
run_counter M-P1 "$D/tools/round63-c2-counter.py" "$D" "$T" PYTHONPATH="$S/poison/json-shadow" HTTP_PROXY=http://127.0.0.1:9 LD_PRELOAD="$S/poison/preload/mark.so"
run_counter M-P0 "$D/tools/round63-c2-counter.py" "$D" "$T" KAMA_PROBE_LEAK=1 LD_PRELOAD="$S/poison/preload/mark.so"
run_counter U-P0 "$L/tools/round63-c2-counter.py" "$L" 03a6a1d850902a66a13dfad33f89cf3a8b759a09 KAMA_PROBE_LEAK=1 LD_PRELOAD="$S/poison/preload/mark.so"
run_driver D-allow-clean "$L/tools/round63-c2-counter.py" allow
run_driver D-allow-P1 "$L/tools/round63-c2-counter.py" allow PYTHONPATH="$S/poison/json-shadow" HTTP_PROXY=http://127.0.0.1:9 LD_PRELOAD="$S/poison/preload/mark.so"
run_driver D-full-P1 "$D/tools/round63-c2-counter.py" full PYTHONPATH="$S/poison/json-shadow" HTTP_PROXY=http://127.0.0.1:9 LD_PRELOAD="$S/poison/preload/mark.so"
run_driver D-full-P0 "$D/tools/round63-c2-counter.py" full KAMA_PROBE_LEAK=1 LD_PRELOAD="$S/poison/preload/mark.so"
echo ALLDONE > "$S/runs/ALLDONE"
