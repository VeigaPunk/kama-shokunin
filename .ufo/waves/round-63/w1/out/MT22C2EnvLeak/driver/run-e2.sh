#!/bin/bash
S="/fast/scratch/hyaku/kama-r63/w/MT22C2EnvLeak"; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; D="/fast/scratch/hyaku/kama-r63/w/MT22C2EnvLeak/clone"; T="58ba80d086cdb703eeac8c970c9a36c2c1e3c7b9"
cd "$S/runs"
run_counter() { local name=$1 tool=$2 repo=$3 tip=$4; shift 4
  env "$@" POISON_MARK="$S/marks/$name.txt" python3 "$tool" --repo "$repo" --tip "$tip" --work "$S/runs/work-$name" > "$S/runs/$name.out" 2> "$S/runs/$name.err"; echo "rc=$?" >> "$S/runs/$name.out"; }
run_driver() { local name=$1 tool=$2 mode=$3; shift 3
  env "$@" POISON_MARK="$S/marks/$name.txt" python3 "$S/driver/rowdiff.py" "$tool" "$mode" "$L" 03a6a1d850902a66a13dfad33f89cf3a8b759a09 "$S/runs/work-$name" > "$S/runs/$name.out" 2> "$S/runs/$name.err"; echo "rc=$?" >> "$S/runs/$name.out"; }
run_driver D-full-proxy "$D/tools/round63-c2-counter.py" full HTTP_PROXY=http://127.0.0.1:9 LD_PRELOAD="$S/poison/preload/mark.so"
run_driver D-full-json "$D/tools/round63-c2-counter.py" full PYTHONPATH="$S/poison/json-shadow" LD_PRELOAD="$S/poison/preload/mark.so"
run_driver D-full-forge "$D/tools/round63-c2-counter.py" full PYTHONPATH="$S/poison/forge" LD_PRELOAD="$S/poison/preload/mark.so"
run_driver D-allow-forge "$L/tools/round63-c2-counter.py" allow PYTHONPATH="$S/poison/forge" LD_PRELOAD="$S/poison/preload/mark.so"
run_counter M-forge "$D/tools/round63-c2-counter.py" "$D" "$T" PYTHONPATH="$S/poison/forge"
run_counter U-forge "$L/tools/round63-c2-counter.py" "$L" 03a6a1d850902a66a13dfad33f89cf3a8b759a09 PYTHONPATH="$S/poison/forge"
echo ALLDONE > "$S/runs/ALLDONE2"
