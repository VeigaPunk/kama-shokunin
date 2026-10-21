#!/bin/sh
# Rebuilds the C2DigestSentinel scratch used by run_all.sh. Reads the lane
# repo only (clone + checkout into /tmp); never writes into the lane.
set -e
W=/tmp/kama-r21-C2DigestSentinel
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$(dirname "$HERE")
LANE_REPO=/home/vgpnk/Projects/shokunin/kama-shokunin
rm -rf "$W"
mkdir -p "$W/attacks" "$W/work/src"
git clone -q "$LANE_REPO" "$W/lane"
git -C "$W/lane" checkout -q a6617149722c73d90e142fbdc8154d6967055f7e
cp "$HERE"/*.py "$HERE"/run_all.sh "$W/attacks/"
cp "$OUT"/src/*.c "$W/work/src/"
cp "$LANE_REPO/.ufo/waves/round-21/runs/b76727f3/live-receipt.json" "$W/work/live-receipt.json"
cd "$W/work"
gcc -shared -fPIC -Wl,-soname,libllama.so.0 -o libllama-A.so.0.7.0 src/libA.c
gcc -shared -fPIC -Wl,-soname,libllama.so.0 -o libllama-B.so.0.7.1 src/libB.c
gcc -o host-bin src/host.c ./libllama-A.so.0.7.0 -Wl,-rpath,'$ORIGIN'
echo "setup-ok: run  sh $W/attacks/run_all.sh"
