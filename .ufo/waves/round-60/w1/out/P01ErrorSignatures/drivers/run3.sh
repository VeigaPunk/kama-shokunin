#!/usr/bin/env bash
set -uo pipefail
S=/fast/scratch/hyaku/kama-r60/P01ErrorSignatures
O=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w1/out/P01ErrorSignatures
export TMPDIR="$S"
BIN=/home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama
GGUF=/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
M=$(cat "$S/model.name")
P=""
for _ in $(seq 1 20); do
  cand=$(python3 -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1])")
  case "$cand" in 8080|34113|11434) continue;; esac
  P="$cand"; break
done
[ -n "$P" ] || exit 1
echo "pass2 port=$P model=$M" >> "$S/meta.txt"

env -i PATH=/usr/bin:/bin HOME="$S/home" OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS="$S/models" \
  OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 \
  GGML_VK_VISIBLE_DEVICES=-1 "$BIN" serve >"$S/serve3.log" 2>&1 &
PID=$!
cleanup() { kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null; }
trap cleanup EXIT
for _ in $(seq 1 120); do
  curl -sS --max-time 1 "http://127.0.0.1:$P/api/version" >/dev/null 2>&1 && break
  sleep 0.5
done
printf 'FROM %s\n' "$GGUF" > "$S/Modelfile"
env -i PATH=/usr/bin:/bin HOME="$S/home" OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS="$S/models" \
  OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 \
  GGML_VK_VISIBLE_DEVICES=-1 "$BIN" create "$M" -f "$S/Modelfile" >"$S/create3.log" 2>&1
echo "CREATE3_EXIT=$?"
python3 "$S/driver3.py" "$P" "$M" "$S/captures3.jsonl"; DRV=$?
echo "DRIVER3_EXIT=$DRV"
cleanup; trap - EXIT
kill -0 "$PID" 2>/dev/null && echo "PID_STILL_ALIVE=$PID" || echo "PID_DEAD=$PID"
cp "$S/captures3.jsonl" "$O/captures-full.jsonl"
{ echo "--- pass2 port/model ---"; echo "$P $M"; echo "--- serve2 listen ---"; grep -E "Listening on" "$S/serve3.log" | head -3; } >> "$O/session.txt"
exit "$DRV"
