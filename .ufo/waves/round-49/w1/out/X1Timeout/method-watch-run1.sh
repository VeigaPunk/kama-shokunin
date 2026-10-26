#!/bin/bash
# Witness-timeout observation: run a witnessed replay with --witness-timeout 5 and
# never create the release file. Record the timeline of the harness child's life.
set -u
S=/fast/scratch/hyaku/kama-r49/X1Timeout
export TMPDIR="$S"
L="$S/lane"
W="$S/wit"
mkdir -p "$W"
rm -f "$W/ready.json" "$W/release"
LOG="$S/timeline.log"
: > "$LOG"
T0=$(date +%s%3N)
echo "$T0 replay_start_ms" >> "$LOG"
python3 "$L/tools/kama-live-replay.py" \
  --receipt "$L/.ufo/waves/round-48/c2/live/receipt-2.json" \
  --work "$S/work" --out "$S/replay-out.json" \
  --witness-dir "$W" --witness-timeout 5 \
  > "$S/replay.log" 2>&1 &
RP=$!
PID=""
PORT=""
while kill -0 "$RP" 2>/dev/null; do
  if [ -z "$PID" ] && [ -f "$W/ready.json" ]; then
    read -r PID PORT < <(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d["pid"], d["port"])' "$W/ready.json" 2>/dev/null)
    TR=$(date +%s%3N)
    echo "$TR ready_seen_ms pid=$PID port=$PORT alive=$( [ -e /proc/$PID ] && echo yes || echo no)" >> "$LOG"
    echo "exe=$(readlink /proc/$PID/exe 2>&1)" >> "$LOG"
    echo "cmdline=$(tr '\0' ' ' < /proc/$PID/cmdline 2>&1)" >> "$LOG"
  fi
  sleep 0.02
done
wait "$RP"; rc=$?
TEND=$(date +%s%3N)
echo "$TEND replay_exit=$rc dur_ms=$((TEND-T0))" >> "$LOG"
if [ -n "$PID" ]; then
  echo "$TEND pid=$PID alive_after=$( [ -e /proc/$PID ] && echo yes || echo no )" >> "$LOG"
  ps -o pid=,stat=,cmd= -p "$PID" >> "$LOG" 2>&1 || echo "ps: gone" >> "$LOG"
fi
echo "listen on recorded port ${PORT:-none}:" >> "$LOG"
ss -ltnp 2>/dev/null | grep -F ":$PORT " >> "$LOG" 2>&1 || echo "no listener on $PORT" >> "$LOG"
echo "pgrep llama-server:" >> "$LOG"
pgrep -af llama-server >> "$LOG" 2>&1 || echo "none" >> "$LOG"
echo "witness dir:" >> "$LOG"
ls -la "$W" >> "$LOG" 2>&1
echo "ready.json:" >> "$LOG"
cat "$W/ready.json" >> "$LOG" 2>&1
echo "release exists: $( [ -e "$W/release" ] && echo yes || echo no )" >> "$LOG"
exit 0
