#!/bin/bash
set -u
S=/fast/scratch/hyaku/kama-r51/X1Fresh
export TMPDIR="$S"
mkdir -p "$S/work" "$S/wd"
cd "$S" || exit 9
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work "$S/work" --out "$S/result.json" --witness-dir "$S/wd" \
  > "$S/replay.log" 2>&1 &
RID=$!
echo "replay_pid=$RID"
for i in $(seq 1 3000); do
  if [ -f "$S/wd/ready.json" ]; then break; fi
  if ! kill -0 "$RID" 2>/dev/null; then echo "replay exited before ready"; break; fi
  sleep 0.2
done
if [ -f "$S/wd/ready.json" ]; then
  echo "ready.json:"; cat "$S/wd/ready.json"; echo
  cp "$S/wd/ready.json" "$S/ready-captured.json"
  : > "$S/wd/release"
  echo "released"
else
  echo "no ready.json"
fi
wait "$RID"; echo "exit=$?"
