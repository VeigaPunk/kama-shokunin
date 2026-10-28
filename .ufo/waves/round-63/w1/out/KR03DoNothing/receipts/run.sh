#!/bin/bash
# usage: run.sh <c1|c2> <name>   (commits the mutant clone, runs the counter from its tools dir)
set -u
S=/fast/scratch/hyaku/kama-r63/w/KR03DoNothing; M=$S/m/$2
git -C "$M" rev-parse --show-toplevel | grep -qx "$M" || { echo "not a clone: $M"; exit 9; }
git -C "$M" add -A && git -C "$M" -c user.name=seat -c user.email=seat@seat.invalid commit -q -m mutant
T=$(git -C "$M" rev-parse HEAD)
if [ "$1" = c1 ]; then SC=round63-c1-counter.py; else SC=round63-c2-counter.py; fi
cd "$M/tools" && python3 "$SC" --repo "$M" --tip "$T" --work "$S/w-$2" > "$S/out/$2.stdout" 2> "$S/out/$2.stderr"; echo "exit=$?" >> "$S/out/$2.stdout"
echo "$2 T=$T" >> "$S/out/$2.stdout"
