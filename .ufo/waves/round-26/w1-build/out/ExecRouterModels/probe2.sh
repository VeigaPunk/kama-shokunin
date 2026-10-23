#!/usr/bin/env bash
# Probe2: wide net on remaining endpoints with unknown/weird model fields.
set -u
NAME="${1:?need run name}"
shift
PORT="${PORT:-47669}"
LOGDIR=/fast/scratch/hyaku/kama-r26/ExecRouterModels
mkdir -p "$LOGDIR/$NAME"
LOG="$LOGDIR/$NAME/server.log"
MODEL=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
SERVER=/home/vgpnk/.local/bin/llama-server
rm -f "$LOG"
timeout 120 "$SERVER" -m "$MODEL" --host 127.0.0.1 --port "$PORT" -t 2 "$@" >"$LOG" 2>&1 &
SRVPID=$!
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
POST() { dump "$1" -X POST -H 'Content-Type: application/json' -d "$2" "http://127.0.0.1:$PORT$3"; }

# unknown model name across all inference-ish endpoints
POST "POST /completion unknown model" '{"model":"nope-model-xyz","prompt":"hi","n_predict":4}' /completion
POST "POST /completions unknown model" '{"model":"nope-model-xyz","prompt":"hi","n_predict":4}' /completions
POST "POST /v1/responses unknown model" '{"model":"nope-model-xyz","input":"hi","max_output_tokens":4}' /v1/responses
POST "POST /responses unknown model" '{"model":"nope-model-xyz","input":"hi","max_output_tokens":4}' /responses
POST "POST /v1/messages unknown model" '{"model":"nope-model-xyz","messages":[{"role":"user","content":"hi"}],"max_tokens":4}' /v1/messages
POST "POST /chat/completions/control unknown model" '{"model":"nope-model-xyz","messages":[{"role":"user","content":"hi"}],"action":"stop"}' /chat/completions/control
POST "POST /v1/chat/completions/input_tokens unknown model" '{"model":"nope-model-xyz","messages":[{"role":"user","content":"hi"}]}' /v1/chat/completions/input_tokens
POST "POST /responses/input_tokens unknown model" '{"model":"nope-model-xyz","input":"hi"}' /responses/input_tokens
POST "POST /v1/messages/count_tokens unknown model" '{"model":"nope-model-xyz","messages":[{"role":"user","content":"hi"}]}' /v1/messages/count_tokens
POST "POST /infill unknown model" '{"model":"nope-model-xyz","input_prefix":"a","input_suffix":"b","n_predict":4}' /infill
POST "POST /v1/rerank unknown model" '{"model":"nope-model-xyz","query":"q","documents":["d"]}' /v1/rerank
POST "POST /v1/systemone unknown model" '{"model":"nope-model-xyz","messages":[{"role":"user","content":"hi"}],"max_tokens":4}' /v1/systemone
POST "POST /apply-template unknown model" '{"model":"nope-model-xyz","messages":[{"role":"user","content":"hi"}]}' /apply-template
POST "POST /detokenize unknown model" '{"model":"nope-model-xyz","tokens":[1,2]}' /detokenize
POST "POST /lora-adapters" '{"model":"nope-model-xyz","path":"/tmp/x.gguf"}' /lora-adapters
POST "POST /slots/0 stop" '{"action":"stop"}' /slots/0
# malformed model field types
POST "POST /v1/chat/completions model number" '{"model":123,"messages":[{"role":"user","content":"hi"}],"max_tokens":4}' /v1/chat/completions
POST "POST /v1/chat/completions model null" '{"model":null,"messages":[{"role":"user","content":"hi"}],"max_tokens":4}' /v1/chat/completions
POST "POST /v1/chat/completions model array" '{"model":[1,2],"messages":[{"role":"user","content":"hi"}],"max_tokens":4}' /v1/chat/completions
POST "POST /v1/chat/completions no model" '{"messages":[{"role":"user","content":"hi"}],"max_tokens":4}' /v1/chat/completions
POST "POST /v1/chat/completions empty messages" '{"model":"nope-model-xyz","messages":[],"max_tokens":4}' /v1/chat/completions
POST "POST /tokenize model number" '{"model":123,"content":"hi"}' /tokenize
POST "POST /completion prompt not string" '{"prompt":123,"n_predict":2}' /completion
# model-name-in-path
dump "GET /v1/models/nope-model-xyz" http://127.0.0.1:$PORT/v1/models/nope-model-xyz
dump "GET /models/nope-model-xyz" http://127.0.0.1:$PORT/models/nope-model-xyz
dump "GET /v1/models/health" http://127.0.0.1:$PORT/v1/models/health
kill "$SRVPID" 2>/dev/null
wait "$SRVPID" 2>/dev/null
echo "== server stopped"
