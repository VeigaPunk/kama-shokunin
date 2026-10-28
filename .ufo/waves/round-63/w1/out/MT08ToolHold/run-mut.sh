#!/bin/bash
# usage: run-mut.sh NAME REP  (NAME = M1a|...; commits the clone's edit, runs the unmutated counter from the clone)
S=/fast/scratch/hyaku/kama-r63/w/MT08ToolHold
NAME=$1; REP=$2
D=$S/clone-$NAME
test "$(git -C $D rev-parse --show-toplevel)" = "$D" || { echo "toplevel mismatch"; exit 9; }
git -C $D add -A
git -C $D -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "mutant $NAME" 2>/dev/null
T=$(git -C $D rev-parse HEAD)
W=$S/work-$NAME-$REP
rm -rf $W; mkdir -p $W
t0=$(date +%s%N)
( cd $D/tools && python3 round63-c1-counter.py --repo $D --tip $T --work $W > $S/out-$NAME-$REP.txt 2> $S/err-$NAME-$REP.txt )
rc=$?
t1=$(date +%s%N)
echo "$NAME rep=$REP tip=$T rc=$rc wall_ms=$(( (t1-t0)/1000000 ))"
cat $S/out-$NAME-$REP.txt
head -c 600 $S/err-$NAME-$REP.txt
