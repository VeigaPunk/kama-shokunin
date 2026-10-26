#!/bin/bash
# Second sample of the witness-timeout path: prove the server is up AND listening
# AND answering during the hold, then gone after the 5 s timeout expires.
set -u
S=/fast/scratch/hyaku/kama-r49/X1Timeout
export TMPDIR="$S"
L="$S/lane"
W="$S/wit2"
mkdir -p "$W"
rm -f "$W/ready.json" "$W/release"
LOG="$S/timeline2.log"
: > "$LOG"
T0=$(date +%s%3N)
python3 "$L/tools/kama-live-replay.py" \
  --receipt "$L/.ufo/waves/round-48/c2/live/receipt-2.json" \
  --work "$S/work2" --out "$S/replay-out2.json" \
  --witness-dir "$W" --witness-timeout 5 \
  > "$S/replay2.log" 2>&1 &
RP=$!
PID=""; PORT=""
while kill -0 "$RP" 2>/dev/null; do
  if [ -z "$PID" ] && [ -f "$W/ready.json" ]; then
    read -r PID PORT < <(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d["pid"], d["port"])' "$W/ready.json" 2>/dev/null)
    TR=$(date +%s%3N)
    echo "$TR ready_seen_ms pid=$PID port=$PORT alive=$( [ -e /proc/$PID ] && echo yes || echo no) since_start_ms=$((TR-T0))" >> "$LOG"
    ss -ltnp 2>/dev/null | grep -F ":$PORT " >> "$LOG" 2>&1 || echo "NO LISTENER on $PORT" >> "$LOG"
    echo "health=$(curl -s --max-time 3 -o - -w ' status=%{http_code}' "http://127.0.0.1:$PORT/health" 2>&1)" >> "$LOG"
    echo "tokenize=$(curl -s --max-time 3 -X POST -H 'Content-Type: application/json' -d '{"content":"kama witness deadbeef","with_pieces":true}' "http://127.0.0.1:$PORT/tokenize" 2>&1 | head -c 200)" >> "$LOG"
  fi
  sleep 0.02
done
wait "$RP"; rc=$?
TEND=$(date +%s%3N)
echo "$TEND replay_exit=$rc dur_ms=$((TEND-T0)) hold_after_ready_ms=$((TEND-TR))" >> "$LOG"
echo "$TEND pid=$PID alive_after=$( [ -e /proc/$PID ] && echo yes || echo no )" >> "$LOG"
echo "ss after: $(ss -ltn 2>/dev/null | grep -cF ":$PORT ")" >> "$LOG"
echo "connect after: $(curl -s --max-time 2 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/health" 2>&1; echo " rc=$?")" >> "$LOG"
pgrep -af 'llama-server .*' | grep -F "$S" >> "$LOG" 2>&1 || echo "no server of mine left" >> "$LOG"
ls -la "$W" >> "$LOG" 2>&1
exit 0
