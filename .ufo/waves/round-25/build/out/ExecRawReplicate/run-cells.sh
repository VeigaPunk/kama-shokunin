#!/usr/bin/env bash
# ExecRawReplicate - independent raw replication of C2 (round 25) without the lane tool.
# Plain shell only: llama-server + curl + python3 (json).
# One child at a time, one port per cell, teardown confirmed per cell.
set -u

SERVER="$HOME/.local/bin/llama-server"
MODEL="$HOME/.cache/kama-shokunin/models/stories260K.gguf"
OUT="/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/build/out/ExecRawReplicate"
SCRATCH="/fast/scratch/hyaku/kama-r25/ExecRawReplicate"
HOST="127.0.0.1"

mkdir -p "$OUT" "$SCRATCH"

# cell id : port : server args
CELLS=(
  "K1 47420 -c 0"
  "K2 47421 -c 2048 -np 2 --no-kv-unified"
  "K3 47422 -c 2048 -np 2 --kv-unified"
  "K4 47423 -c 1024 -np 1"
  "K5 47424 -c 4096 -np 1"
  "K6 47425 -c 1000 -np 3 --no-kv-unified"
  "K7 47426 -np 2 --kv-unified-per-slot 512"
  "K8 47427 -c 4096 -np 4 --kv-unified --kv-unified-per-slot 512"
)

RUNLOG="$OUT/run-cells.log"
: > "$RUNLOG"

for spec in "${CELLS[@]}"; do
  set -- $spec
  CELL="$1"; PORT="$2"; shift 2
  ARGS="$*"
  CDIR="$OUT/$CELL"
  mkdir -p "$CDIR"
  LOG="$SCRATCH/$CELL.server.log"

  {
    echo "=== cell $CELL ==="
    echo "port: $PORT"
    echo "args: $ARGS"
    echo "started_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$CDIR/meta.txt"

  # 1. port must be free before launch
  if ss -ltn | grep -q ":$PORT[[:space:]]"; then
    echo "port $PORT NOT FREE before launch" >> "$CDIR/meta.txt"
    echo "$CELL: PORT_BUSY $PORT" >> "$RUNLOG"
    continue
  fi
  echo "port_free_before: yes" >> "$CDIR/meta.txt"

  # 2. launch one child
  "$SERVER" -m "$MODEL" --host "$HOST" --port "$PORT" $ARGS > "$LOG" 2>&1 &
  PID=$!
  echo "pid: $PID" >> "$CDIR/meta.txt"

  # 3. wait for readiness (GET /health -> 200)
  READY=0
  for i in $(seq 1 60); do
    if ! kill -0 "$PID" 2>/dev/null; then break; fi
    CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "http://$HOST:$PORT/health" || echo 000)
    if [ "$CODE" = "200" ]; then READY=1; break; fi
    sleep 1
  done
  echo "ready: $READY (health 200 attempts=$i)" >> "$CDIR/meta.txt"

  # 4. capture raw bodies
  for ep in props slots v1/models; do
    fname=$(echo "$ep" | tr '/' '_')
    http=$(curl -s --max-time 10 -o "$CDIR/$fname.json" -w '%{http_code}' "http://$HOST:$PORT/$ep")
    rc=$?
    echo "curl /$ep http=$http exit=$rc bytes=$(wc -c < "$CDIR/$fname.json")" >> "$CDIR/meta.txt"
  done

  # 5. copy the server log into the capture dir
  cp "$LOG" "$CDIR/server.log"

  # 6. teardown: kill the child, wait, confirm the port is closed
  kill "$PID" 2>/dev/null
  kill_rc=$?
  for i in $(seq 1 20); do
    kill -0 "$PID" 2>/dev/null || break
    sleep 0.5
  done
  if kill -0 "$PID" 2>/dev/null; then
    kill -9 "$PID" 2>/dev/null
    echo "SIGKILL needed" >> "$CDIR/meta.txt"
  fi
  wait "$PID" 2>/dev/null
  wait_rc=$?
  sleep 1
  if ss -ltn | grep -q ":$PORT[[:space:]]"; then
    CLOSED=no
  else
    CLOSED=yes
  fi
  {
    echo "kill_exit: $kill_rc"
    echo "wait_exit: $wait_rc"
    echo "port_closed_after_kill: $CLOSED"
    echo "ended_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >> "$CDIR/meta.txt"
  echo "$CELL: ready=$READY port=$PORT closed=$CLOSED" >> "$RUNLOG"
done

echo "done"
