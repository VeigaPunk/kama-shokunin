#!/bin/sh
# X5Selftest (round 52): reproduce the sabotage matrix in this directory.
# Read-only on the lane: every sabotage is applied to a copy with `patch -o`.
# Usage: S=/fast/scratch/hyaku/kama-r52/X5Selftest ./reproduce.sh
set -u
O=$(cd "$(dirname "$0")" && pwd)
S=${S:?set S to your scratch dir}
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
BUILD=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8          # round-52 build
CLONE=$S/lane
export TMPDIR=$S

[ -d "$CLONE/.git" ] || git clone -q --shared "$LANE" "$CLONE"
git -C "$CLONE" checkout -q "$BUILD"
git -C "$CLONE" rev-parse HEAD

mkdir -p "$S/r"
# replay-side sabotages a, a2, b, c, d (selftest --scratch needs an existing dir)
for t in a a2 b c d; do
    mkdir -p "$S/r/$t"
    patch -s -o "$S/r/$t/kama-live-replay.py" "$CLONE/tools/kama-live-replay.py" < "$O/sabotage-$t.diff"
    python3 "$S/r/$t/kama-live-replay.py" --selftest --scratch "$S/r/$t" > "$S/r/$t.out" 2>&1
    echo "sabotage-$t exit=$?  $(grep -c '^FAIL' "$S/r/$t.out") FAIL lines"
done
# live-side sabotages e, f, g: the tool needs <lane>/registry beside tools/
for t in e f g; do
    mkdir -p "$S/r/$t/tools"
    ln -sfn "$CLONE/registry" "$S/r/$t/registry"
    patch -s -o "$S/r/$t/tools/kama-llamacpp-live.py" "$CLONE/tools/kama-llamacpp-live.py" < "$O/sabotage-$t.diff"
    python3 "$S/r/$t/tools/kama-llamacpp-live.py" --selftest > "$S/r/$t.out" 2>&1
    echo "sabotage-$t exit=$?"
done
# the two proposals, on the pristine tool and on each of their sabotages
mkdir -p "$S/r/prop/tools" "$S/r/e/tools" "$S/r/f/tools" "$S/r/g/tools"
ln -sfn "$CLONE/registry" "$S/r/prop/registry"
patch -s -o "$S/r/prop/tools/kama-llamacpp-live.py" "$CLONE/tools/kama-llamacpp-live.py" \
    < "$O/proposal-live-server-fd-selftest.diff"
python3 "$S/r/prop/tools/kama-llamacpp-live.py" --selftest; echo "proposal-live on pristine exit=$?"
for t in e f g; do
    patch -s -o "$S/r/$t/tools/prop.py" "$S/r/$t/tools/kama-llamacpp-live.py" \
        < "$O/proposal-live-server-fd-selftest.diff"
    python3 "$S/r/$t/tools/prop.py" --selftest; echo "proposal-live on sabotage-$t exit=$?"
done
patch -s -o "$S/r/hard.py" "$CLONE/tools/kama-live-replay.py" < "$O/proposal-replay-sealed-member-case.diff"
mkdir -p "$S/r/hard"
python3 "$S/r/hard.py" --selftest --scratch "$S/r/hard" | tail -1
echo "proposal-replay on pristine exit=$?"
patch -s -o "$S/r/a/hard.py" "$S/r/a/kama-live-replay.py" < "$O/proposal-replay-sealed-member-case.diff"
python3 "$S/r/a/hard.py" --selftest --scratch "$S/r/a" > "$S/r/a-hard.out" 2>&1
echo "proposal-replay on sabotage-a exit=$?  $(grep -c '^FAIL' "$S/r/a-hard.out") FAIL lines"
