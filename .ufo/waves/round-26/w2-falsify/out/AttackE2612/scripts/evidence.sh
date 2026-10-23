#!/bin/bash
set -u
PORT=47744
MODEL=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
O=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/AttackE2612
ss -ltn | grep -E ':(4774[4-7])\b' && { echo "PORT BUSY"; exit 1; }
echo "== launch ==" 
echo "timeout 300 ~/.local/bin/llama-server -m $MODEL --host 127.0.0.1 --port $PORT -t 2"
timeout 300 /home/vgpnk/.local/bin/llama-server -m "$MODEL" --host 127.0.0.1 --port $PORT -t 2 > "$O/server-47744.log" 2>&1 &
PID=$!
for i in $(seq 1 240); do s=$(curl -s -o /dev/null -w '%{http_code}' --max-time 1 "http://127.0.0.1:$PORT/health" 2>/dev/null); [ "$s" = "200" ] && { echo "GET /health -> 200 after $i tries"; break; }; sleep 0.25; done
{
echo "== [A] registry-exact trigger: POST /v1/audio/transcriptions, Content-Type application/json, body {} =="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions" -H 'Content-Type: application/json' -d '{}'; echo; echo "curl_exit=$?"
echo
echo "== [B] body not-json (guard precedes json::parse?) =="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions" -H 'Content-Type: application/json' -d 'not-json'; echo; echo "curl_exit=$?"
echo
echo "== [C] bodyless POST, no Content-Type (row trigger text alone) =="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions"; echo; echo "curl_exit=$?"
echo
echo "== [D] multipart upload =="
curl -sS -i --max-time 20 -X POST "http://127.0.0.1:$PORT/v1/audio/transcriptions" -F "file=@/etc/hostname" -F "model=stories260K"; echo; echo "curl_exit=$?"
echo
echo "== [E] GET same path =="
curl -sS -i --max-time 20 "http://127.0.0.1:$PORT/v1/audio/transcriptions"; echo; echo "curl_exit=$?"
echo
echo "== [F] /props modalities =="
curl -sS --max-time 20 "http://127.0.0.1:$PORT/props" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({"modalities":d.get("modalities"),"build_info":d.get("build_info")}, sort_keys=True))'
} 2>&1 | tee "$O/trigger-47744.out"
kill -TERM $PID 2>/dev/null; wait $PID 2>/dev/null; sleep 1
ss -ltn | grep -q ":$PORT " && echo "PORT STILL OPEN" || echo "port $PORT closed"
echo "== startup log grep for signature =="
grep -c "does not support audio input" "$O/server-47744.log"; echo "grep_exit=$?"
echo "== response body sha256 =="
printf '%s' '{"error":{"code":501,"message":"The current model does not support audio input.","type":"not_supported_error"}}' | sha256sum
