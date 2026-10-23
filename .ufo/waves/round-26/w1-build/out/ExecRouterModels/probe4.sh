#!/usr/bin/env bash
set -u
PORT="${PORT:-47671}"
LOGDIR=/fast/scratch/hyaku/kama-r26/ExecRouterModels
mkdir -p "$LOGDIR/probe4"
LOG="$LOGDIR/probe4/server.log"
MODEL=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
SERVER=/home/vgpnk/.local/bin/llama-server
rm -f "$LOG"
timeout 120 "$SERVER" -m "$MODEL" --host 127.0.0.1 --port "$PORT" -t 2 >"$LOG" 2>&1 &
SRVPID=$!
for i in $(seq 1 100); do
  if ! kill -0 "$SRVPID" 2>/dev/null; then echo "SERVER DIED EARLY"; cat "$LOG"; exit 1; fi
  CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:$PORT/health 2>/dev/null)
  if [ "$CODE" = "200" ]; then break; fi
  sleep 0.2
done
dump() { echo "### $1"; shift; curl -s -m 15 -w '\n__STATUS__%{http_code}\n' "$@"; }
POST() { dump "$1" -X POST -H 'Content-Type: application/json' -d "$2" "http://127.0.0.1:$PORT$3"; }
POST "POST /v1/chat/completions/control unknown model" '{"model":"nope-model-xyz","messages":[{"role":"user","content":"hi"}],"action":"stop"}' /v1/chat/completions/control
POST "POST /v1/chat/completions/control no model" '{"messages":[{"role":"user","content":"hi"}],"action":"stop"}' /v1/chat/completions/control
POST "POST /v1/chat/completions/control bad action" '{"model":"nope-model-xyz","action":"bogus-action"}' /v1/chat/completions/control
POST "POST /slots/0 invalid slot" '{"action":"stop"}' /slots/7
POST "POST /completion model-only" '{"model":"nope-model-xyz"}' /completion
POST "POST /tokenize empty" '{}' /tokenize
POST "POST /props unknown model" '{"model":"nope-model-xyz"}' /props
dump "GET /lora-adapters" http://127.0.0.1:$PORT/lora-adapters
kill "$SRVPID" 2>/dev/null; wait "$SRVPID" 2>/dev/null; echo "== server stopped"
