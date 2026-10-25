#!/bin/bash
# usage: run.sh <mutation-name>
# Fixture repo = shared clone of the lane clone, checked out at the measured candidate 3d9bd8d,
# with the named mutation staged into tools/ and committed on top.  Writes
# $SEAT/<name>.{out,err,selftest,diff,dir,toplevel}
set -u
NAME=$1
TIP=3d9bd8d72366e281fab291874524130428ee423d
SEAT=/fast/scratch/kama-r42/seats/R42B20
D=$(mktemp -d -p /fast/scratch/kama-r42/seats)
rmdir "$D"
git clone -q --shared /fast/scratch/kama-r42/clone "$D" || exit 4
git -C "$D" checkout -q "$TIP" || exit 4
TOP=$(git -C "$D" rev-parse --show-toplevel)
[ "$TOP" = "$D" ] || { echo "toplevel mismatch: $TOP != $D" >&2; exit 4; }
REV=$TIP
if [ "$NAME" != none ]; then
    python3 "$SEAT/mut.py" "$NAME" "$D" || exit 3
    git -C "$D" add -A -- tools/ || exit 3
    git -C "$D" -c user.name=R42B20 -c user.email=r42b20@seat.invalid commit -qm "mutation $NAME" || exit 3
    REV=$(git -C "$D" rev-parse HEAD)
    git -C "$D" diff "$TIP" -- tools/ > "$SEAT/$NAME.diff"
fi
export TMPDIR="$SEAT/tmp"
python3 "$D/tools/digest-ledger.py" selftest > "$SEAT/$NAME.selftest" 2>&1
echo "selftest_exit=$?" >> "$SEAT/$NAME.selftest"
S=$(date +%s%N)
python3 "$D/tools/round42-digest-audit.py" --repo "$D" --tip "$REV" --seed 42 > "$SEAT/$NAME.out" 2> "$SEAT/$NAME.err"
echo "counter_exit=$?" >> "$SEAT/$NAME.out"
echo "wall_ms=$(( ($(date +%s%N) - S) / 1000000 ))" >> "$SEAT/$NAME.out"
echo "$D" > "$SEAT/$NAME.dir"
