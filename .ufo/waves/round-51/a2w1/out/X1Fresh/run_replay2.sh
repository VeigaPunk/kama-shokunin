#!/bin/bash
set -u
S=/fast/scratch/hyaku/kama-r51/X1Fresh
export TMPDIR="$S"
cd "$S" || exit 9
mkdir -p "$S/work2" "$S/wd2"
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work "$S/work2" --out "$S/result2.json" --witness-dir "$S/wd2" \
  > "$S/replay2.log" 2>&1 &
RID=$!
echo "replay_pid=$RID"
for i in $(seq 1 3000); do
  [ -f "$S/wd2/ready.json" ] && break
  kill -0 "$RID" 2>/dev/null || { echo "replay exited before ready"; break; }
  sleep 0.2
done
echo "--- dirs after start:"; ls -ld "$S/work2" "$S/wd2" 2>&1
if [ -f "$S/wd2/ready.json" ]; then
  cat "$S/wd2/ready.json"; echo
  echo "--- holding release 8s; result.json exists? $( [ -f "$S/result2.json" ] && echo yes || echo no )"
  ps -o pid,ppid,etimes,comm -p 863942 2>/dev/null >/dev/null
  pgrep -af llama-server
  sleep 8
  echo "--- after 8s: result2 exists? $( [ -f "$S/result2.json" ] && echo yes || echo no ); replay alive? $(kill -0 $RID 2>/dev/null && echo yes || echo no)"
  : > "$S/wd2/release"
  echo released
else
  echo "no ready.json"
fi
wait "$RID"; echo "exit=$?"
