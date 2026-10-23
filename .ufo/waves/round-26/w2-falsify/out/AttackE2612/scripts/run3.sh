#!/bin/bash
set -u
PORT=47746
D=/fast/scratch/hyaku/kama-r26w2/AttackE2612/run
MODEL=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
timeout 240 /home/vgpnk/.local/bin/llama-server -m "$MODEL" --host 127.0.0.1 --port $PORT -t 2 >"$D/e2612-run3.log" 2>&1 &
PID=$!
for i in $(seq 1 240); do s=$(curl -s -o /dev/null -w '%{http_code}' --max-time 1 "http://127.0.0.1:$PORT/health" 2>/dev/null); [ "$s" = "200" ] && { echo "ready"; break; }; sleep 0.25; done
echo "=== (a) POST no body, no content-type ==="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions"; echo "curl_exit=$?"
echo "=== (b) POST empty body with content-type json ==="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions" -H 'Content-Type: application/json' --data-binary ''; echo "curl_exit=$?"
echo "=== (c) POST /audio/transcriptions (no v1) body {} ==="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/audio/transcriptions" -H 'Content-Type: application/json' -d '{}'; echo "curl_exit=$?"
echo "=== (d) /props keys ==="
curl -sS --max-time 20 "http://127.0.0.1:$PORT/props" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(sorted(d.keys())); print(json.dumps(d,indent=0)[:600])' 2>&1
echo "=== (e) help/version contain signature? ==="
timeout 30 /home/vgpnk/.local/bin/llama-server --help 2>&1 | grep -F -c "The current model does not support audio input." ; echo "help_grep_exit=$?"
timeout 30 /home/vgpnk/.local/bin/llama-server --version 2>&1 | grep -F -c "The current model does not support audio input." ; echo "ver_grep_exit=$?"
kill -TERM $PID 2>/dev/null; wait $PID 2>/dev/null; sleep 1
ss -ltn | grep -q ":$PORT " && echo "PORT STILL OPEN" || echo "port $PORT closed"
