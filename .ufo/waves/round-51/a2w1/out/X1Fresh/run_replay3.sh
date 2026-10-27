#!/bin/bash
set -u
S=/fast/scratch/hyaku/kama-r51/X1Fresh
export TMPDIR="$S"
cd "$S" || exit 9
mkdir -p "$S/wd3"          # witness dir created; work3 and out parent NOT created
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work "$S/work3" --out "$S/nodir3/result3.json" --witness-dir "$S/wd3" \
  > "$S/replay3.log" 2>&1 &
RID=$!
for i in $(seq 1 3000); do
  [ -f "$S/wd3/ready.json" ] && break
  kill -0 "$RID" 2>/dev/null || { echo "replay exited before ready"; break; }
  sleep 0.2
done
echo "-- work3 exists? $( [ -d "$S/work3" ] && echo yes || echo no )"
echo "-- nodir3 exists? $( [ -d "$S/nodir3" ] && echo yes || echo no )"
[ -f "$S/wd3/ready.json" ] && { cat "$S/wd3/ready.json"; echo; sleep 2; : > "$S/wd3/release"; echo released; }
wait "$RID"; echo "exit=$?"
echo "-- after: nodir3 exists? $( [ -d "$S/nodir3" ] && echo yes || echo no )"
