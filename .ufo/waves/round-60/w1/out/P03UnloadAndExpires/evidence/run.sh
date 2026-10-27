#!/usr/bin/env bash
set -uo pipefail
S=/fast/scratch/hyaku/kama-r60/P03UnloadAndExpires
export TMPDIR=$S
mkdir -p "$S/home" "$S/models" "$S/out"
P=$(python3 -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1])")
NONCE=$(python3 -c "import secrets;print(secrets.token_hex(6))")
NAME="kama-$NONCE"
echo "port=$P name=$NAME" > "$S/run.env"

env -i PATH=/usr/bin:/bin HOME=$S/home OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS=$S/models \
  OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 \
  GGML_VK_VISIBLE_DEVICES=-1 ~/.local/opt/ollama-v0.40.11/bin/ollama serve >"$S/serve.log" 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null; wait $PID 2>/dev/null' EXIT
echo "pid=$PID" >> "$S/run.env"

ready=0
for i in $(seq 1 300); do
  if python3 - "$P" <<'EOF' 2>/dev/null
import sys, urllib.request
urllib.request.urlopen("http://127.0.0.1:%s/" % sys.argv[1], timeout=1).read()
EOF
  then ready=1; break; fi
  sleep 0.1
done
echo "ready=$ready" >> "$S/run.env"
if [ "$ready" != "1" ]; then echo "SERVER NOT READY"; tail -20 "$S/serve.log"; exit 3; fi

printf 'FROM %s\n' "$HOME/.cache/kama-shokunin/models/stories260K.gguf" > "$S/Modelfile"
env -i PATH=/usr/bin:/bin HOME=$S/home OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS=$S/models \
  OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 ~/.local/opt/ollama-v0.40.11/bin/ollama create "$NAME" -f "$S/Modelfile" \
  >"$S/create.log" 2>&1
echo "create_exit=$?" >> "$S/run.env"

python3 "$S/driver.py" "$P" "$S" "$NAME" > "$S/out/notes.stdout" 2>"$S/out/driver.err"
echo "driver_exit=$?" >> "$S/run.env"
tail -5 "$S/out/driver.err"
wc -l "$S/out/captures.jsonl"
