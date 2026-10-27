#!/usr/bin/env bash
set -uo pipefail
S=/fast/scratch/hyaku/kama-r60/P03UnloadAndExpires
export TMPDIR=$S
mkdir -p "$S/home" "$S/models" "$S/out"
NAME=$(python3 -c "import secrets;print('kama-'+secrets.token_hex(6))")
: > "$S/out/tz.jsonl"
for TZNAME in UTC Asia/Tokyo; do
  P=$(python3 -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1])")
  env -i PATH=/usr/bin:/bin HOME=$S/home TZ=$TZNAME OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS=$S/models \
    OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 \
    GGML_VK_VISIBLE_DEVICES=-1 ~/.local/opt/ollama-v0.40.11/bin/ollama serve >"$S/serve-${TZNAME//\//_}.log" 2>&1 &
  PID=$!
  ready=0
  for i in $(seq 1 300); do
    if python3 - "$P" <<'EOF' 2>/dev/null
import sys, urllib.request
urllib.request.urlopen("http://127.0.0.1:%s/" % sys.argv[1], timeout=1).read()
EOF
    then ready=1; break; fi
    sleep 0.1
  done
  if [ "$ready" != "1" ]; then echo "NOT READY $TZNAME pid=$PID"; kill $PID; wait $PID 2>/dev/null; continue; fi
  printf 'FROM %s\n' "$HOME/.cache/kama-shokunin/models/stories260K.gguf" > "$S/Modelfile"
  env -i PATH=/usr/bin:/bin HOME=$S/home TZ=$TZNAME OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS=$S/models \
    ~/.local/opt/ollama-v0.40.11/bin/ollama create "$NAME" -f "$S/Modelfile" >"$S/create-${TZNAME//\//_}.log" 2>&1
  python3 "$S/tzprobe.py" "$P" "$S" "$NAME" "$TZNAME" >> "$S/out/tz.jsonl" 2>"$S/out/tz-${TZNAME//\//_}.err"
  echo "--- $TZNAME exit=$? pid=$PID" >> "$S/out/tz.jsonl"
  kill $PID 2>/dev/null; wait $PID 2>/dev/null
done
echo "done"; grep -c . "$S/out/tz.jsonl"
