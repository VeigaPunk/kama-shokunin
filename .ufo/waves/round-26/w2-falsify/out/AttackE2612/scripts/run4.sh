#!/bin/bash
set -u
PORT=47747
D=/fast/scratch/hyaku/kama-r26w2/AttackE2612/run
MODEL=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
timeout 240 /home/vgpnk/.local/bin/llama-server -m "$MODEL" --host 127.0.0.1 --port $PORT -t 2 >"$D/e2612-run4.log" 2>&1 &
PID=$!
for i in $(seq 1 240); do s=$(curl -s -o /dev/null -w '%{http_code}' --max-time 1 "http://127.0.0.1:$PORT/health" 2>/dev/null); [ "$s" = "200" ] && { echo "ready"; break; }; sleep 0.25; done
echo "=== (a) POST no body, no content-type ==="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions"; echo; echo "curl_exit=$?"
echo "=== modalities in /props ==="
curl -sS --max-time 20 "http://127.0.0.1:$PORT/props" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get("modalities"), indent=1)); print("media_marker=",repr(d.get("media_marker")))'
kill -TERM $PID 2>/dev/null; wait $PID 2>/dev/null; sleep 1
ss -ltn | grep -q ":$PORT " && echo "PORT STILL OPEN" || echo "port $PORT closed"
