#!/bin/bash
# usage: run.sh <tag> <port> <extra args...>
set -u
S=/fast/scratch/hyaku/kama-r26w2/AttackE2605
tag=$1; port=$2; shift 2
M=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
ss -ltn | grep -q ":$port " && { echo "port $port busy"; exit 3; }
timeout 120 /home/vgpnk/.local/bin/llama-server -m $M --host 127.0.0.1 --port $port "$@" >$S/$tag-server.log 2>&1 </dev/null &
pid=$!
for i in $(seq 1 120); do
  c=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:$port/health); [ "$c" = 200 ] && break; sleep 0.25
done
echo "health=$c"
for p in /v1/embeddings /embedding /embeddings /v1/embedding; do
  f=$S/$tag-$(echo $p | tr / _).out
  curl -s -o $f -w "$p status=%{http_code}\n" -X POST -H 'Content-Type: application/json' --data '{"model": "stories260K", "input": "hello"}' http://127.0.0.1:$port$p
  echo "  body: $(cat $f)"
done
kill -TERM $pid; wait $pid; echo "server exit=$?"
sleep 0.5; ss -ltn | grep -q ":$port " && echo "port $port STILL OPEN" || echo "port $port closed"
