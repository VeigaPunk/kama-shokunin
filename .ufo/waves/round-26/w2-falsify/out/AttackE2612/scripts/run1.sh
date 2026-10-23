#!/bin/bash
set -u
PORT=$1
TAG=$2
D=/fast/scratch/hyaku/kama-r26w2/AttackE2612/run
LOG=$D/$TAG.log
MODEL=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
timeout 300 /home/vgpnk/.local/bin/llama-server -m "$MODEL" --host 127.0.0.1 --port "$PORT" -t 2 >"$LOG" 2>&1 &
PID=$!
for i in $(seq 1 240); do
  s=$(curl -s -o /dev/null -w '%{http_code}' --max-time 1 "http://127.0.0.1:$PORT/health" 2>/dev/null)
  if [ "$s" = "200" ]; then echo "ready after ${i}00ms"; break; fi
  sleep 0.25
done
echo "=== POST /v1/audio/transcriptions Content-Type: application/json body {} ==="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions" -H 'Content-Type: application/json' -d '{}' ; echo "curl_exit=$?"
echo "=== POST same path with non-JSON body 'not-json' ==="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions" -H 'Content-Type: application/json' -d 'not-json' ; echo "curl_exit=$?"
echo "=== POST same path with multipart file=true (openai style) ==="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions" -F "file=@/etc/hostname" -F "model=stories260K"; echo "curl_exit=$?"
echo "=== GET /v1/audio/transcriptions ==="
curl -sS -i --max-time 20 "http://127.0.0.1:$PORT/v1/audio/transcriptions"; echo "curl_exit=$?"
echo "=== props audio capability ==="
curl -sS --max-time 20 "http://127.0.0.1:$PORT/props" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ("has_mtmd","has_inp_audio","has_inp_video","model_path")}, indent=1))' 2>&1
kill -TERM $PID 2>/dev/null
wait $PID 2>/dev/null
sleep 1
ss -ltn | grep -q ":$PORT " && echo "PORT STILL OPEN" || echo "port $PORT closed"
grep -c "does not support audio input" "$LOG" || true
echo "log_lines=$(wc -l <"$LOG")"
