#!/bin/bash
# Third sample: sample the held server's liveness every 200 ms so the hold window
# (server continuously alive) and the teardown instant are both measured.
set -u
S=/fast/scratch/hyaku/kama-r49/X1Timeout
export TMPDIR="$S"
L="$S/lane"
W="$S/wit3"
mkdir -p "$W"
rm -f "$W/ready.json" "$W/release"
LOG="$S/timeline3.log"
: > "$LOG"
T0=$(date +%s%3N)
python3 "$L/tools/kama-live-replay.py" \
  --receipt "$L/.ufo/waves/round-48/c2/live/receipt-2.json" \
  --work "$S/work3" --out "$S/replay-out3.json" \
  --witness-dir "$W" --witness-timeout 5 \
  > "$S/replay3.log" 2>&1 &
RP=$!
PID=""; TR=0; LAST_ALIVE=0
while kill -0 "$RP" 2>/dev/null; do
  if [ -z "$PID" ] && [ -f "$W/ready.json" ]; then
    PID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["pid"])' "$W/ready.json")
    TR=$(date +%s%3N)
    echo "$TR ready_seen_ms pid=$PID" >> "$LOG"
  fi
  if [ -n "$PID" ]; then
    TN=$(date +%s%3N)
    if [ -e "/proc/$PID" ]; then LAST_ALIVE=$TN; echo "$TN alive t_since_ready_ms=$((TN-TR))" >> "$LOG"; fi
  fi
  sleep 0.2
done
wait "$RP"; rc=$?
TEND=$(date +%s%3N)
echo "$TEND replay_exit=$rc dur_ms=$((TEND-T0)) t_since_ready_ms=$((TEND-TR))" >> "$LOG"
echo "last_alive_t_since_ready_ms=$((LAST_ALIVE-TR)) death_after_ready_ms=$((TEND-TR))" >> "$LOG"
echo "alive_after=$( [ -e /proc/$PID ] && echo yes || echo no )" >> "$LOG"
echo "port=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["port"])' "$W/ready.json")" >> "$LOG"
ss -ltn 2>/dev/null | grep -F "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["port"])' "$W/ready.json")" >> "$LOG" 2>&1 || echo "no listener after exit" >> "$LOG"
pgrep -af "X1Timeout" >> "$LOG" 2>&1 || echo "no process of mine left" >> "$LOG"
exit 0
