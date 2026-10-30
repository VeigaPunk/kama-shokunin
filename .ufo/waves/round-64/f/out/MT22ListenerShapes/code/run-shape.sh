#!/bin/bash
# MT22 driver: build one forged shape, score it with the UNMUTATED amended
# counter from the clone path (verdict) and with the diagnostic copy
# (observation). usage: run-shape.sh <shape>
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT22ListenerShapes
CLONE=$S/clone
SHAPE=$1

cd "$S"
OUT=$(python3 "$S/mt22-build.py" "$SHAPE")
TIP=$(echo "$OUT" | awk '{print $2}')
echo "$OUT" >> "$S/shapes.tsv"

rm -f "$S/forge-on"
printf '{"mode": "%s"}\n' "$SHAPE" > "$S/forge-on"

DAEMON_PID=""
if [[ "$SHAPE" == *daemon ]]; then
  sudo -n python3 "$S/mt22-daemon.py" "$S/mt22-daemon.sock" 2>"$S/daemon.err" &
  DAEMON_PID=$!
  for i in $(seq 1 100); do [[ -S "$S/mt22-daemon.sock" ]] && break; sleep 0.1; done
  echo "daemon pid=$DAEMON_PID up"
fi

# --- verdict run: the unmutated counter at the clone path -------------------
python3 "$CLONE/tools/round64-c1-counter.py" --repo "$CLONE" --tip "$TIP" \
  --work "$S/work-$SHAPE" > "$S/run-$SHAPE.out" 2> "$S/run-$SHAPE.err"
RC=$?
echo "verdict run rc=$RC"

# --- observation run: the diagnostic wrapper (same logic, raw dump) ---------
rm -f "$S/forge-on"; printf '{"mode": "%s"}\n' "$SHAPE" > "$S/forge-on"
MT22_DIAG="$S/diag-$SHAPE.jsonl" python3 "$S/mt22-diag.py" \
  "$CLONE/tools/round64-c1-counter.py" --repo "$CLONE" --tip "$TIP" \
  --work "$S/diag-$SHAPE" > "$S/diag-$SHAPE.out" 2> "$S/diag-$SHAPE.err"

echo "--- verdict ($SHAPE, tip $TIP) ---"
cat "$S/run-$SHAPE.out"
echo "--- stderr tail ---"
tail -4 "$S/run-$SHAPE.err"
echo "--- diag snapshots ---"
cat "$S/diag-$SHAPE.jsonl" 2>/dev/null || echo "(none)"
echo "--- diag verdict line ---"
head -1 "$S/diag-$SHAPE.out"

if [[ -n "$DAEMON_PID" ]]; then
  sudo -n kill "$DAEMON_PID" 2>/dev/null
  sleep 0.3
fi
# clean my own leftovers
pkill -f "$S/clone/tools/.*/mt22-helper" 2>/dev/null
pkill -f "mt22-helper.py" 2>/dev/null
sleep 0.2
rm -f "$S/forge-on"
echo "done $SHAPE"
