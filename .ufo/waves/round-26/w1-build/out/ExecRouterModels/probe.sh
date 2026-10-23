#!/usr/bin/env bash
# Probe llama-server fixture for round-26 C1 candidate signatures.
# Usage: probe.sh DAYNAME [extra server args...]
set -u
NAME="${1:?need run name}"
shift
PORT="${PORT:-47668}"
LOGDIR=/fast/scratch/hyaku/kama-r26/ExecRouterModels
mkdir -p "$LOGDIR/$NAME"
LOG="$LOGDIR/$NAME/server.log"
MODEL=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
SERVER=/home/vgpnk/.local/bin/llama-server
rm -f "$LOG"
timeout 120 "$SERVER" -m "$MODEL" --host 127.0.0.1 --port "$PORT" -t 2 "$@" >"$LOG" 2>&1 &
SRVPID=$!
# wait for health
READY=0
for i in $(seq 1 100); do
  if ! kill -0 "$SRVPID" 2>/dev/null; then echo "SERVER DIED EARLY"; cat "$LOG"; exit 1; fi
  CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:$PORT/health 2>/dev/null)
  if [ "$CODE" = "200" ]; then READY=1; break; fi
  sleep 0.2
done
if [ "$READY" != "1" ]; then echo "NOT READY"; cat "$LOG"; kill "$SRVPID" 2>/dev/null; wait "$SRVPID" 2>/dev/null; exit 1; fi
echo "== server ready pid=$SRVPID port=$PORT"
dump() {
  echo "### $1"
  shift
  curl -s -m 15 -w '\n__STATUS__%{http_code}\n' "$@"
}
dump "GET /health" http://127.0.0.1:$PORT/health
dump "GET /v1/models" http://127.0.0.1:$PORT/v1/models
dump "GET /props" http://127.0.0.1:$PORT/props
dump "GET /slots" http://127.0.0.1:$PORT/slots
dump "POST /models/load missing model" -X POST -H 'Content-Type: application/json' -d '{"model":"nope-model-xyz"}' http://127.0.0.1:$PORT/models/load
dump "POST /models/unload missing model" -X POST -H 'Content-Type: application/json' -d '{"model":"nope-model-xyz"}' http://127.0.0.1:$PORT/models/unload
dump "POST /models" -X POST -H 'Content-Type: application/json' -d '{"model":"nope-model-xyz"}' http://127.0.0.1:$PORT/models
dump "POST /models/load empty body" -X POST -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:$PORT/models/load
dump "POST /models/load bad json" -X POST -H 'Content-Type: application/json' -d '{bad json' http://127.0.0.1:$PORT/models/load
dump "POST /completion bad json" -X POST -H 'Content-Type: application/json' -d '{bad json' http://127.0.0.1:$PORT/completion
dump "POST /v1/chat/completions unknown model" -X POST -H 'Content-Type: application/json' -d '{"model":"nope-model-xyz","messages":[{"role":"user","content":"hi"}]}' http://127.0.0.1:$PORT/v1/chat/completions
dump "POST /v1/completions unknown model" -X POST -H 'Content-Type: application/json' -d '{"model":"nope-model-xyz","prompt":"hi"}' http://127.0.0.1:$PORT/v1/completions
dump "POST /tokenize unknown-extra" -X POST -H 'Content-Type: application/json' -d '{"content":"hi","model":"nope-model-xyz"}' http://127.0.0.1:$PORT/tokenize
dump "POST /properties" -X POST -H 'Content-Type: application/json' -d '{"foo":"bar"}' http://127.0.0.1:$PORT/props
dump "POST /embeddings unknown model" -X POST -H 'Content-Type: application/json' -d '{"model":"nope-model-xyz","input":"hi"}' http://127.0.0.1:$PORT/embeddings
dump "GET /does-not-exist-xyz" http://127.0.0.1:$PORT/does-not-exist-xyz
kill "$SRVPID" 2>/dev/null
wait "$SRVPID" 2>/dev/null
echo "== server stopped"
