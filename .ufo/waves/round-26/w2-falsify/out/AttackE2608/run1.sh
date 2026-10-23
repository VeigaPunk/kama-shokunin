#!/bin/bash
PORT=$1; TAG=$2; shift 2
LOG=run-$TAG.log
timeout 120 ~/.local/bin/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port $PORT "$@" -t 2 > $LOG 2>&1 &
SRV=$!
for i in $(seq 1 60); do
  if curl -sf -o /dev/null --max-time 2 http://127.0.0.1:$PORT/health; then break; fi
  if ! kill -0 $SRV 2>/dev/null; then echo "SERVER_EXITED_EARLY"; break; fi
  sleep 1
done
echo "=== POST /v1/rerank (port $PORT, args: $@) ==="
curl -sS --max-time 30 -w '\nHTTP_STATUS=%{http_code}\n' -X POST http://127.0.0.1:$PORT/v1/rerank \
  -H 'Content-Type: application/json' -d '{"query":"test","documents":["a","b"]}' | tee body-$TAG.txt
echo "curl_rc=$?"
echo "=== signature in startup log? ==="
grep -c -F 'This server does not support reranking' $LOG; echo "grep_log_rc=$?"
kill $SRV 2>/dev/null; wait $SRV 2>/dev/null; echo "server_wait_rc=$?"
sleep 0.5
ss -ltn | grep -q ":$PORT " && echo "PORT_STILL_OPEN" || echo "PORT_$PORT_CLOSED"
