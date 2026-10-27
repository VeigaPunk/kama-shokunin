#!/bin/bash
set -u
S=/fast/scratch/hyaku/kama-r60/P02AliasAndCopy
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w1/out/P02AliasAndCopy
export TMPDIR=$S
NONCE=$(python3 -c "import secrets;print(secrets.token_hex(4))")
P=$(python3 -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1])")
echo "nonce=$NONCE port=$P"
mkdir -p "$S/home3" "$S/models3"
env -i PATH=/usr/bin:/bin HOME=$S/home3 TMPDIR=$S OLLAMA_HOST=127.0.0.1:$P OLLAMA_MODELS=$S/models3 \
  OLLAMA_NO_CLOUD=1 OLLAMA_NOPRUNE=1 CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 GGML_VK_VISIBLE_DEVICES=-1 \
  "$HOME/.local/opt/ollama-v0.40.11/bin/ollama" serve >"$S/serve3.log" 2>&1 &
SRV=$!
echo "server_pid=$SRV"
cleanup() { kill "$SRV" 2>/dev/null; }
trap cleanup EXIT
python3 "$S/capture2.py" "$P" "$OUT" "$NONCE" captures.jsonl
RC=$?
echo "capture_exit=$RC"
kill "$SRV" 2>/dev/null
for i in $(seq 1 40); do kill -0 "$SRV" 2>/dev/null || break; sleep 0.1; done
kill -0 "$SRV" 2>/dev/null && echo "server_still_alive=1" || echo "server_still_alive=0"
python3 - "$P" <<'PY'
import socket, sys
s = socket.socket(); s.settimeout(2)
print("port_after_kill=", "refused" if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) else "open")
PY
echo "--- tags-empty check ---"
python3 - <<'PY'
import json
p="/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w1/out/P02AliasAndCopy/captures.jsonl"
rows=[json.loads(l) for l in open(p)]
by={r['name']:r for r in rows}
print("tags-empty:", by['tags-empty']['body'][:80])
print("tags-all:", [m['name'] for m in json.loads(by['tags-all']['body'])['models']])
print("ps:", [(m['name'],) for m in json.loads(by['ps-after-name2']['body'])['models']])
PY
exit $RC
