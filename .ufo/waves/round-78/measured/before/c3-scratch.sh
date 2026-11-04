#!/usr/bin/env bash
# round-78 C3 before/control harness (wave evidence, not the claim counter).
# Usage: c3-scratch.sh <scratch-root> <live|dead>
#   live — start the pinned llama-server child on a scratch port, then probe
#   dead — probe the same three-row registry with no server listening
# Prints the probe's stdout/stderr and its exit; the child is always torn down.
set -uo pipefail

S=${1:?scratch root}
MODE=${2:?live|dead}
mkdir -p "$S"
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
BIN=$HOME/.local/opt/llama-b11755/llama-server
MODEL=$HOME/.cache/kama-shokunin/models/stories260K.gguf
PORT=38517
DEADPORT=38518

printf 'baseURL=http://127.0.0.1:%s/v1\n' "$PORT" > "$S/pin-live.txt"
printf 'baseURL=http://127.0.0.1:%s/v1\n' "$DEADPORT" > "$S/pin-dead.txt"
{
  printf 'id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n'
  printf 'live-match\t%s\tgrep:http://\thttp://127.0.0.1:%s/v1\tstories260K\tround-78 scratch row\n' "$S/pin-live.txt" "$PORT"
  printf 'live-mismatch\t%s\tgrep:http://\thttp://127.0.0.1:%s/v1\tdefinitely-not-the-model\tround-78 scratch row\n' "$S/pin-live.txt" "$PORT"
  printf 'dead-row\t%s\tgrep:http://\thttp://127.0.0.1:%s/v1\t-\tround-78 scratch row\n' "$S/pin-dead.txt" "$DEADPORT"
} > "$S/registry.tsv"

SPID=""
cleanup() { [ -n "$SPID" ] && kill "$SPID" 2>/dev/null && wait "$SPID" 2>/dev/null; }
trap cleanup EXIT

if [ "$MODE" = live ]; then
  "$BIN" -m "$MODEL" --host 127.0.0.1 --port "$PORT" -c 256 --parallel 1 > "$S/server.log" 2>&1 &
  SPID=$!
  for _ in $(seq 1 120); do
    if curl -s -o /dev/null -m 1 "http://127.0.0.1:$PORT/health"; then break; fi
    sleep 0.5
  done
  curl -sS -m 2 "http://127.0.0.1:$PORT/health" >/dev/null || { echo "COULD-NOT-EVALUATE: child never answered /health"; exit 2; }
fi

bash "$LANE/tools/kama-probe.sh" check --registry "$S/registry.tsv" --timeout 2 --connect-timeout 1
rc=$?
echo "PROBE_EXIT=$rc"
exit "$rc"
