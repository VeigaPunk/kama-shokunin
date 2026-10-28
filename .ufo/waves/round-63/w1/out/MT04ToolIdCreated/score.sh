#!/bin/bash
# usage: score.sh <repo-clone> <label>   commits working tree in clone, scores unmutated counter at that commit
set -u
S=/fast/scratch/hyaku/kama-r63/w/MT04ToolIdCreated
D=$1; L=$2
test "$(git -C $D rev-parse --show-toplevel)" = "$D" || { echo "NOT A FIXTURE $D"; exit 9; }
git -C $D add -A && git -C $D -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "mutant $L"
T=$(git -C $D rev-parse HEAD)
echo "== $L tip=$T"
cd $S/tool/tools 2>/dev/null || cd $D/tools
python3 $D/tools/round63-c1-counter.py --repo $D --tip $T --work $S/work-$L 2>$S/err-$L.txt
echo "rc=$? stderr:"; head -c 600 $S/err-$L.txt; echo
