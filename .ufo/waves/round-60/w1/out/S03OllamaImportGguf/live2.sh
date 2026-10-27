set -u
S=/fast/scratch/hyaku/kama-r60/S03OllamaImportGguf
export TMPDIR=$S
P=$(python3 -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1])")
echo "port=$P"
env -i PATH=/usr/bin:/bin HOME=$S/home OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS=$S/models OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 GGML_VK_VISIBLE_DEVICES=-1 ~/.local/opt/ollama-v0.40.11/bin/ollama serve >$S/serve.log 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null' EXIT
for i in $(seq 1 150); do curl -sf -o /dev/null "http://127.0.0.1:$P/api/version" && break; sleep 0.2; done
O() { env -i PATH=/usr/bin:/bin HOME=$S/home OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS=$S/models OLLAMA_NO_CLOUD=1 ~/.local/opt/ollama-v0.40.11/bin/ollama "$@"; }
echo "== binary"; env -i PATH=/usr/bin:/bin ~/.local/opt/ollama-v0.40.11/bin/ollama --version 2>&1 | tail -1
echo "== version route"; curl -s "http://127.0.0.1:$P/api/version"; echo
printf 'FROM %s\n' "$HOME/.cache/kama-shokunin/models/stories260K.gguf" > $S/Modelfile.s03
echo "== Modelfile"; cat $S/Modelfile.s03
echo "== step1 create bare name s03g5281"
O create s03g5281 -f $S/Modelfile.s03; echo "create_exit=$?"
echo "== step2 create explicit tag s03g5281:probe"
O create s03g5281:probe -f $S/Modelfile.s03 >/dev/null 2>&1; echo "create_tagged_exit=$?"
echo "== ollama list"; O list; echo "list_exit=$?"
echo "== /api/tags names"
curl -s "http://127.0.0.1:$P/api/tags" | python3 -c "import json,sys;d=json.load(sys.stdin);print(sorted(m['name'] for m in d['models']));print({m['name']:m['digest'][:12] for m in d['models']})"
echo "== /api/show s03g5281 model_details.digest"
curl -s "http://127.0.0.1:$P/api/show" -d '{"model":"s03g5281"}' | python3 -c "import json,sys;d=json.load(sys.stdin);print('digest=',d.get('model_info',{}).get('general.basename'),'details=',d.get('details'))" 2>/dev/null || true
echo "== server log: listening line"; grep -m1 "Listening on" $S/serve.log
kill $PID 2>/dev/null; wait $PID 2>/dev/null
echo "== port closed after kill"; curl -s -o /dev/null -w '%{http_code}\n' --max-time 2 "http://127.0.0.1:$P/api/version" || echo "conn_refused"
