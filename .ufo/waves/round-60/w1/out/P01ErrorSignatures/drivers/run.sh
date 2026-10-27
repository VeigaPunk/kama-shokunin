#!/usr/bin/env bash
set -uo pipefail
S=/fast/scratch/hyaku/kama-r60/P01ErrorSignatures
O=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w1/out/P01ErrorSignatures
mkdir -p "$S/home" "$S/models" "$O"
export TMPDIR="$S"
BIN=/home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama
GGUF=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
M="p01errsig-$(python3 -c 'import secrets;print(secrets.token_hex(4))')"
P=""
for _ in $(seq 1 20); do
  cand=$(python3 -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1])")
  case "$cand" in 8080|34113|11434) continue;; esac
  P="$cand"; break
done
[ -n "$P" ] || { echo "NO_PORT" >&2; exit 1; }
echo "$M" > "$S/model.name"; echo "$P" > "$S/port"
{
  echo "seat=P01ErrorSignatures"; echo "port=$P"; echo "model=$M"
  sha256sum "$BIN" "$GGUF"
  "$BIN" --version 2>&1 | head -2
} > "$S/meta.txt"

env -i PATH=/usr/bin:/bin HOME="$S/home" OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS="$S/models" \
  OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 \
  GGML_VK_VISIBLE_DEVICES=-1 "$BIN" serve >"$S/serve.log" 2>&1 &
PID=$!
cleanup() { kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null; }
trap cleanup EXIT

ok=0
for _ in $(seq 1 120); do
  if curl -sS --max-time 1 "http://127.0.0.1:$P/api/version" >"$S/ready.txt" 2>/dev/null; then ok=1; break; fi
  sleep 0.5
done
[ "$ok" = 1 ] || { echo "SERVER_NOT_READY"; tail -20 "$S/serve.log"; exit 1; }

printf 'FROM %s\n' "$GGUF" > "$S/Modelfile"
env -i PATH=/usr/bin:/bin HOME="$S/home" OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS="$S/models" \
  OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 \
  GGML_VK_VISIBLE_DEVICES=-1 "$BIN" create "$M" -f "$S/Modelfile" >"$S/create.log" 2>&1
echo "CREATE_EXIT=$?"
cat "$S/create.log"

python3 "$S/driver.py" "$P" "$M" "$S/captures.jsonl"
DRV=$?
echo "DRIVER_EXIT=$DRV"

# server-side evidence: log size, listener identity from the log line
grep -E "Listening on|Ollama" "$S/serve.log" | head -5 > "$S/serve-listen.txt"

cleanup; trap - EXIT
sleep 0.5
kill -0 "$PID" 2>/dev/null && echo "PID_STILL_ALIVE=$PID" || echo "PID_DEAD=$PID"

cp "$S/captures.jsonl" "$S/meta.txt" "$O/"
{ echo "--- meta ---"; cat "$S/meta.txt"; echo "--- ready /api/version ---"; cat "$S/ready.txt"; echo;
  echo "--- serve.log (listen + errors) ---"; grep -E "Listening on|error|level=ERROR" "$S/serve.log" | head -10; } > "$O/session.txt"
wc -l "$O/captures.jsonl"
exit "$DRV"
