#!/bin/bash
PORT=$1; TAG=$2; shift 2
LOG=run3-$TAG.log
timeout 180 ~/.local/bin/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port $PORT "$@" -t 2 > $LOG 2>&1 &
SRV=$!
READY=0
for i in $(seq 1 90); do
  if curl -sf -o /dev/null --max-time 2 http://127.0.0.1:$PORT/health; then READY=1; break; fi
  if ! kill -0 $SRV 2>/dev/null; then echo "SERVER_EXITED_EARLY rc=$(wait $SRV; echo $?)"; break; fi
  sleep 0.5
done
echo "READY=$READY log_bytes=$(stat -c%s $LOG)"
pgrep -a llama-server
echo "=== POST /v1/rerank port $PORT args:[$*] ==="
curl -sS --max-time 30 -w '\nHTTP_STATUS=%{http_code}\n' -X POST http://127.0.0.1:$PORT/v1/rerank \
  -H 'Content-Type: application/json' -d '{"query":"test","documents":["a","b"]}' | tee body3-$TAG.txt
echo "sig_in_log_lines=$(grep -c -F 'This server does not support reranking' $LOG)"
kill $SRV 2>/dev/null; wait $SRV 2>/dev/null; echo "killed"
sleep 0.5
ss -ltn | grep -q ":$PORT " && echo "PORT_${PORT}_STILL_OPEN" || echo "PORT_${PORT}_CLOSED"
