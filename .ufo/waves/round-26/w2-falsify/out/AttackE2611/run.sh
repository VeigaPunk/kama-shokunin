#!/usr/bin/env bash
# One llama-server child at a time on 127.0.0.1:47740; registered E26-11 trigger plus next-action probes.
set -u
P=47740
OUT=/fast/scratch/hyaku/kama-r26w2/AttackE2611
RUN=$1
SRV=$HOME/.local/bin/llama-server
M=$HOME/.cache/kama-shokunin/models/stories260K.gguf
LOG=$OUT/server-run$RUN.log
timeout 180 "$SRV" -m "$M" --host 127.0.0.1 --port $P -t 2 >"$LOG" 2>&1 &
PID=$!
for i in $(seq 1 240); do
  s=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:$P/health)
  [ "$s" = 200 ] && break
  sleep 0.25
done
echo "run $RUN health=$s"
req() { # name method path body
  echo "--- $1: $2 $3 body=$4"
  curl -s -w '\nHTTP %{http_code}\n' -X "$2" -H 'Content-Type: application/json' ${4:+--data-binary "$4"} "http://127.0.0.1:$P$3"
}
req registered POST /lora-adapters '{"id": 0, "scale": 1.0}'
if [ "$RUN" = 1 ]; then
  req get-list GET /lora-adapters ''
  req wrapped POST /lora-adapters '[{"id": 0, "scale": 1.0}]'
  req empty-array POST /lora-adapters '[]'
  req string-body POST /lora-adapters '"x"'
  req not-json POST /lora-adapters 'not json'
  req empty-body POST /lora-adapters ''
fi
kill -TERM $PID 2>/dev/null; wait $PID; echo "server exit $?"
for i in $(seq 1 20); do ss -ltn | grep -q ":$P " || break; sleep 0.25; done
ss -ltn | grep ":$P " && echo "PORT STILL OPEN" || echo "port $P closed"
