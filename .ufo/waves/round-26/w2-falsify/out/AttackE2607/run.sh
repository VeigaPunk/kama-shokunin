#!/usr/bin/env bash
# usage: run.sh <label> <port> <server args...>   ; then requests from REQS file
set -u
label=$1; port=$2; shift 2
d=/fast/scratch/hyaku/kama-r26w2/AttackE2607
log=$d/$label.server.log
out=$d/$label.out
: >"$out"
timeout 120 ~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port "$port" "$@" >"$log" 2>&1 &
pid=$!
for i in $(seq 1 240); do
  if curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$port/health" 2>/dev/null | grep -q 200; then break; fi
  sleep 0.25
done
echo "argv_extra: $*" >>"$out"
while IFS=$'\t' read -r method path body; do
  [ -z "$method" ] && continue
  printf '\n=== %s %s body=%s\n' "$method" "$path" "$body" >>"$out"
  if [ "$body" = "-" ]; then
    curl -sS -i -X "$method" "http://127.0.0.1:$port$path" >>"$out" 2>&1
  else
    curl -sS -i -X "$method" -H 'Content-Type: application/json' --data-binary "$body" "http://127.0.0.1:$port$path" >>"$out" 2>&1
  fi
  echo " [curl_rc=$?]" >>"$out"
done <"$d/$label.reqs"
kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
echo "server_exit=$?" >>"$out"
for i in $(seq 1 20); do ss -ltn | grep -q ":$port " || break; sleep 0.25; done
ss -ltn | grep -q ":$port " && echo "PORT_STILL_OPEN $port" >>"$out" || echo "port_closed $port" >>"$out"
